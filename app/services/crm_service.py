from sqlite3 import Row
from typing import Any

from app.db.database import get_connection, run_write_with_retry
from app.services.consultation_service import CONSULTATION_STATUSES


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def create_contact_attempt(
    lead_id: int,
    date: str,
    message_text: str | None,
    outcome: str | None,
    next_action: str | None,
) -> int:
    parsed_date = date.strip() or None
    insert_values = (
        lead_id,
        parsed_date,
        _strip_optional(message_text),
        _strip_optional(outcome),
        _strip_optional(next_action),
    )

    def _operation() -> int:
        with get_connection() as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO contact_attempts (
                        lead_id,
                        date,
                        message_text,
                        outcome,
                        next_action
                    )
                    VALUES (?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?, ?)
                    """,
                    insert_values,
                )
                return int(cursor.lastrowid)

    return run_write_with_retry(_operation)


def list_contact_attempts(lead_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(
            """
            SELECT id, lead_id, date, message_text, outcome, next_action, created_at
            FROM contact_attempts
            WHERE lead_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            """,
            (lead_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_consultation(
    lead_id: int,
    planned_at: str,
    status: str,
    result: str | None,
) -> int:
    normalized_status = status.strip() or "planned"
    if normalized_status not in CONSULTATION_STATUSES:
        normalized_status = "planned"

    normalized_planned_at = planned_at.strip() or "1970-01-01 00:00:00"
    stored_result = _strip_optional(result)

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


def list_consultations(lead_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(
            """
            SELECT id, lead_id, planned_at, status, result, created_at
            FROM consultations
            WHERE lead_id = ?
            ORDER BY datetime(created_at) DESC, id DESC
            """,
            (lead_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def update_consultation_status(
    consultation_id: int,
    status: str,
    result: str | None,
) -> None:
    normalized_status = status.strip()
    if normalized_status not in CONSULTATION_STATUSES:
        raise ValueError(f"Unknown consultation status: {normalized_status}")

    stored_result = _strip_optional(result)
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
