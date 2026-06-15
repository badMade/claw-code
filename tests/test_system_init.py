import unittest
from unittest.mock import patch, MagicMock
from src.system_init import build_system_init_message

class TestSystemInit(unittest.TestCase):

    @patch('src.system_init.built_in_command_names')
    @patch('src.system_init.get_commands')
    @patch('src.system_init.get_tools')
    @patch('src.system_init.run_setup')
    def test_build_system_init_message_trusted_true(
        self, mock_run_setup, mock_get_tools, mock_get_commands, mock_built_in_command_names
    ):
        # Setup mocks
        mock_setup_report = MagicMock()
        mock_setup_report.trusted = True
        mock_setup_report.setup.startup_steps.return_value = ("step 1", "step 2")
        mock_run_setup.return_value = mock_setup_report

        mock_get_commands.return_value = [1, 2, 3] # length 3
        mock_get_tools.return_value = [1, 2, 3, 4, 5] # length 5
        mock_built_in_command_names.return_value = {"cmd1", "cmd2"} # length 2

        # Call function
        result = build_system_init_message(trusted=True)

        # Assertions
        mock_run_setup.assert_called_once_with(trusted=True)

        expected_lines = [
            '# System Init',
            '',
            'Trusted: True',
            'Built-in command names: 2',
            'Loaded command entries: 3',
            'Loaded tool entries: 5',
            '',
            'Startup steps:',
            '- step 1',
            '- step 2',
        ]
        expected_output = '\n'.join(expected_lines)

        self.assertEqual(result, expected_output)

    @patch('src.system_init.built_in_command_names')
    @patch('src.system_init.get_commands')
    @patch('src.system_init.get_tools')
    @patch('src.system_init.run_setup')
    def test_build_system_init_message_trusted_false(
        self, mock_run_setup, mock_get_tools, mock_get_commands, mock_built_in_command_names
    ):
        # Setup mocks
        mock_setup_report = MagicMock()
        mock_setup_report.trusted = False
        mock_setup_report.setup.startup_steps.return_value = ("step A",)
        mock_run_setup.return_value = mock_setup_report

        mock_get_commands.return_value = [] # length 0
        mock_get_tools.return_value = [1] # length 1
        mock_built_in_command_names.return_value = {"cmd"} # length 1

        # Call function
        result = build_system_init_message(trusted=False)

        # Assertions
        mock_run_setup.assert_called_once_with(trusted=False)

        expected_lines = [
            '# System Init',
            '',
            'Trusted: False',
            'Built-in command names: 1',
            'Loaded command entries: 0',
            'Loaded tool entries: 1',
            '',
            'Startup steps:',
            '- step A',
        ]
        expected_output = '\n'.join(expected_lines)

        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
