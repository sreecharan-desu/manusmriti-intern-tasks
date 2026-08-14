from __future__ import annotations

from ticket_classifier.llm import LlmError, complete
from ticket_classifier.offline import classify_offline
from ticket_classifier.parse import ParseError, parse_classification
from ticket_classifier.prompts import build_prompt


def classify(message: str, *, allow_offline: bool = True) -> dict:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Text input cannot be empty.")

    prompt = build_prompt(cleaned)
    try:
        raw = complete(prompt)
        parsed = parse_classification(raw)
        parsed["mode"] = "llm"
        return parsed
    except (LlmError, ParseError):
        if not allow_offline:
            raise
        try:
            raw = complete(prompt + "\nReturn valid JSON only.")
            parsed = parse_classification(raw)
            parsed["mode"] = "llm_retry"
            return parsed
        except (LlmError, ParseError):
            result = classify_offline(cleaned)
            return result
