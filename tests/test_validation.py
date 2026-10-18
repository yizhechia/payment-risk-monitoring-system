"""Contract violations must be visible and must not publish an analytical database."""

import json
from decimal import Decimal

import duckdb
import pytest

from payment_risk.contracts import (
    BALANCES,
    COLUMNS,
    MONEY,
    MONEY_TYPE,
    REQUEST_COLUMNS,
    fingerprint,
)
from payment_risk.pipeline import ValidationError, ingest


def test_exact_money_and_layer_separation(demo_run):
    output, report = demo_run
    assert report["status"] == "passed"
    assert report["input_mode"] == "fixture"
    assert report["observed"]["rows"] == 12
    assert report["observed"]["fraud_rows"] == 3
    assert report["observed"]["flagged_rows"] == 2
    assert report["observed"]["min_step"] == 1
    assert report["observed"]["max_step"] == 5
    assert report["observed"]["distinct_steps"] == 4
    assert report["observed"]["merchant_zero_balance_rows"] == 3
    assert all(count == 0 for count in report["value_checks"].values())
    assert all(precision <= 2 for precision in report["maximum_effective_decimal_places"].values())
    assert json.loads((output / "validation.json").read_text()) == report
    with duckdb.connect(str(output / "payments.duckdb"), read_only=True) as db:
        columns = tuple(row[0] for row in db.execute("DESCRIBE request_transactions").fetchall())
        assert columns == REQUEST_COLUMNS
        assert not (set(BALANCES) | {"isFraud", "isFlaggedFraud"}) & set(columns)
        assert db.execute("SELECT sum(amount) FROM transactions").fetchone()[0] == Decimal(
            "1020153.40"
        )
        assert db.execute("SELECT amount FROM transactions WHERE row_id = 2").fetchone()[
            0
        ] == Decimal("10.10")
        assert db.execute("SELECT count(DISTINCT row_id) FROM transactions").fetchone()[0] == 12
        assert json.loads(db.execute("SELECT document FROM run_metadata").fetchone()[0]) == report
    assert report["observed"]["typed_schema"]["amount"] == MONEY_TYPE


@pytest.mark.parametrize("field", COLUMNS)
@pytest.mark.parametrize("missing", ["", " "])
def test_missing_fields_fail(field, missing, demo_rows, make_csv, tmp_path):
    demo_rows[0][field] = missing
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(make_csv(demo_rows), output, canonical=False)
    report = json.loads((output / "validation.json").read_text())
    assert report["value_checks"][f"missing_{field}"] == 1
    assert report["status"] == "failed"
    assert not (output / "payments.duckdb").exists()


@pytest.mark.parametrize("field", MONEY)
@pytest.mark.parametrize(
    "value",
    [
        "-1",
        "NaN",
        "Infinity",
        "1.001",
        "1e-3",
        "10000000000000000",
    ],
)
def test_invalid_money_rejected_without_rounding(field, value, demo_rows, make_csv, tmp_path):
    demo_rows[0][field] = value
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(make_csv(demo_rows), output, canonical=False)
    report = json.loads((output / "validation.json").read_text())
    assert report["value_checks"][f"invalid_{field}"] == 1
    assert not (output / "payments.duckdb").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("step", "0"),
        ("step", "-1"),
        ("step", "1.5"),
        ("step", "2147483648"),
        ("type", "WIRE"),
        ("isFraud", "2"),
        ("isFraud", "True"),
        ("isFlaggedFraud", "-1"),
    ],
)
def test_invalid_categories_and_steps(field, value, demo_rows, make_csv, tmp_path):
    demo_rows[0][field] = value
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(make_csv(demo_rows), output, canonical=False)
    assert json.loads((output / "validation.json").read_text())["errors"]
    assert not (output / "payments.duckdb").exists()


def test_duplicates_are_measured_and_retained(demo_rows, make_csv, tmp_path):
    demo_rows.append(demo_rows[0].copy())
    output = tmp_path / "duplicates"
    report = ingest(make_csv(demo_rows), output, canonical=False)
    assert report["observed"]["duplicate_extra_rows"] == 1
    assert report["observed"]["rows"] == 13
    assert any("retained" in warning for warning in report["warnings"])


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1.916920493E7", "19169204.93"),
        ("123E-2", "1.23"),
        ("1e3", "1000.00"),
        ("0.01", "0.01"),
    ],
)
def test_raw_scientific_values_are_preserved_exactly(raw, expected, demo_rows, make_csv, tmp_path):
    demo_rows[0]["amount"] = raw
    output = tmp_path / "precision"
    report = ingest(make_csv(demo_rows), output, canonical=False)
    assert report["maximum_effective_decimal_places"]["amount"] == 2
    with duckdb.connect(str(output / "payments.duckdb"), read_only=True) as db:
        amount = db.execute("SELECT amount FROM transactions WHERE row_id = 1").fetchone()[0]
    assert amount == Decimal(expected)


@pytest.mark.parametrize("kind", ["header", "short_row", "extra_column", "empty", "invalid_utf8"])
def test_schema_and_parser_failures(kind, demo_rows, make_csv, tmp_path):
    path = make_csv(demo_rows if kind != "empty" else [])
    text = path.read_text()
    if kind == "header":
        path.write_text(text.replace("oldbalanceOrg", "oldbalanceOrig", 1))
    elif kind == "short_row":
        path.write_text(text + "1,TRANSFER,10\n")
    elif kind == "extra_column":
        lines = text.splitlines()
        lines[1] += ",unexpected"
        path.write_text("\n".join(lines) + "\n")
    elif kind == "invalid_utf8":
        path.write_bytes(text.encode() + b"\xff\n")
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(path, output, canonical=False)
    assert json.loads((output / "validation.json").read_text())["status"] == "failed"
    assert not (output / "payments.duckdb").exists()


def test_hash_mismatch_fails_before_parsing(demo_rows, make_csv, tmp_path):
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(make_csv(demo_rows), output, canonical=False, expected_sha256="0" * 64)
    assert "SHA-256" in (output / "validation.json").read_text()
    assert not (output / "payments.duckdb").exists()


def test_fixture_cannot_be_promoted_to_canonical(demo_rows, make_csv, tmp_path):
    path = make_csv(demo_rows)
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(path, output, canonical=True, expected_sha256=fingerprint(path)["sha256"])
    assert "no override allowed" in (output / "validation.json").read_text()


def test_missing_input_emits_report(tmp_path):
    output = tmp_path / "bad"
    with pytest.raises(ValidationError):
        ingest(tmp_path / "missing.csv", output, canonical=False)
    assert "FileNotFoundError" in (output / "validation.json").read_text()


def test_existing_output_is_never_overwritten(demo_run, make_csv, demo_rows):
    output, _ = demo_run
    before = fingerprint(output / "payments.duckdb")
    with pytest.raises(FileExistsError):
        ingest(make_csv(demo_rows), output, canonical=False)
    assert fingerprint(output / "payments.duckdb") == before
