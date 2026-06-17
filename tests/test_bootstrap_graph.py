import unittest
from src.bootstrap_graph import BootstrapGraph, build_bootstrap_graph


class TestBootstrapGraph(unittest.TestCase):
    def test_as_markdown(self):
        graph = BootstrapGraph(stages=("stage A", "stage B", "stage C"))
        expected = "# Bootstrap Graph\n\n- stage A\n- stage B\n- stage C"
        self.assertEqual(graph.as_markdown(), expected)

    def test_build_bootstrap_graph(self):
        graph = build_bootstrap_graph()
        self.assertIsInstance(graph, BootstrapGraph)

        expected_stages = (
            "top-level prefetch side effects",
            "warning handler and environment guards",
            "CLI parser and pre-action trust gate",
            "setup() + commands/agents parallel load",
            "deferred init after trust",
            "mode routing: local / remote / ssh / teleport / direct-connect / deep-link",
            "query engine submit loop",
        )

        self.assertEqual(graph.stages, expected_stages)


if __name__ == "__main__":
    unittest.main()
