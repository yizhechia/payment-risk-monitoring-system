# Leakage Register

## Scope and status

This register applies to an authorization-time payment-risk decision made before the transaction is executed or cancelled.

All controls below are **designed but not yet implemented or tested**. A risk marked “controlled” means the intended treatment is documented; it does not mean code currently enforces it.

## Registered risks

| ID | Source | Leakage mechanism | Consequence if used | Required control | Planned verification | Status |
|---|---|---|---|---|---|---|
| LR-001 | `isFraud` | Direct target leakage. The field is the simulator-generated outcome that the system is meant to predict or detect. | Produces meaningless near-perfect performance because the answer is included in the inputs. | Keep only as the target/evaluation label. Explicitly exclude it from every feature contract. | A schema test must fail if `isFraud` appears in the feature matrix. | Controlled by design; untested |
| LR-002 | `isFlaggedFraud` | Existing-policy leakage. It is the output of a pre-existing large-transfer rule, not an independent payment attribute. It may be contemporaneously computable, but using it would cause the new system to inherit and obscure the legacy rule. | Inflated apparent performance and an invalid claim that a new method independently discovered risk. | Exclude from candidate features. Retain separately as the legacy-rule benchmark. A future downstream-review model could use it only after explicitly changing and documenting the decision architecture. | Feature allow-list test; rule-versus-system comparison must report it as a benchmark, not a predictor. | Controlled by design; untested |
| LR-003 | `newbalanceOrig` | Post-decision state. The value reflects execution, cancellation, or another ledger update after the original decision point. | Lets the system infer what happened after the decision and can expose cancellation behaviour associated with fraud. | Exclude from authorization-time features. Permit only schema validation, reconciliation checks, and clearly labelled post-event investigation. | Feature allow-list test plus a decision-time classification assertion. | Controlled by design; untested |
| LR-004 | `newbalanceDest` | Post-decision state, with additional structural unavailability for merchant destinations. | Reveals downstream processing and may treat merchant placeholder zeros as genuine balances. | Exclude from authorization-time features. Permit only qualified data-quality or post-event analysis. | Feature allow-list test; merchant-balance checks must distinguish unavailable from true zero. | Controlled by design; untested |
| LR-005 | Future aggregates | Counts, sums, means, encodings, thresholds, or account histories computed with rows from later steps—or fitted using validation/test data—contain information unavailable at decision time. Examples include full-dataset sender counts, centred windows, final account totals, and global category statistics. | Optimistic validation metrics and features that cannot be reproduced online. | For a row in step `t`, use historical transactions only from steps `< t`. Fit learned preprocessing statistics on training data only. Never use centred or forward-looking windows. | Future-invariance test: changing rows at steps `> t` must not change features at or before `t`. Split-boundary tests for fitted transformations. | Controlled by design; untested |
| LR-006 | Same-step ordering | `step` identifies only an hour. The source provides no documented ordering within that hour, and CSV position is not a trustworthy event timestamp. Treating earlier file rows in the same step as history can silently use information that was actually concurrent or later. | Non-reproducible velocity features and within-hour look-ahead leakage. Chronological train/test contamination is also possible if a step is divided between partitions. | Authorization-time features for step `t` may use only completed steps `< t`. Never infer chronology from row order. Keep an entire step in one train, validation, or test partition. | Same-step permutation test: shuffling rows within a step must not change their historical features. Partition test: no step may appear in more than one split. | Controlled by design; untested |
| LR-007 | All four balance fields | Dataset-generation artifact risk. The publisher explicitly states that detected fraud transactions are cancelled and warns against using `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, and `newbalanceDest` for fraud detection. Even pre-transaction balances may therefore participate in simulator-specific patterns that do not represent deployable real-world signal. | A model or rule could learn PaySim cancellation mechanics rather than general payment risk. | Initial predictive feature policy excludes all four balance fields. Preserve them for data-quality work and retrospective investigation. Any later exception requires a recorded rationale, ablation comparison, and explicit synthetic-data caveat. | Feature-contract test covering all four balance fields; later ablation test only if the decision is revisited. | Open design restriction; untested |

## Leakage-safe separation

The future curated data layer should distinguish:

1. **Request-time inputs:** fields eligible for real-time rules or features.
2. **Restricted audit fields:** balance fields retained for quality checks and retrospective explanation.
3. **Policy outputs:** `isFlaggedFraud`, retained for comparison.
4. **Outcome labels:** `isFraud`, retained for evaluation.

Physical separation is preferred over relying on analysts to remember which columns to drop.

## Same-step policy

The conservative rule is:

```text
history available to a transaction in step t = all eligible rows with step < t
```

Rows with `step = t` are contemporaneous for feature-engineering purposes. Sorting them by CSV position creates deterministic processing order, but it does not create genuine event-time knowledge.

A different batch-monitoring use case could intentionally aggregate the completed hour and score after the hour closes. That would be a different decision point and must not be mixed with authorization-time results.
