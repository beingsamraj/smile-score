CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    employee_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'hr', 'nurse')),
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (id, employee_code, full_name, email, role, status) VALUES
('USR001', 'ADMIN001', 'Admin User', 'admin@smilescore.com', 'admin', 'active'),
('USR002', 'NURSE001', 'Godwin Samraj', 'samrajgodwin7@gmail.com', 'nurse', 'active')
ON CONFLICT(employee_code) DO NOTHING;
