import argparse
import unittest
import sys

from src.main import build_parser


class TestBuildParser(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_build_parser_returns_argument_parser(self):
        self.assertIsInstance(self.parser, argparse.ArgumentParser)

    def test_simple_commands(self):
        simple_commands = [
            "summary",
            "manifest",
            "parity-audit",
            "setup-report",
            "command-graph",
            "tool-pool",
            "bootstrap-graph",
        ]
        for cmd in simple_commands:
            with self.subTest(cmd=cmd):
                args = self.parser.parse_args([cmd])
                self.assertEqual(args.command, cmd)

    def test_subsystems_command(self):
        args = self.parser.parse_args(["subsystems"])
        self.assertEqual(args.command, "subsystems")
        self.assertEqual(args.limit, 32)

        args = self.parser.parse_args(["subsystems", "--limit", "10"])
        self.assertEqual(args.limit, 10)

    def test_commands_command(self):
        args = self.parser.parse_args(["commands"])
        self.assertEqual(args.command, "commands")
        self.assertEqual(args.limit, 20)
        self.assertIsNone(args.query)
        self.assertFalse(args.no_plugin_commands)
        self.assertFalse(args.no_skill_commands)

        args = self.parser.parse_args(
            [
                "commands",
                "--limit",
                "5",
                "--query",
                "test",
                "--no-plugin-commands",
                "--no-skill-commands",
            ]
        )
        self.assertEqual(args.limit, 5)
        self.assertEqual(args.query, "test")
        self.assertTrue(args.no_plugin_commands)
        self.assertTrue(args.no_skill_commands)

    def test_tools_command(self):
        args = self.parser.parse_args(["tools"])
        self.assertEqual(args.command, "tools")
        self.assertEqual(args.limit, 20)
        self.assertIsNone(args.query)
        self.assertFalse(args.simple_mode)
        self.assertFalse(args.no_mcp)
        self.assertEqual(args.deny_tool, [])
        self.assertEqual(args.deny_prefix, [])

        args = self.parser.parse_args(
            [
                "tools",
                "--limit",
                "5",
                "--query",
                "test",
                "--simple-mode",
                "--no-mcp",
                "--deny-tool",
                "tool1",
                "--deny-tool",
                "tool2",
                "--deny-prefix",
                "pref1",
            ]
        )
        self.assertEqual(args.limit, 5)
        self.assertEqual(args.query, "test")
        self.assertTrue(args.simple_mode)
        self.assertTrue(args.no_mcp)
        self.assertEqual(args.deny_tool, ["tool1", "tool2"])
        self.assertEqual(args.deny_prefix, ["pref1"])

    def test_route_command(self):
        args = self.parser.parse_args(["route", "my prompt"])
        self.assertEqual(args.command, "route")
        self.assertEqual(args.prompt, "my prompt")
        self.assertEqual(args.limit, 5)

        args = self.parser.parse_args(["route", "my prompt", "--limit", "10"])
        self.assertEqual(args.limit, 10)

    def test_bootstrap_command(self):
        args = self.parser.parse_args(["bootstrap", "my prompt"])
        self.assertEqual(args.command, "bootstrap")
        self.assertEqual(args.prompt, "my prompt")
        self.assertEqual(args.limit, 5)

        args = self.parser.parse_args(["bootstrap", "my prompt", "--limit", "10"])
        self.assertEqual(args.limit, 10)

    def test_turn_loop_command(self):
        args = self.parser.parse_args(["turn-loop", "my prompt"])
        self.assertEqual(args.command, "turn-loop")
        self.assertEqual(args.prompt, "my prompt")
        self.assertEqual(args.limit, 5)
        self.assertEqual(args.max_turns, 3)
        self.assertFalse(args.structured_output)

        args = self.parser.parse_args(
            [
                "turn-loop",
                "my prompt",
                "--limit",
                "10",
                "--max-turns",
                "5",
                "--structured-output",
            ]
        )
        self.assertEqual(args.limit, 10)
        self.assertEqual(args.max_turns, 5)
        self.assertTrue(args.structured_output)

    def test_single_arg_commands(self):
        commands = [
            ("flush-transcript", "prompt"),
            ("load-session", "session_id"),
            ("remote-mode", "target"),
            ("ssh-mode", "target"),
            ("teleport-mode", "target"),
            ("direct-connect-mode", "target"),
            ("deep-link-mode", "target"),
            ("show-command", "name"),
            ("show-tool", "name"),
        ]

        for cmd, arg_name in commands:
            with self.subTest(cmd=cmd):
                args = self.parser.parse_args([cmd, "test_value"])
                self.assertEqual(args.command, cmd)
                self.assertEqual(getattr(args, arg_name), "test_value")

    def test_exec_command(self):
        args = self.parser.parse_args(["exec-command", "cmd_name", "cmd_prompt"])
        self.assertEqual(args.command, "exec-command")
        self.assertEqual(args.name, "cmd_name")
        self.assertEqual(args.prompt, "cmd_prompt")

    def test_exec_tool(self):
        args = self.parser.parse_args(["exec-tool", "tool_name", "tool_payload"])
        self.assertEqual(args.command, "exec-tool")
        self.assertEqual(args.name, "tool_name")
        self.assertEqual(args.payload, "tool_payload")

    def test_missing_command_raises_error(self):
        # Prevent argparse from printing to stderr during the test
        with self.assertRaises(SystemExit):
            # parse_args should exit with status 2 if required arguments are missing
            # However, we need to suppress stderr so the test output is clean
            sys_stderr = sys.stderr
            try:
                import io

                sys.stderr = io.StringIO()
                self.parser.parse_args([])
            finally:
                sys.stderr = sys_stderr

    def test_missing_required_arguments_raises_error(self):
        commands_needing_args = [
            "route",
            "bootstrap",
            "turn-loop",
            "flush-transcript",
            "load-session",
            "remote-mode",
            "ssh-mode",
            "teleport-mode",
            "direct-connect-mode",
            "deep-link-mode",
            "show-command",
            "show-tool",
            "exec-command",
            "exec-tool",
        ]

        for cmd in commands_needing_args:
            with self.subTest(cmd=cmd):
                with self.assertRaises(SystemExit):
                    sys_stderr = sys.stderr
                    try:
                        import io

                        sys.stderr = io.StringIO()
                        self.parser.parse_args([cmd])
                    finally:
                        sys.stderr = sys_stderr


if __name__ == "__main__":
    unittest.main()
