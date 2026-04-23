from __future__ import annotations

import unittest
from unittest.mock import patch

from src.command_graph import CommandGraph, build_command_graph
from src.models import PortingModule


class TestCommandGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.builtin_1 = PortingModule(
            name="cmd1", responsibility="do something", source_hint="core"
        )
        self.builtin_2 = PortingModule(
            name="cmd2", responsibility="do another", source_hint="base"
        )
        self.plugin_1 = PortingModule(
            name="plugin1", responsibility="plugin action", source_hint="my_plugin"
        )
        self.plugin_2 = PortingModule(
            name="plugin2", responsibility="plugin action 2", source_hint="PLUGIN_DIR"
        )
        self.skill_1 = PortingModule(
            name="skill1", responsibility="skill action", source_hint="skills_repo"
        )
        self.skill_2 = PortingModule(
            name="skill2", responsibility="skill action 2", source_hint="SKILLS"
        )

        self.graph = CommandGraph(
            builtins=(self.builtin_1, self.builtin_2),
            plugin_like=(self.plugin_1, self.plugin_2),
            skill_like=(self.skill_1, self.skill_2),
        )

    def test_flattened(self) -> None:
        flattened = self.graph.flattened()
        self.assertEqual(len(flattened), 6)
        self.assertEqual(
            flattened,
            (
                self.builtin_1,
                self.builtin_2,
                self.plugin_1,
                self.plugin_2,
                self.skill_1,
                self.skill_2,
            ),
        )

    def test_as_markdown(self) -> None:
        markdown = self.graph.as_markdown()
        expected = (
            "# Command Graph\n"
            "\n"
            "Builtins: 2\n"
            "Plugin-like commands: 2\n"
            "Skill-like commands: 2"
        )
        self.assertEqual(markdown, expected)

    @patch("src.command_graph.get_commands")
    def test_build_command_graph(self, mock_get_commands) -> None:
        mock_get_commands.return_value = (
            self.builtin_1,
            self.builtin_2,
            self.plugin_1,
            self.plugin_2,
            self.skill_1,
            self.skill_2,
        )

        graph = build_command_graph()
        self.assertIsInstance(graph, CommandGraph)
        self.assertEqual(graph.builtins, (self.builtin_1, self.builtin_2))
        self.assertEqual(graph.plugin_like, (self.plugin_1, self.plugin_2))
        self.assertEqual(graph.skill_like, (self.skill_1, self.skill_2))


if __name__ == "__main__":
    unittest.main()
