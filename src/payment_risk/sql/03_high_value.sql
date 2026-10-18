-- Question: Which high-value payments warrant retrospective inspection?
-- This amount cutoff is an investigation parameter, not a tuned decision policy.
SELECT row_id, step, type, amount, nameOrig, nameDest, isFraud, isFlaggedFraud,
       count(*) OVER () AS matching_population
FROM transactions
WHERE amount >= $minimum_amount
ORDER BY amount DESC, step, row_id
LIMIT $result_limit;
