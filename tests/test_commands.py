from __future__ import annotations

import unittest
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
    CommandExecution
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
        self.assertTrue(len(names) > 0)
        self.assertIn(PORTED_COMMANDS[0].name, names)

    def test_build_command_backlog(self) -> None:
        backlog = build_command_backlog()
        self.assertIsInstance(backlog, PortingBacklog)
        self.assertEqual(backlog.title, "Command surface")
        self.assertEqual(len(backlog.modules), len(PORTED_COMMANDS))

    def test_command_names(self) -> None:
        names = command_names()
        self.assertIsInstance(names, list)
        self.assertEqual(len(names), len(PORTED_COMMANDS))
        self.assertIn(PORTED_COMMANDS[0].name, names)

    def test_get_command(self) -> None:
        first_command = PORTED_COMMANDS[0]
        command = get_command(first_command.name)
        self.assertIsNotNone(command)
        if command:
            self.assertEqual(command.name, first_command.name)

        # test case insensitive
        command_upper = get_command(first_command.name.upper())
        self.assertIsNotNone(command_upper)
        if command_upper:
            self.assertEqual(command_upper.name, first_command.name)

        # test non-existent
        self.assertIsNone(get_command("nonexistent_command_name_123"))

    def test_get_commands(self) -> None:
        commands = get_commands()
        self.assertIsInstance(commands, tuple)
        self.assertEqual(len(commands), len(PORTED_COMMANDS))

        # test filtering
        no_plugins = get_commands(include_plugin_commands=False)
        for cmd in no_plugins:
            self.assertNotIn("plugin", cmd.source_hint.lower())

        no_skills = get_commands(include_skill_commands=False)
        for cmd in no_skills:
            self.assertNotIn("skills", cmd.source_hint.lower())

    def test_find_commands(self) -> None:
        if PORTED_COMMANDS:
            first_cmd = PORTED_COMMANDS[0]
            matches = find_commands(first_cmd.name.lower())
            self.assertTrue(len(matches) > 0)
            self.assertIn(first_cmd, matches)

            # test limit
            limited_matches = find_commands("a", limit=1)
            self.assertEqual(len(limited_matches), 1)

    def test_execute_command(self) -> None:
        if PORTED_COMMANDS:
            first_cmd = PORTED_COMMANDS[0]
            execution = execute_command(first_cmd.name, prompt="test prompt")
            self.assertIsInstance(execution, CommandExecution)
            self.assertTrue(execution.handled)
            self.assertEqual(execution.name, first_cmd.name)
            self.assertEqual(execution.prompt, "test prompt")
            self.assertIn("Mirrored command", execution.message)

        # test unknown command
        unknown = execute_command("nonexistent_cmd_123")
        self.assertFalse(unknown.handled)
        self.assertEqual(unknown.name, "nonexistent_cmd_123")
        self.assertIn("Unknown mirrored command", unknown.message)

    def test_render_command_index(self) -> None:
        output = render_command_index(limit=5)
        self.assertIsInstance(output, str)
        self.assertIn(f"Command entries: {len(PORTED_COMMANDS)}", output)

        output_filtered = render_command_index(limit=5, query="a")
        self.assertIn("Filtered by: a", output_filtered)
