# Ticket classifier

Not a trained model. A Gemini/OpenAI wrapper with an allowlist.

The model returns JSON. `parse.py` rejects any category that is not in the list — the same pattern as GetPGN, where a model guess is checked against chess legality before it is accepted.

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

Concurrent classify calls share a thread lock and a file lock (`CLASSIFY_LOCK_PATH`). Empty input is rejected before the lock. If the lock wait exceeds `CLASSIFY_LOCK_TIMEOUT`, the HTTP API returns `429`.

```bash
uv run uvicorn ticket_classifier.http:app --host 127.0.0.1 --port 8003
```

Pipeline: empty input → reject · lock · prompt with allowed categories · LLM JSON · parse/allowlist · one retry · offline fallback.

Allowed: `order_issue` `return_request` `payment_issue` `account_issue` `product_information` `complaint` `other`
