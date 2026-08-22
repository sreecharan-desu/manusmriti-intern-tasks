from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from auth_service.settings import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    email_verified INTEGER NOT NULL DEFAULT 0,
    verification_token TEXT,
    verification_expires TEXT
)
"""

_COLUMNS = (
    ("email_verified", "INTEGER NOT NULL DEFAULT 0"),
    ("verification_token", "TEXT"),
    ("verification_expires", "TEXT"),
)


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=5000")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute(SCHEMA)
    existing = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
    for name, definition in _COLUMNS:
        if name not in existing:
            connection.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")
    connection.commit()
    return connection


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
