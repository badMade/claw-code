from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from src.commands import (
    load_command_snapshot,
    build_command_backlog,
    command_names,
    get_command,
    get_commands,
    find_commands,
    execute_command,
    render_command_index,
    built_in_command_names,
    PORTED_COMMANDS,
)
from src.models import PortingBacklog, PortingModule


class TestCommands(unittest.TestCase):
    def test_load_command_snapshot(self) -> None:
        # Load directly against the actual JSON to follow established test patterns
        commands = load_command_snapshot()
        self.assertIsInstance(commands, tuple)
        self.assertTrue(len(commands) > 0)
        for command in commands:
            self.assertIsInstance(command, PortingModule)
            self.assertEqual(command.status, "mirrored")

    @patch("src.commands.PORTED_COMMANDS", tuple())
    @patch("src.commands._get_command_lookup")
    def test_empty_snapshot(self, mock_lookup: MagicMock) -> None:
        mock_lookup.return_value = {}

        self.assertIsNone(get_command("test"))
        self.assertEqual(get_commands(), tuple())
        self.assertEqual(find_commands("test"), [])

        execution = execute_command("test")
        self.assertFalse(execution.handled)
        self.assertEqual(execution.message, "Unknown mirrored command: test")

    def test_build_command_backlog(self) -> None:
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, "Command surface")
        self.assertEqual(len(backlog.modules), len(PORTED_COMMANDS))
        self.assertEqual(backlog.modules, list(PORTED_COMMANDS))

    def test_command_names(self) -> None:
        names = command_names()
        self.assertIsInstance(names, list)
        self.assertEqual(len(names), len(PORTED_COMMANDS))
        self.assertEqual(names, [m.name for m in PORTED_COMMANDS])

    def test_built_in_command_names(self) -> None:
        names = built_in_command_names()
        self.assertIsInstance(names, frozenset)
        # Compare unique names
        unique_names = frozenset(m.name for m in PORTED_COMMANDS)
        self.assertEqual(len(names), len(unique_names))
        self.assertEqual(names, unique_names)

    def test_get_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_command = PORTED_COMMANDS[0]
        # Exact match
        self.assertEqual(get_command(first_command.name), first_command)
        # Case-insensitive match
        self.assertEqual(get_command(first_command.name.lower()), first_command)
        self.assertEqual(get_command(first_command.name.upper()), first_command)
        # Unknown command
        self.assertIsNone(get_command("NonExistentCommandNamexyz123"))

    def test_get_commands(self) -> None:
        # Default
        all_commands = get_commands()
        self.assertEqual(len(all_commands), len(PORTED_COMMANDS))

        # include_plugin_commands=False
        plugin_commands = [
            c for c in PORTED_COMMANDS if "plugin" in c.source_hint.lower()
        ]
        if plugin_commands:
            no_plugins = get_commands(include_plugin_commands=False)
            self.assertTrue(len(no_plugins) < len(PORTED_COMMANDS))
            for cmd in no_plugins:
                self.assertNotIn("plugin", cmd.source_hint.lower())

        # include_skill_commands=False
        skill_commands = [
            c for c in PORTED_COMMANDS if "skills" in c.source_hint.lower()
        ]
        if skill_commands:
            no_skills = get_commands(include_skill_commands=False)
            self.assertTrue(len(no_skills) < len(PORTED_COMMANDS))
            for cmd in no_skills:
                self.assertNotIn("skills", cmd.source_hint.lower())

    def test_find_commands(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        command = PORTED_COMMANDS[0]
        # Find by name
        matches = find_commands(command.name)
        self.assertIn(command, matches)

        # Find by source_hint
        matches = find_commands(command.source_hint)
        self.assertIn(command, matches)

        # Limit
        limit = 2
        matches = find_commands("", limit=limit)
        self.assertLessEqual(len(matches), limit)

    def test_execute_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        command = PORTED_COMMANDS[0]
        # Success
        execution = execute_command(command.name, "test prompt")
        self.assertTrue(execution.handled)
        self.assertEqual(execution.name, command.name)
        self.assertEqual(execution.source_hint, command.source_hint)
        self.assertEqual(execution.prompt, "test prompt")
        self.assertIn(command.name, execution.message)
        self.assertIn(command.source_hint, execution.message)
        self.assertIn("test prompt", execution.message)

        # Failure
        unknown_name = "UnknownCommandNamexyz123"
        execution = execute_command(unknown_name)
        self.assertFalse(execution.handled)
        self.assertEqual(execution.name, unknown_name)
        self.assertIn(f"Unknown mirrored command: {unknown_name}", execution.message)

    def test_render_command_index(self) -> None:
        # No query
        output = render_command_index(limit=5)
        self.assertIn(f"Command entries: {len(PORTED_COMMANDS)}", output)

        # With query
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        command = PORTED_COMMANDS[0]
        output = render_command_index(query=command.name)
        self.assertIn(f"Filtered by: {command.name}", output)
        self.assertIn(command.name, output)


if __name__ == "__main__":
    unittest.main()
