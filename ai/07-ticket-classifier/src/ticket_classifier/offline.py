from ticket_classifier.categories import CATEGORIES


def classify_offline(message: str) -> dict:
    text = message.lower()
    rules = [
        ("order_issue", ("hasn't arrived", "hasnt arrived", "not arrived", "tracking", "late order", "supposed to arrive")),
        ("return_request", ("return", "send it back", "don't like", "dont like")),
        ("payment_issue", ("charged twice", "credit card", "payment", "refund")),
        ("account_issue", ("password", "cannot login", "can't login", "reset")),
        ("product_information", ("16gb", "ram", "specs", "does this", "tell me whether")),
        ("complaint", ("damaged", "unusable", "broken")),
    ]
    hits = [name for name, needles in rules if any(needle in text for needle in needles)]
    if len(hits) > 1:
        category = hits[0]
        reason = "multiple issues present; first matching category used"
        confidence = 0.62
    elif hits:
        category = hits[0]
        reason = "offline keyword match"
        confidence = 0.8
    else:
        category = "other"
        reason = "no keyword matched an allowed category"
        confidence = 0.7
    assert category in CATEGORIES
    return {"category": category, "confidence": confidence, "reason": reason, "mode": "offline"}
