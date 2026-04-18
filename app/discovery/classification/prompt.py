"""LLM prompts: binary pain classification, JSON-only response, no free-form generation."""

SYSTEM_PROMPT = """You are a strict classifier. Your only job is to read a short user-generated text (e.g. from a social post or comment) and decide if it clearly expresses a personal emotional pain signal or distress (not generic news, ads, or jokes).

Rules:
- Output a SINGLE JSON object with keys exactly: "is_pain" (boolean), "confidence" (number 0-1), "reason" (short string, max ~200 chars, English).
- If uncertain or borderline, set is_pain to false and confidence low.
- Do not generate stories, advice, or any text outside that JSON object.
- Do not include markdown fences or commentary."""

USER_TEMPLATE = """Classify the following text.

Text:
---
{text}
---

Respond with JSON only. Schema:
{{"is_pain": <bool>, "confidence": <float 0-1>, "reason": "<short string>"}}"""


def build_user_message(text: str) -> str:
    return USER_TEMPLATE.format(text=text.strip())
