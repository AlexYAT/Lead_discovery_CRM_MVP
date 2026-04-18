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


def _add_column_if_missing(
    connection: sqlite3.Connection, table: str, column: str, column_def: str
) -> bool:
    """Idempotent migration helper for SQLite (IMP-021 CRM columns). Returns True if added."""
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    names = {str(row[1]) for row in rows}
    if column in names:
        return False
    connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")
    return True


def _ensure_imp021_crm_columns(connection: sqlite3.Connection) -> None:
    """Ensure CRM tables match IMP-021 (created_at on contact_attempts, consultations)."""
    # SQLite ADD COLUMN requires a constant default; backfill when we actually add the column.
    sentinel = "'1970-01-01T00:00:00'"
    added_attempts = _add_column_if_missing(
        connection,
        "contact_attempts",
        "created_at",
        f"TEXT NOT NULL DEFAULT {sentinel}",
    )
    if added_attempts:
        connection.execute(
            """
            UPDATE contact_attempts
            SET created_at = COALESCE(NULLIF(trim(date), ''), datetime('now'))
            WHERE created_at = '1970-01-01T00:00:00'
            """
        )

    added_consultations = _add_column_if_missing(
        connection,
        "consultations",
        "created_at",
        f"TEXT NOT NULL DEFAULT {sentinel}",
    )
    if added_consultations:
        connection.execute(
            """
            UPDATE consultations
            SET created_at = COALESCE(NULLIF(trim(planned_at), ''), datetime('now'))
            WHERE created_at = '1970-01-01T00:00:00'
            """
        )


def init_db() -> None:
    """Apply schema DDL. Safe on existing DBs: CREATE/INDEX use IF NOT EXISTS (see DOA-AUD-002)."""
    with get_connection() as connection:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
        _ensure_imp021_crm_columns(connection)


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
