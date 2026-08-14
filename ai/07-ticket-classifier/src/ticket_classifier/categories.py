CATEGORIES = (
    "order_issue",
    "return_request",
    "payment_issue",
    "account_issue",
    "product_information",
    "complaint",
    "other",
)

CATEGORY_HINTS = {
    "order_issue": "delivery, shipping, hasn't arrived, tracking, late order",
    "return_request": "return, send it back, don't like the product",
    "payment_issue": "charged twice, refund, credit card, payment failed",
    "account_issue": "password, login, account locked, reset",
    "product_information": "specs, RAM, does this have, product details",
    "complaint": "damaged, unusable, terrible quality, broken on arrival",
    "other": "anything that does not fit the categories above",
}
