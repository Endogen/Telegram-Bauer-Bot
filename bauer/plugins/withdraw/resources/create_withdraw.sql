CREATE TABLE withdraw (
	username TEXT NOT NULL,
	address TEXT NOT NULL,
	amount REAL NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)