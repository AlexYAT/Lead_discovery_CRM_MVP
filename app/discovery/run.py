"""
CLI entrypoint for VK discovery pipeline (DOA-OP-007-A, IMP-030; config IMP-031).

Usage:
    python -m app.discovery.run --query "..." --limit 10
"""

from __future__ import annotations

import argparse

from app.discovery.classification import classify_candidates
from app.discovery.config import load_config_from_env, merge_cli_overrides
from app.discovery.ingestion import ingest_candidates
from app.discovery.normalization import normalize_candidates
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_cfg = load_config_from_env()
    cfg = merge_cli_overrides(
        base_cfg,
        llm=args.llm,
        source=args.source,
        limit=args.limit,
    )

    bounded_limit = max(0, min(cfg.default_limit, 20))
    hits = search_candidates(args.query, bounded_limit, brave_api_key=cfg.brave_api_key)
    classified = classify_candidates(
        hits,
        llm_enabled=cfg.llm_enabled,
        openai_api_key=cfg.openai_api_key,
    )
    classified = qualify_candidates(
        classified,
        enabled=cfg.qualification_enabled,
        min_confidence=cfg.qualification_min_confidence,
    )
    cls_mode = "llm" if (cfg.llm_enabled and cfg.openai_api_key) else "stub"
    normalized = normalize_candidates(classified, classification_mode=cls_mode)

    if args.dry_run:
        saved_ids: list[int] = []
    else:
        saved_ids = ingest_candidates(normalized)

    pain_count = sum(1 for row in classified if row[1].is_pain)

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
