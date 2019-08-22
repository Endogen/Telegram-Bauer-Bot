CREATE TABLE terms (
	username TEXT NOT NULL PRIMARY KEY,
	terms_accepted INTEGER NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(username) REFERENCES users(username),
	CONSTRAINT bool_check CHECK (terms_accepted = 0 OR terms_accepted = 1)
)