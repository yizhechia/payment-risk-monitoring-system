# Payment Risk Monitoring and Investigation System

A Python and DuckDB pipeline for validating payment transactions and investigating risk patterns with SQL. The current release covers ingestion, data-quality checks and nine retrospective investigations using synthetic PaySim data.

## Features

- Version-pinned dataset download with SHA-256 verification.
- Strict schema, missing-value, range and duplicate checks.
- Exact-decimal storage, including scientific-notation inputs.
- Separate request, balance, outcome and policy tables in DuckDB.
- Parameterised SQL for transaction trends, repeated activity and account histories.
- JSON results and a Markdown report with reconciled counts and amounts.

## Quick start

Requires Python 3.11-3.13.

```bash
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```bash
python -m pip install ".[dev]"
payment-risk demo --output artifacts/demo
```

The demo uses a 12-row test fixture. Each run needs a new output directory.

For a locked environment with uv:

```bash
uv sync --locked --extra dev
uv run payment-risk demo --output artifacts/demo-locked
```

## Run with PaySim

Download the canonical [PaySim version-2 dataset](https://www.kaggle.com/datasets/ealaxi/paysim1) and run the pipeline:

```bash
payment-risk download --output data/raw
payment-risk run --csv data/raw/PS_20174392719_1491204439457_log.csv --output artifacts/paysim
```

If Kaggle requires sign-in, download version 2 manually and pass the extracted CSV to `run`. The pipeline checks its filename, size and checksum against the bundled manifest.

The raw file is about 471 MiB. Allow several GiB of free disk space. DuckDB uses one thread, with engine memory limits of 1 GB for ingestion and 2 GB for investigations; temporary spill files may use additional disk space.

Optional filters:

```bash
payment-risk run --csv data/raw/PS_20174392719_1491204439457_log.csv --output artifacts/account-review --minimum-amount 200000 --limit 25 --account C1231006815
```

`--minimum-amount` sets an investigation cutoff. `--limit` controls returned listings; population counts are calculated before limiting.

## Outputs

| File | Contents |
| --- | --- |
| `validation.json` | Input fingerprint, schema, data-quality checks and population counts |
| `payments.duckdb` | Validated tables and a retrospective transaction view |
| `results.json` | Query results, parameters, SQL hashes and reconciliation status |
| `investigation.md` | Findings and query tables |
| `run.json` | Run status |

Validation failures return exit code 2 and produce no database. Argument or execution errors return exit code 1. Existing runs are never overwritten. Missing values are rejected, duplicates are reported and retained, and unsupported monetary precision is rejected before casting.

## Investigations

| Query | Purpose |
| --- | --- |
| [00_overview](src/payment_risk/sql/00_overview.sql) | Population totals, high-value payments and supplied-policy counts |
| [01_volume_by_step](src/payment_risk/sql/01_volume_by_step.sql) | Hourly transaction volume and fraud rates |
| [02_risk_by_type](src/payment_risk/sql/02_risk_by_type.sql) | Transaction-type comparisons |
| [03_high_value](src/payment_risk/sql/03_high_value.sql) | High-value payment listings |
| [04_repeat_entities](src/payment_risk/sql/04_repeat_entities.sql) | Repeated sender and recipient activity |
| [05_pair_concentration](src/payment_risk/sql/05_pair_concentration.sql) | Sender-recipient concentration |
| [06_prior_hour_activity](src/payment_risk/sql/06_prior_hour_activity.sql) | Activity in the previous completed hour |
| [07_receiver_fraud_concentration](src/payment_risk/sql/07_receiver_fraud_concentration.sql) | Recipients linked to labelled fraud |
| [08_account_history](src/payment_risk/sql/08_account_history.sql) | Payments involving a selected account |

The full-data run covers **6,362,620 transactions**, including **8,213 fraud labels**, across **743 hourly steps**. See the [results summary](reports/paysim-v0.1.0/README.md) and [investigation report](reports/paysim-v0.1.0/investigation.md).

## Data considerations

PaySim is synthetic mobile-money data. Amounts use an unspecified local currency. Hourly steps provide no ordering within an hour, and the dataset has no device, IP, precise timestamp or label-delay fields.

Request fields are stored separately from all four balances, the fraud label and the supplied policy flag. The prior-hour query uses exactly `step = t - 1`. Full-period counts and outcome-selected leads are retrospective analyses. The publisher's balance warning, merchant placeholders and the discrepancy in the supplied policy flag are documented in the [data dictionary](docs/DATA_DICTIONARY.md), [provenance record](docs/DATASET_PROVENANCE.md) and [leakage register](docs/LEAKAGE_REGISTER.md).

Monetary values use `DECIMAL(18,2)`. Validation accounts for exponents in scientific notation before checking precision. JSON stores monetary values as decimal strings.

## Development

```bash
pytest -q
ruff check .
ruff format --check .
```

The suite contains 102 tests covering validation failures, exact amounts, data-layer separation, SQL totals, temporal boundaries, acquisition and CLI behaviour. CI runs on Python 3.11 and 3.13. Test fixtures run without downloading PaySim; full-data results are stored separately.

Runtime dependencies: Python and DuckDB. Development dependencies: pytest and Ruff. See [system design](docs/SYSTEM_DESIGN.md), [project status](PROJECT_STATE.md) and [roadmap](docs/MILESTONES.md).

## Data attribution and license

PaySim: Edgar Lopez-Rojas and collaborators, [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1), version 2, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Dataset-derived report tables retain the same attribution and license. The raw CSV and generated database are not bundled.

A license for the original project code has not been selected.
