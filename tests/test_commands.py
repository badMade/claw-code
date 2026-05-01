from __future__ import annotations

import unittest
from unittest.mock import patch
from src.commands import get_commands, PORTED_COMMANDS

class TestCommands(unittest.TestCase):
    def test_get_commands_returns_all_by_default(self) -> None:
        commands = get_commands()
        self.assertIsInstance(commands, tuple)
        self.assertEqual(len(commands), len(PORTED_COMMANDS))
        self.assertEqual(commands, PORTED_COMMANDS)

    def test_get_commands_excludes_plugin_commands(self) -> None:
        commands = get_commands(include_plugin_commands=False)
        self.assertIsInstance(commands, tuple)
        self.assertTrue(len(commands) < len(PORTED_COMMANDS))
        for cmd in commands:
            self.assertNotIn("plugin", cmd.source_hint.lower())

        # Validate that the correct number of commands were excluded
        plugin_commands = [c for c in PORTED_COMMANDS if "plugin" in c.source_hint.lower()]
        if plugin_commands:
            self.assertEqual(len(commands), len(PORTED_COMMANDS) - len(plugin_commands))

    def test_get_commands_excludes_skill_commands(self) -> None:
        commands = get_commands(include_skill_commands=False)
        self.assertIsInstance(commands, tuple)
        self.assertTrue(len(commands) < len(PORTED_COMMANDS))
        for cmd in commands:
            self.assertNotIn("skills", cmd.source_hint.lower())

        # Validate that the correct number of commands were excluded
        skill_commands = [c for c in PORTED_COMMANDS if "skills" in c.source_hint.lower()]
        if skill_commands:
            self.assertEqual(len(commands), len(PORTED_COMMANDS) - len(skill_commands))

    def test_get_commands_excludes_both(self) -> None:
        commands = get_commands(include_plugin_commands=False, include_skill_commands=False)
        self.assertIsInstance(commands, tuple)

        plugin_commands = [c for c in PORTED_COMMANDS if "plugin" in c.source_hint.lower()]
        skill_commands = [c for c in PORTED_COMMANDS if "skills" in c.source_hint.lower()]
        expected_excluded = set(plugin_commands) | set(skill_commands)

        if expected_excluded:
            self.assertEqual(len(commands), len(PORTED_COMMANDS) - len(expected_excluded))

        for cmd in commands:
            self.assertNotIn("plugin", cmd.source_hint.lower())
            self.assertNotIn("skills", cmd.source_hint.lower())

    @patch('src.commands.PORTED_COMMANDS', tuple())
    def test_get_commands_empty_snapshot(self) -> None:
        # Test behavior when there are no commands available
        commands = get_commands()
        self.assertIsInstance(commands, tuple)
        self.assertEqual(len(commands), 0)

        commands_no_plugins = get_commands(include_plugin_commands=False)
        self.assertIsInstance(commands_no_plugins, tuple)
        self.assertEqual(len(commands_no_plugins), 0)

if __name__ == '__main__':
    unittest.main()
