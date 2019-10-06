SELECT to_username, SUM(amount)
FROM tip
GROUP BY to_username
ORDER BY 2 DESC
LIMIT 10