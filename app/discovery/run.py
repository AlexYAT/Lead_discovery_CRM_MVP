"""
CLI entrypoint for VK discovery pipeline (DOA-OP-007-A, IMP-030; config IMP-031; env IMP-036).

Calls ``initialize_environment()`` before importing discovery config so ``.env`` is applied first.

Usage:
    python -m app.discovery.run --query "..." --limit 10
"""

from __future__ import annotations

import argparse
import sys
from contextvars import Token

from app.core.env_init import initialize_environment

initialize_environment()

from app.discovery.classification import classify_candidates
from app.discovery.config import load_config_from_env, merge_cli_overrides
from app.discovery.ingestion import ingest_candidates
from app.discovery.normalization import normalize_candidates
from app.discovery.observability import (
    PipelineObservabilityCollector,
    attach_pipeline_observability,
    detach_pipeline_observability,
    observe_after_classification,
    observe_after_normalization,
    observe_after_qualification,
    observe_after_search,
)
from app.discovery.observability.debug_cli import (
    parse_diff_stages_arg,
    read_debug_stages,
    render_diff_view_lines,
    render_stage_view_lines,
)
from app.discovery.qualification import qualify_candidates
from app.discovery.search import search_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VK discovery pipeline (search → classify → normalize → ingest).")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max raw hits (overrides DISCOVERY_DEFAULT_LIMIT / config default)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Execution-level source label (overrides DISCOVERY_SOURCE)",
    )
    parser.add_argument(
        "--llm",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override LLM: --llm / --no-llm; omit to use DISCOVERY_LLM_ENABLED",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run through normalization only; do not ingest into Candidate Queue",
    )
    parser.add_argument(
        "--discovery-observability",
        action="store_true",
        help="In-memory per-run stage snapshots for debug (no DB; see DOA-IMP-037)",
    )
    dbg = parser.add_mutually_exclusive_group()
    dbg.add_argument(
        "--discovery-debug-stage",
        choices=["search", "classification", "qualification", "normalization"],
        default=None,
        metavar="STAGE",
        help="Print one observability stage to stderr (requires --discovery-observability; DOA-IMP-038)",
    )
    dbg.add_argument(
        "--discovery-debug-diff",
        type=parse_diff_stages_arg,
        default=None,
        metavar="A,B",
        help="Diff two stages as identity sets (stderr; requires --discovery-observability)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (args.discovery_debug_stage is not None or args.discovery_debug_diff is not None) and (
        not args.discovery_observability
    ):
        print(
            "discovery_debug: error: --discovery-debug-stage / --discovery-debug-diff "
            "require --discovery-observability",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(2)
    base_cfg = load_config_from_env()
    cfg = merge_cli_overrides(
        base_cfg,
        llm=args.llm,
        source=args.source,
        limit=args.limit,
    )

    collector: PipelineObservabilityCollector | None = None
    obs_token: Token | None = None
    if args.discovery_observability:
        collector = PipelineObservabilityCollector()
        obs_token = attach_pipeline_observability(collector)

    try:
        bounded_limit = max(0, min(cfg.default_limit, 20))
        hits = search_candidates(args.query, bounded_limit, brave_api_key=cfg.brave_api_key)
        if collector is not None:
            observe_after_search(hits)
        classified = classify_candidates(
            hits,
            llm_enabled=cfg.llm_enabled,
            openai_api_key=cfg.openai_api_key,
        )
        if collector is not None:
            observe_after_classification(classified)
        classified = qualify_candidates(
            classified,
            enabled=cfg.qualification_enabled,
            min_confidence=cfg.qualification_min_confidence,
        )
        if collector is not None:
            observe_after_qualification(classified)
        cls_mode = "llm" if (cfg.llm_enabled and cfg.openai_api_key) else "stub"
        normalized = normalize_candidates(classified, classification_mode=cls_mode)
        if collector is not None:
            observe_after_normalization(normalized)

        if args.dry_run:
            saved_ids: list[int] = []
        else:
            saved_ids = ingest_candidates(normalized)

        pain_count = sum(1 for row in classified if row[1].is_pain)
    finally:
        if obs_token is not None:
            detach_pipeline_observability(obs_token)

    if collector is not None:
        print(
            f"discovery_observability: stages={len(collector.export_stages())}",
            file=sys.stderr,
            flush=True,
        )
        if args.discovery_debug_stage is not None:
            stages = read_debug_stages(collector)
            for line in render_stage_view_lines(stages, args.discovery_debug_stage):
                print(line, file=sys.stderr, flush=True)
        elif args.discovery_debug_diff is not None:
            a, b = args.discovery_debug_diff
            stages = read_debug_stages(collector)
            for line in render_diff_view_lines(stages, a, b):
                print(line, file=sys.stderr, flush=True)

    has_openai_key = bool(cfg.openai_api_key)
    has_brave_key = bool(cfg.brave_api_key)
    print(
        f"llm_enabled={cfg.llm_enabled} source={cfg.source!r} limit={cfg.default_limit} "
        f"has_openai_key={has_openai_key} has_brave_key={has_brave_key} "
        f"qualification_enabled={cfg.qualification_enabled}"
    )
    print(f"found(raw)={len(hits)}")
    print(f"passed_classification(pain)={pain_count}")
    print(f"normalized={len(normalized)}")
    if args.dry_run:
        print("saved=0 (dry-run)")
    else:
        print(f"saved={len(saved_ids)}")


if __name__ == "__main__":
    main()
