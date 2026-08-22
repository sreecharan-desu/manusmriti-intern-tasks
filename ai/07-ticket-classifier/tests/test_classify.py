from concurrent.futures import ThreadPoolExecutor

import pytest

from ticket_classifier.classify import classify
from ticket_classifier.parse import ParseError, parse_classification


@pytest.mark.parametrize(
    ("message", "category"),
    [
        ("My order was supposed to arrive yesterday but I still haven't received it.", "order_issue"),
        ("I don't like the product and would like to return it.", "return_request"),
        ("My credit card was charged twice for the same order.", "payment_issue"),
        ("I forgot my password and cannot login to my account.", "account_issue"),
        ("Can you tell me whether this laptop has 16GB RAM?", "product_information"),
        ("The product I received is completely damaged and unusable.", "complaint"),
        ("What time does your warehouse close on Sundays?", "other"),
    ],
)
def test_required_cases(message: str, category: str) -> None:
    result = classify(message)
    assert result["category"] == category
    assert 0 <= result["confidence"] <= 1


def test_empty_input() -> None:
    with pytest.raises(ValueError):
        classify("  ")


def test_rejects_illegal_category() -> None:
    with pytest.raises(ParseError):
        parse_classification('{"category": "refund_please", "confidence": 0.9}')


def test_parses_fenced_json() -> None:
    raw = '```json\n{"category": "other", "confidence": 0.4, "reason": "hours"}\n```'
    parsed = parse_classification(raw)
    assert parsed["category"] == "other"


def test_multiple_issues_still_one_category() -> None:
    result = classify("Order ORD99881 was damaged and I was also charged twice.")
    assert result["category"] in {"complaint", "payment_issue"}


def test_confidence_out_of_range() -> None:
    with pytest.raises(ParseError):
        parse_classification('{"category": "other", "confidence": 1.4}')


def test_blank_json_object_rejected() -> None:
    with pytest.raises(ParseError):
        parse_classification("{}")


def test_concurrent_classify_uses_lock() -> None:
    message = "What time does your warehouse close on Sundays?"
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(classify, [message] * 4))
    assert all(item["category"] == "other" for item in results)
