CREATE TABLE terms_accepted (
    user_id TEXT NOT NULL,
	username TEXT NOT NULL PRIMARY KEY,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)