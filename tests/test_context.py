from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
from src.context import PortContext, build_port_context, render_context


class TestContext(unittest.TestCase):
    def test_build_port_context_happy_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)

            # Setup standard directory structure
            (base / "src").mkdir()
            (base / "tests").mkdir()
            (base / "assets").mkdir()

            archive_src = base / "archive" / "claude_code_ts_snapshot" / "src"
            archive_src.mkdir(parents=True)

            # Add files to src
            (base / "src" / "file1.py").touch()
            (base / "src" / "file2.py").touch()
            (base / "src" / "not_python.txt").touch()

            # Add files to tests
            (base / "tests" / "test1.py").touch()
            (base / "tests" / "test_not_python.txt").touch()

            # Add files to assets
            (base / "assets" / "image.png").touch()
            (base / "assets" / "data.json").touch()

            context = build_port_context(base)

            self.assertEqual(context.source_root, base / "src")
            self.assertEqual(context.tests_root, base / "tests")
            self.assertEqual(context.assets_root, base / "assets")
            self.assertEqual(context.archive_root, archive_src)

            self.assertEqual(context.python_file_count, 2)
            self.assertEqual(context.test_file_count, 1)
            self.assertEqual(context.asset_file_count, 2)
            self.assertTrue(context.archive_available)

    def test_build_port_context_empty_repo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)

            # Create just the base directory, no subdirectories or files
            context = build_port_context(base)

            self.assertEqual(context.source_root, base / "src")
            self.assertEqual(context.tests_root, base / "tests")
            self.assertEqual(context.assets_root, base / "assets")
            self.assertEqual(
                context.archive_root,
                base / "archive" / "claude_code_ts_snapshot" / "src",
            )

            self.assertEqual(context.python_file_count, 0)
            self.assertEqual(context.test_file_count, 0)
            self.assertEqual(context.asset_file_count, 0)
            self.assertFalse(context.archive_available)

    def test_render_context(self):
        context = PortContext(
            source_root=Path("/mock/src"),
            tests_root=Path("/mock/tests"),
            assets_root=Path("/mock/assets"),
            archive_root=Path("/mock/archive/claude_code_ts_snapshot/src"),
            python_file_count=42,
            test_file_count=10,
            asset_file_count=5,
            archive_available=True,
        )

        rendered = render_context(context)

        self.assertIn("Source root: /mock/src", rendered)
        self.assertIn("Test root: /mock/tests", rendered)
        self.assertIn("Assets root: /mock/assets", rendered)
        self.assertIn(
            "Archive root: /mock/archive/claude_code_ts_snapshot/src", rendered
        )
        self.assertIn("Python files: 42", rendered)
        self.assertIn("Test files: 10", rendered)
        self.assertIn("Assets: 5", rendered)
        self.assertIn("Archive available: True", rendered)


if __name__ == "__main__":
    unittest.main()
