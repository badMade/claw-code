from __future__ import annotations

import unittest
from src.commands import get_command, PORTED_COMMANDS


class TestCommands(unittest.TestCase):
    def test_get_command(self) -> None:
        if not PORTED_COMMANDS:
            self.skipTest("No commands available in snapshot")

        # Find a command that appears multiple times to test first-match priority
        seen_names = set()
        duplicate_name = None
        for cmd in PORTED_COMMANDS:
            if cmd.name in seen_names:
                duplicate_name = cmd.name
                break
            seen_names.add(cmd.name)

        first_tool = PORTED_COMMANDS[0]

        # Exact match
        self.assertEqual(get_command(first_tool.name), first_tool)

        # Case-insensitive match
        self.assertEqual(get_command(first_tool.name.lower()), first_tool)
        self.assertEqual(get_command(first_tool.name.upper()), first_tool)

        # Unknown command
        self.assertIsNone(get_command("NonExistentCommandNamexyz123"))

        # First-match priority for duplicates
        if duplicate_name:
            # Find the first occurrence in the snapshot manually
            first_occurrence = next(c for c in PORTED_COMMANDS if c.name.lower() == duplicate_name.lower())
            # Find the last occurrence in the snapshot manually
            last_occurrence = next(c for c in reversed(PORTED_COMMANDS) if c.name.lower() == duplicate_name.lower())

            # Ensure the duplicate actually points to different modules
            if first_occurrence is not last_occurrence:
                # get_command should return the first occurrence
                self.assertEqual(get_command(duplicate_name), first_occurrence)
                self.assertNotEqual(get_command(duplicate_name), last_occurrence)


if __name__ == '__main__':
    unittest.main()
