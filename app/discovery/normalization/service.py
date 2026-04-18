from app.discovery.classification.models import ClassificationResult
from app.discovery.normalization.models import NormalizedCandidate
from app.discovery.normalization.normalizer import normalize_hit
from app.discovery.search.models import SearchHit


def normalize_candidates(
    classified_hits: list[tuple[SearchHit, ClassificationResult]],
    *,
    classification_mode: str | None = None,
) -> list[NormalizedCandidate]:
    """Normalize only pain-positive hits; order preserved."""
    out: list[NormalizedCandidate] = []
    for hit, classification in classified_hits:
        if classification.is_pain:
            out.append(
                normalize_hit(hit, classification, classification_mode=classification_mode)
            )
    return out
