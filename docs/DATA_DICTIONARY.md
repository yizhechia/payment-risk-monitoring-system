# PaySim Field-Level Data Dictionary

## Decision point

For this project, the operational decision point is:

> The instant immediately before the transaction is allowed or blocked and before either account balance is mutated.

A field can be useful for retrospective investigation without being valid for an authorization-time risk decision. “Available” below means causally available at that decision point; it does not automatically mean that the field is approved as a model feature.

## Availability classes

| Class | Meaning |
|---|---|
| `REQUEST` | Supplied with, or deterministically known from, the transaction request before the decision. |
| `PRE_STATE` | Describes system state immediately before the transaction, but operational access may depend on whether the account is visible to the payment system. |
| `POST_STATE` | Created only after execution, cancellation, or ledger mutation. Unavailable for the original authorization decision. |
| `POLICY_OUTPUT` | Produced by an existing decision rule during the decision process. It is not an independent transaction attribute. |
| `OUTCOME` | Ground truth assigned after or outside the decision process. |
| `TIME_AMBIGUOUS` | The coarse time bucket is known, but it does not establish an order among records in that bucket. |

## Raw fields

| Field | Expected raw type | Meaning and constraints | Decision-time classification | Approved use at this stage |
|---|---|---|---|---|
| `step` | Integer | Simulated hourly bucket. Source documentation says 744 hours; full-file validation measured values `1`-`743`, with 743 distinct buckets. No calendar timestamp or time zone is supplied. | `REQUEST` + `TIME_AMBIGUOUS` | Chronological grouping and step-level trends. It must not establish order between rows in the same step. |
| `type` | String / category | Expected values: `CASH_IN`, `CASH_OUT`, `DEBIT`, `PAYMENT`, `TRANSFER`. | `REQUEST` | Candidate authorization-time input and investigation dimension. |
| `amount` | Non-negative numeric | Transaction value in an undisclosed local currency. No currency code is supplied. | `REQUEST` | Candidate authorization-time input. Do not label values as dollars. |
| `nameOrig` | String | Synthetic identifier of the initiating customer. Expected to be non-null; identifier pattern must be measured from the file rather than assumed. | `REQUEST` | Entity key for historical sender activity. It is not a real customer identity. |
| `oldbalanceOrg` | Non-negative numeric | Origin account balance before the transaction. | `PRE_STATE` but **dataset-restricted** | Temporally pre-decision in principle, but not approved for predictive features because the publisher warns against using all balance fields when detected fraud is cancelled. May be retained for data-quality and retrospective investigation. |
| `newbalanceOrig` | Non-negative numeric | Origin account balance after processing or cancellation. | `POST_STATE` | Excluded from authorization-time features. Retain only for validation and post-event investigation. |
| `nameDest` | String | Synthetic recipient identifier. Customer and merchant identifiers are distinguishable by their prefixes in the artifact. | `REQUEST` | Entity key for recipient history and concentration analysis. |
| `oldbalanceDest` | Non-negative numeric | Recipient balance before the transaction. The publisher states that merchant destinations beginning with `M` have no balance information; zero is therefore structurally ambiguous. | `PRE_STATE`, operationally conditional, and **dataset-restricted** | Not approved for predictive features. May support carefully qualified validation or retrospective investigation for eligible customer destinations. |
| `newbalanceDest` | Non-negative numeric | Recipient balance after processing or cancellation. Merchant values are structurally unavailable. | `POST_STATE` | Excluded from authorization-time features. Retain only for validation and post-event investigation. |
| `isFraud` | Integer / Boolean | Simulator-generated ground-truth label: `1` fraud, `0` legitimate. | `OUTCOME` | Target and evaluation field only. Never an input feature. |
| `isFlaggedFraud` | Integer / Boolean | Output of the existing simulated business rule for large transfers; the publisher describes the rule as flagging transfer attempts above 200,000 local-currency units. | `POLICY_OUTPUT` | Retain as a legacy-rule benchmark. Exclude from candidate model features and from any “independent” risk signal calculation. |

## Important absences

The raw artifact has no:

- transaction ID;
- exact event timestamp;
- intra-hour sequence;
- date or time zone;
- currency code;
- country identifier;
- device, IP, authentication, channel, or geographic fields;
- investigation outcome date or label-delay information.

A generated row number may be used only as a technical ingestion key. It must not be presented as a source-system transaction ID or used to infer same-step chronology.

## Decision-time feature boundary

For a transaction in step `t`, an authorization-time feature may use:

- request fields on that transaction; and
- aggregates of eligible request-time activity from completed steps strictly less than `t`.

It may not use:

- either post-transaction balance;
- the fraud label;
- the existing flag as an independent predictor;
- any transaction from a future step;
- any other row from step `t` under an assumed CSV ordering.

Past fraud labels are not automatically available history. The dataset has no label-availability timestamps, so historical fraud-label aggregates are excluded from the initial feature policy.

This conservative boundary sacrifices some apparent signal in exchange for a defensible simulation of what the risk system could have known.

## Implemented storage contract

All 11 source fields are first parsed as strings so schema inference cannot silently alter them. The validated representation uses `INTEGER` for `step`, `UTINYINT` for binary labels, `VARCHAR` for type/entity fields, and `DECIMAL(18,2)` for all five monetary fields. Ordinary decimals and scientific notation are accepted only when the exponent-adjusted scale is at most two and the value fits the non-negative decimal range. Greater precision is rejected before casting. This scale is observed in the selected artifact; the currency remains unspecified.

`row_id` is a generated `BIGINT`, assigned under single-thread, nonparallel CSV ingestion. It joins the request, balance, outcome and supplied-policy tables. The joined `transactions` view is retrospective. A schema test checks that the request table excludes labels, policy outputs and all balances. A model feature-matrix contract remains future work.
