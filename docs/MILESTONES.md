# Milestones and Acceptance Evidence

Progress is milestone-based. There is no calendar schedule. Work advances only after the current milestone's evidence is reviewed and accepted.

## Progress labels

- **BUILT:** a named artifact or component exists. A design document is not an implemented control.
- **TESTED:** recorded checks passed for the named scope and input. Fixture tests do not establish canonical-dataset validation.
- **UNDERSTOOD:** the user can explain the design and complete a small modification or investigation without relying on a generated answer.
- **INTERVIEW READY:** the implementation, evidence and explanation agree, and the limitations can be defended.

None of these labels automatically implies the next one.

## Milestone 1: Problem and Data Foundation

**Current status: ingestion and canonical validation implemented and tested; user understanding pending.**

Exit evidence:

1. A canonical-source manifest identifies the exact filename, dataset version, source terms, observed byte size and recorded SHA-256. Publisher-reported and locally measured values are distinguished.
2. A fresh run loads the reviewed artifact reproducibly, with explicit input instructions and dependency versions.
3. Schema, missing-value, duplicate, value-range, label and step checks produce an inspectable report. Deliberately invalid fixtures fail visibly; records are not silently removed.
4. Monetary representation follows inspected raw precision. The time-range discrepancy and structural merchant-balance placeholders have documented treatment.
5. The user explains label semantics, restricted balances, decision-time availability and same-step ambiguity. The comprehension gate is recorded, not assumed.

The user explicitly requested completion of the first ingestion + SQL release before returning to the learning check. Technical work in Milestone 2 is authorised under that exception. It does not accept the understanding gate or authorise model training.

## Milestone 2: SQL Investigation

**Status: implemented and tested on fixtures and the full canonical file; user understanding pending.**

Exit evidence:

1. Versioned SQL answers the stated questions about volume, fraud rates, high-value payments, repeated entities, transaction types, prior-hour activity, account histories and segment risk.
2. Query totals reconcile with the validated data; joins and denominators are checked rather than inferred.
3. At least three suspicious patterns have reproducible query references, result evidence, a plausible risk interpretation and a limitation or alternative explanation.
4. Retrospective label-based analysis is distinguished from information available to an authorisation-time policy. No minute-level sequence is invented.

## Milestone 3: Features and Rule-Based Baseline

**Status: not started.**

Exit evidence:

1. Every implemented feature has a definition, risk rationale and decision-time classification. Exact time-gap features are replaced by defensible step-based equivalents; balance features remain excluded from prediction.
2. Feature allow-list, future-invariance and same-step permutation tests pass. All rows from a step remain in the same partition.
3. An interpretable rule set is fixed without consulting the final test results and measured on chronological held-out data alongside the existing-policy benchmark.
4. Precision, recall, false-positive volume, denominators and segment results are reproducible; the user can explain a flagged case and a failure mode.

## Milestone 4: Predictive Modelling

**Status: not started; model code is outside v0.1.0.**

Exit evidence:

1. Logistic regression and one justified tree-based comparison use the same eligible inputs and chronological train/validation/test partitions.
2. Preprocessing is fitted on training data only, with explicit class-imbalance treatment and recorded seeds and dependencies.
3. Precision, recall, PR-AUC definition, confusion matrix and false-positive rate are reported with support counts. False negatives, transaction-type segments and time stability are examined.
4. Coefficients or feature importance, rule-versus-model differences and synthetic-data limitations are explained. Accuracy or ROC-AUC alone does not determine the winner.

## Milestone 5: Decision Strategy

**Status: not started.**

Exit evidence:

1. A versioned cost contract states simulated fraud-loss exposure, recovery assumptions, false-positive/customer-friction cost and investigation capacity, with units.
2. Threshold selection uses validation data only. The fixed recommendation is evaluated once on the untouched test partition.
3. Hand-computed examples and tests reconcile confusion counts, estimated missed loss, false-positive costs and total simulated cost.
4. Sensitivity results show how the recommendation changes with costs and capacity. No simulated saving is described as a realised company result.

## Milestone 6: Monitoring and Investigation Dashboard

**Status: not started.**

Exit evidence:

1. Streamlit displays risk KPIs, time trends, segment filters, rule/model comparisons, policy controls, an investigation queue and transaction/account detail.
2. Displayed totals and policy calculations reconcile with offline outputs. Interactive policy exploration does not silently retune the locked test-set recommendation.
3. Three documented cases link the underlying records, relevant SQL, available signals, decision and limitations. Retrospective evidence is labelled separately.
4. A reviewer can reproduce why each case was flagged; the interface does not imply a live production service.

## Milestone 7: Reliability and Presentation

**Status: not started.**

Exit evidence:

1. A clean environment can reproduce the raw-data-to-decisions workflow using documented acquisition and execution commands.
2. Critical transformations, leakage boundaries and cost calculations have passing tests. Evidence identifies the tested artifact, configuration and code revision.
3. README, architecture, limitations, three cases, two resume bullets and a concise GitHub description match the implemented release.
4. The user can give a two-minute explanation, answer ten relevant technical questions and modify a small component. No production, performance or personal-understanding claim exceeds the evidence.

## Acceptance decisions

Record each review in `PROJECT_STATE.md` as **ACCEPT**, **REPAIR** or **BLOCK**, with the evidence and next action. Software verification and publication do not establish user understanding or interview readiness. The current learning exception is recorded in PROJECT_STATE.md.
