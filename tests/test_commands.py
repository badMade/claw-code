from __future__ import annotations

import unittest
from unittest.mock import patch

from src.models import PortingModule, PortingBacklog
import src.commands
from src.commands import (
    load_command_snapshot,
    built_in_command_names,
    build_command_backlog,
    command_names,
    get_command,
    get_commands,
    find_commands,
    execute_command,
    render_command_index,
    CommandExecution,
)

# Mock data
MOCK_COMMANDS = (
    PortingModule(
        name="TestCommand1",
        responsibility="Does test 1",
        source_hint="Core",
        status="mirrored",
    ),
    PortingModule(
        name="TestPluginCommand",
        responsibility="Does plugin stuff",
        source_hint="plugin source",
        status="mirrored",
    ),
    PortingModule(
        name="TestSkillCommand",
        responsibility="Does skill stuff",
        source_hint="skills module",
        status="mirrored",
    ),
)


class TestCommands(unittest.TestCase):
    def setUp(self):
        # Patch PORTED_COMMANDS in src.commands
        self.patcher = patch("src.commands.PORTED_COMMANDS", MOCK_COMMANDS)
        self.mock_ported_commands = self.patcher.start()

        # Clear lru_caches because they retain state across tests
        src.commands.built_in_command_names.cache_clear()
        src.commands._get_command_lookup.cache_clear()

    def tearDown(self):
        self.patcher.stop()

        # Clear caches again after unpatching so real command lookups are not contaminated
        src.commands.built_in_command_names.cache_clear()
        src.commands._get_command_lookup.cache_clear()

    def test_load_command_snapshot(self):
        # We don't need to patch for this test if we call the function directly
        # but the file is loaded so we just test the real load to ensure snapshot parsing works.
        snapshot = load_command_snapshot()
        self.assertIsInstance(snapshot, tuple)
        self.assertTrue(len(snapshot) > 0)
        for cmd in snapshot:
            self.assertIsInstance(cmd, PortingModule)
            self.assertEqual(cmd.status, "mirrored")

    def test_built_in_command_names(self):
        names = built_in_command_names()
        self.assertIsInstance(names, frozenset)
        self.assertEqual(names, frozenset(c.name for c in MOCK_COMMANDS))

    def test_build_command_backlog(self):
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, "Command surface")
        self.assertEqual(backlog.modules, list(MOCK_COMMANDS))

    def test_command_names(self):
        names = command_names()
        self.assertIsInstance(names, list)
        self.assertEqual(names, [c.name for c in MOCK_COMMANDS])

    def test_get_command(self):
        # Exact match
        self.assertEqual(get_command("TestCommand1"), MOCK_COMMANDS[0])
        # Case insensitive match
        self.assertEqual(get_command("testcommand1"), MOCK_COMMANDS[0])
        self.assertEqual(get_command("TESTCOMMAND1"), MOCK_COMMANDS[0])
        # Not found
        self.assertIsNone(get_command("NonExistentCommand"))

    def test_get_commands(self):
        # All
        all_cmds = get_commands()
        self.assertEqual(all_cmds, MOCK_COMMANDS)

        # No plugin
        no_plugins = get_commands(include_plugin_commands=False)
        self.assertEqual(len(no_plugins), 2)
        self.assertNotIn(MOCK_COMMANDS[1], no_plugins)

        # No skill
        no_skills = get_commands(include_skill_commands=False)
        self.assertEqual(len(no_skills), 2)
        self.assertNotIn(MOCK_COMMANDS[2], no_skills)

        # Neither plugin nor skill
        core_only = get_commands(
            include_plugin_commands=False, include_skill_commands=False
        )
        self.assertEqual(len(core_only), 1)
        self.assertEqual(core_only[0], MOCK_COMMANDS[0])

    def test_find_commands(self):
        # Match by name
        matches = find_commands("TestCommand1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], MOCK_COMMANDS[0])

        # Match by source_hint
        matches = find_commands("Core")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], MOCK_COMMANDS[0])

        # Partial match
        matches = find_commands("Test")
        self.assertEqual(len(matches), 3)

        # Limit
        matches = find_commands("Test", limit=2)
        self.assertEqual(len(matches), 2)

    def test_execute_command(self):
        # Success
        result = execute_command("TestCommand1", "do something")
        self.assertIsInstance(result, CommandExecution)
        self.assertTrue(result.handled)
        self.assertEqual(result.name, "TestCommand1")
        self.assertEqual(result.source_hint, "Core")
        self.assertEqual(result.prompt, "do something")
        self.assertIn("Mirrored command 'TestCommand1'", result.message)

        # Unknown
        result = execute_command("UnknownCmd", "do something")
        self.assertIsInstance(result, CommandExecution)
        self.assertFalse(result.handled)
        self.assertEqual(result.name, "UnknownCmd")
        self.assertEqual(result.prompt, "do something")
        self.assertIn("Unknown mirrored command", result.message)

    def test_render_command_index(self):
        # No query
        output = render_command_index(limit=5)
        self.assertIn("Command entries: 3", output)
        self.assertIn("- TestCommand1 \u2014 Core", output)

        # With query
        output = render_command_index(query="TestCommand1")
        self.assertIn("Command entries: 3", output)
        self.assertIn("Filtered by: TestCommand1", output)
        self.assertIn("- TestCommand1 \u2014 Core", output)
        self.assertNotIn("TestPluginCommand", output)


if __name__ == "__main__":
    unittest.main()
