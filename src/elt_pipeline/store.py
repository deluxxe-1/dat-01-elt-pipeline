"""Load step: SQLite-backed raw and marts tables with idempotent upserts."""

import sqlite3
from contextlib import closing

RAW_TABLE = "raw_orders"
MART_TABLE = "mart_customer_orders"

RAW_DDL = f"""
CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    amount      REAL    NOT NULL,
    status      TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);
"""

MART_DDL = f"""
CREATE TABLE IF NOT EXISTS {MART_TABLE} (
    customer_id     INTEGER PRIMARY KEY,
    order_count     INTEGER NOT NULL,
    total_amount    REAL    NOT NULL,
    last_created_at TEXT    NOT NULL
);
"""

_UPSERT_RAW_SQL = (
    f"INSERT INTO {RAW_TABLE} (id, customer_id, amount, status, created_at) "
    "VALUES (:id, :customer_id, :amount, :status, :created_at) "
    "ON CONFLICT(id) DO UPDATE SET "
    "customer_id = excluded.customer_id, "
    "amount = excluded.amount, "
    "status = excluded.status, "
    "created_at = excluded.created_at"
)


def connect(database_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_schema(database_path: str) -> None:
    """Create the raw and marts tables if they do not exist."""

    with closing(connect(database_path)) as connection:
        connection.executescript(RAW_DDL + MART_DDL)
        connection.commit()


def upsert_raw(database_path: str, orders: list[dict]) -> int:
    """Idempotently load raw records keyed by ``id``.

    Re-running with the same payload updates existing rows in place, so the
    row count stays stable across repeated runs.

    Returns:
        The number of rows affected by the statement.
    """

    if not orders:
        return 0
    with closing(connect(database_path)) as connection:
        cursor = connection.executemany(_UPSERT_RAW_SQL, orders)
        connection.commit()
        return cursor.rowcount


def read_raw(database_path: str) -> list[dict]:
    """Return every row from the raw table ordered by ``id``."""

    with closing(connect(database_path)) as connection:
        rows = connection.execute(
            f"SELECT id, customer_id, amount, status, created_at "
            f"FROM {RAW_TABLE} ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def write_marts(database_path: str, mart_rows: list[dict]) -> int:
    """Full-refresh the marts table (idempotent by construction)."""

    with closing(connect(database_path)) as connection:
        connection.execute(f"DELETE FROM {MART_TABLE}")
        connection.executemany(
            f"INSERT INTO {MART_TABLE} "
            "(customer_id, order_count, total_amount, last_created_at) "
            "VALUES (:customer_id, :order_count, :total_amount, :last_created_at)",
            mart_rows,
        )
        connection.commit()
    return len(mart_rows)


def read_marts(database_path: str) -> list[dict]:
    """Return every row from the marts table ordered by ``customer_id``."""

    with closing(connect(database_path)) as connection:
        rows = connection.execute(
            f"SELECT customer_id, order_count, total_amount, last_created_at "
            f"FROM {MART_TABLE} ORDER BY customer_id"
        ).fetchall()
    return [dict(row) for row in rows]


def count_rows(database_path: str, table: str) -> int:
    """Count rows in a known table (guards against SQL injection)."""

    if table not in (RAW_TABLE, MART_TABLE):
        raise ValueError(f"unknown table: {table}")
    with closing(connect(database_path)) as connection:
        (total,) = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(total)
