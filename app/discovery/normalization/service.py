from app.discovery.classification.models import ClassificationResult
from app.discovery.normalization.models import NormalizedCandidate
from app.discovery.normalization.normalizer import normalize_hit
from app.discovery.search.models import SearchHit

_ClassifiedRow = tuple[SearchHit, ClassificationResult] | tuple[SearchHit, ClassificationResult, dict[str, str]]


def normalize_candidates(
    classified_hits: list[_ClassifiedRow],
    *,
    classification_mode: str | None = None,
) -> list[NormalizedCandidate]:
    """Normalize only pain-positive hits; order preserved."""
    out: list[NormalizedCandidate] = []
    for row in classified_hits:
        if len(row) == 3:
            hit, classification, qmeta = row
        else:
            hit, classification = row
            qmeta = {}
        if classification.is_pain:
            out.append(
                normalize_hit(
                    hit,
                    classification,
                    classification_mode=classification_mode,
                    qualification_meta=qmeta or None,
                )
            )
    return out
