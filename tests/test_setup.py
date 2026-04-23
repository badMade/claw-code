import unittest
from pathlib import Path
from unittest.mock import patch

from src.deferred_init import DeferredInitResult
from src.prefetch import PrefetchResult
from src.setup import SetupReport, WorkspaceSetup, build_workspace_setup, run_setup


class TestSetup(unittest.TestCase):
    @patch("src.setup.sys")
    @patch("src.setup.platform")
    def test_build_workspace_setup(self, mock_platform, mock_sys):
        # Mock sys.version_info
        mock_sys.version_info = (3, 10, 4, "final", 0)
        # Mock platform functions
        mock_platform.python_implementation.return_value = "CPython"
        mock_platform.platform.return_value = (
            "Linux-5.4.0-104-generic-x86_64-with-glibc2.31"
        )

        setup = build_workspace_setup()

        self.assertIsInstance(setup, WorkspaceSetup)
        self.assertEqual(setup.python_version, "3.10.4")
        self.assertEqual(setup.implementation, "CPython")
        self.assertEqual(
            setup.platform_name, "Linux-5.4.0-104-generic-x86_64-with-glibc2.31"
        )
        self.assertEqual(setup.test_command, "python3 -m unittest discover -s tests -v")

    def test_workspace_setup_startup_steps(self):
        setup = WorkspaceSetup(
            python_version="3.10.4",
            implementation="CPython",
            platform_name="Linux",
        )
        steps = setup.startup_steps()
        self.assertEqual(
            steps,
            (
                "start top-level prefetch side effects",
                "build workspace context",
                "load mirrored command snapshot",
                "load mirrored tool snapshot",
                "prepare parity audit hooks",
                "apply trust-gated deferred init",
            ),
        )

    def test_setup_report_as_markdown(self):
        setup = WorkspaceSetup(
            python_version="3.10.4",
            implementation="CPython",
            platform_name="Linux",
        )

        prefetch1 = PrefetchResult(name="test_prefetch", started=True, detail="success")
        prefetch2 = PrefetchResult(name="another_prefetch", started=True, detail="done")

        deferred_init = DeferredInitResult(
            trusted=True,
            plugin_init=True,
            skill_init=True,
            mcp_prefetch=True,
            session_hooks=True,
        )

        report = SetupReport(
            setup=setup,
            prefetches=(prefetch1, prefetch2),
            deferred_init=deferred_init,
            trusted=True,
            cwd=Path("/test/cwd"),
        )

        markdown = report.as_markdown()

        self.assertIn("# Setup Report", markdown)
        self.assertIn("- Python: 3.10.4 (CPython)", markdown)
        self.assertIn("- Platform: Linux", markdown)
        self.assertIn("- Trusted mode: True", markdown)
        self.assertIn("- CWD: /test/cwd", markdown)
        self.assertIn("Prefetches:", markdown)
        self.assertIn("- test_prefetch: success", markdown)
        self.assertIn("- another_prefetch: done", markdown)
        self.assertIn("Deferred init:", markdown)
        self.assertIn("- plugin_init=True", markdown)

    @patch("src.setup.start_project_scan")
    @patch("src.setup.start_keychain_prefetch")
    @patch("src.setup.start_mdm_raw_read")
    @patch("src.setup.run_deferred_init")
    @patch("src.setup.build_workspace_setup")
    def test_run_setup(
        self,
        mock_build_workspace_setup,
        mock_run_deferred_init,
        mock_start_mdm_raw_read,
        mock_start_keychain_prefetch,
        mock_start_project_scan,
    ):
        mock_workspace = WorkspaceSetup(
            python_version="3.10", implementation="CPython", platform_name="Linux"
        )
        mock_build_workspace_setup.return_value = mock_workspace

        mock_deferred_init = DeferredInitResult(
            trusted=False,
            plugin_init=False,
            skill_init=False,
            mcp_prefetch=False,
            session_hooks=False,
        )
        mock_run_deferred_init.return_value = mock_deferred_init

        mock_prefetch_mdm = PrefetchResult(name="mdm", started=True, detail="ok")
        mock_start_mdm_raw_read.return_value = mock_prefetch_mdm

        mock_prefetch_keychain = PrefetchResult(
            name="keychain", started=True, detail="ok"
        )
        mock_start_keychain_prefetch.return_value = mock_prefetch_keychain

        mock_prefetch_project = PrefetchResult(
            name="project", started=True, detail="ok"
        )
        mock_start_project_scan.return_value = mock_prefetch_project

        test_cwd = Path("/tmp/test_dir")
        report = run_setup(cwd=test_cwd, trusted=False)

        mock_build_workspace_setup.assert_called_once_with()
        mock_start_mdm_raw_read.assert_called_once_with()
        mock_start_keychain_prefetch.assert_called_once_with()
        mock_start_project_scan.assert_called_once_with(test_cwd)
        mock_run_deferred_init.assert_called_once_with(trusted=False)

        self.assertEqual(report.setup, mock_workspace)
        self.assertEqual(
            report.prefetches,
            (mock_prefetch_mdm, mock_prefetch_keychain, mock_prefetch_project),
        )
        self.assertEqual(report.deferred_init, mock_deferred_init)
        self.assertFalse(report.trusted)
        self.assertEqual(report.cwd, test_cwd)

    @patch("src.setup.start_project_scan")
    @patch("src.setup.start_keychain_prefetch")
    @patch("src.setup.start_mdm_raw_read")
    @patch("src.setup.run_deferred_init")
    @patch("src.setup.build_workspace_setup")
    def test_run_setup_default_cwd(
        self,
        mock_build_workspace_setup,
        mock_run_deferred_init,
        mock_start_mdm_raw_read,
        mock_start_keychain_prefetch,
        mock_start_project_scan,
    ):
        mock_workspace = WorkspaceSetup(
            python_version="3.10", implementation="CPython", platform_name="Linux"
        )
        mock_build_workspace_setup.return_value = mock_workspace

        mock_deferred_init = DeferredInitResult(
            trusted=True,
            plugin_init=True,
            skill_init=True,
            mcp_prefetch=True,
            session_hooks=True,
        )
        mock_run_deferred_init.return_value = mock_deferred_init

        mock_prefetch_mdm = PrefetchResult(name="mdm", started=True, detail="ok")
        mock_start_mdm_raw_read.return_value = mock_prefetch_mdm

        mock_prefetch_keychain = PrefetchResult(
            name="keychain", started=True, detail="ok"
        )
        mock_start_keychain_prefetch.return_value = mock_prefetch_keychain

        mock_prefetch_project = PrefetchResult(
            name="project", started=True, detail="ok"
        )
        mock_start_project_scan.return_value = mock_prefetch_project

        # Test without passing cwd
        report = run_setup()

        expected_cwd = Path("src/setup.py").resolve().parent.parent
        mock_start_project_scan.assert_called_once_with(expected_cwd)

        self.assertEqual(report.cwd, expected_cwd)
        self.assertTrue(report.trusted)


if __name__ == "__main__":
    unittest.main()
