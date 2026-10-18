-- Question: What are the volume, labelled fraud and high-value review populations?
-- Retrospective labels; a high amount alone is not a fraud verdict.
SELECT count(*) AS transactions,
       sum(amount) AS total_amount,
       sum(isFraud) AS fraud_transactions,
       sum(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS labelled_fraud_amount,
       count(*) FILTER (WHERE amount >= $minimum_amount) AS high_value_transactions,
       count(*) FILTER (WHERE amount >= $minimum_amount AND isFraud = 1)
           AS high_value_fraud_transactions,
       count(*) FILTER (WHERE isFlaggedFraud = 1 AND isFraud = 1) AS legacy_true_positives,
       count(*) FILTER (WHERE isFlaggedFraud = 1 AND isFraud = 0) AS legacy_false_positives,
       count(*) FILTER (WHERE isFlaggedFraud = 0 AND isFraud = 1) AS legacy_false_negatives,
       count(*) FILTER (WHERE isFlaggedFraud = 0 AND isFraud = 0) AS legacy_true_negatives,
       count(*) FILTER (WHERE type = 'TRANSFER' AND amount > 200000)
           AS transfers_above_documented_cutoff,
       count(*) FILTER (
           WHERE (type = 'TRANSFER' AND amount > 200000) <> (isFlaggedFraud = 1)
       ) AS legacy_description_disagreements
FROM transactions;
