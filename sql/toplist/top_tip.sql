SELECT from_username, SUM(amount)
FROM tip
GROUP BY from_username
ORDER BY 2 DESC
LIMIT 10