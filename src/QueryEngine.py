from __future__ import annotations

from .query_engine import QueryEnginePort


class QueryEngineRuntime(QueryEnginePort):
    pass


__all__ = ["QueryEnginePort", "QueryEngineRuntime"]
