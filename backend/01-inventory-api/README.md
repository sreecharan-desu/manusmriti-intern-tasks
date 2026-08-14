# Inventory API

FastAPI + SQLite inventory service. Unique SKUs, non-negative price/stock, paginated list.

```bash
uv sync --dev
uv run pytest -q
uv run inventory-api
```

Open [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/health` | SQLite ping |
| `GET` | `/products?page=1&page_size=10` | paginated |
| `GET` | `/products/{id}` | `404` if missing |
| `POST` | `/products` | `201`; duplicate SKU → `409` |
| `PUT` | `/products/{id}` | full replace |
| `DELETE` | `/products/{id}` | `204` |

SKU values are trimmed and uppercased before insert. Database path: `INVENTORY_DB_PATH` (defaults to `inventory.sqlite`).
