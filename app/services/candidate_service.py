from sqlite3 import Row
from typing import Any

from app.db.database import get_connection, run_write_with_retry

# Candidate queue lifecycle (DEC-004). FSM for leads is separate.
CANDIDATE_STATUSES_NEW = "new"


def _row_to_dict(row: Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def create_candidate(
    platform: str,
    profile_name: str,
    profile_url: str,
    notes: str = "",
) -> int:
    insert_values = (
        platform.strip(),
        profile_name.strip(),
        profile_url.strip(),
        notes.strip() or None,
    )

    def _operation() -> int:
        with get_connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO candidates (
                        platform,
                        profile_name,
                        profile_url,
                        notes,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (*insert_values, CANDIDATE_STATUSES_NEW),
                )
                return int(cursor.lastrowid)

    return run_write_with_retry(_operation)


def list_candidates(
    *,
    status_filter: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, platform, profile_name, profile_url, notes, status, lead_id,
               created_at, updated_at
        FROM candidates
        WHERE 1=1
    """
    params: list[Any] = []
    if status_filter is not None and status_filter.strip():
        query += " AND status = ?"
        params.append(status_filter.strip())
    query += " ORDER BY datetime(created_at) DESC, id DESC"
    if limit is not None and limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_candidate(candidate_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        connection.row_factory = Row
        row = connection.execute(
            """
            SELECT id, platform, profile_name, profile_url, notes, status, lead_id,
                   created_at, updated_at
            FROM candidates
            WHERE id = ?
            """,
            (candidate_id,),
        ).fetchone()
    return _row_to_dict(row)
