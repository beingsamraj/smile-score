CREATE TABLE IF NOT EXISTS factories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id TEXT NOT NULL UNIQUE,
    factory_name TEXT NOT NULL,
    location TEXT,
    status INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO factories (factory_id, factory_name, location, status) 
VALUES 
('FAC001', 'Primary Facility', 'New York', 1),
('FAC002', 'Secondary Assembly', 'Austin', 1);

CREATE VIEW IF NOT EXISTS emotions AS
SELECT 
    f.created_at,
    f.timestamp,
    f.feedback as emotion,
    CASE 
        WHEN f.feedback = 'HAPPY' THEN 85.0
        WHEN f.feedback = 'OK' THEN 60.0
        WHEN f.feedback = 'SAD' THEN 30.0
        ELSE 50.0 
    END as smile_score,
    COALESCE(d.location, 'FAC001') as factory_id
FROM feedback_events f
LEFT JOIN devices d ON f.device_id = d.device_id;
