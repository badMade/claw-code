from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.system_init import build_system_init_message


class TestSystemInit(unittest.TestCase):
    @patch("src.system_init.run_setup")
    @patch("src.system_init.get_commands")
    @patch("src.system_init.get_tools")
    @patch("src.system_init.built_in_command_names")
    def test_build_system_init_message(
        self,
        mock_built_in_command_names: MagicMock,
        mock_get_tools: MagicMock,
        mock_get_commands: MagicMock,
        mock_run_setup: MagicMock,
    ) -> None:
        # Arrange
        mock_setup_report = MagicMock()
        mock_setup_report.trusted = True
        mock_setup_report.setup.startup_steps.return_value = ("step 1", "step 2")
        mock_run_setup.return_value = mock_setup_report

        mock_built_in_command_names.return_value = ["cmd1", "cmd2"]
        mock_get_commands.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_get_tools.return_value = [MagicMock()]

        # Act
        message = build_system_init_message(trusted=True)

        # Assert
        mock_run_setup.assert_called_once_with(trusted=True)

        expected_lines = [
            "# System Init",
            "",
            "Trusted: True",
            "Built-in command names: 2",
            "Loaded command entries: 3",
            "Loaded tool entries: 1",
            "",
            "Startup steps:",
            "- step 1",
            "- step 2",
        ]
        expected_message = "\n".join(expected_lines)
        self.assertEqual(message, expected_message)

    @patch("src.system_init.run_setup")
    @patch("src.system_init.get_commands")
    @patch("src.system_init.get_tools")
    @patch("src.system_init.built_in_command_names")
    def test_build_system_init_message_untrusted(
        self,
        mock_built_in_command_names: MagicMock,
        mock_get_tools: MagicMock,
        mock_get_commands: MagicMock,
        mock_run_setup: MagicMock,
    ) -> None:
        # Arrange
        mock_setup_report = MagicMock()
        mock_setup_report.trusted = False
        mock_setup_report.setup.startup_steps.return_value = ("step 1",)
        mock_run_setup.return_value = mock_setup_report

        mock_built_in_command_names.return_value = []
        mock_get_commands.return_value = []
        mock_get_tools.return_value = []

        # Act
        message = build_system_init_message(trusted=False)

        # Assert
        mock_run_setup.assert_called_once_with(trusted=False)

        expected_lines = [
            "# System Init",
            "",
            "Trusted: False",
            "Built-in command names: 0",
            "Loaded command entries: 0",
            "Loaded tool entries: 0",
            "",
            "Startup steps:",
            "- step 1",
        ]
        expected_message = "\n".join(expected_lines)
        self.assertEqual(message, expected_message)


if __name__ == "__main__":
    unittest.main()
