from typing import Protocol

from app.discovery.search.models import SearchHit


class SearchProvider(Protocol):
    """Pluggable search backend (Brave, fallback, mocks)."""

    def search(self, query: str, limit: int) -> list[SearchHit]:
        """Return up to ``limit`` hits for ``query``."""
