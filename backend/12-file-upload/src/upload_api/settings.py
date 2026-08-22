from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("UPLOAD_DB_PATH", ROOT / "uploads.sqlite"))
STORAGE_DIR = Path(os.getenv("UPLOAD_STORAGE_DIR", ROOT / "storage"))
MAX_BYTES = 5 * 1024 * 1024
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "UPLOAD_CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
CORS_ORIGIN_REGEX = os.getenv("UPLOAD_CORS_ORIGIN_REGEX", r"https://([a-z0-9-]+\.)*vercel\.app")
