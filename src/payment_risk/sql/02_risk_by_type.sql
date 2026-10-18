-- Question: Which payment types contain labelled fraud, and with what denominators?
SELECT type, count(*) AS transactions, sum(amount) AS total_amount,
       sum(isFraud) AS fraud_transactions,
       sum(isFraud)::DOUBLE / count(*) AS fraud_rate
FROM transactions
GROUP BY type
ORDER BY fraud_rate DESC, type;
