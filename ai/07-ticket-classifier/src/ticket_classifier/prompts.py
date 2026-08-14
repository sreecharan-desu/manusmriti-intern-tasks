from ticket_classifier.categories import CATEGORIES, CATEGORY_HINTS


def build_prompt(message: str) -> str:
    lines = [
        "Classify the customer message into exactly one category.",
        "Return JSON only: {\"category\": \"<one of the allowed values>\", \"confidence\": 0.0, \"reason\": \"short\"}",
        "Do not invent categories. If unsure, use other.",
        "",
        "Allowed categories:",
    ]
    for name in CATEGORIES:
        lines.append(f"- {name}: {CATEGORY_HINTS[name]}")
    lines.extend(
        [
            "",
            "Examples:",
            "Input: My order hasn't arrived yet.",
            'Output: {"category": "order_issue", "confidence": 0.95, "reason": "late delivery"}',
            "Input: I want to return the shoes I purchased.",
            'Output: {"category": "return_request", "confidence": 0.93, "reason": "customer wants a return"}',
            "",
            f"Customer message: {message}",
        ]
    )
    return "\n".join(lines)
