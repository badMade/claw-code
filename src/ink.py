from __future__ import annotations

import re


def _get_visible_length(s: str) -> int:
    """Calculate the visible length of a string by removing ANSI escape sequences."""
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return len(ansi_escape.sub('', s))


def render_markdown_panel(text: str) -> str:
    lines = text.split('\n')
    max_len = max((_get_visible_length(line) for line in lines), default=0)
    border_len = max(40, max_len)
    border = '=' * border_len
    return f"{border}\n{text}\n{border}"
