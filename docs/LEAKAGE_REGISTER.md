# Leakage Register

The intended operational decision is before execution or cancellation. Request fields are separated from balances, outcomes and the supplied policy flag. Future model inputs require their own explicit feature contract.

| ID | Risk | Treatment in v0.1.0 | Verification and remaining work |
| --- | --- | --- | --- |
| LR-001 | `isFraud`: direct target leakage | Stored separately in `outcomes`; used openly for retrospective analysis | Request-table exclusion tested. Model-matrix exclusion remains pending. |
| LR-002 | `isFlaggedFraud`: existing-policy dependence | Stored in `legacy_policy`; audited as the supplied comparator | Request-table exclusion and hand-counted confusion identities tested. |
| LR-003 | `newbalanceOrig`: post-decision state | Restricted to `audit_balances` | Request-table exclusion tested; future feature allow-list pending. |
| LR-004 | `newbalanceDest`: post-decision state and merchant placeholders | Restricted to `audit_balances`; merchant zero placeholders reported | Request-table exclusion and placeholder counts tested. No imputation to true zero. |
| LR-005 | Future aggregates, train/test preprocessing | Full-period investigations explicitly labelled retrospective; prior-hour SQL reads exactly `t - 1` | Future-row invariance tested for this SQL query only. Train-only preprocessing and chronological split tests pending. |
| LR-006 | Same-step ordering and split contamination | Row IDs are display/ingestion keys only; prior-hour window excludes the current step | Reordering and missing-step fixtures tested. Whole-step model partitions remain pending. |
| LR-007 | All four balance fields: simulator cancellation artifacts | All balances excluded from the request table, including nominal pre-state values | Table schema checked. Predictive use would require a documented rationale and ablation comparison. |
| LR-008 | Historical fraud outcomes may not yet be known | No label-derived history in the prior-hour query | Query uses only request activity. Label-delay contract and future model-feature exclusion still required. |

The source publisher warns against using all balance fields for fraud detection because detected fraud is cancelled. This is a simulator-specific restriction beyond the ordinary post-transaction leakage rule. Source: [canonical dataset metadata](https://www.kaggle.com/datasets/ealaxi/paysim1).

## Retrospective views and leads

The joined `transactions` view intentionally contains audit, outcome and policy fields. It is convenient for investigation and is unsafe as a model feature matrix through `SELECT *`. The recipient-fraud-concentration query selects leads using labels and cannot be an authorisation-time predictor.

Full-period account repeats and pair concentration also contain future information relative to earlier payments. They answer descriptive questions; they cannot be copied into a predictive feature set unchanged.

## Future evaluation exposure

The full dataset has been used for descriptive SQL investigation. The evaluation protocol should record this exploration, fix chronological partitions before tuning, fit preprocessing only on training data and tune thresholds on validation data.
