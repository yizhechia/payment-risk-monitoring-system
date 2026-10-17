# Changelog

## 0.1.0 - Data foundation and SQL investigation

- Added version-pinned canonical PaySim acquisition and SHA-256 enforcement.
- Implemented strict schema/value validation with visible failure reports, no silent row removal and separate duplicate warnings.
- Preserved source numeric values with `DECIMAL(18,2)` after full-file inspection confirmed at most two effective decimal places, including scientific notation. Validation checks exponent-adjusted scale before casting.
- Separated request fields, balance audit fields, outcomes and the supplied policy flag in DuckDB.
- Added nine versioned SQL investigations, parameterised account lookup, exact population/amount reconciliation and reproducible reports.
- Audited the supplied policy flag against the publisher's simplified transfer-cutoff description without rewriting either.
- Added handcrafted fixture tests, CLI/acquisition tests and a software-only CI configuration.
- Replaced documentation-preview claims with current implementation evidence and explicit pending learning gates.

Models, tuned policies, a dashboard and user understanding remain outside this release's completion claims.

## Earlier documentation preview

Established dataset provenance, field meanings, decision-time restrictions and a leakage register. That checkpoint contained no executable pipeline or verified analytical results.
