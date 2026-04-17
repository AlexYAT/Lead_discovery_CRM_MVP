from sqlite3 import Row
from typing import Any

from app.db.database import get_connection, run_write_with_retry

CONSULTATION_STATUSES = [
    "planned",
    "confirmed",
    "completed",
    "cancelled",
]


def create_consultation(
    lead_id: int,
    planned_at: str,
    status: str,
    result: str,
) -> int:
    normalized_status = status.strip() or "planned"
    if normalized_status not in CONSULTATION_STATUSES:
        normalized_status = "planned"

    normalized_planned_at = planned_at.strip() or "1970-01-01 00:00:00"
    stored_result = result.strip() or None
    insert_values = (
        lead_id,
        normalized_planned_at,
        normalized_status,
        stored_result,
    )

    def _operation() -> int:
        with get_connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO consultations (
                        lead_id,
                        planned_at,
                        status,
                        result
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    insert_values,
                )
                return int(cursor.lastrowid)

    return run_write_with_retry(_operation)


def list_consultations_by_lead(lead_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(
            """
            SELECT id, lead_id, planned_at, status, result
            FROM consultations
            WHERE lead_id = ?
            ORDER BY datetime(planned_at) DESC, id DESC
            """,
            (lead_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_consultation(consultation_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        connection.row_factory = Row
        row = connection.execute(
            """
            SELECT id, lead_id, planned_at, status, result
            FROM consultations
            WHERE id = ?
            """,
            (consultation_id,),
        ).fetchone()
    return dict(row) if row else None


def update_consultation_status_result(
    consultation_id: int,
    status: str,
    result: str,
) -> None:
    normalized_status = status.strip()
    if normalized_status not in CONSULTATION_STATUSES:
        raise ValueError(f"Unknown consultation status: {normalized_status}")

    stored_result = result.strip() or None
    update_values = (normalized_status, stored_result, consultation_id)

    def _operation() -> None:
        with get_connection() as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE consultations
                    SET status = ?, result = ?
                    WHERE id = ?
                    """,
                    update_values,
                )

    run_write_with_retry(_operation)
