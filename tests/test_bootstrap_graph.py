import unittest
from src.bootstrap_graph import BootstrapGraph, build_bootstrap_graph


class TestBootstrapGraph(unittest.TestCase):
    def test_build_bootstrap_graph(self):
        graph = build_bootstrap_graph()
        self.assertIsInstance(graph, BootstrapGraph)
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

    def test_as_markdown_typical(self):
        graph = BootstrapGraph(stages=("step 1", "step 2", "step 3"))
        expected = "# Bootstrap Graph\n\n- step 1\n- step 2\n- step 3"
        self.assertEqual(graph.as_markdown(), expected)

    def test_as_markdown_empty(self):
        graph = BootstrapGraph(stages=())
        expected = "# Bootstrap Graph\n"
        self.assertEqual(graph.as_markdown(), expected)

    def test_as_markdown_single_stage(self):
        graph = BootstrapGraph(stages=("only step",))
        expected = "# Bootstrap Graph\n\n- only step"
        self.assertEqual(graph.as_markdown(), expected)

    def test_as_markdown_special_characters(self):
        graph = BootstrapGraph(
            stages=("step with *bold*", "step with `code`", "step with\nnewline")
        )
        expected = "# Bootstrap Graph\n\n- step with *bold*\n- step with `code`\n- step with\nnewline"
        self.assertEqual(graph.as_markdown(), expected)


if __name__ == "__main__":
    unittest.main()
