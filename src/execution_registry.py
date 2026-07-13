from __future__ import annotations

import functools
from dataclasses import dataclass

from .commands import PORTED_COMMANDS, execute_command
from .tools import PORTED_TOOLS, execute_tool


@dataclass(frozen=True)
class MirroredCommand:
    name: str
    source_hint: str

    def execute(self, prompt: str) -> str:
        return execute_command(self.name, prompt).message


@dataclass(frozen=True)
class MirroredTool:
    name: str
    source_hint: str

    def execute(self, payload: str) -> str:
        return execute_tool(self.name, payload).message


@dataclass(frozen=True)
class ExecutionRegistry:
    commands: tuple[MirroredCommand, ...]
    tools: tuple[MirroredTool, ...]

    # ⚡ Bolt Optimization: Cache the command dictionary map for O(1) lookups.
    # Why: Avoids O(N) linear list search for every command lookup. Iterating in reverse preserves first-match precedence.
    @functools.cached_property
    def _command_map(self) -> dict[str, MirroredCommand]:
        return {cmd.name.lower(): cmd for cmd in reversed(self.commands)}

    # ⚡ Bolt Optimization: Cache the tool dictionary map for O(1) lookups.
    # Why: Avoids O(N) linear list search for every tool lookup. Iterating in reverse preserves first-match precedence.
    @functools.cached_property
    def _tool_map(self) -> dict[str, MirroredTool]:
        return {tool.name.lower(): tool for tool in reversed(self.tools)}

    def command(self, name: str) -> MirroredCommand | None:
        return self._command_map.get(name.lower())

    def tool(self, name: str) -> MirroredTool | None:
        return self._tool_map.get(name.lower())

def build_execution_registry() -> ExecutionRegistry:
    return ExecutionRegistry(
        commands=tuple(MirroredCommand(module.name, module.source_hint) for module in PORTED_COMMANDS),
        tools=tuple(MirroredTool(module.name, module.source_hint) for module in PORTED_TOOLS),
    )
