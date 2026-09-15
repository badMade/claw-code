from __future__ import annotations

import re

def _visual_length(text: str) -> int:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return len(ansi_escape.sub('', text))

def render_markdown_panel(text: str) -> str:
    lines = text.splitlines()
    max_len = max((_visual_length(line) for line in lines), default=0)
    width = max(40, max_len)
    border = '=' * width
    return f"{border}\n{text}\n{border}"
