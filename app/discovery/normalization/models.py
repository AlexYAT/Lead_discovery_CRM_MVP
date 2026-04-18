from dataclasses import dataclass


@dataclass
class NormalizedCandidate:
    """Unified discovery record for ingestion (not yet persisted)."""

    text: str
    source_link: str
    source: str
    author: str | None
    detected_theme: str | None
    score: float | None
    metadata: dict[str, str] | None

    def __post_init__(self) -> None:
        if self.metadata is not None:
            self.metadata = dict(self.metadata)
