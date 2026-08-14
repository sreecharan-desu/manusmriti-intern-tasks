from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("INVENTORY_DB_PATH", ROOT / "inventory.sqlite"))
