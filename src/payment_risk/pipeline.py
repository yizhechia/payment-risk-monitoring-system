"""Strict, non-destructive ingestion. No imputation, row removal or predictive modelling."""

import csv
import json
import platform
import tempfile
from pathlib import Path

import duckdb

from payment_risk import __version__
from payment_risk.contracts import (
    BALANCES,
    COLUMNS,
    MONEY,
    MONEY_SCALE,
    MONEY_TYPE,
    REQUEST_COLUMNS,
    TYPES,
    fingerprint,
    manifest,
)


class ValidationError(ValueError):
    """The validation report explains why no analytical database was published."""


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, default=str, allow_nan=False) + "\n", encoding="utf-8"
    )


def _money_expressions(field: str) -> tuple[str, str, str]:
    """Validate decimal/scientific syntax and scale before a cast can round it."""
    pattern = "[0-9]+(?:\\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?"
    fraction = f"regexp_extract({field}, '{pattern}', 1)"
    raw_exponent = f"regexp_extract({field}, '{pattern}', 2)"
    exponent = f"CASE WHEN {raw_exponent} = '' THEN 0 ELSE try_cast({raw_exponent} AS INTEGER) END"
    scale = f"greatest(0, length({fraction})::BIGINT - ({exponent}))"
    return pattern, exponent, scale


def _value_checks(connection: duckdb.DuckDBPyConnection, report: dict) -> None:
    expressions = []
    names = []
    for field in COLUMNS:
        names.append(f"missing_{field}")
        expressions.append(f"count(*) FILTER (WHERE {field} IS NULL OR trim({field}) = '')")
    for field in MONEY:
        pattern, exponent, scale = _money_expressions(field)
        names.append(f"invalid_{field}")
        expressions.append(
            f"count(*) FILTER (WHERE {field} IS NOT NULL AND "
            f"(NOT regexp_full_match({field}, '{pattern}') "
            f"OR ({exponent}) IS NULL OR ({scale}) > {MONEY_SCALE} "
            f"OR try_cast({field} AS {MONEY_TYPE}) IS NULL))"
        )
    names.extend(["invalid_step", "invalid_type", "invalid_isFraud", "invalid_isFlaggedFraud"])
    types = ",".join(f"'{value}'" for value in TYPES)
    expressions.extend(
        [
            "count(*) FILTER (WHERE step IS NOT NULL AND "
            "(NOT regexp_full_match(step, '[0-9]+') OR try_cast(step AS INTEGER) IS NULL "
            "OR try_cast(step AS INTEGER) < 1))",
            f"count(*) FILTER (WHERE type IS NOT NULL AND type NOT IN ({types}))",
            "count(*) FILTER (WHERE isFraud IS NOT NULL AND isFraud NOT IN ('0', '1'))",
            "count(*) FILTER (WHERE isFlaggedFraud IS NOT NULL "
            "AND isFlaggedFraud NOT IN ('0', '1'))",
        ]
    )
    counts = connection.execute("SELECT " + ",".join(expressions) + " FROM raw").fetchone()
    report["value_checks"] = dict(zip(names, counts, strict=True))
    for name, count in report["value_checks"].items():
        if count:
            report["errors"].append(f"{name}: {count} row(s)")
    precision_sql = ",".join(f"max({_money_expressions(name)[2]})" for name in MONEY)
    precision = connection.execute(f"SELECT {precision_sql} FROM raw").fetchone()
    report["maximum_effective_decimal_places"] = dict(zip(MONEY, precision, strict=True))
    scientific = connection.execute(
        "SELECT "
        + ",".join(f"count(*) FILTER (WHERE regexp_matches({name}, '[eE]'))" for name in MONEY)
        + " FROM raw"
    ).fetchone()
    report["scientific_notation_rows"] = dict(zip(MONEY, scientific, strict=True))


