"""
database.py — SQLite data layer for AquaGuard IoT Water Leakage Detection System

Manages TWO databases:
  • water_leakage.db  — detailed tables: sensor_readings, leak_events
  • water_data.db     — simplified logs table (as per project spec):
                        logs(id, time, flow, moisture, status)

All functions are safe to call from multiple Streamlit reruns.
"""

import sqlite3
from datetime import datetime

# ── Database paths ──────────────────────────────────────────────────────────
DB_MAIN = "water_leakage.db"   # full detail DB (sensor_readings + leak_events)
DB_LOGS = "water_data.db"      # simplified logs DB  (logs table)


# ══════════════════════════════════════════════════════════════════════════════
# ── CONNECTION HELPER ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _conn(path: str) -> sqlite3.Connection:
    """Return a SQLite connection with Row factory for dict-like access."""
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c


# ══════════════════════════════════════════════════════════════════════════════
# ── SCHEMA INITIALISATION ────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def init_db():
    """Create all tables in both databases if they don't already exist."""

    # ── water_leakage.db ──────────────────────────────────────────────────────
    conn = _conn(DB_MAIN)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            flow_rate   REAL    NOT NULL,
            moisture    REAL    NOT NULL,
            leak_status INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS leak_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            trigger     TEXT    NOT NULL,
            flow_rate   REAL    NOT NULL,
            moisture    REAL    NOT NULL
        );
    """)
    conn.commit()
    conn.close()

    # ── water_data.db — required 'logs' table ────────────────────────────────
    conn2 = _conn(DB_LOGS)
    conn2.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            time     TEXT    NOT NULL,
            flow     REAL    NOT NULL,
            moisture REAL    NOT NULL,
            status   TEXT    NOT NULL
        )
    """)
    conn2.commit()
    conn2.close()


# ══════════════════════════════════════════════════════════════════════════════
# ── WRITE OPERATIONS ─────────────────────────════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════

def log_reading(flow_rate: float, moisture: float, leak_status: bool):
    """Write one sensor tick to BOTH databases."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_str = "Leak Detected" if leak_status else "Normal"

    conn = _conn(DB_MAIN)
    conn.execute(
        "INSERT INTO sensor_readings (timestamp, flow_rate, moisture, leak_status) VALUES (?,?,?,?)",
        (now, flow_rate, moisture, int(leak_status))
    )
    conn.commit()
    conn.close()

    conn2 = _conn(DB_LOGS)
    conn2.execute(
        "INSERT INTO logs (time, flow, moisture, status) VALUES (?,?,?,?)",
        (now, flow_rate, moisture, status_str)
    )
    conn2.commit()
    conn2.close()


def log_leak_event(trigger: str, flow_rate: float, moisture: float):
    """Insert a leak event row into water_leakage.db -> leak_events."""
    conn = _conn(DB_MAIN)
    conn.execute(
        "INSERT INTO leak_events (timestamp, trigger, flow_rate, moisture) VALUES (?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trigger, flow_rate, moisture)
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# ── READ OPERATIONS ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def get_recent_readings(limit: int = 60) -> list:
    """Fetch most recent N sensor readings in chronological order."""
    conn = _conn(DB_MAIN)
    rows = conn.execute(
        "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def get_leak_history(limit: int = 20) -> list:
    """Fetch most recent N leak events (newest first)."""
    conn = _conn(DB_MAIN)
    rows = conn.execute(
        "SELECT * FROM leak_events ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_logs(limit: int = 50) -> list:
    """Fetch most recent N rows from water_data.db -> logs (for st.dataframe)."""
    conn = _conn(DB_LOGS)
    rows = conn.execute(
        "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_leak_logs(limit: int = 50) -> list:
    """Fetch only Leak Detected rows from logs table."""
    conn = _conn(DB_LOGS)
    rows = conn.execute(
        "SELECT * FROM logs WHERE status='Leak Detected' ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Return aggregate statistics for sidebar summary cards."""
    conn  = _conn(DB_MAIN)
    total = conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0]
    leaks = conn.execute("SELECT COUNT(*) FROM leak_events").fetchone()[0]
    avg_f = conn.execute("SELECT AVG(flow_rate) FROM sensor_readings").fetchone()[0] or 0
    avg_m = conn.execute("SELECT AVG(moisture)  FROM sensor_readings").fetchone()[0] or 0
    conn.close()

    conn2      = _conn(DB_LOGS)
    total_logs = conn2.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    leak_logs  = conn2.execute("SELECT COUNT(*) FROM logs WHERE status='Leak Detected'").fetchone()[0]
    conn2.close()

    return {
        "total_readings": total,
        "total_leaks":    leaks,
        "avg_flow":       round(avg_f, 2),
        "avg_moisture":   round(avg_m, 2),
        "total_logs":     total_logs,
        "leak_logs":      leak_logs,
    }