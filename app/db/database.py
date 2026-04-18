import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, TypeVar

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "lead_discovery_crm_mvp.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
SQLITE_CONNECT_TIMEOUT_SEC = 10.0
SQLITE_BUSY_TIMEOUT_MS = 5000
WRITE_RETRY_MAX_ATTEMPTS = 3
WRITE_RETRY_BACKOFF_SEC = 0.05
T = TypeVar("T")


def _configure_connection(connection: sqlite3.Connection) -> None:
    # Required SQLite pragmas for single-user multi-instance runtime hardening.
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    connection.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS};")


def _is_transient_busy_error(error: sqlite3.OperationalError) -> bool:
    message = str(error).lower()
    return "database is locked" in message or "database table is locked" in message


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
    """Apply schema DDL. Safe on existing DBs: CREATE/INDEX use IF NOT EXISTS (see DOA-AUD-002)."""
    with get_connection() as connection:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema_sql)


def run_write_with_retry(operation: Callable[[], T]) -> T:
    attempt = 0
    while True:
        try:
            return operation()
        except sqlite3.OperationalError as error:
            attempt += 1
            if not _is_transient_busy_error(error):
                raise
            if attempt >= WRITE_RETRY_MAX_ATTEMPTS:
                raise
            time.sleep(WRITE_RETRY_BACKOFF_SEC * attempt)
