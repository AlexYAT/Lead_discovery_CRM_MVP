"""Soft qualification after classification (DOA-DEC-012 / IMP-035)."""

from __future__ import annotations

from app.discovery.classification.models import ClassificationResult
from app.discovery.search.models import SearchHit


def qualify_candidates(
    rows: list[tuple[SearchHit, ClassificationResult]],
    *,
    enabled: bool,
    min_confidence: float,
) -> list[tuple[SearchHit, ClassificationResult, dict[str, str]]]:
    """
    Enrich classified rows with soft qualification metadata (no drops).

    When ``enabled`` is False, returns the same rows with empty metadata dicts
    (pass-through for downstream).
    """
    if not enabled:
        return [(hit, cls, {}) for hit, cls in rows]

    out: list[tuple[SearchHit, ClassificationResult, dict[str, str]]] = []
    floor = max(0.0, min(1.0, float(min_confidence)))
    for hit, cls in rows:
        if not cls.is_pain:
            tier = "none"
        elif cls.confidence >= floor:
            tier = "high"
        else:
            tier = "medium"
        meta = {
            "qualification_tier": tier,
            "qualification_min_confidence": f"{floor:.2f}",
            "qualification_layer": "v1",
        }
        out.append((hit, cls, meta))
    return out
