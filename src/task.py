from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PortingTask:
    name: str
    description: str


__all__ = ["PortingTask"]
