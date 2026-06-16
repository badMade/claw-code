import unittest
from unittest.mock import patch, MagicMock

from src.execution_registry import (
    MirroredCommand,
    MirroredTool,
    ExecutionRegistry,
    build_execution_registry,
)
from src.commands import PORTED_COMMANDS
from src.tools import PORTED_TOOLS


class TestExecutionRegistry(unittest.TestCase):
    def test_execution_registry_command_lookup(self):
        cmd1 = MirroredCommand("TestCmd", "hint1")
        cmd2 = MirroredCommand("duplicate", "hint2")
        cmd3 = MirroredCommand("DUPLICATE", "hint3")

        registry = ExecutionRegistry(commands=(cmd1, cmd2, cmd3), tools=())

        # Exact match
        self.assertEqual(registry.command("TestCmd"), cmd1)

        # Case insensitive match
        self.assertEqual(registry.command("testcmd"), cmd1)
        self.assertEqual(registry.command("TESTCMD"), cmd1)

        # Missing entry
        self.assertIsNone(registry.command("MissingCmd"))

        # First-match priority for duplicates
        self.assertEqual(registry.command("duplicate"), cmd2)
        self.assertEqual(registry.command("DuPlIcAtE"), cmd2)

    def test_execution_registry_tool_lookup(self):
        tool1 = MirroredTool("TestTool", "hint1")
        tool2 = MirroredTool("duplicate", "hint2")
        tool3 = MirroredTool("DUPLICATE", "hint3")

        registry = ExecutionRegistry(commands=(), tools=(tool1, tool2, tool3))

        # Exact match
        self.assertEqual(registry.tool("TestTool"), tool1)

        # Case insensitive match
        self.assertEqual(registry.tool("testtool"), tool1)
        self.assertEqual(registry.tool("TESTTOOL"), tool1)

        # Missing entry
        self.assertIsNone(registry.tool("MissingTool"))

        # First-match priority for duplicates
        self.assertEqual(registry.tool("duplicate"), tool2)
        self.assertEqual(registry.tool("DuPlIcAtE"), tool2)

    @patch("src.execution_registry.execute_command")
    def test_mirrored_command_execute(self, mock_execute_command):
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.message = "Command executed successfully"
        mock_execute_command.return_value = mock_result

        cmd = MirroredCommand("MyCmd", "hint")
        result = cmd.execute("my prompt")

        mock_execute_command.assert_called_once_with("MyCmd", "my prompt")
        self.assertEqual(result, "Command executed successfully")

    @patch("src.execution_registry.execute_tool")
    def test_mirrored_tool_execute(self, mock_execute_tool):
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.message = "Tool executed successfully"
        mock_execute_tool.return_value = mock_result

        tool = MirroredTool("MyTool", "hint")
        result = tool.execute("my payload")

        mock_execute_tool.assert_called_once_with("MyTool", "my payload")
        self.assertEqual(result, "Tool executed successfully")

    def test_build_execution_registry(self):
        # We use the real PORTED_COMMANDS and PORTED_TOOLS as per "prefer real imported modules"
        # and verify they are correctly transformed into Mirrored instances.
        registry = build_execution_registry()

        self.assertIsInstance(registry, ExecutionRegistry)
        self.assertEqual(len(registry.commands), len(PORTED_COMMANDS))
        self.assertEqual(len(registry.tools), len(PORTED_TOOLS))

        if PORTED_COMMANDS:
            first_cmd_module = PORTED_COMMANDS[0]
            first_cmd_mirrored = registry.commands[0]
            self.assertEqual(first_cmd_mirrored.name, first_cmd_module.name)
            self.assertEqual(
                first_cmd_mirrored.source_hint, first_cmd_module.source_hint
            )

        if PORTED_TOOLS:
            first_tool_module = PORTED_TOOLS[0]
            first_tool_mirrored = registry.tools[0]
            self.assertEqual(first_tool_mirrored.name, first_tool_module.name)
            self.assertEqual(
                first_tool_mirrored.source_hint, first_tool_module.source_hint
            )


if __name__ == "__main__":
    unittest.main()
