from app.discovery.classification.classifier import classify_text
from app.discovery.classification.models import ClassificationResult
from app.discovery.search.models import SearchHit


def classify_candidates(
    candidates: list[SearchHit],
    *,
    llm_enabled: bool = False,
    openai_api_key: str | None = None,
) -> list[tuple[SearchHit, ClassificationResult]]:
    """Run classification on each raw hit; CRM-independent."""
    return [
        (
            hit,
            classify_text(hit.text, llm_enabled=llm_enabled, openai_api_key=openai_api_key),
        )
        for hit in candidates
    ]
