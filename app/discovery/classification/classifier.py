from __future__ import annotations

import json
import os
import re
from typing import Any

from app.discovery.classification.models import ClassificationResult
from app.discovery.classification.prompt import SYSTEM_PROMPT, build_user_message

_CONFIDENCE_IF_UNPARSEABLE = 0.0


def _clamp_confidence(value: Any) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, c))


def _parse_json_object(content: str) -> ClassificationResult:
    data = json.loads(content)
    is_pain = bool(data.get("is_pain", False))
    confidence = _clamp_confidence(data.get("confidence", 0.0))
    reason = str(data.get("reason", "")).strip() or "no reason provided"
    if len(reason) > 500:
        reason = reason[:497] + "..."
    # Conservative merge: low confidence treated as no pain
    if confidence < 0.35:
        is_pain = False
    return ClassificationResult(is_pain=is_pain, confidence=confidence, reason=reason)


def _classify_openai(text: str) -> ClassificationResult:
    try:
        from openai import OpenAI
    except ImportError as error:
        return ClassificationResult(
            is_pain=False,
            confidence=_CONFIDENCE_IF_UNPARSEABLE,
            reason=f"openai package not installed: {error}",
        )

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(text)},
        ],
    )
    raw = completion.choices[0].message.content or ""
    raw = raw.strip()
    try:
        return _parse_json_object(raw)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return ClassificationResult(
            is_pain=False,
            confidence=_CONFIDENCE_IF_UNPARSEABLE,
            reason="invalid or non-json model output; conservative default",
        )


_PAIN_HINTS = re.compile(
    r"(тревог|тревож|боюсь|страшн|не понимаю|непонятн|застря|пустот|тяжел|помощ|отношен|"
    r"повторя|энерг|выбираю|партн|одинаков|внутри|кризис|distress|anxious|"
    r"stuck|helpless|relationship|panic|empty|depress)",
    re.IGNORECASE,
)


def _classify_keyword_stub(text: str) -> ClassificationResult:
    """Deterministic offline stub when OPENAI_API_KEY is unset (MVP / dev)."""
    if _PAIN_HINTS.search(text):
        return ClassificationResult(
            is_pain=True,
            confidence=0.55,
            reason="keyword stub: possible emotional distress signal (no LLM)",
        )
    return ClassificationResult(
        is_pain=False,
        confidence=0.4,
        reason="keyword stub: no strong pain pattern (no LLM)",
    )


def classify_text(text: str, *, llm_enabled: bool = False) -> ClassificationResult:
    """
    Classify a single text for pain signal (binary + confidence + short reason).

    Does not generate user-facing prose beyond the structured fields returned.

    ``llm_enabled`` is the explicit execution switch (DEC-008); when False, stub path
    is always used regardless of ``OPENAI_API_KEY`` presence.
    """
    stripped = (text or "").strip()
    if not stripped:
        return ClassificationResult(
            is_pain=False,
            confidence=0.0,
            reason="empty text",
        )

    if llm_enabled and os.environ.get("OPENAI_API_KEY"):
        return _classify_openai(stripped)
    return _classify_keyword_stub(stripped)
