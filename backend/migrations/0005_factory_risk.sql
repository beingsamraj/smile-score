CREATE TABLE IF NOT EXISTS factory_risk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    confidence REAL NOT NULL,
    average_smile_score REAL,
    sad_ratio REAL,
    happy_ratio REAL,
    active_workers INTEGER,
    calculated_at TEXT NOT NULL,
    model_version TEXT,
    FOREIGN KEY (factory_id) REFERENCES factories(factory_id)
);
