from __future__ import annotations

import unittest
from src.commands import get_command, PORTED_COMMANDS

class TestCommands(unittest.TestCase):
    def test_get_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        first_command = PORTED_COMMANDS[0]

        # Normal operation: Exact match
        self.assertEqual(get_command(first_command.name), first_command)

        # Missing keys: Unknown command
        self.assertIsNone(get_command("NonExistentCommandNamexyz123"))

        # Edge cases: Case-insensitive match
        self.assertEqual(get_command(first_command.name.lower()), first_command)
        self.assertEqual(get_command(first_command.name.upper()), first_command)

        # Edge cases: Empty string
        self.assertIsNone(get_command(""))

if __name__ == '__main__':
    unittest.main()
