-- 0001_initial_schema.sql

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    employee_name TEXT NOT NULL,
    rfid_uid TEXT UNIQUE,
    department TEXT NOT NULL,
    workstation TEXT,
    shift TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL UNIQUE,
    device_name TEXT,
    device_type TEXT NOT NULL DEFAULT 'WELLBEING_STATION',
    workstation TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'OFFLINE',
    last_seen_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    employee_id TEXT NOT NULL,
    device_id TEXT,
    feedback TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    employee_id TEXT NOT NULL,
    device_id TEXT,
    skin_temperature REAL,
    heart_rate REAL,
    spo2 REAL,
    gsr REAL,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES feedback_events(event_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE ml_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    employee_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    risk_score REAL,
    risk_level TEXT,
    prediction TEXT,
    confidence REAL,
    explanation TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES feedback_events(event_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE missing_feedback_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    device_id TEXT,
    expected_at TEXT NOT NULL,
    detected_at TEXT,
    gap_minutes INTEGER,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- INDEXES
CREATE INDEX idx_employees_employee_id ON employees(employee_id);
CREATE INDEX idx_employees_rfid ON employees(rfid_uid);
CREATE INDEX idx_employees_department ON employees(department);

CREATE INDEX idx_feedback_employee ON feedback_events(employee_id);
CREATE INDEX idx_feedback_timestamp ON feedback_events(timestamp);
CREATE INDEX idx_feedback_device ON feedback_events(device_id);

CREATE INDEX idx_sensor_employee ON sensor_readings(employee_id);
CREATE INDEX idx_sensor_event ON sensor_readings(event_id);
CREATE INDEX idx_sensor_timestamp ON sensor_readings(timestamp);

CREATE INDEX idx_prediction_employee ON ml_predictions(employee_id);
CREATE INDEX idx_prediction_event ON ml_predictions(event_id);
CREATE INDEX idx_prediction_risk ON ml_predictions(risk_level);

CREATE INDEX idx_missing_employee ON missing_feedback_events(employee_id);
CREATE INDEX idx_missing_status ON missing_feedback_events(status);
