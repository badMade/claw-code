from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from src.system_init import build_system_init_message
from src.setup import SetupReport, WorkspaceSetup


class TestSystemInit(unittest.TestCase):
    @patch("src.system_init.get_tools")
    @patch("src.system_init.get_commands")
    @patch("src.system_init.built_in_command_names")
    @patch("src.system_init.run_setup")
    def test_build_system_init_message_trusted(
        self, mock_run_setup: MagicMock, mock_built_in: MagicMock, mock_get_commands: MagicMock, mock_get_tools: MagicMock
    ) -> None:
        # Setup mocks
        mock_setup = MagicMock(spec=SetupReport)
        mock_setup.trusted = True
        mock_workspace = MagicMock(spec=WorkspaceSetup)
        mock_workspace.startup_steps.return_value = ("step 1", "step 2")
        mock_setup.setup = mock_workspace
        mock_run_setup.return_value = mock_setup

        mock_built_in.return_value = ["cmd1", "cmd2"]
        mock_get_commands.return_value = [1, 2, 3, 4]  # Length 4
        mock_get_tools.return_value = [1, 2, 3]  # Length 3

        # Call the function
        result = build_system_init_message(trusted=True)

        # Assertions
        mock_run_setup.assert_called_once_with(trusted=True)

        expected_lines = [
            "# System Init",
            "",
            "Trusted: True",
            "Built-in command names: 2",
            "Loaded command entries: 4",
            "Loaded tool entries: 3",
            "",
            "Startup steps:",
            "- step 1",
            "- step 2",
        ]
        self.assertEqual(result, "\n".join(expected_lines))

    @patch("src.system_init.get_tools")
    @patch("src.system_init.get_commands")
    @patch("src.system_init.built_in_command_names")
    @patch("src.system_init.run_setup")
    def test_build_system_init_message_untrusted(
        self, mock_run_setup: MagicMock, mock_built_in: MagicMock, mock_get_commands: MagicMock, mock_get_tools: MagicMock
    ) -> None:
        # Setup mocks
        mock_setup = MagicMock(spec=SetupReport)
        mock_setup.trusted = False
        mock_workspace = MagicMock(spec=WorkspaceSetup)
        mock_workspace.startup_steps.return_value = ("only safe step",)
        mock_setup.setup = mock_workspace
        mock_run_setup.return_value = mock_setup

        mock_built_in.return_value = []
        mock_get_commands.return_value = []
        mock_get_tools.return_value = []

        # Call the function
        result = build_system_init_message(trusted=False)

        # Assertions
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
            "- only safe step",
        ]
        self.assertEqual(result, "\n".join(expected_lines))


if __name__ == "__main__":
    unittest.main()
