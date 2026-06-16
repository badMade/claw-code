from __future__ import annotations

import unittest
from src.execution_registry import (
    build_execution_registry,
    ExecutionRegistry,
    MirroredCommand,
    MirroredTool,
)
from src.commands import PORTED_COMMANDS
from src.tools import PORTED_TOOLS


class TestExecutionRegistry(unittest.TestCase):
    def test_build_execution_registry(self) -> None:
        registry = build_execution_registry()

        self.assertIsInstance(registry, ExecutionRegistry)

        # Verify commands are mirrored correctly
        self.assertEqual(len(registry.commands), len(PORTED_COMMANDS))
        for reg_cmd, src_cmd in zip(registry.commands, PORTED_COMMANDS):
            self.assertIsInstance(reg_cmd, MirroredCommand)
            self.assertEqual(reg_cmd.name, src_cmd.name)
            self.assertEqual(reg_cmd.source_hint, src_cmd.source_hint)

        # Verify tools are mirrored correctly
        self.assertEqual(len(registry.tools), len(PORTED_TOOLS))
        for reg_tool, src_tool in zip(registry.tools, PORTED_TOOLS):
            self.assertIsInstance(reg_tool, MirroredTool)
            self.assertEqual(reg_tool.name, src_tool.name)
            self.assertEqual(reg_tool.source_hint, src_tool.source_hint)

    def test_execution_registry_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No ported commands available to test.")

        registry = build_execution_registry()
        first_command = PORTED_COMMANDS[0]

        # Test exact match
        found = registry.command(first_command.name)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, first_command.name)

        # Test case-insensitive match
        found_lower = registry.command(first_command.name.lower())
        self.assertIsNotNone(found_lower)
        assert found_lower is not None
        self.assertEqual(found_lower.name, first_command.name)

        found_upper = registry.command(first_command.name.upper())
        self.assertIsNotNone(found_upper)
        assert found_upper is not None
        self.assertEqual(found_upper.name, first_command.name)

        # Test not found
        self.assertIsNone(registry.command("NonExistentCommandXyz123"))

    def test_execution_registry_tool(self) -> None:
        if not PORTED_TOOLS:
            self.skipTest("No ported tools available to test.")

        registry = build_execution_registry()
        first_tool = PORTED_TOOLS[0]

        # Test exact match
        found = registry.tool(first_tool.name)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.name, first_tool.name)

        # Test case-insensitive match
        found_lower = registry.tool(first_tool.name.lower())
        self.assertIsNotNone(found_lower)
        assert found_lower is not None
        self.assertEqual(found_lower.name, first_tool.name)

        found_upper = registry.tool(first_tool.name.upper())
        self.assertIsNotNone(found_upper)
        assert found_upper is not None
        self.assertEqual(found_upper.name, first_tool.name)

        # Test not found
        self.assertIsNone(registry.tool("NonExistentToolXyz123"))

    def test_mirrored_command_execute(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No ported commands available to test.")

        src_cmd = PORTED_COMMANDS[0]
        cmd = MirroredCommand(src_cmd.name, src_cmd.source_hint)

        prompt = "test prompt"
        result = cmd.execute(prompt)

        self.assertIsInstance(result, str)
        self.assertIn(src_cmd.name, result)
        self.assertIn(prompt, result)
        self.assertIn(src_cmd.source_hint, result)

    def test_mirrored_tool_execute(self) -> None:
        if not PORTED_TOOLS:
            self.skipTest("No ported tools available to test.")

        src_tool = PORTED_TOOLS[0]
        tool = MirroredTool(src_tool.name, src_tool.source_hint)

        payload = "test payload"
        result = tool.execute(payload)

        self.assertIsInstance(result, str)
        self.assertIn(src_tool.name, result)
        self.assertIn(payload, result)
        self.assertIn(src_tool.source_hint, result)


if __name__ == "__main__":
    unittest.main()
