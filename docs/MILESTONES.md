# Roadmap

## 1. Data foundation - implemented

- Pin the source artifact and document its fields and limitations.
- Validate schema, missing values, numeric ranges, labels, duplicates and step coverage.
- Preserve exact monetary values and keep incompatible inputs out of the analytical database.

Acceptance: the canonical file loads reproducibly, invalid fixtures fail visibly, and validation results identify the input artifact.

## 2. SQL investigation - implemented

- Investigate volume, fraud rates, high-value payments, repeated entities and account histories.
- Check activity from the previous completed hour without assuming within-hour order.
- Record findings with query parameters, denominators and source references.

Acceptance: totals reconcile with validation and at least three patterns are supported by reproducible query results.

## 3. Features and rule baseline - planned

- Define whole-step chronological partitions and an explicit feature allow-list.
- Implement past-only activity features and a small interpretable rule set.
- Add future-invariance, same-step permutation and split-boundary checks.

Acceptance: feature definitions have a risk rationale, temporal tests pass, and held-out rule results include precision, recall, false positives and segment counts.

## 4. Predictive modelling - planned

- Train logistic regression and one justified tree-based comparator on the same eligible inputs.
- Fit preprocessing on training data only and document class-imbalance handling.
- Report precision, recall, Average Precision, confusion counts and results by time and segment.

Acceptance: chronological evaluation is reproducible and differences from the rule baseline are explained. Full-dataset descriptive exploration is recorded in the evaluation protocol.

## 5. Decision policy - planned

- Define simulated fraud-loss, customer-friction and review-capacity assumptions.
- Select thresholds using validation data and evaluate the fixed policy on the test partition.
- Reconcile costs and confusion counts with hand-calculated examples.

Acceptance: sensitivity analysis shows how the policy changes with costs and capacity, with simulated assumptions identified explicitly.

## 6. Dashboard and cases - planned

- Add a Streamlit interface for trends, segments, policy comparison and account investigation.
- Document three cases with traceable transactions, SQL and interpretation limits.

Acceptance: displayed values match offline calculations and each case can be reproduced from its source records.

## 7. Release reliability - ongoing

- Maintain passing tests, pinned dependencies and reproducible run instructions.
- Keep reports, documentation and dashboard calculations consistent.

Acceptance: a clean environment reproduces the supported workflow and published results identify the corresponding input and configuration.
