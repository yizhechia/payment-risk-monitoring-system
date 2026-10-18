-- Question: What payments involve the requested synthetic account?
-- row_id breaks display ties only. It does not establish within-hour event order.
SELECT row_id, step, type, amount, nameOrig, nameDest, isFraud, isFlaggedFraud
FROM transactions
WHERE nameOrig = $account_id OR nameDest = $account_id
ORDER BY step, row_id
LIMIT $result_limit;
