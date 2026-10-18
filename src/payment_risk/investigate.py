"""Execute versioned, parameterised SQL and reconcile the published summaries."""

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import duckdb

from payment_risk.contracts import MONEY_SCALE, MONEY_TYPE, sql_text
from payment_risk.pipeline import write_json

QUERIES = (
    ("00_overview", "Population and existing-policy audit", ("minimum_amount",)),
    ("01_volume_by_step", "Transaction and fraud trends", ()),
    ("02_risk_by_type", "Risk by transaction type", ()),
    ("03_high_value", "High-value investigation sample", ("minimum_amount", "result_limit")),
    ("04_repeat_entities", "Repeated senders and recipients", ("result_limit",)),
    ("05_pair_concentration", "Sender-recipient concentration", ("result_limit",)),
    ("06_prior_hour_activity", "Previous completed-hour activity", ("result_limit",)),
    ("07_receiver_fraud_concentration", "Outcome-selected recipient leads", ("result_limit",)),
    ("08_account_history", "Account history", ("account_id", "result_limit")),
)


def query(connection: duckdb.DuckDBPyConnection, name: str, parameters: dict) -> list[dict]:
    cursor = connection.execute(sql_text(name), parameters)
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]


def reconcile(results: dict, validation: dict) -> None:
    overview = results["00_overview"][0]
    for name in ("01_volume_by_step", "02_risk_by_type"):
        for column in ("transactions", "fraud_transactions", "total_amount"):
            if sum(row[column] for row in results[name]) != overview[column]:
                raise ValueError(f"Reconciliation failed: {name}.{column}")
    if overview["transactions"] != validation["observed"]["rows"]:
        raise ValueError("Investigated row count differs from the validated input.")
    if overview["fraud_transactions"] != validation["observed"]["fraud_rows"]:
        raise ValueError("Investigated fraud count differs from validation.")
    confusion = sum(
        overview[f"legacy_{name}"]
        for name in ("true_positives", "false_positives", "false_negatives", "true_negatives")
    )
    if confusion != overview["transactions"]:
        raise ValueError("Legacy-policy confusion counts do not cover the population.")
    if (
        overview["legacy_true_positives"] + overview["legacy_false_negatives"]
        != overview["fraud_transactions"]
    ):
        raise ValueError("Legacy-policy fraud counts differ from the observed labels.")
    if (
        overview["legacy_true_positives"] + overview["legacy_false_positives"]
        != validation["observed"]["flagged_rows"]
    ):
        raise ValueError("Legacy-policy flag counts differ from validation.")


def _cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _table(rows: list[dict], maximum: int = 8) -> str:
    if not rows:
        return "No matching rows.\n"
    keys = list(rows[0])
    lines = ["| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    lines.extend(
        "| " + " | ".join(_cell(row[key]) for key in keys) + " |" for row in rows[:maximum]
    )
    if len(rows) > maximum:
        lines.extend(["", f"Showing {maximum} of {len(rows)} returned rows; see results.json."])
    return "\n".join(lines) + "\n"


def findings(results: dict, minimum_amount: Decimal) -> list[str]:
    overview = results["00_overview"][0]
    fraud_types = [
        f"{row['type']}: {row['fraud_transactions']:,}/{row['transactions']:,}"
        for row in results["02_risk_by_type"]
        if row["fraud_transactions"]
    ]
    distribution = "; ".join(fraud_types) if fraud_types else "No labelled fraud observed"
    high_count = overview["high_value_transactions"]
    high_fraud = overview["high_value_fraud_transactions"]
    amount_finding = (
        f"At the declared review cutoff of {minimum_amount} local-currency units, "
        f"{high_count:,} payments contain {high_fraud:,} labelled fraud outcomes, out of "
        f"{overview['fraud_transactions']:,} labelled fraud outcomes overall. "
        "The cutoff is an investigation assumption, not an optimised or validated decision policy."
    )
    receivers = results["07_receiver_fraud_concentration"]
    if receivers:
        top = receivers[0]
        recurrence = (
            f"The highest-ranked fraud-linked recipient, {top['nameDest']}, has "
            f"{top['fraud_transactions']:,} labelled fraud payments among "
            f"{top['transactions']:,} payments from {top['distinct_senders']:,} distinct senders. "
            "This lead was selected using outcomes. It is not an authorisation-time signal "
            "and does not establish a fraud network or coordinated behaviour."
        )
    else:
        recurrence = "No fraud-linked recipient lead is available in this input."
    return [
        f"Labelled fraud by transaction type: {distribution}. "
        "Compare the denominators; transaction type alone is not a fraud verdict.",
        amount_finding,
        recurrence,
    ]


