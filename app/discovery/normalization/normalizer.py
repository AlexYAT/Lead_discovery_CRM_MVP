from app.discovery.classification.models import ClassificationResult
from app.discovery.normalization.models import NormalizedCandidate
from app.discovery.search.models import SearchHit


def _detected_theme(reason: str) -> str | None:
    """Lightweight theme hint from classifier reason (MVP heuristic)."""
    r = (reason or "").lower()
    if any(k in r for k in ("relationship", "отношен", "партн")):
        return "relationships"
    if any(k in r for k in ("anxious", "anxiety", "тревог", "panic")):
        return "anxiety"
    if any(k in r for k in ("distress", "emotional", "эмоцион", "distress")):
        return "emotional_distress"
    if "stub" in r or "keyword" in r:
        return "unspecified_pain_stub"
    if r.strip():
        return "general_distress"
    return None


def normalize_hit(
    hit: SearchHit,
    classification: ClassificationResult,
    *,
    classification_mode: str | None = None,
    qualification_meta: dict[str, str] | None = None,
) -> NormalizedCandidate:
    """
    Map search hit + classification into a normalized discovery record.

    Caller is responsible for filtering to pain-positive rows when needed.
    """
    mode_label = classification_mode if classification_mode is not None else "stub"
    meta: dict[str, str] = {
        "classifier_reason": (classification.reason or "")[:500],
        "classification_mode": mode_label,
    }
    if qualification_meta:
        for key, val in qualification_meta.items():
            meta[str(key)[:80]] = str(val)[:200]
    theme = _detected_theme(classification.reason) if classification.is_pain else None
    score = float(classification.confidence) if classification.is_pain else None

    return NormalizedCandidate(
        text=hit.text,
        source_link=hit.source_link,
        source="vk",
        author=None,
        detected_theme=theme,
        score=score,
        metadata=meta,
    )
