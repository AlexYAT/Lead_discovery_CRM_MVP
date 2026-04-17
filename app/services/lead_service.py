from sqlite3 import Row
from typing import Any

from app.db.database import get_connection

LEAD_STATUSES = [
    "new",
    "reviewed",
    "contacted",
    "replied",
    "consultation_booked",
    "converted",
    "not_interested",
]

ALLOWED_STATUS_TRANSITIONS = {
    "new": {"reviewed", "not_interested"},
    "reviewed": {"contacted", "not_interested"},
    "contacted": {"replied", "not_interested"},
    "replied": {"consultation_booked", "not_interested"},
    "consultation_booked": {"converted", "not_interested"},
    "converted": set(),
    "not_interested": set(),
}


class InvalidStatusTransitionError(ValueError):
    pass


def _row_to_dict(row: Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def create_lead(
    platform: str,
    profile_name: str,
    profile_url: str,
    source_url: str,
    source_text: str,
    detected_theme: str,
    score: str,
    notes: str,
) -> int:
    parsed_score = float(score) if score else None
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO leads (
                platform,
                profile_name,
                profile_url,
                source_url,
                source_text,
                detected_theme,
                score,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)
            """,
            (
                platform.strip(),
                profile_name.strip(),
                profile_url.strip(),
                source_url.strip() or None,
                source_text.strip() or None,
                detected_theme.strip() or None,
                parsed_score,
                notes.strip() or None,
            ),
        )
        return int(cursor.lastrowid)


def list_leads() -> list[dict[str, Any]]:
    with get_connection() as connection:
        connection.row_factory = Row
        rows = connection.execute(
            """
            SELECT id, platform, profile_name, profile_url, status, notes, created_at
            FROM leads
            ORDER BY datetime(created_at) DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_lead(lead_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        connection.row_factory = Row
        row = connection.execute(
            """
            SELECT
                id,
                platform,
                profile_name,
                profile_url,
                source_url,
                source_text,
                detected_theme,
                score,
                status,
                notes,
                created_at
            FROM leads
            WHERE id = ?
            """,
            (lead_id,),
        ).fetchone()
    return _row_to_dict(row)


def get_allowed_next_statuses(current_status: str) -> list[str]:
    return sorted(ALLOWED_STATUS_TRANSITIONS.get(current_status, set()))


def update_lead_status(lead_id: int, new_status: str) -> None:
    if new_status not in LEAD_STATUSES:
        raise InvalidStatusTransitionError(f"Unknown status: {new_status}")

    lead = get_lead(lead_id)
    if lead is None:
        raise InvalidStatusTransitionError("Lead not found")

    current_status = str(lead["status"])
    if new_status == current_status:
        return

    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next:
        raise InvalidStatusTransitionError(
            f"Transition {current_status} -> {new_status} is not allowed"
        )

    with get_connection() as connection:
        connection.execute(
            "UPDATE leads SET status = ? WHERE id = ?",
            (new_status, lead_id),
        )


def update_lead_notes(lead_id: int, notes: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE leads SET notes = ? WHERE id = ?",
            (notes.strip() or None, lead_id),
        )
