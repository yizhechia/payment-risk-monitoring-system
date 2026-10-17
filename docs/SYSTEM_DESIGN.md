# System Design

## Current release boundary

v0.1.0 implements validated acquisition, ingestion, DuckDB storage and retrospective SQL investigation. It is a local batch workflow. No prediction model, tuned decision policy, dashboard or authorisation service exists yet.

## Inputs, outputs and assumptions

Input is the canonical version-2 CSV pinned by name, size and SHA-256 in `src/payment_risk/paysim_manifest.json`. Demo mode explicitly substitutes a handcrafted software fixture. Credentials and raw records are excluded from Git.

The pipeline creates a fresh run directory, writes a validation report, and publishes a DuckDB database only after blocking checks pass. Nine SQL queries then create exact result JSON, a Markdown investigation report and a run-status record. A failed SQL stage retains the validated database but does not produce a successful run status.

A file hash establishes reproducibility against the recorded acquisition, not independent authenticity. The canonical source, versioned download endpoint, file size and observed schema accompany that fingerprint. An optional expected-hash assertion cannot override the canonical pin.

## Implemented flow

1. Verify raw name, byte size and SHA-256 before parsing.
2. Require all 11 header names in their exact order.
3. Read fields as strings under strict CSV parsing. Reject missing values, unsupported monetary syntax/precision/range, nonpositive steps, unknown transaction types and nonbinary labels.
4. Validate ordinary decimal and scientific notation, applying the exponent when checking precision. Convert monetary values to `DECIMAL(18,2)`, matching the maximum two effective decimal places observed across all five monetary columns. Reject greater effective precision before casting; do not silently round. Store steps as `INTEGER` and labels as `UTINYINT`.
5. Measure row/label/flag counts, step coverage, type counts, duplicates, merchant placeholders, monetary ranges and typed schema. Compare canonical row and fraud counts with the manifest. Retain duplicate-valued records because no business transaction ID proves they are erroneous copies.
6. Re-fingerprint the raw file to detect changes during ingestion.
7. Create four tables and a metadata record in a transaction. Close and move the temporary database into the run directory only on success.
8. Run parameterised SQL on a read-only connection. Verify that supplied validation matches the database's embedded ingestion metadata. Reconcile population, fraud, policy and monetary totals before reporting success.

DuckDB uses one thread, a 1 GB engine limit during ingestion and a 2 GB limit for SQL; spilling may use disk. A full-file test exceeded 1 GB in the account-hour window query, so the investigation budget was raised explicitly. Insertion-order preservation is disabled for analysis because every displayed listing has an explicit order and row IDs were already assigned during ingestion. This is memory-conscious batch processing, not a demonstrated production throughput claim. Reusable logic and SQL live in the installable package, outside notebooks.

## Data layers

| Object | Contents | Purpose |
| --- | --- | --- |
| `request_transactions` | `row_id`, `step`, `type`, `amount`, `nameOrig`, `nameDest` | Eligible request fields and entity keys |
| `audit_balances` | `row_id` and all four balances | Restricted data-quality and retrospective audit |
| `outcomes` | `row_id`, `isFraud` | Retrospective reporting and future evaluation |
| `legacy_policy` | `row_id`, `isFlaggedFraud` | Audit the supplied policy output |
| `transactions` | Joined view of the four tables | Retrospective SQL only; not a prediction-input table |
| `run_metadata` | Successful ingestion report | Tie investigation to its validated input |

The row number is stable for the selected file and distinguishes duplicate-valued rows. It supplies no knowledge of actual within-hour order. Separation is a useful boundary, not a security access-control system or a completed model leakage safeguard.

## Time and interpretation contract

For a payment at step `t`, the decision-time history contains eligible request activity from steps strictly less than `t`. The implemented prior-hour query uses exactly `t - 1` via an explicit numeric `RANGE` window. It does not substitute the previous observed step when hours are missing.

Whole-period repeats, pair shares, labels and account histories remain retrospective. The recipient lead query is explicitly selected using outcomes. Prior-hour query tests cover same-step permutation and adding future rows; general model-feature, preprocessing and split-boundary tests remain future work.

All records in a step must eventually remain together in a chronological partition. Label-delay timestamps are absent, so historical label aggregates remain excluded from future predictive inputs. The source has already been explored descriptively; later evaluation must disclose this rather than claim a wholly unseen dataset.

## A likely failure mode

A naive `LAG` over observed account-hours can treat step 3 as step 5's previous hour. A row-ordered window can include events from the same hour. Both invent temporal precision. The explicit step-range window and tests with a missing step and reordered records address those mistakes for the present SQL query.

Another practical failure is a changed upstream artifact. The pipeline fails visibly on a fingerprint mismatch rather than silently switching to a mirror or a newer file. Source availability remains external to this repository.

## Later stages

Time-safe features and rules; logistic regression and one justified tree; chronological evaluation; simulated cost/capacity policy selection; a compact Streamlit investigation interface. No Spark, Kubernetes, deep learning, LLM agents, fake streaming or premature API service is required.
