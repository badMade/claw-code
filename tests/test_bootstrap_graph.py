from __future__ import annotations

import unittest
from src.bootstrap_graph import BootstrapGraph, build_bootstrap_graph


class TestBootstrapGraph(unittest.TestCase):
    def test_build_bootstrap_graph(self) -> None:
        """Test that build_bootstrap_graph returns the expected graph."""
        graph = build_bootstrap_graph()

        self.assertIsInstance(graph, BootstrapGraph)
        self.assertEqual(len(graph.stages), 7)
        self.assertEqual(
            graph.stages,
            (
                "top-level prefetch side effects",
                "warning handler and environment guards",
                "CLI parser and pre-action trust gate",
                "setup() + commands/agents parallel load",
                "deferred init after trust",
                "mode routing: local / remote / ssh / teleport / direct-connect / deep-link",
                "query engine submit loop",
            ),
        )

    def test_bootstrap_graph_as_markdown(self) -> None:
        """Test the markdown formatting of the BootstrapGraph."""
        # Using a subset of stages for the markdown test to keep it focused
        graph = BootstrapGraph(stages=("stage 1", "stage 2"))

        expected_markdown = "# Bootstrap Graph\n\n- stage 1\n- stage 2"

        self.assertEqual(graph.as_markdown(), expected_markdown)

    def test_bootstrap_graph_as_markdown_empty(self) -> None:
        """Test markdown formatting when there are no stages."""
        graph = BootstrapGraph(stages=())
        expected_markdown = "# Bootstrap Graph\n"
        self.assertEqual(graph.as_markdown(), expected_markdown)


if __name__ == "__main__":
    unittest.main()
