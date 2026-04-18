import json
from typing import Any

from app.discovery.normalization.models import NormalizedCandidate
from app.services.candidate_service import create_candidate


def _format_discovery_notes(candidate: NormalizedCandidate) -> str:
    """Pack discovery-only fields into candidates.notes (no schema change)."""
    payload: dict[str, Any] = {
        "discovery": "vk",
        "text": candidate.text,
        "detected_theme": candidate.detected_theme,
        "score": candidate.score,
        "metadata": candidate.metadata,
    }
    return json.dumps(payload, ensure_ascii=False)


def ingest_candidates(candidates: list[NormalizedCandidate]) -> list[int]:
    """
    Insert normalized discovery rows into the existing Candidate Queue.

    Uses ``create_candidate`` baseline (no new table, no CRM changes).
    MVP: no deduplication — each row is inserted.
    """
    created: list[int] = []
    for row in candidates:
        platform = (row.source or "vk").strip() or "vk"
        profile_name = (row.author or "VK discovery").strip() or "VK discovery"
        profile_url = row.source_link.strip()
        if not profile_url:
            continue
        notes = _format_discovery_notes(row)
        created.append(
            create_candidate(
                platform=platform[:200],
                profile_name=profile_name[:200],
                profile_url=profile_url,
                notes=notes,
            )
        )
    return created
