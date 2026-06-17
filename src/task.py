from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortingTask:
    name: str
    description: str


__all__ = ["PortingTask"]
