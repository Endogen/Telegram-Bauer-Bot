SELECT to_username, SUM(amount)
FROM rain
GROUP BY to_username
ORDER BY 2 DESC
LIMIT 10