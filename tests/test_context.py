from __future__ import annotations

import unittest
from unittest import mock
from pathlib import Path

from src.context import PortContext, build_port_context, render_context


class TestContext(unittest.TestCase):
    def test_build_port_context_with_base(self) -> None:
        base = Path("/fake/base")

        # We need to patch Path.rglob and Path.exists so we don't hit the real filesystem
        with (
            mock.patch("pathlib.Path.rglob") as mock_rglob,
            mock.patch("pathlib.Path.exists") as mock_exists,
        ):
            # Setup the mocks
            def fake_rglob(pattern):
                if pattern == "*.py":
                    # return a couple of fake paths that simulate files
                    fake_file1 = mock.MagicMock(spec=Path)
                    fake_file1.is_file.return_value = True
                    fake_file2 = mock.MagicMock(spec=Path)
                    fake_file2.is_file.return_value = True
                    return [fake_file1, fake_file2]
                elif pattern == "*":
                    fake_file = mock.MagicMock(spec=Path)
                    fake_file.is_file.return_value = True
                    return [fake_file]
                return []

            mock_rglob.side_effect = fake_rglob
            mock_exists.return_value = True

            context = build_port_context(base)

            self.assertEqual(context.source_root, base / "src")
            self.assertEqual(context.tests_root, base / "tests")
            self.assertEqual(context.assets_root, base / "assets")
            self.assertEqual(
                context.archive_root,
                base / "archive" / "claude_code_ts_snapshot" / "src",
            )
            self.assertEqual(context.python_file_count, 2)
            self.assertEqual(context.test_file_count, 2)
            self.assertEqual(context.asset_file_count, 1)
            self.assertTrue(context.archive_available)

    def test_build_port_context_without_base(self) -> None:
        # We need to patch Path.rglob and Path.exists so we don't hit the real filesystem
        with (
            mock.patch("pathlib.Path.rglob") as mock_rglob,
            mock.patch("pathlib.Path.exists") as mock_exists,
        ):
            # Setup the mocks
            def fake_rglob(pattern):
                return []

            mock_rglob.side_effect = fake_rglob
            mock_exists.return_value = False

            context = build_port_context()

            self.assertIsInstance(context.source_root, Path)
            self.assertIsInstance(context.tests_root, Path)
            self.assertIsInstance(context.assets_root, Path)
            self.assertIsInstance(context.archive_root, Path)
            self.assertEqual(context.python_file_count, 0)
            self.assertEqual(context.test_file_count, 0)
            self.assertEqual(context.asset_file_count, 0)
            self.assertFalse(context.archive_available)

    def test_render_context(self) -> None:
        context = PortContext(
            source_root=Path("/fake/src"),
            tests_root=Path("/fake/tests"),
            assets_root=Path("/fake/assets"),
            archive_root=Path("/fake/archive"),
            python_file_count=10,
            test_file_count=5,
            asset_file_count=2,
            archive_available=True,
        )

        output = render_context(context)

        self.assertIn("Source root: /fake/src", output)
        self.assertIn("Test root: /fake/tests", output)
        self.assertIn("Assets root: /fake/assets", output)
        self.assertIn("Archive root: /fake/archive", output)
        self.assertIn("Python files: 10", output)
        self.assertIn("Test files: 5", output)
        self.assertIn("Assets: 2", output)
        self.assertIn("Archive available: True", output)


if __name__ == "__main__":
    unittest.main()
