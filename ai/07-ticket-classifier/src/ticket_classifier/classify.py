from __future__ import annotations

from ticket_classifier.llm import LlmError, complete
from ticket_classifier.lock import classify_lock, finish_flight, single_flight, wait_flight
from ticket_classifier.offline import classify_offline
from ticket_classifier.parse import ParseError, parse_classification
from ticket_classifier.prompts import build_prompt


def classify(message: str, *, allow_offline: bool = True) -> dict:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Text input cannot be empty.")

    flight, owner = single_flight(cleaned)
    if not owner:
        return wait_flight(flight)

    try:
        with classify_lock():
            result = _classify_locked(cleaned, allow_offline=allow_offline)
        finish_flight(cleaned, flight, result=result)
        return result
    except BaseException as exc:
        finish_flight(cleaned, flight, error=exc)
        raise


def _classify_locked(cleaned: str, *, allow_offline: bool) -> dict:
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
            return classify_offline(cleaned)
