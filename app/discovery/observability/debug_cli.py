"""CLI debug view over observability snapshots (DOA-IMP-038); read-only, DEC-015 identity."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

from app.discovery.observability.access import get_observability_stages_for_current_execution
from app.discovery.observability.collector import PipelineObservabilityCollector

ALLOWED_STAGES = frozenset({"search", "classification", "qualification", "normalization"})


def parse_diff_stages_arg(value: str) -> tuple[str, str]:
    raw = (value or "").strip()
    if "," not in raw:
        raise argparse.ArgumentTypeError("Expected STAGE_A,STAGE_B (comma-separated).")
    a, b = [x.strip() for x in raw.split(",", 1)]
    if not a or not b:
        raise argparse.ArgumentTypeError("Both stage names are required.")
    if a not in ALLOWED_STAGES or b not in ALLOWED_STAGES:
        raise argparse.ArgumentTypeError(
            f"Unknown stage; allowed: {', '.join(sorted(ALLOWED_STAGES))}."
        )
    return a, b


def read_debug_stages(collector: PipelineObservabilityCollector) -> list[dict[str, Any]]:
    """
    Read-only snapshot of stages.

    Prefers ``get_observability_stages_for_current_execution()`` while the observability
    context is attached; after detach (typical CLI end), falls back to ``export_stages()``.
    """
    via_access = get_observability_stages_for_current_execution()
    if via_access is not None:
        return via_access
    return collector.export_stages()


def _extract_link_and_text(item: dict[str, Any], stage: str) -> tuple[str, str]:
    if stage == "search":
        link = str(item.get("source_link") or "").strip()
        text = str(item.get("text") or "")
        return link, text
    if stage in ("classification", "qualification"):
        hit = item.get("hit") or {}
        link = str(hit.get("source_link") or "").strip()
        text = str(hit.get("text") or "")
        return link, text
    if stage == "normalization":
        link = str(item.get("source_link") or "").strip()
        text = str(item.get("text") or "")
        return link, text
    return "", ""


def candidate_identity(item: dict[str, Any], *, stage: str) -> str:
    """DOA-DEC-015: primary ``source_link``, fallback stable hash of ``text``."""
    link, text = _extract_link_and_text(item, stage)
    if link:
        return f"link:{link}"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"text:{digest}"


def _stage_data(stages: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for row in stages:
        if row.get("stage") == name:
            data = row.get("data")
            if isinstance(data, dict):
                return data
            return None
    return None


def _items_list(data: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not data:
        return []
    items = data.get("items")
    if not isinstance(items, list):
        return []
    return [x for x in items if isinstance(x, dict)]


def render_stage_view_lines(stages: list[dict[str, Any]], stage_name: str) -> list[str]:
    if stage_name not in ALLOWED_STAGES:
        return [f"discovery_debug: error: unknown stage {stage_name!r}"]
    data = _stage_data(stages, stage_name)
    if data is None:
        return [f"discovery_debug: error: no data for stage {stage_name!r}"]
    total = data.get("total")
    truncated = data.get("truncated")
    lines = [
        f"discovery_debug: stage={stage_name}",
        f"discovery_debug: total={total!r} truncated={truncated!r}",
        "discovery_debug: ---",
    ]
    items = _items_list(data)
    if not items:
        lines.append("discovery_debug: (no items in snapshot)")
        return lines
    for i, item in enumerate(items, start=1):
        cid = candidate_identity(item, stage=stage_name)
        preview: dict[str, Any] = dict(item)
        if "hit" in preview:
            preview = {"hit": preview.get("hit"), "classification": preview.get("classification")}
        snippet = json.dumps(preview, ensure_ascii=False, default=str)[:500]
        lines.append(f"discovery_debug: [{i}] id={cid}")
        lines.append(f"discovery_debug:     {snippet}")
    return lines


def render_diff_view_lines(
    stages: list[dict[str, Any]],
    stage_a: str,
    stage_b: str,
    *,
    symmetric: bool = True,
) -> list[str]:
    if stage_a not in ALLOWED_STAGES or stage_b not in ALLOWED_STAGES:
        return ["discovery_debug: error: invalid stage name in diff"]
    da = _stage_data(stages, stage_a)
    db = _stage_data(stages, stage_b)
    if da is None:
        return [f"discovery_debug: error: no data for stage {stage_a!r}"]
    if db is None:
        return [f"discovery_debug: error: no data for stage {stage_b!r}"]
    items_a = _items_list(da)
    items_b = _items_list(db)
    ids_a = {candidate_identity(it, stage=stage_a): it for it in items_a}
    ids_b = {candidate_identity(it, stage=stage_b): it for it in items_b}
    only_a = [k for k in ids_a if k not in ids_b]
    lines = [
        f"discovery_debug: diff {stage_a} -> {stage_b}",
        f"discovery_debug: only_in_{stage_a}_not_in_{stage_b} count={len(only_a)} (primary: filtered out vs later stage)",
        "discovery_debug: ---",
    ]
    for k in only_a:
        lines.append(f"discovery_debug:   - id={k}")
    if symmetric:
        only_b = [k for k in ids_b if k not in ids_a]
        lines.append(
            f"discovery_debug: only_in_{stage_b}_not_in_{stage_a} count={len(only_b)} (symmetric)",
        )
        lines.append("discovery_debug: ---")
        for k in only_b:
            lines.append(f"discovery_debug:   + id={k}")
    return lines
