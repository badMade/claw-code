from __future__ import annotations

import unittest
from unittest.mock import patch
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
    PORTED_COMMANDS,
    _get_command_lookup,
)
from src.models import PortingBacklog, PortingModule

class TestCommands(unittest.TestCase):
    def test_load_command_snapshot(self) -> None:
        commands = load_command_snapshot()
        self.assertIsInstance(commands, tuple)
        self.assertTrue(len(commands) > 0)
        for command in commands:
            self.assertIsInstance(command, PortingModule)
            self.assertEqual(command.status, 'mirrored')

    def test_built_in_command_names(self) -> None:
        names = built_in_command_names()
        self.assertIsInstance(names, frozenset)
        self.assertEqual(len(names), len(set(m.name for m in PORTED_COMMANDS)))
        self.assertEqual(names, frozenset(m.name for m in PORTED_COMMANDS))

    def test_build_command_backlog(self) -> None:
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, 'Command surface')
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

        # Test exclusions if applicable commands exist
        plugin_commands = [c for c in PORTED_COMMANDS if 'plugin' in c.source_hint.lower()]
        if plugin_commands:
            no_plugin_commands = get_commands(include_plugin_commands=False)
            self.assertTrue(len(no_plugin_commands) < len(PORTED_COMMANDS))
            for command in no_plugin_commands:
                self.assertNotIn('plugin', command.source_hint.lower())

        skill_commands = [c for c in PORTED_COMMANDS if 'skills' in c.source_hint.lower()]
        if skill_commands:
            no_skill_commands = get_commands(include_skill_commands=False)
            self.assertTrue(len(no_skill_commands) < len(PORTED_COMMANDS))
            for command in no_skill_commands:
                self.assertNotIn('skills', command.source_hint.lower())

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
        self.assertIn("'test prompt'", execution.message)

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


    def test_empty_snapshot_edge_cases(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        known_command = PORTED_COMMANDS[0].name
        self.assertIsNotNone(get_command(known_command))
        self.assertTrue(execute_command(known_command).handled)

        with patch('src.commands.PORTED_COMMANDS', tuple()):
            built_in_command_names.cache_clear()
            _get_command_lookup.cache_clear()

            # Test built_in_command_names with empty snapshot
            self.assertEqual(built_in_command_names(), frozenset())

            # Test build_command_backlog with empty snapshot
            backlog = build_command_backlog()
            self.assertEqual(len(backlog.modules), 0)

            # Test command_names with empty snapshot
            self.assertEqual(len(command_names()), 0)

            # Test get_command with empty snapshot using previously valid command
            self.assertIsNone(get_command(known_command))

            # Test get_commands with empty snapshot
            self.assertEqual(len(get_commands()), 0)

            # Test find_commands with empty snapshot
            self.assertEqual(len(find_commands(known_command)), 0)

            # Test execute_command with empty snapshot using previously valid command
            execution = execute_command(known_command, "prompt")
            self.assertFalse(execution.handled)
            self.assertIn("Unknown mirrored command", execution.message)

            # Test render_command_index with empty snapshot
            output = render_command_index()
            self.assertIn("Command entries: 0", output)

        built_in_command_names.cache_clear()
        _get_command_lookup.cache_clear()

if __name__ == '__main__':
    unittest.main()
