# Project State

## Current scope

**v0.1.0: data foundation and SQL investigation.** Milestones 1 and 2 have an implemented, tested technical slice. Their learning acceptance remains open. Milestones 3-7 have not been implemented; no model, tuned policy or dashboard is claimed.

| Component | BUILT | TESTED | UNDERSTOOD | INTERVIEW READY |
| --- | --- | --- | --- | --- |
| Canonical acquisition, ingestion and validation | Yes | Fixtures and full PaySim file | Pending | No |
| Nine DuckDB SQL investigations and report | Yes | Hand-counted fixtures and full-file reconciliation | Pending | No |
| Features and new rules | No | No | Pending | No |
| Models, decision strategy and dashboard | No | No | Pending | No |

## Verified evidence

- Canonical version 2: `PS_20174392719_1491204439457_log.csv`, 493,534,783 bytes, SHA-256 `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b`.
- 6,362,620 rows, 8,213 fraud labels, 16 supplied policy flags; 743 distinct steps spanning 1-743.
- No missing or invalid field values under implemented checks; no duplicate-valued extra rows. 2,151,495 merchant destination rows have structural zero-balance placeholders.
- Ordinary decimal and scientific notation both occur. Every monetary column has at most two effective decimal places after applying its exponent; `DECIMAL(18,2)` preserves the values exactly.
- Nine investigations reconcile population, fraud, supplied-policy confusion counts and monetary totals. SQL hashes, parameters, complete returned results and report are in `reports/paysim-v0.1.0/`.
- 102 software fixture tests passed on Python 3.12.14 / DuckDB 1.4.3. Ruff checks, wheel build and installation into a separate environment passed. The installed wheel's demo completed successfully. Hosted CI status is separate from local evidence.

## Recorded decisions

1. PaySim remains the approved primary dataset. Findings describe synthetic mobile-money behaviour and system methodology, not production performance.
2. The intended decision point precedes execution or cancellation. All balances, outcomes and the supplied policy flag are physically separate from the request table. The joined view is retrospective.
3. Historical prediction inputs must eventually use steps strictly less than the scored step. The implemented prior-hour investigation uses exactly `t - 1`; row IDs do not establish intra-hour sequence. General feature, preprocessing and split leakage safeguards remain pending.
4. Do not silently remove duplicate-valued records, impute balances, round monetary precision, substitute a dataset mirror or override the pinned canonical hash.
5. Use the artifact's measured 1-743 coverage. The source prose's 744-hour description is retained as a documented source discrepancy; its cause is unknown.
6. The supplied flag disagrees with the publisher's simplified transfer-above-200,000 condition on 409,094 rows. Preserve both facts; do not rewrite the flag or invent additional simulator conditions.
7. SQL uses a 2 GB DuckDB engine budget after the full account-hour query exceeded 1 GB. Ingestion uses 1 GB. These are not whole-process memory caps.
8. The user explicitly requested completing the first ingestion + SQL release before the learning check. That permits this technical slice, but does not mark understanding complete or authorise moving into models.
9. Raw data, generated databases, credentials, the private brief and personal resume stay outside Git. Original project code has no chosen open-source license; dataset-derived reports retain CC BY-SA 4.0 attribution.

## Acceptance and open work

**Technical release: ACCEPT for the named ingestion + SQL scope. Learning gates: PENDING. Progression to model work: BLOCK.**

Before Milestone 3, the user must explain decision-time availability and the implemented SQL, then make a small independent change. A future feature allow-list, whole-step chronological partitioning, train-only preprocessing and label-delay policy are not yet implemented. Later evaluation must disclose that the full dataset has already been explored descriptively.

## Exact next action

Review `00_overview.sql`, `02_risk_by_type.sql` and `06_prior_hour_activity.sql`. Explain which history a payment in step 20 may use and why its post-transaction balance cannot be a pre-decision input. Then modify the type-risk query to include legitimate transaction counts and verify that each segment's fraud plus legitimate counts equals its total. Do not begin model code until this learning check is accepted.
