from __future__ import annotations

import unittest
from src.commands import (
    get_command,
    get_commands,
    command_names,
    build_command_backlog,
    PORTED_COMMANDS,
)
from src.models import PortingBacklog


class TestCommands(unittest.TestCase):
    def test_get_command_exact_match(self):
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_cmd = PORTED_COMMANDS[0]
        # Exact match
        self.assertEqual(get_command(first_cmd.name), first_cmd)

    def test_get_command_case_insensitive(self):
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_cmd = PORTED_COMMANDS[0]
        # Case-insensitive match
        self.assertEqual(get_command(first_cmd.name.upper()), first_cmd)
        self.assertEqual(get_command(first_cmd.name.lower()), first_cmd)

    def test_get_command_not_found(self):
        # Unknown command
        self.assertIsNone(get_command("NonExistentCommandxyz123"))

    def test_get_commands_default(self):
        # Default behavior includes everything
        all_commands = get_commands()
        self.assertEqual(len(all_commands), len(PORTED_COMMANDS))

    def test_get_commands_no_plugins(self):
        # Filter plugins
        plugins_exist = any("plugin" in m.source_hint.lower() for m in PORTED_COMMANDS)
        no_plugins = get_commands(include_plugin_commands=False)
        if plugins_exist:
            self.assertTrue(len(no_plugins) < len(PORTED_COMMANDS))
        for cmd in no_plugins:
            self.assertNotIn("plugin", cmd.source_hint.lower())

    def test_get_commands_no_skills(self):
        # Filter skills
        skills_exist = any("skills" in m.source_hint.lower() for m in PORTED_COMMANDS)
        no_skills = get_commands(include_skill_commands=False)
        if skills_exist:
            self.assertTrue(len(no_skills) < len(PORTED_COMMANDS))
        for cmd in no_skills:
            self.assertNotIn("skills", cmd.source_hint.lower())

    def test_command_names(self):
        names = command_names()
        self.assertEqual(len(names), len(PORTED_COMMANDS))
        self.assertEqual(names, [m.name for m in PORTED_COMMANDS])

    def test_build_command_backlog(self):
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, "Command surface")
        self.assertEqual(len(backlog.modules), len(PORTED_COMMANDS))
        self.assertEqual(backlog.modules, list(PORTED_COMMANDS))


if __name__ == "__main__":
    unittest.main()
