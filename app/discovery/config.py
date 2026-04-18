"""Discovery pipeline configuration (DOA-OP-008 / IMP-031; API keys IMP-032). Stdlib only."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _normalize_secret(value: str | None) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


@dataclass(frozen=True)
class DiscoveryConfig:
    llm_enabled: bool
    source: str
    default_limit: int
    openai_api_key: str | None
    brave_api_key: str | None
    qualification_enabled: bool
    qualification_min_confidence: float


def _parse_bool_env(value: str | None, default: bool) -> bool:
    if value is None or not str(value).strip():
        return default
    v = str(value).strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return default


def _parse_float_env(value: str | None, default: float) -> float:
    if value is None or not str(value).strip():
        return default
    try:
        return max(0.0, min(1.0, float(str(value).strip())))
    except ValueError:
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
        openai_api_key=_normalize_secret(os.getenv("OPENAI_API_KEY")),
        brave_api_key=_normalize_secret(os.getenv("BRAVE_API_KEY")),
        qualification_enabled=_parse_bool_env(os.getenv("DISCOVERY_QUALIFICATION_ENABLED"), False),
        qualification_min_confidence=_parse_float_env(
            os.getenv("DISCOVERY_QUALIFICATION_MIN_CONFIDENCE"),
            0.45,
        ),
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
        openai_api_key=base.openai_api_key,
        brave_api_key=base.brave_api_key,
        qualification_enabled=base.qualification_enabled,
        qualification_min_confidence=base.qualification_min_confidence,
    )
