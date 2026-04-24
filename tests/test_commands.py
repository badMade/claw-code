from __future__ import annotations

import unittest
from src.commands import (
    load_command_snapshot,
    build_command_backlog,
    command_names,
    get_command,
    get_commands,
    find_commands,
    execute_command,
    render_command_index,
    PORTED_COMMANDS,
)
from src.models import PortingBacklog, PortingModule


class TestCommands(unittest.TestCase):
    def test_load_command_snapshot(self) -> None:
        commands = load_command_snapshot()
        self.assertIsInstance(commands, tuple)
        self.assertTrue(len(commands) > 0)
        for cmd in commands:
            self.assertIsInstance(cmd, PortingModule)
            self.assertEqual(cmd.status, "mirrored")

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

    def test_get_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_cmd = PORTED_COMMANDS[0]
        # Exact match
        self.assertEqual(get_command(first_cmd.name), first_cmd)
        # Case-insensitive match
        self.assertEqual(get_command(first_cmd.name.lower()), first_cmd)
        self.assertEqual(get_command(first_cmd.name.upper()), first_cmd)
        # Unknown command
        self.assertIsNone(get_command("NonExistentCommandNamexyz123"))

    def test_get_commands(self) -> None:
        # Default
        all_commands = get_commands()
        self.assertEqual(len(all_commands), len(PORTED_COMMANDS))

        # Test include_plugin_commands=False
        plugin_commands = [
            c for c in PORTED_COMMANDS if "plugin" in c.source_hint.lower()
        ]
        if plugin_commands:
            no_plugin_cmds = get_commands(include_plugin_commands=False)
            self.assertTrue(len(no_plugin_cmds) < len(PORTED_COMMANDS))
            for cmd in no_plugin_cmds:
                self.assertNotIn("plugin", cmd.source_hint.lower())

        # Test include_skill_commands=False
        skill_commands = [
            c for c in PORTED_COMMANDS if "skills" in c.source_hint.lower()
        ]
        if skill_commands:
            no_skill_cmds = get_commands(include_skill_commands=False)
            self.assertTrue(len(no_skill_cmds) < len(PORTED_COMMANDS))
            for cmd in no_skill_cmds:
                self.assertNotIn("skills", cmd.source_hint.lower())

    def test_find_commands(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        cmd = PORTED_COMMANDS[0]
        # Find by name
        matches = find_commands(cmd.name)
        self.assertIn(cmd, matches)

        # Find by source_hint
        matches = find_commands(cmd.source_hint)
        self.assertIn(cmd, matches)

        # Limit
        limit = 2
        matches = find_commands("", limit=limit)
        self.assertLessEqual(len(matches), limit)

    def test_execute_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        cmd = PORTED_COMMANDS[0]
        # Success
        execution = execute_command(cmd.name, "test prompt")
        self.assertTrue(execution.handled)
        self.assertEqual(execution.name, cmd.name)
        self.assertEqual(execution.source_hint, cmd.source_hint)
        self.assertEqual(execution.prompt, "test prompt")
        self.assertIn(cmd.name, execution.message)
        self.assertIn(cmd.source_hint, execution.message)

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

        cmd = PORTED_COMMANDS[0]
        output = render_command_index(query=cmd.name)
        self.assertIn(f"Filtered by: {cmd.name}", output)
        self.assertIn(cmd.name, output)


if __name__ == "__main__":
    unittest.main()
