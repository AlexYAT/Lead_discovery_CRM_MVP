from sqlite3 import Row
from typing import Any

from app.db.database import get_connection, run_write_with_retry


def create_contact_attempt(
    lead_id: int,
    date: str,
    message_text: str,
    outcome: str,
    next_action: str,
) -> int:
    parsed_date = date.strip() or None
    def _operation() -> int:
        with get_connection() as connection:
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
                (
                    lead_id,
                    parsed_date,
                    message_text.strip() or None,
                    outcome.strip() or None,
                    next_action.strip() or None,
                ),
            )
            return int(cursor.lastrowid)

    return run_write_with_retry(_operation)


def list_contact_attempts_by_lead(lead_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(
            """
            SELECT id, lead_id, date, message_text, outcome, next_action
            FROM contact_attempts
            WHERE lead_id = ?
            ORDER BY datetime(date) DESC, id DESC
            """,
            (lead_id,),
        ).fetchall()
    return [dict(row) for row in rows]
