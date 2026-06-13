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

    # Performance optimization:
    # We use cached properties to build dictionary maps of commands and tools
    # for O(1) lookups. We iterate in reverse to preserve first-match
    # precedence if duplicate names exist in the tuples.
    @functools.cached_property
    def _command_map(self) -> dict[str, MirroredCommand]:
        return {command.name.lower(): command for command in reversed(self.commands)}

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
