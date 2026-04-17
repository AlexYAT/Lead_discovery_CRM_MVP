from app.db.database import get_connection
from app.services.lead_service import LEAD_STATUSES


def get_lead_dashboard_metrics() -> dict[str, object]:
    with get_connection() as connection:
        total_leads = int(connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0])
        rows = connection.execute(
            """
            SELECT status, COUNT(*) AS cnt
            FROM leads
            GROUP BY status
            """
        ).fetchall()

    counts_map = {str(status): int(count) for status, count in rows}
    status_counts = [
        {"status": status_name, "count": counts_map.get(status_name, 0)}
        for status_name in LEAD_STATUSES
    ]

    return {
        "total_leads": total_leads,
        "status_counts": status_counts,
    }