def _create_typed(connection: duckdb.DuckDBPyConnection) -> None:
    money = set(MONEY)
    fields = []
    for name in COLUMNS:
        kind = (
            MONEY_TYPE
            if name in money
            else (
                "INTEGER"
                if name == "step"
                else "UTINYINT"
                if name in {"isFraud", "isFlaggedFraud"}
                else "VARCHAR"
            )
        )
        fields.append(f"cast({name} AS {kind}) AS {name}")
    connection.execute(
        "CREATE TEMP TABLE typed AS SELECT row_id, " + ",".join(fields) + " FROM raw"
    )


def _measure(connection: duckdb.DuckDBPyConnection, report: dict) -> None:
    names = ["rows", "fraud_rows", "flagged_rows", "min_step", "max_step", "distinct_steps"]
    values = connection.execute(
        "SELECT count(*), sum(isFraud), sum(isFlaggedFraud), min(step), max(step), "
        "count(DISTINCT step) FROM typed"
    ).fetchone()
    report["observed"].update(dict(zip(names, values, strict=True)))
    columns = ",".join(COLUMNS)
    duplicates = connection.execute(
        f"SELECT coalesce(sum(n - 1), 0) FROM "
        f"(SELECT {columns}, count(*) AS n FROM typed GROUP BY {columns} HAVING count(*) > 1)"
    ).fetchone()[0]
    report["observed"]["duplicate_extra_rows"] = int(duplicates)
    if duplicates:
        report["warnings"].append(
            f"{duplicates} value-identical extra row(s) retained; "
            "no business ID proves duplication."
        )
    merchants = connection.execute(
        "SELECT count(*) FROM typed WHERE starts_with(nameDest, 'M') "
        "AND oldbalanceDest = 0 AND newbalanceDest = 0"
    ).fetchone()[0]
    report["observed"]["merchant_zero_balance_rows"] = merchants
    report["warnings"].append(
        "Merchant balance zeros are structurally unavailable, not verified zero balances."
    )
    report["observed"]["transaction_types"] = dict(
        connection.execute(
            "SELECT type, count(*) FROM typed GROUP BY type ORDER BY type"
        ).fetchall()
    )
    report["observed"]["typed_schema"] = {
        row[0]: row[1] for row in connection.execute("DESCRIBE typed").fetchall()
    }
    report["observed"]["money_ranges"] = {
        name: dict(
            zip(
                ("minimum", "maximum"),
                (
                    str(value)
                    for value in connection.execute(
                        f"SELECT min({name}), max({name}) FROM typed"
                    ).fetchone()
                ),
                strict=True,
            )
        )
        for name in MONEY
    }


def _publish_tables(connection: duckdb.DuckDBPyConnection, report: dict) -> None:
    connection.execute("BEGIN TRANSACTION")
    try:
        groups = {
            "request_transactions": REQUEST_COLUMNS,
            "audit_balances": ("row_id", *BALANCES),
            "outcomes": ("row_id", "isFraud"),
            "legacy_policy": ("row_id", "isFlaggedFraud"),
        }
        for name, fields in groups.items():
            connection.execute(f"CREATE TABLE {name} AS SELECT {','.join(fields)} FROM typed")
        connection.execute(
            "CREATE VIEW transactions AS SELECT r.*, a.* EXCLUDE(row_id), "
            "o.isFraud, p.isFlaggedFraud FROM request_transactions r "
            "JOIN audit_balances a USING(row_id) JOIN outcomes o USING(row_id) "
            "JOIN legacy_policy p USING(row_id)"
        )
        connection.execute("CREATE TABLE run_metadata (document JSON)")
        connection.execute("INSERT INTO run_metadata VALUES (?)", [json.dumps(report)])
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise


