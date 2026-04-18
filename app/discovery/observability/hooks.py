"""Non-invasive observability hooks — no-op when debug collector is not attached."""

from __future__ import annotations

from app.discovery.classification.models import ClassificationResult
from app.discovery.observability.context import current_pipeline_observability
from app.discovery.normalization.models import NormalizedCandidate
from app.discovery.observability import snapshots
from app.discovery.search.models import SearchHit

_ClassifiedRow = tuple[SearchHit, ClassificationResult] | tuple[SearchHit, ClassificationResult, dict[str, str]]


def _record(stage: str, data: object) -> None:
    collector = current_pipeline_observability()
    if collector is None:
        return
    collector.add_stage(stage, data)


def observe_after_search(hits: list[SearchHit]) -> None:
    _record("search", snapshots.snapshot_search_hits(hits))


def observe_after_classification(rows: list[tuple[SearchHit, ClassificationResult]]) -> None:
    _record("classification", snapshots.snapshot_classified_rows(rows))


def observe_after_qualification(rows: list[_ClassifiedRow]) -> None:
    _record("qualification", snapshots.snapshot_classified_rows(rows))


def observe_after_normalization(candidates: list[NormalizedCandidate]) -> None:
    _record("normalization", snapshots.snapshot_normalized_candidates(candidates))
