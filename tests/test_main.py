import argparse
import unittest

from src.main import build_parser


class TestMainParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def test_build_parser_returns_argument_parser(self) -> None:
        self.assertIsInstance(self.parser, argparse.ArgumentParser)
        self.assertEqual(
            self.parser.description,
            "Python porting workspace for the Claude Code rewrite effort",
        )

    def test_parser_has_expected_commands(self) -> None:
        # Check a few simple commands that require no extra arguments
        args = self.parser.parse_args(["summary"])
        self.assertEqual(args.command, "summary")

        args = self.parser.parse_args(["manifest"])
        self.assertEqual(args.command, "manifest")

        args = self.parser.parse_args(["tool-pool"])
        self.assertEqual(args.command, "tool-pool")

    def test_parser_commands_with_arguments(self) -> None:
        # Check a command with default arguments
        args = self.parser.parse_args(["subsystems"])
        self.assertEqual(args.command, "subsystems")
        self.assertEqual(args.limit, 32)

        # Check overriding default arguments
        args = self.parser.parse_args(["subsystems", "--limit", "10"])
        self.assertEqual(args.command, "subsystems")
        self.assertEqual(args.limit, 10)

        # Check command requiring positional arguments
        args = self.parser.parse_args(["route", "test prompt", "--limit", "2"])
        self.assertEqual(args.command, "route")
        self.assertEqual(args.prompt, "test prompt")
        self.assertEqual(args.limit, 2)

    def test_parser_invalid_command(self) -> None:
        # argparse uses sys.exit(2) for invalid arguments
        with self.assertRaises(SystemExit) as cm:
            self.parser.parse_args(["this-command-does-not-exist"])
        self.assertEqual(cm.exception.code, 2)

    def test_parser_missing_required_command(self) -> None:
        # argparse uses sys.exit(2) when a required subcommand is missing
        with self.assertRaises(SystemExit) as cm:
            self.parser.parse_args([])
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
