"""Read-only access to observability data for the active execution (e.g. future debug UI)."""

from __future__ import annotations

from typing import Any

from app.discovery.observability.context import current_pipeline_observability


def get_observability_stages_for_current_execution() -> list[dict[str, Any]] | None:
    """
    Return a shallow copy of captured stages while a collector is attached; otherwise None.

    Valid only for the duration of the pipeline run that attached observability.
    """
    collector = current_pipeline_observability()
    if collector is None:
        return None
    return collector.export_stages()
