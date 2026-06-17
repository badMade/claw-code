from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
import shutil

from src.port_manifest import build_port_manifest, PortManifest
from src.models import Subsystem


class TestPortManifest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for each test
        self.test_dir = tempfile.mkdtemp()
        self.root_path = Path(self.test_dir)

    def tearDown(self):
        # Clean up the temporary directory after each test
        shutil.rmtree(self.test_dir)

    def test_build_port_manifest_empty(self):
        manifest = build_port_manifest(self.root_path)
        self.assertEqual(manifest.src_root, self.root_path)
        self.assertEqual(manifest.total_python_files, 0)
        self.assertEqual(manifest.top_level_modules, ())

    def test_build_port_manifest_ignores_non_python(self):
        (self.root_path / "test.txt").touch()
        (self.root_path / "README.md").touch()
        manifest = build_port_manifest(self.root_path)
        self.assertEqual(manifest.total_python_files, 0)

    def test_build_port_manifest_ignores_pycache(self):
        # Create __pycache__ directory with a .py file
        pycache_dir = self.root_path / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.py").touch()

        manifest = build_port_manifest(self.root_path)
        self.assertEqual(manifest.total_python_files, 0)

    def test_build_port_manifest_standard(self):
        # Setup files
        (self.root_path / "main.py").touch()
        (self.root_path / "__init__.py").touch()

        # module_a
        module_a = self.root_path / "module_a"
        module_a.mkdir()
        (module_a / "foo.py").touch()
        (module_a / "bar.py").touch()

        # module_b (nested)
        module_b = self.root_path / "module_b"
        module_b.mkdir()
        module_b_nested = module_b / "nested"
        module_b_nested.mkdir()
        (module_b_nested / "baz.py").touch()

        manifest = build_port_manifest(self.root_path)

        self.assertEqual(manifest.src_root, self.root_path)
        self.assertEqual(manifest.total_python_files, 5)

        self.assertEqual(len(manifest.top_level_modules), 4)

        module_names = {m.name: m for m in manifest.top_level_modules}

        self.assertIn("module_a", module_names)
        self.assertEqual(module_names["module_a"].file_count, 2)

        self.assertIn("module_b", module_names)
        self.assertEqual(module_names["module_b"].file_count, 1)

        self.assertIn("main.py", module_names)
        self.assertEqual(module_names["main.py"].file_count, 1)
        self.assertEqual(module_names["main.py"].notes, "CLI entrypoint")

        self.assertIn("__init__.py", module_names)
        self.assertEqual(module_names["__init__.py"].file_count, 1)
        self.assertEqual(module_names["__init__.py"].notes, "package export surface")

    def test_port_manifest_to_markdown(self):
        manifest = PortManifest(
            src_root=Path("/test/root"),
            total_python_files=3,
            top_level_modules=(
                Subsystem(
                    name="main.py",
                    path="src/main.py",
                    file_count=1,
                    notes="CLI entrypoint",
                ),
                Subsystem(
                    name="module_a",
                    path="src/module_a",
                    file_count=2,
                    notes="Python port support module",
                ),
            ),
        )

        expected_markdown = (
            "Port root: `/test/root`\n"
            "Total Python files: **3**\n"
            "\n"
            "Top-level Python modules:\n"
            "- `main.py` (1 files) — CLI entrypoint\n"
            "- `module_a` (2 files) — Python port support module"
        )

        self.assertEqual(manifest.to_markdown(), expected_markdown)


if __name__ == "__main__":
    unittest.main()
