from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).resolve().parent / "reference_data" / "modules_snapshot.json"

@lru_cache(maxsize=1)
def load_modules_snapshot() -> dict[str, list[dict[str, str]]]:
    """Load the combined modules snapshot file."""
    return json.loads(SNAPSHOT_PATH.read_text())
