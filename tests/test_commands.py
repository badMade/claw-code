from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from src.commands import (
    load_command_snapshot,
    get_command,
    get_commands,
    find_commands,
    execute_command,
    PORTED_COMMANDS,
)


class TestCommands(unittest.TestCase):
    def test_get_commands(self) -> None:
        # Default: both True
        all_commands = get_commands()
        self.assertEqual(len(all_commands), len(PORTED_COMMANDS))

        # include_plugin_commands=False
        no_plugins = get_commands(include_plugin_commands=False)
        for cmd in no_plugins:
            self.assertNotIn("plugin", cmd.source_hint.lower())

        # Check that we actually filtered something out if plugins exist
        plugins_exist = any(
            "plugin" in cmd.source_hint.lower() for cmd in PORTED_COMMANDS
        )
        if plugins_exist:
            self.assertLess(len(no_plugins), len(PORTED_COMMANDS))

        # include_skill_commands=False
        no_skills = get_commands(include_skill_commands=False)
        for cmd in no_skills:
            self.assertNotIn("skills", cmd.source_hint.lower())

        skills_exist = any(
            "skills" in cmd.source_hint.lower() for cmd in PORTED_COMMANDS
        )
        if skills_exist:
            self.assertLess(len(no_skills), len(PORTED_COMMANDS))

        # both False
        no_plugins_no_skills = get_commands(
            include_plugin_commands=False, include_skill_commands=False
        )
        for cmd in no_plugins_no_skills:
            self.assertNotIn("plugin", cmd.source_hint.lower())
            self.assertNotIn("skills", cmd.source_hint.lower())

        if plugins_exist or skills_exist:
            self.assertLess(len(no_plugins_no_skills), len(PORTED_COMMANDS))

    def test_load_command_snapshot_errors(self) -> None:
        # The function uses lru_cache, so we need to clear it to test error states
        load_command_snapshot.cache_clear()

        # Test FileNotFoundError
        with patch("pathlib.Path.read_text", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                load_command_snapshot()
        load_command_snapshot.cache_clear()

        # Test PermissionError
        with patch("pathlib.Path.read_text", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                load_command_snapshot()
        load_command_snapshot.cache_clear()

        # Test json.JSONDecodeError
        with patch("pathlib.Path.read_text", return_value="invalid json"):
            with self.assertRaises(json.JSONDecodeError):
                load_command_snapshot()
        load_command_snapshot.cache_clear()

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


if __name__ == "__main__":
    unittest.main()
