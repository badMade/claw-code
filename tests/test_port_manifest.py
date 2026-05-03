from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.models import Subsystem
from src.port_manifest import DEFAULT_SRC_ROOT, PortManifest, build_port_manifest


class TestPortManifest(unittest.TestCase):
    def test_to_markdown(self) -> None:
        manifest = PortManifest(
            src_root=Path("/fake/root"),
            total_python_files=10,
            top_level_modules=(
                Subsystem(
                    name="module1", path="src/module1", file_count=5, notes="note1"
                ),
                Subsystem(
                    name="module2", path="src/module2", file_count=5, notes="note2"
                ),
            ),
        )
        md = manifest.to_markdown()
        self.assertIn("Port root: `/fake/root`", md)
        self.assertIn("Total Python files: **10**", md)
        self.assertIn("- `module1` (5 files) — note1", md)
        self.assertIn("- `module2` (5 files) — note2", md)

    def test_build_port_manifest_default(self) -> None:
        manifest = build_port_manifest()
        self.assertEqual(manifest.src_root, DEFAULT_SRC_ROOT)
        self.assertGreaterEqual(manifest.total_python_files, 0)
        self.assertTrue(isinstance(manifest.top_level_modules, tuple))
        self.assertTrue(len(manifest.top_level_modules) > 0)

    def test_build_port_manifest_with_custom_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create some python files
            (tmp_path / "main.py").touch()
            (tmp_path / "commands.py").touch()

            # Create a subdirectory with python files
            sub_dir = tmp_path / "utils"
            sub_dir.mkdir()
            (sub_dir / "helpers.py").touch()
            (sub_dir / "__init__.py").touch()

            # Create a non-python file
            (tmp_path / "README.md").touch()

            # Create a file that should be excluded by the path.name != '__pycache__' check if it matched
            (tmp_path / "__pycache__").touch()

            manifest = build_port_manifest(src_root=tmp_path)

            self.assertEqual(manifest.src_root, tmp_path)
            self.assertEqual(manifest.total_python_files, 4)

            module_names = [m.name for m in manifest.top_level_modules]
            self.assertIn("utils", module_names)
            self.assertIn("main.py", module_names)
            self.assertIn("commands.py", module_names)

            utils_module = next(
                m for m in manifest.top_level_modules if m.name == "utils"
            )
            self.assertEqual(utils_module.file_count, 2)
            self.assertEqual(utils_module.notes, "Python port support module")

            main_module = next(
                m for m in manifest.top_level_modules if m.name == "main.py"
            )
            self.assertEqual(main_module.file_count, 1)
            self.assertEqual(main_module.notes, "CLI entrypoint")


if __name__ == "__main__":
    unittest.main()
