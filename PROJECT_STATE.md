# Project Status

Current version: **0.1.0 - ingestion and SQL investigation**.

| Component | Status |
| --- | --- |
| Dataset acquisition and fingerprinting | Implemented |
| Schema and value validation | Implemented |
| DuckDB data layers | Implemented |
| Nine SQL investigations | Implemented |
| Findings report and reconciliation | Implemented |
| Historical features and rule baseline | Planned |
| Predictive models and decision policy | Planned |
| Streamlit dashboard | Planned |

## Validation

The PaySim version-2 run contains 6,362,620 transactions, 8,213 fraud labels and 743 hourly steps. All implemented data-quality checks and query reconciliations passed. The software suite contains 102 tests. See [run results](reports/paysim-v0.1.0/README.md) and [verification metadata](reports/paysim-v0.1.0/verification.json).

## Design decisions

- Pin the canonical source artifact by filename, size and SHA-256.
- Store request fields separately from balances, outcomes and the supplied policy flag.
- Preserve numeric values with `DECIMAL(18,2)` after exponent-adjusted precision checks.
- Use only completed earlier steps for historical activity; row IDs do not imply event order.
- Retain duplicate-valued rows and report merchant balance placeholders.
- Preserve the source's policy flag and report its discrepancy with the simplified published rule.

## Next milestone

Chronological partitions, past-only feature calculations and an interpretable rule baseline. Completion criteria are in the [roadmap](docs/MILESTONES.md).
