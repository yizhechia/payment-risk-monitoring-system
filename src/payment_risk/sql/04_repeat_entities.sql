-- Question: Which senders or recipients occur repeatedly? Roles remain separate.
WITH activity AS (
    SELECT 'sender' AS role, nameOrig AS account_id, amount FROM request_transactions
    UNION ALL
    SELECT 'recipient' AS role, nameDest AS account_id, amount FROM request_transactions
)
SELECT role, account_id, count(*) AS transactions, sum(amount) AS total_amount
FROM activity
GROUP BY role, account_id
HAVING count(*) > 1
ORDER BY transactions DESC, role, account_id
LIMIT $result_limit;
