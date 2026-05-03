import argparse
import unittest
import sys
from io import StringIO
from src.main import build_parser

class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def test_build_parser_returns_argument_parser(self) -> None:
        self.assertIsInstance(self.parser, argparse.ArgumentParser)
        self.assertEqual(self.parser.description, 'Python porting workspace for the Claude Code rewrite effort')

    def test_build_parser_parses_summary_command(self) -> None:
        args = self.parser.parse_args(['summary'])
        self.assertEqual(args.command, 'summary')

    def test_build_parser_parses_manifest_command(self) -> None:
        args = self.parser.parse_args(['manifest'])
        self.assertEqual(args.command, 'manifest')

    def test_build_parser_parses_parity_audit_command(self) -> None:
        args = self.parser.parse_args(['parity-audit'])
        self.assertEqual(args.command, 'parity-audit')

    def test_build_parser_fails_without_command(self) -> None:
        # Redirect stderr to suppress argparse errors during test
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                self.parser.parse_args([])
            self.assertEqual(cm.exception.code, 2)
        finally:
            sys.stderr = original_stderr

    def test_build_parser_fails_with_unknown_command(self) -> None:
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                self.parser.parse_args(['unknown_command_xyz'])
            self.assertEqual(cm.exception.code, 2)
        finally:
            sys.stderr = original_stderr

if __name__ == '__main__':
    unittest.main()
