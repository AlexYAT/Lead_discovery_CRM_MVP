"""Discovery pipeline configuration (DOA-OP-008 / IMP-031). Stdlib only."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveryConfig:
    llm_enabled: bool
    source: str
    default_limit: int


def _parse_bool_env(value: str | None, default: bool) -> bool:
    if value is None or not str(value).strip():
        return default
    v = str(value).strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return default


def _parse_int_env(value: str | None, default: int) -> int:
    if value is None or not str(value).strip():
        return default
    try:
        parsed = int(str(value).strip(), 10)
    except ValueError:
        return default
    return max(1, parsed)


def load_config_from_env() -> DiscoveryConfig:
    """Load baseline discovery config from environment (DISCOVERY_*)."""
    raw_source = os.getenv("DISCOVERY_SOURCE")
    source = (raw_source or "vk").strip() or "vk"
    return DiscoveryConfig(
        llm_enabled=_parse_bool_env(os.getenv("DISCOVERY_LLM_ENABLED"), False),
        source=source,
        default_limit=_parse_int_env(os.getenv("DISCOVERY_DEFAULT_LIMIT"), 10),
    )


def merge_cli_overrides(
    base: DiscoveryConfig,
    *,
    llm: bool | None,
    source: str | None,
    limit: int | None,
) -> DiscoveryConfig:
    """CLI wins over env-loaded base (DEC-008 precedence)."""
    next_llm = base.llm_enabled if llm is None else llm
    if source is None:
        next_source = base.source
    else:
        next_source = source.strip() or "vk"
    next_limit = base.default_limit if limit is None else max(1, int(limit))
    return DiscoveryConfig(
        llm_enabled=next_llm,
        source=next_source,
        default_limit=next_limit,
    )
