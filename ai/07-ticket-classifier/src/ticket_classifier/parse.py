from __future__ import annotations

import json
import re

from ticket_classifier.categories import CATEGORIES


class ParseError(ValueError):
    pass


def parse_classification(raw: str) -> dict:
    payload = _extract_json(raw)
    category = str(payload.get("category", "")).strip().lower()
    if category not in CATEGORIES:
        raise ParseError(f"Illegal category: {category!r}")
    try:
        confidence = float(payload.get("confidence", 0))
    except (TypeError, ValueError) as exc:
        raise ParseError("confidence must be a number") from exc
    if not 0.0 <= confidence <= 1.0:
        raise ParseError("confidence must be between 0 and 1")
    reason = str(payload.get("reason", "")).strip()
    return {"category": category, "confidence": round(confidence, 3), "reason": reason}


def _extract_json(raw: str) -> dict:
    text = raw.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ParseError("Model did not return JSON")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ParseError("JSON was not an object")
    return parsed
