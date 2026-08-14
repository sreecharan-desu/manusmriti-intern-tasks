from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator

from inventory_api.settings import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    category TEXT NOT NULL
)
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(SCHEMA)
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


def row_to_product(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "product_name": row["product_name"],
        "sku": row["sku"],
        "price": row["price"],
        "stock_quantity": row["stock_quantity"],
        "category": row["category"],
    }
