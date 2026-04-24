from __future__ import annotations

import unittest
from src.commands import (
    build_command_backlog,
    command_names,
    get_command,
    get_commands,
    PORTED_COMMANDS
)
from src.models import PortingBacklog

class TestCommands(unittest.TestCase):
    def test_build_command_backlog(self):
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, 'Command surface')
        self.assertEqual(len(backlog.modules), len(PORTED_COMMANDS))
        self.assertEqual(backlog.modules, list(PORTED_COMMANDS))

    def test_command_names(self):
        names = command_names()
        self.assertIsInstance(names, list)
        self.assertEqual(len(names), len(PORTED_COMMANDS))
        self.assertEqual(names, [m.name for m in PORTED_COMMANDS])

    def test_get_command_exact_match(self):
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_cmd = PORTED_COMMANDS[0]
        self.assertEqual(get_command(first_cmd.name), first_cmd)

    def test_get_command_case_insensitive(self):
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_cmd = PORTED_COMMANDS[0]
        self.assertEqual(get_command(first_cmd.name.lower()), first_cmd)
        self.assertEqual(get_command(first_cmd.name.upper()), first_cmd)

    def test_get_command_missing(self):
        self.assertIsNone(get_command("NonExistentCommandXYZ123"))

    def test_get_commands(self):
        # Default all commands
        all_commands = get_commands()
        self.assertEqual(len(all_commands), len(PORTED_COMMANDS))
        self.assertEqual(all_commands, tuple(PORTED_COMMANDS))

        # Test include_plugin_commands=False
        plugin_commands = [c for c in PORTED_COMMANDS if "plugin" in c.source_hint.lower()]
        if plugin_commands:
            no_plugins = get_commands(include_plugin_commands=False)
            self.assertTrue(len(no_plugins) < len(PORTED_COMMANDS))
            for cmd in no_plugins:
                self.assertNotIn("plugin", cmd.source_hint.lower())

        # Test include_skill_commands=False
        skill_commands = [c for c in PORTED_COMMANDS if "skills" in c.source_hint.lower()]
        if skill_commands:
            no_skills = get_commands(include_skill_commands=False)
            self.assertTrue(len(no_skills) < len(PORTED_COMMANDS))
            for cmd in no_skills:
                self.assertNotIn("skills", cmd.source_hint.lower())

if __name__ == '__main__':
    unittest.main()
