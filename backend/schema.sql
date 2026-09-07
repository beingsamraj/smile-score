-- factories (updated with new fields)
CREATE TABLE IF NOT EXISTS public.factories (
    factory_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(255),
    manager_name VARCHAR(150),
    contact_number VARCHAR(20),
    email VARCHAR(150),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- users (already provided by the user)
-- public.users (...)

-- departments
CREATE TABLE IF NOT EXISTS public.departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    production_line VARCHAR(100),
    factory_id VARCHAR(20) REFERENCES public.factories(factory_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- workers
CREATE TABLE IF NOT EXISTS public.workers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id UUID REFERENCES public.departments(id),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- devices
CREATE TABLE IF NOT EXISTS public.devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_code VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'OFFLINE',
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- emotions
CREATE TABLE IF NOT EXISTS public.emotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID REFERENCES public.workers(id),
    emotion VARCHAR(20) NOT NULL, -- 'happy', 'ok', 'sad'
    source VARCHAR(20) NOT NULL, -- 'button', 'camera', 'fusion'
    smile_score NUMERIC(5, 2), -- e.g., 85.5
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    device_id UUID REFERENCES public.devices(id)
);

-- production_risk
CREATE TABLE IF NOT EXISTS public.production_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'NO_DATA'
    confidence NUMERIC(5, 2),
    reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- alerts
CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    severity VARCHAR(20) NOT NULL, -- 'INFO', 'WARNING', 'CRITICAL'
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    related_worker_id UUID REFERENCES public.workers(id),
    related_device_id UUID REFERENCES public.devices(id)
);

-- shifts
CREATE TABLE IF NOT EXISTS public.shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL, -- 'Morning', 'Afternoon', 'Night'
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);


-- --------------------------------------------------------
-- USERS TABLE ALTERATIONS (Added for Users CRUD module)
-- --------------------------------------------------------
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS employee_code VARCHAR(50) UNIQUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS full_name VARCHAR(150);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(150);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS rfid_uid VARCHAR(100) UNIQUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS auth_user_id UUID UNIQUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- NOTE: existing columns user_id, username, user_pin, user_role, factory_id, status, created_at
-- are retained for login compatibility.


-- --------------------------------------------------------
-- DEVICES TABLE ALTERATIONS (Added for Devices CRUD module)
-- --------------------------------------------------------
ALTER TABLE public.devices ADD COLUMN IF NOT EXISTS device_type VARCHAR(50) DEFAULT 'other';
ALTER TABLE public.devices ADD COLUMN IF NOT EXISTS mac_address VARCHAR(50) UNIQUE;
ALTER TABLE public.devices ADD COLUMN IF NOT EXISTS firmware_version VARCHAR(50);
ALTER TABLE public.devices ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE public.devices ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- NOTE: existing columns device_id, factory_id, device_name, location, status, last_seen, created_at
-- are retained for compatibility.
