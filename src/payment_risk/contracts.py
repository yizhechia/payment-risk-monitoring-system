"""Source schema and conservative decision-time field contract."""

import hashlib
import json
from importlib.resources import files
from pathlib import Path

COLUMNS = (
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
)
MONEY = ("amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest")
BALANCES = MONEY[1:]
MONEY_SCALE = 2
MONEY_TYPE = "DECIMAL(18,2)"
REQUEST_COLUMNS = ("row_id", "step", "type", "amount", "nameOrig", "nameDest")
TYPES = ("CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER")


def manifest() -> dict:
    return json.loads(files("payment_risk").joinpath("paysim_manifest.json").read_text())


def fingerprint(path: Path) -> dict:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"filename": path.name, "bytes": path.stat().st_size, "sha256": digest}


def sql_text(name: str) -> str:
    # The caller supplies an internal query name, never an arbitrary path from a user.
    return files("payment_risk").joinpath("sql", name + ".sql").read_text()
