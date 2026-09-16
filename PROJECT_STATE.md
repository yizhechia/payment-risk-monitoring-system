# Project State

## Current milestone

**Milestone 1 — Problem and Data Foundation: IN PROGRESS**

The approved primary dataset is PaySim. No ingestion, schema-validation, SQL-investigation, feature-engineering, or modelling code has been implemented.

## Progress labels

- **BUILT:** Dataset provenance record, field-level data dictionary, and leakage register.
- **TESTED:** Nothing yet. The raw CSV has not been acquired or validated locally.
- **UNDERSTOOD:** Pending the required comprehension check on post-decision leakage.
- **INTERVIEW READY:** No.

## Completed decisions

1. Use PaySim as the primary dataset.
2. Define the operational decision point as immediately before a transaction is allowed or blocked and before ledger balances are changed.
3. Treat `isFraud` as an outcome label, never as an input feature.
4. Treat `isFlaggedFraud` as an existing policy output: retain it for legacy-rule comparison, but exclude it from candidate features.
5. Treat `newbalanceOrig` and `newbalanceDest` as post-decision information and exclude them from authorization-time features.
6. For transaction-level features at step `t`, use only information from completed steps strictly earlier than `t`. CSV row order within a step is not accepted as event order.
7. Keep all rows from the same `step` in the same chronological data partition.
8. Do not commit the raw dataset to Git.

## Built documentation

- `docs/DATASET_PROVENANCE.md`
- `docs/DATA_DICTIONARY.md`
- `docs/LEAKAGE_REGISTER.md`

## Open issues

- Download the canonical version-2 CSV and record its SHA-256 checksum.
- Validate the reported row count, exact headers, types, nulls, duplicates, value ranges, and fraud counts from the raw bytes.
- Resolve the source-documentation discrepancy between “744 steps” and the Kaggle Data Explorer range of `1` through `743`.
- Decide the ingestion representation for monetary values only after inspecting their raw precision.
- Reconcile the project brief's proposed balance features with the dataset publisher's warning that all four balance columns should not be used for fraud detection because detected fraud transactions are cancelled.

## Next action

The user answers the comprehension question about why information produced after a risk decision causes leakage. After a correct explanation, design the ingestion and schema-validation module. Do not begin modelling or broad SQL investigation.
