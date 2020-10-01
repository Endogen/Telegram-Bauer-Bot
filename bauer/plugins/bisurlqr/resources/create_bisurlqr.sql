CREATE TABLE bisurlqr (
    id TEST NOT NULL,
	username TEXT NOT NULL,
	address TEXT NOT NULL,
	amount REAL NOT NULL,
	operation TEXT,
	message TEXT,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)