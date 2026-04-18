"""
CLI entrypoint for VK discovery pipeline (DOA-OP-007-A, IMP-030).

Usage:
    python -m app.discovery.run --query "..." --limit 10
"""

from __future__ import annotations

import argparse
import os

from app.discovery.classification import classify_candidates
from app.discovery.ingestion import ingest_candidates
from app.discovery.normalization import normalize_candidates
from app.discovery.search import search_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VK discovery pipeline (search → classify → normalize → ingest).")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--limit", type=int, default=10, help="Max raw hits (capped by search layer)")
    parser.add_argument("--source", type=str, default="vk", help="Logical source label (logged; pipeline uses VK-shaped mock URLs)")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Allow LLM classification if OPENAI_API_KEY is set; without this flag, stub mode is forced for the run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run through normalization only; do not ingest into Candidate Queue",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    saved_key = os.environ.get("OPENAI_API_KEY")
    try:
        if not args.llm:
            os.environ.pop("OPENAI_API_KEY", None)

        hits = search_candidates(args.query, args.limit)
        classified = classify_candidates(hits)
        normalized = normalize_candidates(classified)

        if args.dry_run:
            saved_ids: list[int] = []
        else:
            saved_ids = ingest_candidates(normalized)

        pain_count = sum(1 for _, c in classified if c.is_pain)

        print(f"source={args.source!r}")
        print(f"found(raw)={len(hits)}")
        print(f"passed_classification(pain)={pain_count}")
        print(f"normalized={len(normalized)}")
        if args.dry_run:
            print("saved=0 (dry-run)")
        else:
            print(f"saved={len(saved_ids)}")
    finally:
        if saved_key is not None:
            os.environ["OPENAI_API_KEY"] = saved_key
        else:
            os.environ.pop("OPENAI_API_KEY", None)


if __name__ == "__main__":
    main()
