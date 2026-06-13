from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.setup import build_workspace_setup, WorkspaceSetup


class TestSetup(unittest.TestCase):
    def test_build_workspace_setup_structure(self) -> None:
        setup = build_workspace_setup()

        self.assertIsInstance(setup, WorkspaceSetup)
        self.assertIsInstance(setup.python_version, str)
        self.assertIsInstance(setup.implementation, str)
        self.assertIsInstance(setup.platform_name, str)

        self.assertTrue(len(setup.python_version) > 0)
        self.assertTrue(len(setup.implementation) > 0)
        self.assertTrue(len(setup.platform_name) > 0)

    @patch("src.setup.platform")
    @patch("src.setup.sys")
    def test_build_workspace_setup_values(
        self, mock_sys: MagicMock, mock_platform: MagicMock
    ) -> None:
        mock_sys.version_info = (3, 10, 4, "final", 0)
        mock_platform.python_implementation.return_value = "CPython"
        mock_platform.platform.return_value = (
            "Linux-5.15.0-60-generic-x86_64-with-glibc2.35"
        )

        setup = build_workspace_setup()

        self.assertEqual(setup.python_version, "3.10.4")
        self.assertEqual(setup.implementation, "CPython")
        self.assertEqual(
            setup.platform_name, "Linux-5.15.0-60-generic-x86_64-with-glibc2.35"
        )


if __name__ == "__main__":
    unittest.main()
