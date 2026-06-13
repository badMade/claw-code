import unittest
from src.replLauncher import build_repl_banner


class TestReplLauncher(unittest.TestCase):
    def test_build_repl_banner(self) -> None:
        """Test that build_repl_banner returns the exact expected string."""
        expected_banner = "Python porting REPL is not interactive yet; use `python3 -m src.main summary` instead."
        self.assertEqual(build_repl_banner(), expected_banner)


if __name__ == "__main__":
    unittest.main()
