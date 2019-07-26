CREATE TABLE users (
	user_id INTEGER NOT NULL PRIMARY KEY,
	username TEXT NOT NULL,
	first_name TEXT NOT NULL,
	last_name TEXT,
	language TEXT,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)