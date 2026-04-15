def is_valid_session_id(session_id: str) -> bool:
    if not session_id:
        return False
    # Check for path separators
    if "/" in session_id or "\\" in session_id:
        return False
    # Check for special segments
    if session_id in (".", ".."):
        return False
    # Check for components like "." or ".." if split by separator (but separators are already blocked)
    # Just to be safe against anything weird
    return True
