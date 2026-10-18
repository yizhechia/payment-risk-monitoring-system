# PaySim Dataset Provenance

## Artifact identity and observed evidence

The canonical source is [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1), published by Edgar Lopez-Rojas (`ealaxi`). The live Kaggle metadata API confirmed version 2 and CC BY-SA 4.0. The acquisition record names the version-pinned endpoint below; a fresh local fingerprint matches it. Full-file validation has passed.

| Property | Value | Evidence |
| --- | --- | --- |
| Dataset | `ealaxi/paysim1`, version 2 | Canonical metadata |
| Source last-updated timestamp | `2017-04-03T08:40:34.403Z` | Canonical metadata |
| File | `PS_20174392719_1491204439457_log.csv` | Download and raw-file fingerprint |
| Bytes | 493,534,783 | Local measurement and canonical file-list metadata |
| SHA-256 | `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b` | Local measurement, pinned in the package manifest |
| Rows | 6,362,620 | Full-file validation |
| Columns | 11 source fields, plus generated `row_id` in DuckDB | Header check and typed schema |
| Fraud / legitimate | 8,213 / 6,354,407 | Full-file validation |
| Supplied policy flags | 16 | Full-file validation |
| Step coverage | 1 through 743; 743 distinct buckets | Full-file validation |
| Missing / invalid field values | 0 for the implemented checks | Full-file validation |
| Duplicate-valued extra rows | 0 | Grouping across all 11 typed source fields |
| Merchant zero-placeholder rows | 2,151,495 | Destination prefix `M` with both destination balances zero |
| Monetary storage | `DECIMAL(18,2)` | At most two effective fractional digits after exponent adjustment |
| Dataset license | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Canonical metadata |

Full observed schema, monetary ranges, checks and notation counts are in [validation.json](../reports/paysim-v0.1.0/validation.json). No records were dropped or imputed.

## Acquisition and pinning

Version-pinned endpoint:

<https://www.kaggle.com/api/v1/datasets/download/ealaxi/paysim1?datasetVersionNumber=2>

Metadata endpoints used:

- <https://www.kaggle.com/api/v1/datasets/view/ealaxi/paysim1>
- <https://www.kaggle.com/api/v1/datasets/list/ealaxi/paysim1>

`payment-risk download` requires the expected ZIP member, uncompressed size and CSV checksum. `payment-risk run` independently checks filename, size, hash, header and contents. Another sample, mirror or hash is not silently substituted. Source access may require Kaggle sign-in; manual canonical version-2 acquisition is documented in the README.

This SHA-256 is the fingerprint of the acquired canonical artifact, not an independently signed publisher checksum. Reproduction verifies identity against this project pin. The raw CSV and generated DuckDB files remain outside Git.

## Source semantics and limitations

The publisher describes this artifact as synthetic mobile-money transactions generated from aggregated properties of private source logs. Fraud labels identify simulated malicious-agent activity. The publication does not provide real customer records, actual fraud adjudication, precise timestamps, label-delay timestamps or realised-loss outcomes.

All four balance fields remain restricted to audit because the publisher warns against their use for fraud detection when detected fraud is cancelled. Merchant destination balance zeros are structurally unavailable, not observed zero customer balances. `isFlaggedFraud` is retained as a supplied policy output, separately from both targets and eligible request fields.

The original PaySim paper explains the simulator. The specific Kaggle artifact's labels, supplied flag and balance warning are sourced to its publisher metadata; they are not attributed solely to the earlier simulator paper.

## Two resolved ingestion questions

**Step coverage:** source prose describes 744 simulation hours; the selected artifact contains exactly 743 distinct step values, 1-743. Code and reporting use that observed range. No extra hour is fabricated. The reason for the source-prose difference is not established.

**Monetary notation:** ordinary decimals and scientific notation both occur. For example, `1.916920493E7` equals `19169204.93`; counting characters after the decimal point would give a false precision warning. Effective scale was measured across all five monetary fields and is at most two. The validator checks syntax, exponent-adjusted precision and decimal range before casting; it rejects unsupported precision rather than relying on a rounding cast.

## Attribution

Edgar Lopez-Rojas and collaborators, *Synthetic Financial Datasets For Fraud Detection*, Kaggle, version 2, CC BY-SA 4.0. Dataset-derived report tables and summaries retain that attribution and license. Changes consist of validation, aggregation and selected-record reporting; no author endorsement is implied.

Methodology reference: E. A. Lopez-Rojas, A. Elmir and S. Axelsson, *PaySim: A Financial Mobile Money Simulator for Fraud Detection*, EMSS 2016. [Original paper](https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf).
