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


def _classify_openai(text: str, *, api_key: str) -> ClassificationResult:
    try:
        from openai import OpenAI
    except ImportError as error:
        return ClassificationResult(
            is_pain=False,
            confidence=_CONFIDENCE_IF_UNPARSEABLE,
            reason=f"openai package not installed: {error}",
        )

    try:
        client = OpenAI(api_key=api_key)
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
    except Exception:
        # Graceful fallback (DEC-009): auth/network/model errors → stub path
        return _classify_keyword_stub(text)


_PAIN_HINTS = re.compile(
    r"(тревог|тревож|боюсь|страшн|не понимаю|непонятн|застря|пустот|тяжел|помощ|отношен|"
    r"повторя|энерг|выбираю|партн|одинаков|внутри|кризис|distress|anxious|"
    r"stuck|helpless|relationship|panic|empty|depress)",
    re.IGNORECASE,
)


def _classify_keyword_stub(text: str) -> ClassificationResult:
    """Deterministic offline stub when LLM path is off or unavailable (MVP / dev)."""
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


def classify_text(
    text: str,
    *,
    llm_enabled: bool = False,
    openai_api_key: str | None = None,
) -> ClassificationResult:
    """
    Classify a single text for pain signal (binary + confidence + short reason).

    Does not generate user-facing prose beyond the structured fields returned.

    ``llm_enabled`` is the explicit execution switch (DEC-008); when False, stub path
    is always used. When True, LLM path is used only if ``openai_api_key`` is non-empty
    (passed explicitly from config; DEC-009 / IMP-032).
    """
    stripped = (text or "").strip()
    if not stripped:
        return ClassificationResult(
            is_pain=False,
            confidence=0.0,
            reason="empty text",
        )

    if llm_enabled and openai_api_key:
        return _classify_openai(stripped, api_key=openai_api_key)
    return _classify_keyword_stub(stripped)
