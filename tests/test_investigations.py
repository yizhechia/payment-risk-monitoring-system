"""Reconcile SQL with hand-counted outcomes and probe temporal/investigation boundaries."""

import copy
import json
from decimal import Decimal

import duckdb
import pytest

from payment_risk.investigate import investigate, query, reconcile
from payment_risk.pipeline import ingest


def test_hand_counted_sql_results(demo_run):
    output, validation = demo_run
    document = investigate(output, validation, account_id="Cdemo01")
    result = document["results"]
    overview = result["00_overview"][0]
    assert overview["transactions"] == 12
    assert overview["total_amount"] == Decimal("1020153.40")
    assert overview["fraud_transactions"] == 3
    assert overview["high_value_transactions"] == 4
    assert overview["high_value_fraud_transactions"] == 3
    assert overview["transfers_above_documented_cutoff"] == 3
    assert overview["legacy_description_disagreements"] == 1
    assert [
        overview[f"legacy_{label}"]
        for label in ("true_positives", "false_positives", "false_negatives", "true_negatives")
    ] == [1, 1, 2, 8]
    by_type = {row["type"]: row for row in result["02_risk_by_type"]}
    assert by_type["TRANSFER"]["transactions"] == 5
    assert by_type["TRANSFER"]["fraud_rate"] == 2 / 5
    assert by_type["PAYMENT"]["fraud_transactions"] == 0
    pair = result["05_pair_concentration"][0]
    assert (pair["nameOrig"], pair["nameDest"]) == ("Cdemo01", "Cdemo90")
    assert pair["pair_transactions"] == 4
    assert pair["sender_transactions"] == 5
    assert pair["sender_count_share"] == 4 / 5
    lead = result["07_receiver_fraud_concentration"][0]
    assert lead["nameDest"] == "Cdemo90"
    assert lead["fraud_transactions"] == 2
    assert lead["transactions"] == 5
    assert lead["distinct_senders"] == 2
    assert len(result["08_account_history"]) == 5
    assert len(document["execution"]) == 9
    assert document["reconciliation"] == "passed"
    assert "NOT PaySim Results" in (output / "investigation.md").read_text()
    stored = json.loads((output / "results.json").read_text())
    assert stored["results"]["00_overview"][0]["total_amount"] == "1020153.40"


def test_prior_hour_excludes_same_step_and_gaps(demo_run):
    output, validation = demo_run
    rows = investigate(output, validation)["results"]["06_prior_hour_activity"]
    # Two receipts in step 1 are available at step 2. Two events in step 5
    # cannot become one another's history, and step 3 is not step 5's previous hour.
    assert rows == [
        {
            "role": "recipient",
            "account_id": "Cdemo90",
            "step": 2,
            "previous_hour_transactions": 2,
            "previous_hour_amount": Decimal("250010.10"),
        }
    ]


def test_prior_hour_is_invariant_to_same_step_order_and_future_rows(
    demo_run, demo_rows, make_csv, tmp_path
):
    output, _ = demo_run
    with duckdb.connect(str(output / "payments.duckdb"), read_only=True) as db:
        original = query(db, "06_prior_hour_activity", {"result_limit": 1000})
    # Reverse storage order and change a future step. Neither may alter values at step 2.
    changed = list(reversed(demo_rows))
    changed.append({**demo_rows[0], "step": "99", "amount": "999999.99"})
    other = tmp_path / "permuted"
    ingest(make_csv(changed, "permuted.csv"), other, canonical=False)
    with duckdb.connect(str(other / "payments.duckdb"), read_only=True) as db:
        after = query(db, "06_prior_hour_activity", {"result_limit": 1000})
    assert [row for row in after if row["step"] <= 2] == original


def test_account_is_a_bound_value_not_sql(demo_run):
    output, validation = demo_run
    document = investigate(output, validation, account_id="' OR 1=1 --")
    assert document["results"]["08_account_history"] == []


def test_limits_do_not_change_population_denominators(demo_run):
    output, validation = demo_run
    document = investigate(output, validation, result_limit=1)
    assert len(document["results"]["03_high_value"]) == 1
    assert document["results"]["03_high_value"][0]["matching_population"] == 4
    assert document["results"]["00_overview"][0]["high_value_transactions"] == 4


@pytest.mark.parametrize(
    "amount",
    [
        "-1",
        "NaN",
        "Infinity",
        "0.0000000000001",
        "10000000000000000",
    ],
)
def test_invalid_cutoff_is_rejected(demo_run, amount):
    output, validation = demo_run
    with pytest.raises(ValueError):
        investigate(output, validation, minimum_amount=Decimal(amount))


@pytest.mark.parametrize("limit", [0, 1001])
def test_invalid_limit_is_rejected(demo_run, limit):
    output, validation = demo_run
    with pytest.raises(ValueError):
        investigate(output, validation, result_limit=limit)


def test_zero_fraud_input_has_valid_empty_leads(demo_rows, make_csv, tmp_path):
    for row in demo_rows:
        row["isFraud"] = "0"
        row["isFlaggedFraud"] = "0"
    output = tmp_path / "no_fraud"
    validation = ingest(make_csv(demo_rows), output, canonical=False)
    result = investigate(output, validation)["results"]
    assert result["00_overview"][0]["fraud_transactions"] == 0
    assert result["07_receiver_fraud_concentration"] == []


def test_reconciliation_detects_bad_totals(demo_run):
    output, validation = demo_run
    document = investigate(output, validation)
    bad = copy.deepcopy(document["results"])
    bad["02_risk_by_type"][0]["total_amount"] += Decimal("0.01")
    with pytest.raises(ValueError, match="Reconciliation"):
        reconcile(bad, validation)


def test_investigation_rejects_unrelated_validation(demo_run):
    output, validation = demo_run
    bad = copy.deepcopy(validation)
    bad["observed"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="does not match"):
        investigate(output, bad)
