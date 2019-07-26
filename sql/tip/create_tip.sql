CREATE TABLE tip (
	from_username TEXT NOT NULL,
	to_username TEXT NOT NULL,
	amount REAL NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(from_username) REFERENCES users(username),
	FOREIGN KEY(to_username) REFERENCES users(username)
)