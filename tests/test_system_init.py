import unittest
from unittest import mock
from src.system_init import build_system_init_message

class TestSystemInit(unittest.TestCase):
    @mock.patch('src.system_init.get_tools')
    @mock.patch('src.system_init.get_commands')
    @mock.patch('src.system_init.built_in_command_names')
    @mock.patch('src.system_init.run_setup')
    def test_build_system_init_message_trusted(
        self,
        mock_run_setup: mock.MagicMock,
        mock_built_in_command_names: mock.MagicMock,
        mock_get_commands: mock.MagicMock,
        mock_get_tools: mock.MagicMock,
    ) -> None:
        mock_setup_report = mock.MagicMock()
        mock_setup_report.trusted = True
        mock_setup_report.setup.startup_steps.return_value = ('step 1', 'step 2')
        mock_run_setup.return_value = mock_setup_report

        mock_built_in_command_names.return_value = ['cmd1', 'cmd2']
        mock_get_commands.return_value = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        mock_get_tools.return_value = [mock.MagicMock()]

        message = build_system_init_message(trusted=True)

        expected_message = '\n'.join([
            '# System Init',
            '',
            'Trusted: True',
            'Built-in command names: 2',
            'Loaded command entries: 3',
            'Loaded tool entries: 1',
            '',
            'Startup steps:',
            '- step 1',
            '- step 2',
        ])

        self.assertEqual(message, expected_message)
        mock_run_setup.assert_called_once_with(trusted=True)

    @mock.patch('src.system_init.get_tools')
    @mock.patch('src.system_init.get_commands')
    @mock.patch('src.system_init.built_in_command_names')
    @mock.patch('src.system_init.run_setup')
    def test_build_system_init_message_untrusted(
        self,
        mock_run_setup: mock.MagicMock,
        mock_built_in_command_names: mock.MagicMock,
        mock_get_commands: mock.MagicMock,
        mock_get_tools: mock.MagicMock,
    ) -> None:
        mock_setup_report = mock.MagicMock()
        mock_setup_report.trusted = False
        mock_setup_report.setup.startup_steps.return_value = ('step A',)
        mock_run_setup.return_value = mock_setup_report

        mock_built_in_command_names.return_value = []
        mock_get_commands.return_value = []
        mock_get_tools.return_value = []

        message = build_system_init_message(trusted=False)

        expected_message = '\n'.join([
            '# System Init',
            '',
            'Trusted: False',
            'Built-in command names: 0',
            'Loaded command entries: 0',
            'Loaded tool entries: 0',
            '',
            'Startup steps:',
            '- step A',
        ])

        self.assertEqual(message, expected_message)
        mock_run_setup.assert_called_once_with(trusted=False)
