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
    def _commands_dict(self) -> dict[str, MirroredCommand]:
        d: dict[str, MirroredCommand] = {}
        for command in self.commands:
            k = command.name.lower()
            if k not in d:
                d[k] = command
        return d

    @functools.cached_property
    def _tools_dict(self) -> dict[str, MirroredTool]:
        d: dict[str, MirroredTool] = {}
        for tool in self.tools:
            k = tool.name.lower()
            if k not in d:
                d[k] = tool
        return d

    def command(self, name: str) -> MirroredCommand | None:
        return self._commands_dict.get(name.lower())

    def tool(self, name: str) -> MirroredTool | None:
        return self._tools_dict.get(name.lower())


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
