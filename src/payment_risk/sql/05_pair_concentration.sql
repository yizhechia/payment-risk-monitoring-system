-- Question: Is a sender's activity concentrated on a particular recipient?
-- Full-period retrospective concentration; never use this as an online feature.
WITH pairs AS (
    SELECT nameOrig, nameDest, count(*) AS pair_transactions, sum(amount) AS total_amount
    FROM request_transactions GROUP BY nameOrig, nameDest
)
SELECT *, sum(pair_transactions) OVER (PARTITION BY nameOrig) AS sender_transactions,
       pair_transactions::DOUBLE / sum(pair_transactions) OVER (PARTITION BY nameOrig)
           AS sender_count_share
FROM pairs
QUALIFY pair_transactions > 1
ORDER BY pair_transactions DESC, nameOrig, nameDest
LIMIT $result_limit;
