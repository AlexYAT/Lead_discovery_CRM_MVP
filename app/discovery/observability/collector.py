"""In-memory observability collector for one pipeline execution (DOA-IMP-037)."""

from __future__ import annotations

from typing import Any

MAX_OBSERVABILITY_ITEMS = 50


class PipelineObservabilityCollector:
    """Per-run collector; not a singleton — construct in orchestration (e.g. CLI)."""

    __slots__ = ("_stages",)

    def __init__(self) -> None:
        self._stages: list[dict[str, Any]] = []

    def add_stage(self, stage_name: str, data: Any) -> None:
        self._stages.append({"stage": stage_name, "data": data})

    def export_stages(self) -> list[dict[str, Any]]:
        return list(self._stages)
