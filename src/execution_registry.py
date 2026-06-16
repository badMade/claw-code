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

    @functools.cached_property
    def _commands_lookup(self) -> dict[str, MirroredCommand]:
        lookup: dict[str, MirroredCommand] = {}
        for command in self.commands:
            name_lower = command.name.lower()
            if name_lower not in lookup:
                lookup[name_lower] = command
        return lookup

    @functools.cached_property
    def _tools_lookup(self) -> dict[str, MirroredTool]:
        lookup: dict[str, MirroredTool] = {}
        for tool in self.tools:
            name_lower = tool.name.lower()
            if name_lower not in lookup:
                lookup[name_lower] = tool
        return lookup

    def command(self, name: str) -> MirroredCommand | None:
        return self._commands_lookup.get(name.lower())

    def tool(self, name: str) -> MirroredTool | None:
        return self._tools_lookup.get(name.lower())


def build_execution_registry() -> ExecutionRegistry:
    return ExecutionRegistry(
        commands=tuple(
            MirroredCommand(module.name, module.source_hint)
            for module in PORTED_COMMANDS
        ),
        tools=tuple(
            MirroredTool(module.name, module.source_hint) for module in PORTED_TOOLS
        ),
    )
