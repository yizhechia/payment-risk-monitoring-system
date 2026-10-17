-- Question: Which recipients recur in labelled fraud outcomes?
-- OUTCOME-SELECTED retrospective leads; these are NOT available online risk scores.
SELECT nameDest, count(*) AS transactions, sum(isFraud) AS fraud_transactions,
       sum(isFraud)::DOUBLE / count(*) AS fraud_rate,
       count(DISTINCT nameOrig) AS distinct_senders
FROM transactions
GROUP BY nameDest
HAVING sum(isFraud) > 0
ORDER BY fraud_transactions DESC, transactions DESC, nameDest
LIMIT $result_limit;
