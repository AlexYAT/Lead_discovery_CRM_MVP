from app.discovery.search.brave_provider import BraveSearchProvider
from app.discovery.search.models import SearchHit
from app.discovery.search.search_provider import SearchProvider

_DEFAULT_MAX = 20


def search_candidates(
    query: str,
    limit: int = 10,
    *,
    brave_api_key: str | None = None,
    provider: SearchProvider | None = None,
) -> list[SearchHit]:
    """
    Run recall search for a single query string.

    Does not classify, ingest, or touch CRM — raw hits only.

    ``brave_api_key`` selects live Brave path when set; otherwise mock (DEC-011 / adapter).
    """
    backend: SearchProvider = (
        provider if provider is not None else BraveSearchProvider(brave_api_key=brave_api_key)
    )
    bounded = max(0, min(int(limit), _DEFAULT_MAX))
    return backend.search(query, bounded)
