from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("AUTH_DB_PATH", ROOT / "auth.sqlite"))
JWT_SECRET = os.getenv("AUTH_JWT_SECRET", "dev-only-change-me")
JWT_ALG = "HS256"
TOKEN_HOURS = int(os.getenv("AUTH_TOKEN_HOURS", "12"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "AUTH_CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173,https://manusmriti-auth-ui.vercel.app",
    ).split(",")
    if origin.strip()
]
CORS_ORIGIN_REGEX = os.getenv("AUTH_CORS_ORIGIN_REGEX", r"https://([a-z0-9-]+\.)*vercel\.app")
