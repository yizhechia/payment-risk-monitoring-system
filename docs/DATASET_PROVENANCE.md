# PaySim Dataset Provenance

## Verification status

**Metadata verified; raw-byte fingerprint pending.**

The canonical dataset record and exact file metadata were checked against Kaggle's live dataset page and public API on 2026-09-16. The CSV itself has not yet been acquired in the project environment, so its SHA-256 checksum and observed contents are not claimed as verified.

## Canonical artifact

| Property | Verified value |
|---|---|
| Dataset title | Synthetic Financial Datasets For Fraud Detection |
| Kaggle reference | `ealaxi/paysim1` |
| Dataset owner | Edgar Lopez-Rojas (`ealaxi`) |
| Dataset version | 2 |
| Version note | Sample PaySim dataset generated |
| Version publication | 2017-04-03T08:40:34.403Z |
| File | `PS_20174392719_1491204439457_log.csv` |
| Files in dataset | 1 |
| Reported file size | 493,534,783 bytes |
| Format | CSV |
| Reported rows | 6,362,620 |
| Reported columns | 11 |
| Reported legitimate rows | 6,354,407 |
| Reported fraud rows | 8,213 |
| License | CC BY-SA 4.0 |
| SHA-256 | **PENDING — compute from the downloaded version-2 file** |

Canonical record: <https://www.kaggle.com/datasets/ealaxi/paysim1>

## Provenance chain

1. The source material was one month of private financial logs from a mobile-money service operating in an African country.
2. The country, company, customers, currency, and raw private records are not disclosed.
3. PaySim used aggregated properties from those logs to calibrate an agent-based simulation of normal mobile-money activity.
4. Fraudulent behaviour was injected through simulated malicious agents; the fraud labels are therefore generated ground truth, not adjudicated real-world fraud outcomes.
5. The Kaggle artifact is described by the publisher as a one-quarter-scale synthetic dataset created specifically for Kaggle.
6. The artifact contains five transaction types: `CASH_IN`, `CASH_OUT`, `DEBIT`, `PAYMENT`, and `TRANSFER`.

Primary methodology reference:

E. A. Lopez-Rojas, A. Elmir, and S. Axelsson, “PaySim: A Financial Mobile Money Simulator for Fraud Detection,” *28th European Modeling and Simulation Symposium*, 2016.

Paper: <https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf>

Thesis referenced by the dataset publisher: <https://urn.kb.se/resolve?urn=urn:nbn:se:bth-12932>

## Known source limitations

- This is synthetic mobile-money data, not anonymised transaction-level production data.
- Results can demonstrate analytical and engineering methods, but cannot establish production fraud-detection performance.
- `step` is an hourly simulation bucket, not a real timestamp. It has no date, time zone, or documented order within an hour.
- The dataset does not include a transaction ID. CSV row position must not be treated as a business identifier.
- Currency is intentionally undisclosed. Monetary values must be described as local-currency units, not dollars.
- Destination balances are not available for merchant identifiers beginning with `M`; zero values for those rows are structural placeholders, not verified zero balances.
- The publisher states that detected fraudulent transactions are cancelled and warns against using all four balance columns for fraud detection. This conflicts with the project brief's provisional balance-feature ideas and is recorded as an open design issue.
- The description says the simulator ran for 744 hourly steps, while Kaggle's Data Explorer reports an artifact range from `1` to `743`. The ingestion stage must measure the actual minimum, maximum, and distinct-step count instead of assuming either interpretation.

## Reproducibility requirements for acquisition

When ingestion work is authorised:

1. Acquire version 2 from the canonical Kaggle reference.
2. Require the exact filename above.
3. Record file size and SHA-256 before parsing.
4. Compare the observed schema and record count with this manifest.
5. Store the raw file outside Git.
6. Fail visibly if the file fingerprint or schema differs; do not silently accept another PaySim mirror or sample.
