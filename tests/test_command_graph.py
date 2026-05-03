from __future__ import annotations

import unittest
from unittest import mock

from src.command_graph import CommandGraph, build_command_graph
from src.models import PortingModule


class TestCommandGraph(unittest.TestCase):
    def test_build_command_graph(self) -> None:
        mock_commands = (
            PortingModule(name="cmd1", responsibility="Do 1", source_hint="core"),
            PortingModule(name="cmd2", responsibility="Do 2", source_hint="plugin_a"),
            PortingModule(name="cmd3", responsibility="Do 3", source_hint="PLUGIN_B"),
            PortingModule(name="cmd4", responsibility="Do 4", source_hint="skills/xyz"),
            PortingModule(name="cmd5", responsibility="Do 5", source_hint="SKILLS/abc"),
            PortingModule(
                name="cmd6", responsibility="Do 6", source_hint="plugin/skills"
            ),  # Both!
        )

        with mock.patch("src.command_graph.get_commands", return_value=mock_commands):
            graph = build_command_graph()

            # Check builtins
            self.assertEqual(len(graph.builtins), 1)
            self.assertEqual(graph.builtins[0].name, "cmd1")

            # Check plugin-like
            self.assertEqual(len(graph.plugin_like), 3)
            self.assertEqual(
                [m.name for m in graph.plugin_like], ["cmd2", "cmd3", "cmd6"]
            )

            # Check skill-like
            self.assertEqual(len(graph.skill_like), 3)
            self.assertEqual(
                [m.name for m in graph.skill_like], ["cmd4", "cmd5", "cmd6"]
            )

    def test_flattened(self) -> None:
        graph = CommandGraph(
            builtins=(PortingModule(name="c1", responsibility="r", source_hint="h"),),
            plugin_like=(
                PortingModule(name="c2", responsibility="r", source_hint="h"),
            ),
            skill_like=(PortingModule(name="c3", responsibility="r", source_hint="h"),),
        )
        flattened = graph.flattened()
        self.assertEqual(len(flattened), 3)
        self.assertEqual([m.name for m in flattened], ["c1", "c2", "c3"])

    def test_as_markdown(self) -> None:
        graph = CommandGraph(
            builtins=(PortingModule(name="c1", responsibility="r", source_hint="h"),),
            plugin_like=(
                PortingModule(name="c2", responsibility="r", source_hint="h"),
            ),
            skill_like=(PortingModule(name="c3", responsibility="r", source_hint="h"),),
        )
        md = graph.as_markdown()
        self.assertIn("# Command Graph", md)
        self.assertIn("Builtins: 1", md)
        self.assertIn("Plugin-like commands: 1", md)
        self.assertIn("Skill-like commands: 1", md)


if __name__ == "__main__":
    unittest.main()
