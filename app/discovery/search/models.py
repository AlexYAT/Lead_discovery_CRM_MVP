from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    """Raw search result for downstream discovery layers (no CRM fields)."""

    text: str
    source_link: str
