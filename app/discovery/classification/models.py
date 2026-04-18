from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    """Pain-signal classification for one text snippet (no CRM fields)."""

    is_pain: bool
    confidence: float
    reason: str
