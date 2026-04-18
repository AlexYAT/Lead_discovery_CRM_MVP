import csv
import io
from sqlite3 import Row
from typing import Any

from app.db.database import get_connection, run_write_with_retry

# Candidate queue lifecycle (DEC-004). FSM for leads is separate.
CANDIDATE_STATUSES_NEW = "new"


class CandidateImportError(ValueError):
    """Raised when CSV import fails validation (fail-fast)."""


def import_candidates_from_csv(csv_text: str) -> int:
    """
    Import UTF-8 CSV with header row.

    Required columns: platform, profile_name, profile_url.
    Optional column: notes.

    Skips fully empty data rows. Trims cell values. Creates only candidates with status ``new``;
    never creates leads.

    **Invalid rows:** fail-fast — raises ``CandidateImportError`` on the first data row that
    has any non-empty cell but fails required-field validation (see DOA-IMP-017).

    All valid rows are written in a **single** short transaction (one ``with connection:``).
    """
    text = (csv_text or "").strip()
    if not text:
        return 0

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return 0

    header = [h.strip() for h in header]
    required = ("platform", "profile_name", "profile_url")
    for name in required:
        if name not in header:
            raise CandidateImportError(f"Missing required column: {name}")

    idx = {name: header.index(name) for name in header}

    prepared: list[tuple[str, str, str, str | None]] = []
    for row_num, row in enumerate(reader, start=2):
        padded = list(row) + [""] * max(0, len(header) - len(row))
        cells = [padded[i].strip() if i < len(padded) else "" for i in range(len(header))]
        if not any(cells):
            continue
        platform = cells[idx["platform"]]
        profile_name = cells[idx["profile_name"]]
        profile_url = cells[idx["profile_url"]]
        notes_val: str | None = None
        if "notes" in idx:
            notes_raw = cells[idx["notes"]].strip()
            notes_val = notes_raw or None
        if not platform or not profile_name or not profile_url:
            raise CandidateImportError(
                f"Row {row_num}: missing required field (platform, profile_name, profile_url)"
            )
        prepared.append((platform, profile_name, profile_url, notes_val))

    if not prepared:
        return 0

    def _operation() -> int:
        with get_connection() as connection:
            with connection:
                for platform, profile_name, profile_url, notes in prepared:
                    connection.execute(
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
                        (platform, profile_name, profile_url, notes, CANDIDATE_STATUSES_NEW),
                    )
                return len(prepared)

    return run_write_with_retry(_operation)


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
