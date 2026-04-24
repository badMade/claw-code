from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .models import PortingModule


@lru_cache(maxsize=None)
def load_porting_modules(snapshot_path: Path) -> tuple[PortingModule, ...]:
    raw_entries = json.loads(snapshot_path.read_text())
    return tuple(
        PortingModule(
            name=entry["name"],
            responsibility=entry["responsibility"],
            source_hint=entry["source_hint"],
            status="mirrored",
        )
        for entry in raw_entries
    )
