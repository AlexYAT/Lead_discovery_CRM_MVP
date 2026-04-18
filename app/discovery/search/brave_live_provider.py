"""Brave Web Search API (live) — stdlib only, returns SearchHit list."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from app.discovery.search.models import SearchHit

_BRAVE_WEB_URL = "https://api.search.brave.com/res/v1/web/search"
_REQUEST_TIMEOUT_SEC = 12.0
_MAX_TEXT = 4000


class BraveLiveSearchProvider:
    """Live Brave web search; caller handles fallback on errors."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key.strip()

    def search(self, query: str, limit: int) -> list[SearchHit]:
        if not self._api_key:
            raise ValueError("missing brave api key")
        trimmed = (query or "").strip()
        q = trimmed or "(empty query)"
        n = max(1, min(int(limit), 20))
        params = urllib.parse.urlencode({"q": q, "count": str(n)})
        url = f"{_BRAVE_WEB_URL}?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self._api_key,
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT_SEC) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        results = data.get("web", {}).get("results")
        if not isinstance(results, list):
            return []
        hits: list[SearchHit] = []
        for item in results[:n]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            desc = str(item.get("description") or "").strip()
            link = str(item.get("url") or "").strip()
            body = f"{title}\n{desc}".strip() if desc else title
            if not body:
                body = link or "(no text)"
            if len(body) > _MAX_TEXT:
                body = body[: _MAX_TEXT - 3] + "..."
            if not link:
                link = "https://brave.com/search?q=" + urllib.parse.quote(q)
            hits.append(SearchHit(text=body, source_link=link))
        return hits
