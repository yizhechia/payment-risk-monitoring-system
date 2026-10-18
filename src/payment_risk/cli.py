"""Small local CLI; no service, credentials store or automatic publication."""

import argparse
import sys
from decimal import Decimal, InvalidOperation
from importlib.resources import as_file, files
from pathlib import Path

import duckdb

from payment_risk.acquire import download
from payment_risk.contracts import MONEY_SCALE
from payment_risk.investigate import investigate
from payment_risk.pipeline import ValidationError, ingest, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    acquisition = commands.add_parser("download", help="Acquire canonical PaySim version 2")
    acquisition.add_argument("--output", type=Path, default=Path("data/raw"))
    for name in ("run", "demo"):
        sub = commands.add_parser(
            name,
            help="Run canonical data"
            if name == "run"
            else "Run a handcrafted software fixture (not PaySim)",
        )
        sub.add_argument(
            "--output", type=Path, required=True, help="New, non-existing run directory"
        )
        sub.add_argument("--minimum-amount", default="200000")
        sub.add_argument("--limit", type=int, default=25)
        sub.add_argument("--account", default=None)
        if name == "run":
            sub.add_argument("--csv", type=Path, required=True)
            sub.add_argument(
                "--expected-sha256",
                default=None,
                help="Additional integrity assertion; cannot override the pinned hash",
            )
    args = parser.parse_args(argv)
    try:
        if args.command == "download":
            download(args.output)
            return 0
        cutoff = Decimal(args.minimum_amount)
        if (
            not cutoff.is_finite()
            or not 0 <= cutoff < 10**16
            or cutoff.as_tuple().exponent < -MONEY_SCALE
        ):
            raise ValueError(f"minimum-amount must fit the {MONEY_SCALE}-decimal money contract.")
        if not 1 <= args.limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        if args.command == "demo":
            print("Validating handcrafted demo (not PaySim)...", flush=True)
            with as_file(files("payment_risk").joinpath("demo.csv")) as demo:
                validation = ingest(demo, args.output, canonical=False)
        else:
            print("Validating pinned PaySim artifact and building DuckDB...", flush=True)
            validation = ingest(args.csv, args.output, expected_sha256=args.expected_sha256)
        try:
            print("Executing nine SQL investigations and reconciling totals...", flush=True)
            investigate(
                args.output,
                validation,
                minimum_amount=cutoff,
                result_limit=args.limit,
                account_id=args.account,
            )
        except Exception as error:
            write_json(
                args.output / "run.json",
                {"status": "failed", "stage": "investigation", "error": str(error)},
            )
            raise
        print(
            f"Validation and SQL reconciliation passed. Report: {args.output / 'investigation.md'}"
        )
        return 0
    except (ValueError, OSError, duckdb.Error, InvalidOperation) as error:
        print(str(error), file=sys.stderr)
        if isinstance(error, ValidationError):
            return 2
        return 1
