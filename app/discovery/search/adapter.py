"""
Search Adapter — single discovery recall entry (DOA-ARCH-010 / DEC-011).

Orchestration selects this path instead of calling a concrete provider directly.
"""

from __future__ import annotations

import json
import urllib.error

from app.discovery.search.brave_live_provider import BraveLiveSearchProvider
from app.discovery.search.mock_provider import MockSearchProvider
from app.discovery.search.models import SearchHit


def discovery_search(query: str, limit: int, *, brave_api_key: str | None) -> list[SearchHit]:
    """
    Live Brave when key present; mock when missing or on live failure (DEC-011).
    """
    key = (brave_api_key or "").strip()
    if not key:
        return MockSearchProvider().search(query, limit)
    try:
        return BraveLiveSearchProvider(api_key=key).search(query, limit)
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ):
        return MockSearchProvider().search(query, limit)