def ingest(
    csv_path: Path, output: Path, *, canonical: bool = True, expected_sha256: str | None = None
) -> dict:
    """Publish a database only on success. Each run requires a new output directory."""
    csv_path = csv_path.resolve()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    spec = manifest()
    report = {
        "status": "failed",
        "input_mode": "canonical_paysim" if canonical else "fixture",
        "dataset": spec["dataset"] if canonical else "HANDCRAFTED SOFTWARE FIXTURE - NOT PAYSIM",
        "dataset_version": spec["version"] if canonical else None,
        "software": {
            "package": __version__,
            "python": platform.python_version(),
            "duckdb": duckdb.__version__,
        },
        "money_type": f"{MONEY_TYPE}; preserve source precision; reject excess rather than round",
        "observed": {},
        "errors": [],
        "warnings": [],
    }
    try:
        report["observed"].update(fingerprint(csv_path))
        pin = spec["sha256"] if canonical else expected_sha256
        report["expected_sha256"] = pin if canonical else expected_sha256
        if canonical:
            if expected_sha256 and expected_sha256 != pin:
                report["errors"].append(
                    "Expected SHA-256 conflicts with the pinned canonical manifest; "
                    "no override allowed."
                )
            if not pin:
                report["errors"].append(
                    "Canonical SHA-256 is not pinned; review acquisition first."
                )
            if csv_path.name != spec["filename"]:
                report["errors"].append("Filename differs from the canonical manifest.")
            if report["observed"]["bytes"] != spec["bytes"]:
                report["errors"].append("Byte size differs from the canonical manifest.")
        if report["expected_sha256"]:
            if report["observed"]["sha256"] != report["expected_sha256"]:
                report["errors"].append("SHA-256 differs from the expected artifact.")
        with csv_path.open(newline="", encoding="utf-8") as source:
            header = next(csv.reader(source), [])
        report["observed"]["headers"] = header
        if header != list(COLUMNS):
            report["errors"].append("Exact header names/order differ from the schema contract.")
        if not report["errors"]:
            with tempfile.TemporaryDirectory(prefix="validation-", dir=output) as temporary:
                database = Path(temporary) / "payments.duckdb"
                connection = duckdb.connect(
                    str(database), config={"threads": 1, "memory_limit": "1GB"}
                )
                try:
                    columns = "{" + ",".join(f"'{name}':'VARCHAR'" for name in COLUMNS) + "}"
                    connection.execute(
                        "CREATE TEMP TABLE raw AS SELECT row_number() OVER () AS row_id, * "
                        "FROM read_csv(?, columns=" + columns + ", header=true, "
                        "auto_detect=false, delim=',', quote='\"', escape='\"', nullstr='', "
                        "parallel=false, strict_mode=true, ignore_errors=false)",
                        [str(csv_path)],
                    )
                    row_count = connection.execute("SELECT count(*) FROM raw").fetchone()[0]
                    if not row_count:
                        report["errors"].append("No transaction rows found.")
                    _value_checks(connection, report)
                    if not report["errors"]:
                        _create_typed(connection)
                        _measure(connection, report)
                        if canonical:
                            for observed, expected in [
                                ("rows", "rows"),
                                ("fraud_rows", "fraud_rows"),
                            ]:
                                if report["observed"][observed] != spec[expected]:
                                    report["errors"].append(
                                        f"Observed {observed} differs from manifest."
                                    )
                        if fingerprint(csv_path) != {
                            key: report["observed"][key] for key in ("filename", "bytes", "sha256")
                        }:
                            report["errors"].append("Raw file changed during ingestion.")
                        if not report["errors"]:
                            report["status"] = "passed"
                            _publish_tables(connection, report)
                finally:
                    connection.close()
                if not report["errors"]:
                    database.rename(output / "payments.duckdb")
    except (OSError, UnicodeError, csv.Error, duckdb.Error) as error:
        report["status"] = "failed"
        report["errors"].append(f"{type(error).__name__}: {error}")
    write_json(output / "validation.json", report)
    if report["errors"]:
        raise ValidationError(f"Validation failed. See {output / 'validation.json'}")
    return report
