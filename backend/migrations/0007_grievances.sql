CREATE TABLE IF NOT EXISTS grievances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grievance_id TEXT NOT NULL UNIQUE,
    employee_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW',
    trigger_reason TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS grievance_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grievance_id TEXT NOT NULL,
    note TEXT NOT NULL,
    added_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grievance_id) REFERENCES grievances(grievance_id)
);

CREATE TABLE IF NOT EXISTS grievance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grievance_id TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grievance_id) REFERENCES grievances(grievance_id)
);

CREATE INDEX idx_grievances_employee ON grievances(employee_id);
CREATE INDEX idx_grievances_status ON grievances(status);
