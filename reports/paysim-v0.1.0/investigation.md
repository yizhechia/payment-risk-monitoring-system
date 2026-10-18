# PaySim SQL Investigation

Input SHA-256: `16910f90577b0d981bf8ff289714510bb89bc71bff7d3f220f024e287e4eea6b`.

Synthetic data only. All fraud labels are retrospective. Monetary values are unspecified local-currency units. No model has been trained and no production performance or prevented loss is claimed.

## Investigation findings

1. Labelled fraud by transaction type: TRANSFER: 4,097/532,909; CASH_OUT: 4,116/2,237,500. Compare the denominators; transaction type alone is not a fraud verdict.
2. At the declared review cutoff of 200000 local-currency units, 1,673,570 payments contain 5,471 labelled fraud outcomes, out of 8,213 labelled fraud outcomes overall. The cutoff is an investigation assumption, not an optimised or validated decision policy.
3. The highest-ranked fraud-linked recipient, C803116137, has 2 labelled fraud payments among 77 payments from 77 distinct senders. This lead was selected using outcomes. It is not an authorisation-time signal and does not establish a fraud network or coordinated behaviour.

## Existing-policy audit

The supplied flag disagrees with `type = 'TRANSFER' AND amount > 200000` on 409,094 of 6,362,620 transactions. This checks the publisher's short description against the actual flag; it does not rewrite the flag or infer undocumented simulator conditions. The flag remains a separately labelled benchmark.

## Query results

Per-query SQL hashes, bound parameters and all returned rows are in results.json. Time and type totals reconcile exactly to the validated input. Long listings are limited intentionally; an empty sample is not proof of no risk.

### Population and existing-policy audit

Query: `00_overview.sql`.

| transactions | total_amount | fraud_transactions | labelled_fraud_amount | high_value_transactions | high_value_fraud_transactions | legacy_true_positives | legacy_false_positives | legacy_false_negatives | legacy_true_negatives | transfers_above_documented_cutoff | legacy_description_disagreements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6362620 | 1144392944759.77 | 8213 | 12056415427.84 | 1673570 | 5471 | 16 | 0 | 8197 | 6354407 | 409110 | 409094 |


### Transaction and fraud trends

Query: `01_volume_by_step.sql`.

| step | transactions | total_amount | fraud_transactions | fraud_rate |
| --- | --- | --- | --- | --- |
| 1 | 2708 | 285429181.15 | 16 | 0.005908 |
| 2 | 1014 | 85921604.02 | 8 | 0.007890 |
| 3 | 552 | 43293884.42 | 4 | 0.007246 |
| 4 | 565 | 72910028.57 | 10 | 0.017699 |
| 5 | 665 | 45548089.75 | 6 | 0.009023 |
| 6 | 1660 | 164310551.22 | 22 | 0.013253 |
| 7 | 6837 | 832930814.24 | 12 | 0.001755 |
| 8 | 21097 | 3439602407.35 | 12 | 0.000569 |

Showing 8 of 743 returned rows; see results.json.


### Risk by transaction type

Query: `02_risk_by_type.sql`.

| type | transactions | total_amount | fraud_transactions | fraud_rate |
| --- | --- | --- | --- | --- |
| TRANSFER | 532909 | 485291987263.17 | 4097 | 0.007688 |
| CASH_OUT | 2237500 | 394412995224.49 | 4116 | 0.001840 |
| CASH_IN | 1399284 | 236367391912.46 | 0 | 0.000000 |
| DEBIT | 41432 | 227199221.28 | 0 | 0.000000 |
| PAYMENT | 2151495 | 28093371138.37 | 0 | 0.000000 |


### High-value investigation sample

Query: `03_high_value.sql`.

| row_id | step | type | amount | nameOrig | nameDest | isFraud | isFlaggedFraud | matching_population |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3686584 | 276 | TRANSFER | 92445516.64 | C1715283297 | C439737079 | 0 | 0 | 1673570 |
| 4060599 | 300 | TRANSFER | 73823490.36 | C2127282686 | C753026640 | 0 | 0 | 1673570 |
| 4146398 | 303 | TRANSFER | 71172480.42 | C2044643633 | C84111522 | 0 | 0 | 1673570 |
| 3946921 | 286 | TRANSFER | 69886731.30 | C1425667947 | C167875008 | 0 | 0 | 1673570 |
| 3911957 | 284 | TRANSFER | 69337316.27 | C1584456031 | C1472140329 | 0 | 0 | 1673570 |
| 3937153 | 286 | TRANSFER | 67500761.29 | C811810230 | C1757599079 | 0 | 0 | 1673570 |
| 4105339 | 302 | TRANSFER | 66761272.21 | C420748282 | C1073241084 | 0 | 0 | 1673570 |
| 3892530 | 284 | TRANSFER | 64234448.19 | C1139847449 | C65111466 | 0 | 0 | 1673570 |

