import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "lead_discovery_crm_mvp.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
SQLITE_CONNECT_TIMEOUT_SEC = 10.0


def _configure_connection(connection: sqlite3.Connection) -> None:
    # Required SQLite pragmas for single-user multi-instance runtime hardening.
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=SQLITE_CONNECT_TIMEOUT_SEC)
    _configure_connection(connection)

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        schema_exists = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'leads'
            LIMIT 1
            """
        ).fetchone()

        if schema_exists:
            return

        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
