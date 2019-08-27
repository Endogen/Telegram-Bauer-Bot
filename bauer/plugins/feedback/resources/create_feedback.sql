CREATE TABLE feedback (
    user_id INTEGER NOT NULL PRIMARY KEY,
    first_name TEXT NOT NULL,
	username TEXT,
	feedback TEXT NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)