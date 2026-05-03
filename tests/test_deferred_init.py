from __future__ import annotations

import unittest
from src.deferred_init import run_deferred_init, DeferredInitResult


class TestDeferredInit(unittest.TestCase):
    def test_run_deferred_init_trusted(self) -> None:
        result = run_deferred_init(True)
        self.assertIsInstance(result, DeferredInitResult)
        self.assertTrue(result.trusted)
        self.assertTrue(result.plugin_init)
        self.assertTrue(result.skill_init)
        self.assertTrue(result.mcp_prefetch)
        self.assertTrue(result.session_hooks)

    def test_run_deferred_init_untrusted(self) -> None:
        result = run_deferred_init(False)
        self.assertIsInstance(result, DeferredInitResult)
        self.assertFalse(result.trusted)
        self.assertFalse(result.plugin_init)
        self.assertFalse(result.skill_init)
        self.assertFalse(result.mcp_prefetch)
        self.assertFalse(result.session_hooks)

    def test_deferred_init_result_as_lines(self) -> None:
        result = DeferredInitResult(
            trusted=True,
            plugin_init=True,
            skill_init=False,
            mcp_prefetch=True,
            session_hooks=False,
        )
        lines = result.as_lines()
        self.assertIsInstance(lines, tuple)
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "- plugin_init=True")
        self.assertEqual(lines[1], "- skill_init=False")
        self.assertEqual(lines[2], "- mcp_prefetch=True")
        self.assertEqual(lines[3], "- session_hooks=False")


if __name__ == "__main__":
    unittest.main()
