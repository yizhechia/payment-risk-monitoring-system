# System Design

The pipeline runs locally in two stages: validate the source CSV and publish a DuckDB database, then run SQL investigations and write reports.

## Input contract

The canonical PaySim version-2 artifact is pinned by filename, byte size and SHA-256 in `src/payment_risk/paysim_manifest.json`. Demo mode uses a separate 12-row test fixture. Every run writes to a new directory.

The fingerprint identifies the recorded artifact. Schema and value validation independently check its contents. An optional expected-hash assertion cannot override the canonical pin.

## Ingestion

1. Check the filename, size, hash and exact 11-column header.
2. Parse fields as strings under strict CSV rules.
3. Reject missing fields, unknown transaction types, invalid labels, nonpositive steps and unsupported monetary values.
4. Check the exponent-adjusted scale before converting amounts and balances to `DECIMAL(18,2)`.
5. Record counts, step coverage, duplicates, merchant placeholders, monetary ranges and the typed schema.
6. Recheck the raw fingerprint to detect changes during ingestion.
7. Create the data layers and metadata in a transaction, then publish the database after successful validation.

Duplicate-valued records are reported and retained because the source has no business transaction identifier. Merchant destination balance zeros remain structural placeholders.

## Data layers

| Object | Contents | Use |
| --- | --- | --- |
| `request_transactions` | `row_id`, `step`, `type`, `amount`, `nameOrig`, `nameDest` | Request fields and entity keys |
| `audit_balances` | `row_id` and all four balances | Data-quality and retrospective audit |
| `outcomes` | `row_id`, `isFraud` | Retrospective reporting |
| `legacy_policy` | `row_id`, `isFlaggedFraud` | Supplied-policy comparison |
| `transactions` | Joined view | Retrospective SQL investigation |
| `run_metadata` | Ingestion report | Input identity and validation results |

`row_id` is a technical key within the pinned file. It distinguishes records but does not establish within-hour event order. Data-layer separation is an analytical boundary rather than an access-control mechanism.

## SQL and reconciliation

Investigations use a read-only connection and bound parameters. Before querying, the supplied validation report must match the database's embedded metadata. Time and transaction-type aggregates reconcile to the overview, including exact amounts. Label and supplied-policy counts reconcile to validation.

Results record query hashes, parameters and returned rows. JSON encodes monetary values as decimal strings. Listings are limited for inspection; population counts are computed before limiting.

## Time semantics

A decision-time history can use only steps strictly earlier than the transaction's step. The previous-hour query uses `RANGE BETWEEN 1 PRECEDING AND 1 PRECEDING`, so step 3 does not become step 5's previous hour when step 4 is absent. Same-step permutation and future-row tests cover this query.

Full-period counts, pair shares and outcome-selected recipients are retrospective analyses. Later feature pipelines need explicit allow-lists, whole-step partitions and training-only preprocessing. Historical fraud-label aggregates also require a label-availability contract, which the source does not provide.

## Resources and failure handling

DuckDB uses one thread, a 1 GB engine limit during ingestion and a 2 GB limit for investigation. These limits do not cap whole-process memory. Analysis disables insertion-order preservation; displayed listings specify their own order. Temporary spill files may use disk.

Validation failures write a report and publish no database. SQL failures retain the validated database and record the failure in `run.json`. Existing run directories are never overwritten.

Future work is listed in the [roadmap](MILESTONES.md).
