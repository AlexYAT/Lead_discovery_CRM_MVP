"""Execution-scoped observability via contextvars (no process-wide collector singleton)."""

from __future__ import annotations

from contextvars import ContextVar, Token

from app.discovery.observability.collector import PipelineObservabilityCollector

_pipeline_observability: ContextVar[PipelineObservabilityCollector | None] = ContextVar(
    "discovery_pipeline_observability_collector",
    default=None,
)


def attach_pipeline_observability(collector: PipelineObservabilityCollector) -> Token:
    """Bind collector for the current execution context; returns reset token."""
    return _pipeline_observability.set(collector)


def detach_pipeline_observability(token: Token) -> None:
    _pipeline_observability.reset(token)


def current_pipeline_observability() -> PipelineObservabilityCollector | None:
    return _pipeline_observability.get()
