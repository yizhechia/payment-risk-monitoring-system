# Verified PaySim v0.1.0 Run

This snapshot was generated from the full canonical version-2 CSV, not the handcrafted software demo. A fresh CLI run completed ingestion and all nine SQL investigations. A repeated run's validation, results, status and report were byte-identical. It demonstrates a local analytical workflow on synthetic data, not a trained detector or production impact.

## Population and quality

| Measure | Observed value |
| --- | --- |
| Transactions | 6,362,620 |
| Fraud labels | 8,213 (0.1291%) |
| Supplied policy flags | 16 |
| Hourly steps | 1-743; 743 distinct buckets |
| Missing / invalid values under implemented checks | 0 |
| Duplicate-valued extra rows | 0 |
| Merchant destination zero-balance placeholders | 2,151,495 |
| Total transaction amount | 1144392944759.77 local-currency units |

The total amount includes all transaction types and is not a measure of net money flow or economic exposure. Source labels and labelled transaction amounts are not realised fraud losses. Currency is unspecified.

## Investigation findings

1. **Type concentration:** 4,097 of 532,909 TRANSFER transactions and 4,116 of 2,237,500 CASH_OUT transactions have fraud labels. The other three types have none in this synthetic artifact. This describes the simulation; it does not establish that those types imply fraud or that other types are safe in practice. Evidence: `02_risk_by_type.sql`.
2. **High value is a broad review filter:** a cutoff of at least 200,000 selects 1,673,570 payments, including 5,471 fraud-labelled and 1,668,099 legitimate-labelled payments. Another 2,742 fraud-labelled payments lie below the cutoff. It is an investigation assumption, not an optimised policy. The counts illustrate why amount alone needs scrutiny before creating customer friction. Evidence: `00_overview.sql` and `03_high_value.sql`.
3. **Recipient recurrence is an investigation lead:** recipient `C803116137` has two fraud-labelled payments among 77 payments from 77 distinct senders. The account was selected using outcomes. This is retrospective evidence, not an available online signal or proof of coordination. Evidence: `07_receiver_fraud_concentration.sql`.
4. **The supplied flag requires qualification:** only 16 rows carry `isFlaggedFraud`, while 409,110 transfers exceed the publisher's described 200,000 cutoff. The simple condition and flag disagree on 409,094 of 6,362,620 rows. The code reports this discrepancy and does not invent missing rule conditions or replace the original flag. Evidence: `00_overview.sql`.

## Evidence files

- [Validation](validation.json): raw fingerprint, observed schema, precision, counts and checks.
- [Complete returned SQL results](results.json): query hashes, bound parameters, result rows and reconciliation. Limited queries return up to 25 rows; complete source populations are not implied by those listings.
- [Readable investigation report](investigation.md): findings, query tables and interpretation limits.
- [Run status](run.json): successful execution of all nine queries.
- [Software verification](verification.json): 102 fixture tests, formatting/lint checks, wheel installation/demo, full CLI replay and source/test file hashes. Hosted CI is not inferred from local checks.

The prior-hour query uses exactly the previous completed step, excluding same-step rows and gaps. Full-period account repeats, pair shares and outcome-selected leads are descriptive investigations. No model evaluation has been performed, and full-dataset exploration must be disclosed in later evaluation work.

## Reproduce

From the repository root after installation and canonical data acquisition:

```bash
payment-risk run --csv data/raw/PS_20174392719_1491204439457_log.csv --output artifacts/paysim
```

The output directory must not already exist. Compare `results.json`, query hashes and input hash; Python-version metadata may differ on another supported interpreter.

Input SHA-256: `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b`.

## Data attribution

Edgar Lopez-Rojas and collaborators, [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1), version 2, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The dataset-derived tables and summaries in this directory are offered under CC BY-SA 4.0. They aggregate and select synthetic source records; no endorsement is implied. The raw CSV and generated DuckDB database are not redistributed here. This attribution does not license unrelated original project code.
