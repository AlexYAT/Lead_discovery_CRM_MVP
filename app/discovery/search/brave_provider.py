"""Primary search provider entry — delegates to Search Adapter (live + fallback)."""

from __future__ import annotations

from app.discovery.search.adapter import discovery_search
from app.discovery.search.models import SearchHit


class BraveSearchProvider:
    """
    Discovery search provider: Brave live path when key present, else mock (DEC-011).

    Implements the ``SearchProvider`` protocol via ``search(query, limit)``.
    """

    def __init__(self, brave_api_key: str | None = None) -> None:
        self._brave_api_key = brave_api_key

    def search(self, query: str, limit: int) -> list[SearchHit]:
        return discovery_search(query, limit, brave_api_key=self._brave_api_key)