Showing 8 of 25 returned rows; see results.json.


### Repeated senders and recipients

Query: `04_repeat_entities.sql`.

| role | account_id | transactions | total_amount |
| --- | --- | --- | --- |
| recipient | C1286084959 | 113 | 77428943.31 |
| recipient | C985934102 | 109 | 42422887.98 |
| recipient | C665576141 | 105 | 88749384.38 |
| recipient | C2083562754 | 102 | 53073938.76 |
| recipient | C1590550415 | 101 | 43206101.59 |
| recipient | C248609774 | 101 | 40680160.99 |
| recipient | C1789550256 | 99 | 177885264.60 |
| recipient | C451111351 | 99 | 37453031.39 |

Showing 8 of 25 returned rows; see results.json.


### Sender-recipient concentration

Query: `05_pair_concentration.sql`.

No matching rows.


### Previous completed-hour activity

Query: `06_prior_hour_activity.sql`.

| role | account_id | step | previous_hour_transactions | previous_hour_amount |
| --- | --- | --- | --- | --- |
| recipient | C1590550415 | 2 | 32 | 21468932.24 |
| recipient | C985934102 | 2 | 32 | 8980236.26 |
| recipient | C564160838 | 2 | 28 | 7181543.05 |
| recipient | C1023714065 | 2 | 22 | 5820096.91 |
| recipient | C33524623 | 2 | 22 | 6460108.41 |
| recipient | C401424608 | 2 | 22 | 5374033.88 |
| recipient | C1286084959 | 2 | 21 | 6500225.34 |
| recipient | C1789550256 | 2 | 20 | 8187248.66 |

Showing 8 of 25 returned rows; see results.json.


### Outcome-selected recipient leads

Query: `07_receiver_fraud_concentration.sql`.

| nameDest | transactions | fraud_transactions | fraud_rate | distinct_senders |
| --- | --- | --- | --- | --- |
| C803116137 | 77 | 2 | 0.025974 | 77 |
| C410033330 | 48 | 2 | 0.041667 | 48 |
| C185805228 | 47 | 2 | 0.042553 | 47 |
| C2020337583 | 41 | 2 | 0.048780 | 41 |
| C1193568854 | 37 | 2 | 0.054054 | 37 |
| C1013511446 | 35 | 2 | 0.057143 | 35 |
| C1655359478 | 34 | 2 | 0.058824 | 34 |
| C200064275 | 33 | 2 | 0.060606 | 33 |

Showing 8 of 25 returned rows; see results.json.


### Account history

Query: `08_account_history.sql`.

| row_id | step | type | amount | nameOrig | nameDest | isFraud | isFlaggedFraud |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 361127 | 17 | PAYMENT | 5530.99 | C1065307291 | M1175397032 | 0 | 0 |
| 1799164 | 162 | CASH_IN | 88230.47 | C1065307291 | C1154752493 | 0 | 0 |
| 4829223 | 347 | PAYMENT | 19717.82 | C1065307291 | M2131079968 | 0 | 0 |


## Interpretation limits

- Same-step row IDs break display ties only; they do not establish event order.
- Whole-period repeats and pair shares are retrospective, not time-safe features.
- The previous-hour query uses only step t-1; gaps are not compressed.
- Recipient leads use fraud outcomes for selection and cannot be used as predictors.
- Legacy-policy counts audit the supplied flag; they do not evaluate a new strategy.
- Labelled transaction value is not realised fraud loss or recoverable exposure.
- The monetary representation rejects unsupported precision rather than rounding.
- No causal inference or claim about real customer behaviour follows from PaySim.

## Data attribution

PaySim: Edgar Lopez-Rojas and collaborators, [Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1), version 2, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This report aggregates and selects synthetic source records; it is not endorsed by the dataset authors. Dataset-derived tables and summaries retain CC BY-SA 4.0 attribution.
