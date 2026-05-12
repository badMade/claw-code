from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from src.setup import run_setup, WorkspaceSetup
from src.prefetch import PrefetchResult
from src.deferred_init import DeferredInitResult


class SetupTests(unittest.TestCase):
    @mock.patch('src.setup.run_deferred_init')
    @mock.patch('src.setup.build_workspace_setup')
    @mock.patch('src.setup.start_mdm_raw_read')
    @mock.patch('src.setup.start_keychain_prefetch')
    @mock.patch('src.setup.start_project_scan')
    def test_run_setup_generates_report(
        self,
        mock_start_project_scan: mock.MagicMock,
        mock_start_keychain_prefetch: mock.MagicMock,
        mock_start_mdm_raw_read: mock.MagicMock,
        mock_build_workspace_setup: mock.MagicMock,
        mock_run_deferred_init: mock.MagicMock,
    ) -> None:
        # Arrange
        mock_mdm_result = PrefetchResult('mdm', True, 'mdm details')
        mock_keychain_result = PrefetchResult('keychain', True, 'keychain details')
        mock_project_result = PrefetchResult('project', True, 'project details')

        mock_start_mdm_raw_read.return_value = mock_mdm_result
        mock_start_keychain_prefetch.return_value = mock_keychain_result
        mock_start_project_scan.return_value = mock_project_result

        mock_workspace = WorkspaceSetup(
            python_version="3.9.0",
            implementation="CPython",
            platform_name="Linux",
        )
        mock_build_workspace_setup.return_value = mock_workspace

        trusted_flag = False
        mock_deferred_init = DeferredInitResult(
            trusted=trusted_flag,
            plugin_init=False,
            skill_init=False,
            mcp_prefetch=False,
            session_hooks=False,
        )
        mock_run_deferred_init.return_value = mock_deferred_init

        test_cwd = Path('/dummy/path')

        # Act
        report = run_setup(cwd=test_cwd, trusted=trusted_flag)

        # Assert
        self.assertEqual(report.cwd, test_cwd)
        self.assertEqual(report.trusted, trusted_flag)

        # Check that setup and deferred_init are correctly populated
        self.assertEqual(report.setup, mock_workspace)
        self.assertEqual(report.deferred_init, mock_deferred_init)

        # Check that prefetches are aggregated correctly
        self.assertEqual(
            report.prefetches,
            (mock_mdm_result, mock_keychain_result, mock_project_result)
        )

        # Verify mocks were called correctly
        mock_start_mdm_raw_read.assert_called_once()
        mock_start_keychain_prefetch.assert_called_once()
        mock_start_project_scan.assert_called_once_with(test_cwd)
        mock_build_workspace_setup.assert_called_once()
        mock_run_deferred_init.assert_called_once_with(trusted=trusted_flag)

if __name__ == '__main__':
    unittest.main()
