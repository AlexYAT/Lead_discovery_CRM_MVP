"""Environment initialization: load `.env` into process env before Config Layer (DOA-IMP-036). Stdlib only."""

from __future__ import annotations

import os
from pathlib import Path

_initialized: bool = False


def _project_root() -> Path:
    # app/core/env_init.py -> parents[2] == repository root
    return Path(__file__).resolve().parents[2]


def _parse_dotenv_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.lower().startswith("export "):
        stripped = stripped[7:].lstrip()
    if "=" not in stripped:
        return None
    key, _, value_part = stripped.partition("=")
    key = key.strip()
    if not key or not all(c.isalnum() or c == "_" for c in key):
        return None
    value = value_part.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return key, value


def _load_dotenv_file(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8-sig")
    for raw_line in text.splitlines():
        parsed = _parse_dotenv_line(raw_line)
        if parsed is None:
            continue
        key, value = parsed
        if key not in os.environ:
            os.environ[key] = value


def initialize_environment() -> None:
    """
    Load `.env` from the repository root if present; idempotent.

    Override policy (DOA-DEC-013): existing process environment wins; `.env` only fills missing keys.
    """
    global _initialized
    if _initialized:
        return
    _initialized = True
    env_path = _project_root() / ".env"
    _load_dotenv_file(env_path)
