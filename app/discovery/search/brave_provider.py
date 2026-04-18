from app.discovery.search.models import SearchHit


class BraveSearchProvider:
    """
    Primary search provider (Brave Search).

    MVP: returns deterministic mock hits so the pipeline runs without API keys.
    Replace ``search`` body with HTTP calls to Brave when credentials are available.
    """

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
