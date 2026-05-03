from __future__ import annotations

import unittest

from src.commands import PORTED_COMMANDS, find_commands


class TestCommands(unittest.TestCase):
    def test_find_commands_excludes_responsibility_boilerplate(self) -> None:
        matches = find_commands("typescript", limit=len(PORTED_COMMANDS))
        self.assertEqual(matches, [])


if __name__ == '__main__':
    unittest.main()
