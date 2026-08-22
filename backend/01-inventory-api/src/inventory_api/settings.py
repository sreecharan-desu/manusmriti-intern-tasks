from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("INVENTORY_DB_PATH", ROOT / "inventory.sqlite"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "INVENTORY_CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
CORS_ORIGIN_REGEX = os.getenv("INVENTORY_CORS_ORIGIN_REGEX", r"https://([a-z0-9-]+\.)*vercel\.app")
