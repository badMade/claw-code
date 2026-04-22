from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredSession:
    session_id: str
    messages: tuple[str, ...]
    input_tokens: int
    output_tokens: int


DEFAULT_SESSION_DIR = Path(".port_sessions")


def validate_session_id(session_id: str) -> None:
    if not session_id:
        raise ValueError("Invalid session ID: cannot be empty")
    if "/" in session_id or "\\" in session_id:
        raise ValueError(f"Invalid session ID: contains path separators ({session_id})")
    if session_id == "." or ".." in session_id:
        raise ValueError(
            f"Invalid session ID: contains directory traversal markers ({session_id})"
        )


def save_session(session: StoredSession, directory: Path | None = None) -> Path:
    validate_session_id(session.session_id)
    target_dir = directory or DEFAULT_SESSION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{session.session_id}.json"
    path.write_text(json.dumps(asdict(session), indent=2))
    return path


def load_session(session_id: str, directory: Path | None = None) -> StoredSession:
    validate_session_id(session_id)
    target_dir = directory or DEFAULT_SESSION_DIR
    data = json.loads((target_dir / f"{session_id}.json").read_text())
    return StoredSession(
        session_id=data["session_id"],
        messages=tuple(data["messages"]),
        input_tokens=data["input_tokens"],
        output_tokens=data["output_tokens"],
    )
