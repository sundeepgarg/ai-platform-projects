import re

from app.models import GuardrailResult


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

BLOCKED_PHRASES = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass policy",
]


class GuardrailEngine:
    def evaluate(self, text: str) -> GuardrailResult:
        reasons: list[str] = []
        lowered = text.lower()

        if len(text) > 2000:
            reasons.append("Prompt exceeds allowed length.")

        for phrase in BLOCKED_PHRASES:
            if phrase in lowered:
                reasons.append(f"Blocked phrase detected: '{phrase}'.")

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                reasons.append("Potential secret detected in request.")

        if reasons:
            return GuardrailResult(status="blocked", reasons=reasons)

        return GuardrailResult(status="allowed", reasons=[])

