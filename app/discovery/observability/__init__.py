"""Discovery pipeline observability (DOA-IMP-037): in-memory, execution-scoped, optional."""

from app.discovery.observability.access import get_observability_stages_for_current_execution
from app.discovery.observability.collector import PipelineObservabilityCollector
from app.discovery.observability.context import (
    attach_pipeline_observability,
    current_pipeline_observability,
    detach_pipeline_observability,
)
from app.discovery.observability.hooks import (
    observe_after_classification,
    observe_after_normalization,
    observe_after_qualification,
    observe_after_search,
)

__all__ = [
    "PipelineObservabilityCollector",
    "attach_pipeline_observability",
    "current_pipeline_observability",
    "detach_pipeline_observability",
    "get_observability_stages_for_current_execution",
    "observe_after_classification",
    "observe_after_normalization",
    "observe_after_qualification",
    "observe_after_search",
]
