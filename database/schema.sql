-- ============================================================
-- DriveEasy Rentals — Vehicle Rental Management System (VRMS)
-- Enhanced Database Schema (SQLite-compatible)
-- ============================================================

-- Enable foreign key enforcement (SQLite)
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- 1. Branches
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Branches (
    branch_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    address      TEXT    NOT NULL,
    city         TEXT    NOT NULL DEFAULT '',
    state        TEXT    NOT NULL DEFAULT '',
    zip_code     TEXT    NOT NULL DEFAULT '',
    phone_number TEXT    NOT NULL,
    email        TEXT,
    opening_hour TEXT    DEFAULT '08:00',
    closing_hour TEXT    DEFAULT '20:00',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- 2. Customers
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Customers (
    customer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name     TEXT NOT NULL,
    last_name      TEXT NOT NULL,
    address        TEXT NOT NULL,
    city           TEXT NOT NULL DEFAULT '',
    state          TEXT NOT NULL DEFAULT '',
    zip_code       TEXT NOT NULL DEFAULT '',
    phone_number   TEXT NOT NULL,
    email          TEXT UNIQUE,
    license_number TEXT UNIQUE NOT NULL,
    license_expiry DATE NOT NULL,
    date_of_birth  DATE,
    loyalty_points INTEGER DEFAULT 0 CHECK (loyalty_points >= 0),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- 3. Vehicle Types (new lookup table)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS VehicleTypes (
    type_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- -----------------------------------------------------------
-- 4. Vehicles
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Vehicles (
    vehicle_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate   TEXT UNIQUE NOT NULL,
    make            TEXT NOT NULL,
    model           TEXT NOT NULL,
    year            INTEGER NOT NULL CHECK (year >= 1990),
    color           TEXT,
    daily_rate      REAL NOT NULL CHECK (daily_rate > 0),
    current_mileage INTEGER NOT NULL CHECK (current_mileage >= 0),
    fuel_type       TEXT DEFAULT 'Gasoline' CHECK (fuel_type IN ('Gasoline','Diesel','Electric','Hybrid')),
    transmission    TEXT DEFAULT 'Automatic' CHECK (transmission IN ('Automatic','Manual')),
    seats           INTEGER DEFAULT 5 CHECK (seats > 0),
    availability    TEXT DEFAULT 'Available' CHECK (availability IN ('Available','Rented','Maintenance','Retired')),
    vehicle_type_id INTEGER,
    branch_id       INTEGER NOT NULL,
    image_url       TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type_id) REFERENCES VehicleTypes(type_id),
    FOREIGN KEY (branch_id)       REFERENCES Branches(branch_id)
);

-- -----------------------------------------------------------
-- 5. Maintenance Staff
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS MaintenanceStaff (
    staff_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    specialization TEXT DEFAULT 'General',
    office_number TEXT,
    phone_number  TEXT,
    email         TEXT UNIQUE,
    hire_date     DATE,
    branch_id     INTEGER NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id)
);

-- -----------------------------------------------------------
-- 6. Rental Agreements
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS RentalAgreements (
    agreement_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id       INTEGER NOT NULL,
    customer_id      INTEGER NOT NULL,
    pickup_branch_id INTEGER NOT NULL,
    return_branch_id INTEGER NOT NULL,
    scheduled_pickup TIMESTAMP NOT NULL,
    scheduled_return TIMESTAMP NOT NULL,
    actual_pickup    TIMESTAMP,
    actual_return    TIMESTAMP,
    estimated_cost   REAL CHECK (estimated_cost >= 0),
    actual_cost      REAL CHECK (actual_cost >= 0),
    insurance_type   TEXT DEFAULT 'Basic' CHECK (insurance_type IN ('None','Basic','Premium','Full')),
    payment_method   TEXT CHECK (payment_method IN ('Credit Card','Debit Card','Cash','Online')),
    status           TEXT NOT NULL DEFAULT 'Booked'
                     CHECK (status IN ('Booked','Active','Completed','Cancelled','Overdue')),
    notes            TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (scheduled_return > scheduled_pickup),
    FOREIGN KEY (vehicle_id)       REFERENCES Vehicles(vehicle_id),
    FOREIGN KEY (customer_id)      REFERENCES Customers(customer_id),
    FOREIGN KEY (pickup_branch_id) REFERENCES Branches(branch_id),
    FOREIGN KEY (return_branch_id) REFERENCES Branches(branch_id)
);

-- -----------------------------------------------------------
-- 7. Maintenance Records
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS MaintenanceRecords (
    record_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id            INTEGER NOT NULL,
    reporting_customer_id INTEGER,
    incident_date         TIMESTAMP NOT NULL,
    issue_type            TEXT NOT NULL CHECK (issue_type IN ('Routine','Urgent','Recall','Inspection')),
    description           TEXT NOT NULL,
    status                TEXT NOT NULL DEFAULT 'Reported'
                          CHECK (status IN ('Reported','In-Progress','Complete','Awaiting Parts','Cancelled')),
    priority              TEXT DEFAULT 'Medium' CHECK (priority IN ('Low','Medium','High','Critical')),
    estimated_cost        REAL CHECK (estimated_cost >= 0),
    actual_cost           REAL CHECK (actual_cost >= 0),
    resolved_at           TIMESTAMP,
    notes                 TEXT,
    staff_id              INTEGER,
    CHECK (resolved_at IS NULL OR resolved_at >= incident_date),
    FOREIGN KEY (vehicle_id)            REFERENCES Vehicles(vehicle_id),
    FOREIGN KEY (reporting_customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (staff_id)              REFERENCES MaintenanceStaff(staff_id)
);

-- -----------------------------------------------------------
-- 8. Payments (new table)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Payments (
    payment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id INTEGER NOT NULL,
    amount       REAL NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method       TEXT CHECK (method IN ('Credit Card','Debit Card','Cash','Online')),
    status       TEXT DEFAULT 'Completed' CHECK (status IN ('Pending','Completed','Refunded','Failed')),
    FOREIGN KEY (agreement_id) REFERENCES RentalAgreements(agreement_id)
);

-- -----------------------------------------------------------
-- Indexes for performance
-- -----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_vehicles_branch      ON Vehicles(branch_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_availability ON Vehicles(availability);
CREATE INDEX IF NOT EXISTS idx_rentals_status        ON RentalAgreements(status);
CREATE INDEX IF NOT EXISTS idx_rentals_customer      ON RentalAgreements(customer_id);
CREATE INDEX IF NOT EXISTS idx_rentals_vehicle       ON RentalAgreements(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle   ON MaintenanceRecords(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_status    ON MaintenanceRecords(status);
