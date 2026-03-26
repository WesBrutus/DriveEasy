"""
Database connection and initialization for DriveEasy VRMS.
Uses SQLite for portability — swap to MySQL/PostgreSQL by changing the connection string.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "driveeasy.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database with row-factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force: bool = False) -> None:
    """Create all tables from schema.sql.  If `force`, drop + recreate."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    if force:
        # Drop all tables in reverse dependency order
        tables = [
            "Payments", "MaintenanceRecords", "RentalAgreements",
            "MaintenanceStaff", "Vehicles", "VehicleTypes", "Customers", "Branches",
        ]
        for t in tables:
            conn.execute(f"DROP TABLE IF EXISTS {t}")
        conn.commit()
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT query and return a list of dicts."""
    conn = get_connection()
    cur = conn.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def execute(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid."""
    conn = get_connection()
    cur = conn.execute(sql, params)
    conn.commit()
    lastid = cur.lastrowid
    conn.close()
    return lastid
