# Publication Notes

## Release scope

v0.1.0 is a runnable **data-foundation and SQL-investigation release**. It supports validated PaySim ingestion, separated DuckDB tables, nine question-led SQL investigations and an evidence-linked findings report. It is suitable for presenting SQL investigation and data-quality work.

It is not the completed seven-milestone project. There are no trained models, optimised thresholds, realised loss savings, production integrations or dashboard in this release. Technical execution does not establish the user's understanding or interview readiness.

Suggested GitHub description:

> Reproducible payment-risk investigation on synthetic PaySim data: validated Python ingestion, DuckDB SQL, leakage-aware data layers and tested findings.

## Publication contents

Include source code, SQL, the project-authored demo fixture, tests, pinned dependencies, documentation, and small verified report snapshots with source attribution. Exclude the raw CSV, generated DuckDB files, temporary runs, credentials, private brief and personal resume.

The published result snapshot is tied to a source hash and recorded query parameters. It contains synthetic selected records and derived summaries, not employer/customer data. Full returned results are JSON; the Markdown report intentionally limits long tables. Decimal strings preserve precision.

## Licensing

The dataset record identifies CC BY-SA 4.0. Dataset-derived report tables and summaries carry attribution to Edgar Lopez-Rojas and collaborators, the canonical source and the license link. Reports describe the changes: aggregation and selection of synthetic source records. The original raw CSV is not bundled.

The project's original code and documentation have no chosen open-source license. Do not call the repository open source or infer a license grant from public visibility. This does not prevent reviewing the work; any intended license grant is a separate owner decision.

## Verification boundaries

The software fixture tests and full-file validation are separate evidence. A passing fixture suite does not establish the canonical dataset's contents. A configured GitHub Actions workflow does not establish a hosted CI pass. Report only checks that actually ran.

The local release preparation does not require changing repository visibility, publishing a hosted service or replacing the default branch. Keep remote publication status explicit in the handoff.

## Interview and resume boundary

An accurate implementation description is:

> Implemented a reproducible PaySim ingestion and DuckDB SQL investigation pipeline with strict validation, separated request/outcome/audit data, exact-decimal storage and reconciled risk summaries.

Use this as a personal capability claim only after explaining the implementation and completing a small independent change. Do not describe retrospective label-selected leads as prospective fraud detection, source flagged outcomes as a newly trained model, or labelled transaction value as prevented losses.
