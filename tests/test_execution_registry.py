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
    @mock.patch(
        "src.execution_registry.PORTED_COMMANDS",
        (
            PortingModule(
                name="cmd1",
                responsibility="Resp 1",
                source_hint="Hint 1",
                status="planned",
            ),
            PortingModule(
                name="cmd2",
                responsibility="Resp 2",
                source_hint="Hint 2",
                status="done",
            ),
        ),
    )
    @mock.patch(
        "src.execution_registry.PORTED_TOOLS",
        (
            PortingModule(
                name="tool1",
                responsibility="Resp 1",
                source_hint="Hint 1",
                status="planned",
            ),
        ),
    )
    def test_build_execution_registry(self):
        registry = build_execution_registry()

        self.assertEqual(len(registry.commands), 2)
        self.assertEqual(registry.commands[0].name, "cmd1")
        self.assertEqual(registry.commands[0].source_hint, "Hint 1")

        self.assertEqual(len(registry.tools), 1)
        self.assertEqual(registry.tools[0].name, "tool1")
        self.assertEqual(registry.tools[0].source_hint, "Hint 1")

    def test_registry_lookups(self):
        cmd1 = MirroredCommand("Cmd1", "hint1")
        cmd2 = MirroredCommand("Cmd2", "hint2")
        tool1 = MirroredTool("Tool1", "thint1")

        registry = ExecutionRegistry(commands=(cmd1, cmd2), tools=(tool1,))

        # Test command lookup (case insensitive)
        self.assertEqual(registry.command("cmd1"), cmd1)
        self.assertEqual(registry.command("CMD2"), cmd2)
        self.assertIsNone(registry.command("cmd3"))

        # Test tool lookup (case insensitive)
        self.assertEqual(registry.tool("tool1"), tool1)
        self.assertEqual(registry.tool("TOOL1"), tool1)
        self.assertIsNone(registry.tool("tool2"))

    @mock.patch("src.execution_registry.execute_command")
    def test_mirrored_command_execute(self, mock_execute_command: mock.MagicMock):
        # mock execute_command to return an object with a message property
        mock_result = mock.MagicMock()
        mock_result.message = "command executed"
        mock_execute_command.return_value = mock_result

        cmd = MirroredCommand("mycmd", "myhint")
        result = cmd.execute("my prompt")

        mock_execute_command.assert_called_once_with("mycmd", "my prompt")
        self.assertEqual(result, "command executed")

    @mock.patch("src.execution_registry.execute_tool")
    def test_mirrored_tool_execute(self, mock_execute_tool: mock.MagicMock):
        mock_result = mock.MagicMock()
        mock_result.message = "tool executed"
        mock_execute_tool.return_value = mock_result

        tool = MirroredTool("mytool", "myhint")
        result = tool.execute("my payload")

        mock_execute_tool.assert_called_once_with("mytool", "my payload")
        self.assertEqual(result, "tool executed")


if __name__ == "__main__":
    unittest.main()
