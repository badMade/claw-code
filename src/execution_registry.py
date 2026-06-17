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
    def _command_lookup(self) -> dict[str, MirroredCommand]:
        lookup = {}
        for command in self.commands:
            lookup.setdefault(command.name.lower(), command)
        return lookup

    def command(self, name: str) -> MirroredCommand | None:
        return self._command_lookup.get(name.lower())

    @functools.cached_property
    def _tool_lookup(self) -> dict[str, MirroredTool]:
        lookup = {}
        for tool in self.tools:
            lookup.setdefault(tool.name.lower(), tool)
        return lookup

    def tool(self, name: str) -> MirroredTool | None:
        return self._tool_lookup.get(name.lower())


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
