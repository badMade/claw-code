from __future__ import annotations

import unittest
from unittest.mock import patch

from src.commands import PORTED_COMMANDS, find_commands, get_commands
from src.models import PortingModule


class TestCommands(unittest.TestCase):
    def test_get_commands(self) -> None:
        commands = get_commands()
        self.assertEqual(commands, PORTED_COMMANDS)

        plugin_commands = [
            command for command in PORTED_COMMANDS if 'plugin' in command.source_hint.lower()
        ]
        if plugin_commands:
            without_plugin_commands = get_commands(include_plugin_commands=False)
            self.assertLess(len(without_plugin_commands), len(PORTED_COMMANDS))
            for command in without_plugin_commands:
                self.assertNotIn('plugin', command.source_hint.lower())

        skill_commands = [
            command for command in PORTED_COMMANDS if 'skills' in command.source_hint.lower()
        ]
        if skill_commands:
            without_skill_commands = get_commands(include_skill_commands=False)
            self.assertLess(len(without_skill_commands), len(PORTED_COMMANDS))
            for command in without_skill_commands:
                self.assertNotIn('skills', command.source_hint.lower())

    def test_get_commands_filters_only_source_hint_classifiers(self) -> None:
        ordinary_command = PortingModule(
            name='ordinary',
            source_hint='commands/ordinary.ts',
            responsibility='mentions plugin and skills boilerplate but is not sourced there',
            status='mirrored',
        )
        plugin_command = PortingModule(
            name='ordinary-plugin',
            source_hint='plugins/ordinary-plugin.ts',
            responsibility='ordinary command',
            status='mirrored',
        )
        skill_command = PortingModule(
            name='ordinary-skill',
            source_hint='commands/skills/ordinary-skill.ts',
            responsibility='ordinary command',
            status='mirrored',
        )

        with patch(
            'src.commands.PORTED_COMMANDS',
            (ordinary_command, plugin_command, skill_command),
        ):
            self.assertEqual(
                get_commands(
                    include_plugin_commands=False,
                    include_skill_commands=False,
                ),
                (ordinary_command,),
            )

    def test_find_commands(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest('No commands available in snapshot')

        command = PORTED_COMMANDS[0]
        self.assertIn(command, find_commands(command.name))
        self.assertIn(command, find_commands(command.source_hint))

        limit = 2
        matches = find_commands('', limit=limit)
        self.assertLessEqual(len(matches), limit)

    def test_find_commands_excludes_responsibility_boilerplate(self) -> None:
        matches = find_commands('typescript', limit=len(PORTED_COMMANDS))
        self.assertEqual(matches, [])


if __name__ == '__main__':
    unittest.main()
