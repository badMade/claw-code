from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath


@dataclass(frozen=True)
class StoredSession:
    session_id: str
    messages: tuple[str, ...]
    input_tokens: int
    output_tokens: int


DEFAULT_SESSION_DIR = Path('.port_sessions')


def validate_session_id(session_id: str) -> None:
    if not session_id:
        raise ValueError("Session ID cannot be empty")
    # Validate against both Unix and Windows path parsing so that malicious
    # identifiers are rejected regardless of the host platform.  This catches
    # path separators, traversal segments (`.`, `..`), root anchors, and
    # Windows drive prefixes such as `C:` or UNC paths.
    for path_cls in (PurePosixPath, PureWindowsPath):
        p = path_cls(session_id)
        if p.drive or p.root or len(p.parts) != 1 or p.parts[0] in (".", ".."):
            raise ValueError(
                f"Invalid session ID '{session_id}': must be a single normal filename component"
            )


def save_session(session: StoredSession, directory: Path | None = None) -> Path:
    validate_session_id(session.session_id)
    target_dir = directory or DEFAULT_SESSION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f'{session.session_id}.json'
    path.write_text(json.dumps(asdict(session), indent=2))
    return path


def load_session(session_id: str, directory: Path | None = None) -> StoredSession:
    validate_session_id(session_id)
    target_dir = directory or DEFAULT_SESSION_DIR
    data = json.loads((target_dir / f'{session_id}.json').read_text())
    return StoredSession(
        session_id=data['session_id'],
        messages=tuple(data['messages']),
        input_tokens=data['input_tokens'],
        output_tokens=data['output_tokens'],
    )
