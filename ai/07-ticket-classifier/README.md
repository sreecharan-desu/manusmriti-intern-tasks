# Ticket classifier

Not a trained model. A Gemini/OpenAI wrapper with an allowlist.

The model returns JSON. `parse.py` rejects any category that is not in the list. Same idea as a chess app that asks a model for a move and then refuses illegal ones.

```bash
uv sync --dev
uv run pytest -q
uv run classify "My order hasn't arrived yet."
```

Optional `.env`:

```
GEMINI_API_KEY=
# or
OPENAI_API_KEY=
```

If no key is set, an offline keyword fallback still returns one of the seven categories so the CLI and tests run.

Pipeline: empty input → reject · prompt with allowed categories · LLM JSON · parse/allowlist · one retry · offline fallback.

Allowed: `order_issue` `return_request` `payment_issue` `account_issue` `product_information` `complaint` `other`
