"""Read-only snapshot dicts for observability (bounded size, no business logic)."""

from __future__ import annotations

from typing import Any, Sequence

from app.discovery.classification.models import ClassificationResult
from app.discovery.normalization.models import NormalizedCandidate
from app.discovery.observability.collector import MAX_OBSERVABILITY_ITEMS
from app.discovery.search.models import SearchHit


def _trim(text: str, max_len: int) -> str:
    t = (text or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def snapshot_search_hits(hits: list[SearchHit]) -> dict[str, Any]:
    total = len(hits)
    cap = min(MAX_OBSERVABILITY_ITEMS, total)
    items = [
        {"text": _trim(h.text, 400), "source_link": h.source_link}
        for h in hits[:cap]
    ]
    return {"total": total, "truncated": total > MAX_OBSERVABILITY_ITEMS, "items": items}


def _snapshot_classification(cls: ClassificationResult) -> dict[str, Any]:
    return {
        "is_pain": cls.is_pain,
        "confidence": cls.confidence,
        "reason": _trim(cls.reason, 240),
    }


def snapshot_classified_rows(rows: Sequence[tuple[Any, ...]]) -> dict[str, Any]:
    total = len(rows)
    cap = min(MAX_OBSERVABILITY_ITEMS, total)
    items: list[dict[str, Any]] = []
    for row in rows[:cap]:
        if len(row) == 3:
            hit, cls, qmeta = row
            items.append(
                {
                    "hit": {"text": _trim(hit.text, 240), "source_link": hit.source_link},
                    "classification": _snapshot_classification(cls),
                    "qualification_meta": dict(qmeta),
                }
            )
        else:
            hit, cls = row
            items.append(
                {
                    "hit": {"text": _trim(hit.text, 240), "source_link": hit.source_link},
                    "classification": _snapshot_classification(cls),
                }
            )
    return {"total": total, "truncated": total > MAX_OBSERVABILITY_ITEMS, "items": items}


def snapshot_normalized_candidates(candidates: list[NormalizedCandidate]) -> dict[str, Any]:
    total = len(candidates)
    cap = min(MAX_OBSERVABILITY_ITEMS, total)
    items: list[dict[str, Any]] = []
    for c in candidates[:cap]:
        items.append(
            {
                "text": _trim(c.text, 400),
                "source_link": c.source_link,
                "source": c.source,
                "detected_theme": c.detected_theme,
                "score": c.score,
                "metadata": dict(c.metadata) if c.metadata else None,
            }
        )
    return {"total": total, "truncated": total > MAX_OBSERVABILITY_ITEMS, "items": items}
