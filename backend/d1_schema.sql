-- Cloudflare D1 SQLite Schema for Smile Score

CREATE TABLE IF NOT EXISTS factories (
    factory_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    department_id TEXT PRIMARY KEY,
    factory_id TEXT,
    name TEXT NOT NULL,
    FOREIGN KEY(factory_id) REFERENCES factories(factory_id)
);

CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    factory_id TEXT NOT NULL,
    department_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    name TEXT NOT NULL,
    rfid_uid TEXT NOT NULL UNIQUE,
    designation TEXT,
    status INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(factory_id, employee_id),
    FOREIGN KEY(factory_id) REFERENCES factories(factory_id),
    FOREIGN KEY(department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS emotions (
    emotion_id TEXT PRIMARY KEY,
    worker_id TEXT NOT NULL,
    department_id TEXT,
    factory_id TEXT,
    emotion TEXT NOT NULL,
    smile_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(worker_id) REFERENCES workers(worker_id),
    FOREIGN KEY(department_id) REFERENCES departments(department_id),
    FOREIGN KEY(factory_id) REFERENCES factories(factory_id)
);
