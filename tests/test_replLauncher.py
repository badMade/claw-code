from __future__ import annotations

import unittest
from src.replLauncher import build_repl_banner


class TestReplLauncher(unittest.TestCase):
    def test_build_repl_banner(self) -> None:
        expected = "Python porting REPL is not interactive yet; use `python3 -m src.main summary` instead."
        self.assertEqual(build_repl_banner(), expected)


if __name__ == "__main__":
    unittest.main()
