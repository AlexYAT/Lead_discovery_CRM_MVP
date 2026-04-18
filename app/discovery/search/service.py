from app.discovery.search.brave_provider import BraveSearchProvider
from app.discovery.search.models import SearchHit
from app.discovery.search.search_provider import SearchProvider

_DEFAULT_MAX = 20


def search_candidates(
    query: str,
    limit: int = 10,
    *,
    provider: SearchProvider | None = None,
) -> list[SearchHit]:
    """
    Run recall search for a single query string.

    Does not classify, ingest, or touch CRM — raw hits only.
    """
    backend: SearchProvider = provider if provider is not None else BraveSearchProvider()
    bounded = max(0, min(int(limit), _DEFAULT_MAX))
    return backend.search(query, bounded)
