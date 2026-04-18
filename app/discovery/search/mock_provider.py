"""Deterministic mock search hits (MVP / dev / fallback)."""

from __future__ import annotations

from app.discovery.search.models import SearchHit


class MockSearchProvider:
    """Synthetic recall when Brave key is absent or live path degrades."""

    def search(self, query: str, limit: int) -> list[SearchHit]:
        trimmed = (query or "").strip()
        q = trimmed or "(empty query)"
        n = max(0, min(limit, 20))
        hits: list[SearchHit] = []
        for index in range(n):
            hits.append(
                SearchHit(
                    text=f"[mock brave] {q} - synthetic discussion snippet #{index + 1}",
                    source_link=f"https://vk.com/wall-mock-{index + 1}?q={index}",
                )
            )
        return hits
