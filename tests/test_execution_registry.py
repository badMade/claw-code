from __future__ import annotations

import unittest
from unittest import mock

from src.execution_registry import (
    MirroredCommand,
    MirroredTool,
    ExecutionRegistry,
    build_execution_registry,
)
from src.models import PortingModule

class TestExecutionRegistry(unittest.TestCase):
    @mock.patch("src.execution_registry.execute_command")
    def test_mirrored_command_execute(self, mock_execute_command: mock.MagicMock) -> None:
        mock_result = mock.MagicMock()
        mock_result.message = "command output"
        mock_execute_command.return_value = mock_result

        cmd = MirroredCommand(name="test_cmd", source_hint="test source")
        result = cmd.execute("my prompt")

        self.assertEqual(result, "command output")
        mock_execute_command.assert_called_once_with("test_cmd", "my prompt")

    @mock.patch("src.execution_registry.execute_tool")
    def test_mirrored_tool_execute(self, mock_execute_tool: mock.MagicMock) -> None:
        mock_result = mock.MagicMock()
        mock_result.message = "tool output"
        mock_execute_tool.return_value = mock_result

        tool = MirroredTool(name="test_tool", source_hint="test source")
        result = tool.execute("my payload")

        self.assertEqual(result, "tool output")
        mock_execute_tool.assert_called_once_with("test_tool", "my payload")

    def test_execution_registry_lookups(self) -> None:
        cmd1 = MirroredCommand("CmdOne", "hint1")
        cmd2 = MirroredCommand("cmdTWO", "hint2")
        tool1 = MirroredTool("ToolOne", "hint3")
        tool2 = MirroredTool("toolTWO", "hint4")

        registry = ExecutionRegistry(
            commands=(cmd1, cmd2),
            tools=(tool1, tool2),
        )

        self.assertEqual(registry.command("cmdone"), cmd1)
        self.assertEqual(registry.command("CMDTWO"), cmd2)
        self.assertIsNone(registry.command("nonexistent"))

        self.assertEqual(registry.tool("toolone"), tool1)
        self.assertEqual(registry.tool("TOOLTWO"), tool2)
        self.assertIsNone(registry.tool("nonexistent"))

    def test_build_execution_registry(self) -> None:
        mock_commands = (
            PortingModule(name="MockCmd", source_hint="mock cmd hint", responsibility="x", status="mirrored"),
        )
        mock_tools = (
            PortingModule(name="MockTool", source_hint="mock tool hint", responsibility="y", status="mirrored"),
        )

        with mock.patch("src.execution_registry.PORTED_COMMANDS", mock_commands):
            with mock.patch("src.execution_registry.PORTED_TOOLS", mock_tools):
                registry = build_execution_registry()

                self.assertEqual(len(registry.commands), 1)
                self.assertEqual(registry.commands[0].name, "MockCmd")
                self.assertEqual(registry.commands[0].source_hint, "mock cmd hint")

                self.assertEqual(len(registry.tools), 1)
                self.assertEqual(registry.tools[0].name, "MockTool")
                self.assertEqual(registry.tools[0].source_hint, "mock tool hint")

if __name__ == '__main__':
    unittest.main()
