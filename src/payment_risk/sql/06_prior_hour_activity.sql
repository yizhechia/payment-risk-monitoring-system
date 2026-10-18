-- Question: What repeated activity was observable in the PREVIOUS completed hour?
-- RANGE counts step t-1 only; an earlier observed row after a time gap is not t-1.
-- No labels, balances, same-step counts or future rows feed the historical values.
WITH activity AS (
    SELECT 'sender' AS role, nameOrig AS account_id, step, amount FROM request_transactions
    UNION ALL
    SELECT 'recipient' AS role, nameDest AS account_id, step, amount FROM request_transactions
), hourly AS (
    SELECT role, account_id, step, count(*) AS current_hour_transactions,
           sum(amount) AS current_hour_amount
    FROM activity GROUP BY role, account_id, step
), history AS (
    SELECT role, account_id, step,
           coalesce(sum(current_hour_transactions) OVER previous_hour, 0)
               AS previous_hour_transactions,
           coalesce(sum(current_hour_amount) OVER previous_hour, 0) AS previous_hour_amount
    FROM hourly
    WINDOW previous_hour AS (
        PARTITION BY role, account_id ORDER BY step
        RANGE BETWEEN 1 PRECEDING AND 1 PRECEDING
    )
)
SELECT * FROM history
WHERE previous_hour_transactions >= 2
ORDER BY previous_hour_transactions DESC, step, role, account_id
LIMIT $result_limit;
