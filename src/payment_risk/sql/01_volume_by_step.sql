-- Question: How do payment volume and labelled fraud vary across simulation hours?
SELECT step, count(*) AS transactions, sum(amount) AS total_amount,
       sum(isFraud) AS fraud_transactions,
       sum(isFraud)::DOUBLE / count(*) AS fraud_rate
FROM transactions
GROUP BY step
ORDER BY step;
