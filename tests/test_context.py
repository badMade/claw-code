from __future__ import annotations

import unittest
from pathlib import Path
import tempfile

from src.context import build_port_context


class TestContext(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_build_port_context_with_base(self) -> None:
        # Create directories
        src_dir = self.base_path / "src"
        tests_dir = self.base_path / "tests"
        assets_dir = self.base_path / "assets"
        archive_dir = self.base_path / "archive" / "claude_code_ts_snapshot" / "src"

        src_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)
        assets_dir.mkdir(parents=True)
        archive_dir.mkdir(parents=True)

        # Create dummy files
        (src_dir / "file1.py").touch()
        (src_dir / "file2.py").touch()
        (src_dir / "not_py.txt").touch()

        (tests_dir / "test1.py").touch()

        (assets_dir / "asset1.png").touch()
        (assets_dir / "asset2.jpg").touch()

        context = build_port_context(base=self.base_path)

        self.assertEqual(context.source_root, src_dir)
        self.assertEqual(context.tests_root, tests_dir)
        self.assertEqual(context.assets_root, assets_dir)
        self.assertEqual(context.archive_root, archive_dir)

        self.assertEqual(context.python_file_count, 2)
        self.assertEqual(context.test_file_count, 1)
        self.assertEqual(context.asset_file_count, 2)
        self.assertTrue(context.archive_available)

    def test_build_port_context_without_base(self) -> None:
        context = build_port_context()

        expected_root = Path(__file__).resolve().parent.parent
        self.assertEqual(context.source_root, expected_root / "src")
        self.assertEqual(context.tests_root, expected_root / "tests")
        self.assertEqual(context.assets_root, expected_root / "assets")
        self.assertEqual(
            context.archive_root,
            expected_root / "archive" / "claude_code_ts_snapshot" / "src",
        )

        self.assertIsInstance(context.python_file_count, int)
        self.assertGreaterEqual(context.python_file_count, 0)

        self.assertIsInstance(context.test_file_count, int)
        self.assertGreaterEqual(context.test_file_count, 0)

        self.assertIsInstance(context.asset_file_count, int)
        self.assertGreaterEqual(context.asset_file_count, 0)

        self.assertIsInstance(context.archive_available, bool)

    def test_build_port_context_no_archive(self) -> None:
        # Create directories except archive
        src_dir = self.base_path / "src"
        tests_dir = self.base_path / "tests"
        assets_dir = self.base_path / "assets"

        src_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)
        assets_dir.mkdir(parents=True)

        context = build_port_context(base=self.base_path)

        self.assertFalse(context.archive_available)


if __name__ == "__main__":
    unittest.main()
