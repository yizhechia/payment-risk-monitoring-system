# Payment Risk Monitoring and Investigation System

A payment-risk portfolio project built around reproducible SQL investigations of synthetic mobile-money transactions.

**v0.1.0: validated ingestion and SQL investigation.** This release loads a pinned PaySim CSV into DuckDB, validates it, runs nine investigation queries and produces an evidence-linked report. Features for model training, predictive models, threshold optimisation and a dashboard remain later milestones.

## Why this project

A payment-risk analyst needs to explain what a suspicious pattern means, check the population behind a fraud rate, and distinguish information available before authorisation from evidence available afterwards. This first release focuses on that investigation foundation. It does not claim employer adoption, production performance or prevented losses.

## Try it without downloading data

Requires Python 3.11-3.13. From the repository root:

```bash
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```bash
python -m pip install ".[dev]"
payment-risk demo --output artifacts/demo
pytest -q
```

The demo is a **12-row handcrafted software fixture**, not a PaySim sample or an estimate of fraud performance. Its intentionally chosen edge cases test the calculations. Each command requires a new output directory; an existing run is never overwritten.

For a locked development environment with uv:

```bash
uv sync --locked --extra dev
uv run payment-risk demo --output artifacts/demo-locked
uv run pytest -q
```

## Run the full PaySim investigation

Obtain the selected [PaySim version-2 dataset](https://www.kaggle.com/datasets/ealaxi/paysim1). The downloader uses its version-pinned canonical endpoint and verifies the CSV hash before publishing the local file:

```bash
payment-risk download --output data/raw
payment-risk run --csv data/raw/PS_20174392719_1491204439457_log.csv --output artifacts/paysim
```

If Kaggle requires sign-in or changes access rules, download version 2 manually from the dataset page and use the same `run` command. No fallback mirror or alternate artifact is accepted automatically. The raw file is about 471 MiB. Allow several GiB of free disk space for raw data, DuckDB and temporary spill files. DuckDB uses one thread, a 1 GB engine limit during ingestion and a 2 GB limit during SQL investigation; these are not whole-process memory caps.

Outputs:

| File | Purpose |
| --- | --- |
| `validation.json` | Fingerprint, exact header, value checks, monetary precision, schema, row and label counts, duplicates and step range |
| `payments.duckdb` | Separate request, balance-audit, outcome and legacy-policy tables, plus a joined retrospective view |
| `results.json` | Complete returned query rows, bound parameters, SQL hashes, findings and reconciliation outcome |
| `investigation.md` | Human-readable findings, query tables and interpretation limits |
| `run.json` | Overall SQL-run status |

A failed validation emits `validation.json`, returns exit code 2 and publishes no analytical database. Invalid arguments or execution failures return exit code 1. Validation does not silently drop duplicates, fill missing fields or round amounts. A later SQL failure preserves the validated database and records the failure in `run.json`; it does not mark the run successful.

Optional investigation parameters:

```bash
payment-risk run --csv data/raw/PS_20174392719_1491204439457_log.csv --output artifacts/account-review --minimum-amount 200000 --limit 25 --account C1231006815
```

The amount is an investigation cutoff, not an optimised decision threshold. Currency is unspecified. Account IDs are synthetic. Limited listings are samples; population counts are calculated before limiting.

## The nine SQL investigations

| SQL | Question |
| --- | --- |
| [00_overview](src/payment_risk/sql/00_overview.sql) | What are the population, labelled amounts, review-cutoff population and supplied-policy confusion counts? |
| [01_volume_by_step](src/payment_risk/sql/01_volume_by_step.sql) | How do volume and labelled fraud vary across hourly simulation buckets? |
| [02_risk_by_type](src/payment_risk/sql/02_risk_by_type.sql) | Which transaction types contain labelled fraud, and with what denominators? |
| [03_high_value](src/payment_risk/sql/03_high_value.sql) | Which high-value payments merit retrospective inspection? |
| [04_repeat_entities](src/payment_risk/sql/04_repeat_entities.sql) | Which senders or recipients occur repeatedly? |
| [05_pair_concentration](src/payment_risk/sql/05_pair_concentration.sql) | Is a sender's full-period activity concentrated on one recipient? |
| [06_prior_hour_activity](src/payment_risk/sql/06_prior_hour_activity.sql) | What activity was visible in the previous completed hour, excluding the current hour and time gaps? |
| [07_receiver_fraud_concentration](src/payment_risk/sql/07_receiver_fraud_concentration.sql) | Which recipients recur in retrospectively labelled fraud? |
| [08_account_history](src/payment_risk/sql/08_account_history.sql) | Which payments involve a chosen account? |

Type and time aggregates reconcile exactly to the overview, including monetary totals. Label counts reconcile to validation, and supplied-policy confusion counts reconcile to both fraud and flag totals. Monetary values are serialized as decimal strings in JSON to preserve precision.

## Read the evidence

- [Verified PaySim run](reports/paysim-v0.1.0/README.md) and [investigation report](reports/paysim-v0.1.0/investigation.md)
- [Dataset provenance](docs/DATASET_PROVENANCE.md), [data dictionary](docs/DATA_DICTIONARY.md) and [leakage register](docs/LEAKAGE_REGISTER.md)
- [Architecture and failure behaviour](docs/SYSTEM_DESIGN.md)
- [Milestones](docs/MILESTONES.md) and [current project state](PROJECT_STATE.md)
- [Release and licensing notes](docs/PUBLICATION_NOTES.md)

## Decision-time boundary

The simulated decision occurs before a payment executes or is cancelled. `request_transactions` contains only `row_id`, `step`, `type`, `amount`, `nameOrig` and `nameDest`. The technical `row_id` identifies a record within the pinned file; it is not a source transaction ID or within-hour event order.

All four balances are restricted to audit, `isFraud` is separated as an outcome, and `isFlaggedFraud` is separated as a supplied policy output. The joined `transactions` view is for retrospective investigation and must not become a model input through `SELECT *`.

The prior-hour query reads request activity from exactly `step = t - 1`. Full-period repeats, account histories and fraud-selected recipients answer retrospective questions. They are not prediction features. Train/validation/test splitting and a model-feature allow-list have not been implemented in this release.

## Data limits

PaySim is **synthetic mobile-money data**, not real adjudicated payment fraud. There are no device, IP, location, exact timestamp, label-delay, review-result or realised-loss fields. Hourly buckets do not support minute-level velocity. Balances contain structural merchant placeholders and the publisher warns against using all balance fields for fraud detection.

The original source uses both ordinary decimal strings and scientific notation. Full-file inspection found at most two effective decimal places after applying the exponent. `DECIMAL(18,2)` preserves those numeric values exactly. Validation checks the exponent-adjusted scale before casting, so unsupported precision is rejected rather than rounded. The scale is an observed artifact property, not a known currency code.

Whole-dataset exploration is for this release's descriptive investigations. A later held-out evaluation must disclose that the dataset has already been explored, fix its protocol and keep future model/threshold fitting within the training/validation boundaries.

## Tests and dependencies

```bash
ruff check .
ruff format --check .
pytest -q
```

Tests cover malformed CSV/schema, missing and invalid values, exact decimals, preserved duplicates, fingerprints, refusal to overwrite, separated data layers, hand-counted SQL, bound account IDs, denominator reconciliation, time gaps, same-step permutations, future-row invariance, acquisition errors and CLI execution. They use constructed fixtures; full-file evidence is recorded separately. The GitHub Actions workflow runs software tests without downloading PaySim. A configured workflow is not evidence of a passed hosted run.

Runtime: Python and DuckDB. Development: pytest and Ruff. Exact direct versions and the uv lock are included. pandas, NumPy, scikit-learn and Streamlit will be added when later milestones use them.

## Attribution and reuse

Dataset: Edgar Lopez-Rojas and collaborators, [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1), version 2, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). PaySim methodology: E. A. Lopez-Rojas, A. Elmir and S. Axelsson, *PaySim: A Financial Mobile Money Simulator for Fraud Detection*, EMSS 2016. Dataset-derived report tables retain attribution and CC BY-SA 4.0 terms. The raw CSV and generated database are excluded from Git and the source package.

No open-source license has been selected for the project's original code and documentation. Public visibility does not itself grant reuse rights. The software fixture is authored for this project and is not a dataset excerpt.