def investigate(
    output: Path,
    validation: dict,
    *,
    minimum_amount: Decimal = Decimal("200000"),
    result_limit: int = 25,
    account_id: str | None = None,
) -> dict:
    if not minimum_amount.is_finite() or minimum_amount < 0 or minimum_amount >= 10**16:
        raise ValueError(f"Review cutoff must be finite, non-negative and fit {MONEY_TYPE}.")
    if minimum_amount.as_tuple().exponent < -MONEY_SCALE:
        raise ValueError(f"Review cutoff supports at most {MONEY_SCALE} decimal places.")
    if not 1 <= result_limit <= 1000:
        raise ValueError("result_limit must be between 1 and 1000.")
    with duckdb.connect(
        str(output / "payments.duckdb"),
        read_only=True,
        config={"threads": 1, "memory_limit": "2GB", "preserve_insertion_order": False},
    ) as connection:
        recorded = json.loads(connection.execute("SELECT document FROM run_metadata").fetchone()[0])
        if validation != recorded or validation["status"] != "passed":
            raise ValueError(
                "Supplied validation does not match this database's successful ingestion."
            )
        if account_id is None:
            account_id = connection.execute(
                "SELECT nameOrig FROM request_transactions GROUP BY nameOrig "
                "ORDER BY count(*) DESC, nameOrig LIMIT 1"
            ).fetchone()[0]
        parameters = {
            "minimum_amount": minimum_amount,
            "result_limit": result_limit,
            "account_id": account_id,
        }
        results = {}
        execution = []
        for name, title, needed in QUERIES:
            bound = {key: parameters[key] for key in needed}
            try:
                results[name] = query(connection, name, bound)
            except duckdb.Error as error:
                raise ValueError(f"SQL investigation {name} failed: {error}") from error
            execution.append(
                {
                    "query": name,
                    "question": title,
                    "parameters": bound,
                    "sql_sha256": hashlib.sha256(sql_text(name).encode()).hexdigest(),
                    "rows_returned": len(results[name]),
                }
            )
    reconcile(results, validation)
    observations = findings(results, minimum_amount)
    document = {
        "input_mode": validation["input_mode"],
        "input_sha256": validation["observed"]["sha256"],
        "reconciliation": "passed",
        "execution": execution,
        "findings": observations,
        "results": results,
    }
    write_json(output / "results.json", document)
    title = (
        "PaySim SQL Investigation"
        if validation["input_mode"] == "canonical_paysim"
        else ("Software Demo - Handcrafted Fixture, NOT PaySim Results")
    )
    lines = [
        f"# {title}",
        "",
        f"Input SHA-256: `{document['input_sha256']}`.",
        "",
        "Synthetic data only. All fraud labels are retrospective. Monetary values are "
        "unspecified local-currency units. No model has been trained and no production "
        "performance or prevented loss is claimed.",
        "",
        "## Investigation findings",
        "",
    ]
    lines.extend(f"{i}. {text}" for i, text in enumerate(observations, 1))
    overview = results["00_overview"][0]
    lines.extend(
        [
            "",
            "## Existing-policy audit",
            "",
            f"The supplied flag disagrees with `type = 'TRANSFER' AND amount > 200000` on "
            f"{overview['legacy_description_disagreements']:,} of "
            f"{overview['transactions']:,} transactions. "
            "This checks the publisher's short description against the actual flag; "
            "it does not rewrite the flag or infer undocumented simulator conditions. "
            "The flag remains a separately labelled benchmark.",
        ]
    )
    lines.extend(
        [
            "",
            "## Query results",
            "",
            "Per-query SQL hashes, bound parameters and all returned rows are in "
            "results.json. Time and type totals reconcile exactly to the validated input. "
            "Long listings are limited intentionally; an empty sample is not proof of no risk.",
            "",
        ]
    )
    for name, title, _ in QUERIES:
        lines.extend([f"### {title}", "", f"Query: `{name}.sql`.", "", _table(results[name]), ""])
    lines.extend(
        [
            "## Interpretation limits",
            "",
            "- Same-step row IDs break display ties only; they do not establish event order.",
            "- Whole-period repeats and pair shares are retrospective, not time-safe features.",
            "- The previous-hour query uses only step t-1; gaps are not compressed.",
            "- Recipient leads use fraud outcomes for selection and cannot be used as predictors.",
            "- Legacy-policy counts audit the supplied flag; they do not evaluate a new strategy.",
            "- Labelled transaction value is not realised fraud loss or recoverable exposure.",
            "- The monetary representation rejects unsupported precision rather than rounding.",
            "- No causal inference or claim about real customer behaviour follows from PaySim.",
            "",
        ]
    )
    attribution = (
        "PaySim: Edgar Lopez-Rojas and collaborators, "
        "[Synthetic Financial Datasets For Fraud Detection]"
        "(https://www.kaggle.com/datasets/ealaxi/paysim1), version 2, "
        "[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). "
        "This report aggregates and selects synthetic source records; it is not endorsed by "
        "the dataset authors. Dataset-derived tables and summaries retain CC BY-SA 4.0 attribution."
        if validation["input_mode"] == "canonical_paysim"
        else "Input is a project-authored software fixture, not a selection from PaySim."
    )
    lines.extend(["## Data attribution", "", attribution, ""])
    (output / "investigation.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(
        output / "run.json",
        {
            "status": "passed",
            "input_mode": validation["input_mode"],
            "input_sha256": document["input_sha256"],
            "queries_executed": len(QUERIES),
            "reconciliation": "passed",
        },
    )
    return document
