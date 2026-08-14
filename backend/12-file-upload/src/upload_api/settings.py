from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("UPLOAD_DB_PATH", ROOT / "uploads.sqlite"))
STORAGE_DIR = Path(os.getenv("UPLOAD_STORAGE_DIR", ROOT / "storage"))
MAX_BYTES = 5 * 1024 * 1024
