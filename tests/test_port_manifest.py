from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from src.port_manifest import build_port_manifest


class TestPortManifest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_file(self, path_str: str) -> Path:
        p = self.root / path_str
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        return p

    def test_empty_directory(self) -> None:
        manifest = build_port_manifest(self.root)
        self.assertEqual(manifest.src_root, self.root)
        self.assertEqual(manifest.total_python_files, 0)
        self.assertEqual(manifest.top_level_modules, ())

    def test_only_non_python_files(self) -> None:
        self.create_file("readme.md")
        self.create_file("data.json")
        self.create_file("src/config.yaml")

        manifest = build_port_manifest(self.root)
        self.assertEqual(manifest.total_python_files, 0)
        self.assertEqual(manifest.top_level_modules, ())

    def test_deeply_nested_files(self) -> None:
        self.create_file("a/b/c/d.py")
        self.create_file("a/b/e.py")
        self.create_file("f/g/h.py")

        manifest = build_port_manifest(self.root)
        self.assertEqual(manifest.total_python_files, 3)

        self.assertEqual(len(manifest.top_level_modules), 2)

        module_a = next(m for m in manifest.top_level_modules if m.name == "a")
        self.assertEqual(module_a.file_count, 2)

        module_f = next(m for m in manifest.top_level_modules if m.name == "f")
        self.assertEqual(module_f.file_count, 1)

    def test_happy_path_and_notes_mapping(self) -> None:
        self.create_file("main.py")
        self.create_file("commands.py")
        self.create_file("unmapped.py")
        self.create_file("subdir/foo.py")
        self.create_file("subdir/bar.py")

        manifest = build_port_manifest(self.root)
        self.assertEqual(manifest.total_python_files, 5)

        self.assertEqual(len(manifest.top_level_modules), 4)

        main_mod = next(m for m in manifest.top_level_modules if m.name == "main.py")
        self.assertEqual(main_mod.notes, "CLI entrypoint")

        commands_mod = next(
            m for m in manifest.top_level_modules if m.name == "commands.py"
        )
        self.assertEqual(commands_mod.notes, "command backlog metadata")

        unmapped_mod = next(
            m for m in manifest.top_level_modules if m.name == "unmapped.py"
        )
        self.assertEqual(unmapped_mod.notes, "Python port support module")

        subdir_mod = next(m for m in manifest.top_level_modules if m.name == "subdir")
        self.assertEqual(subdir_mod.notes, "Python port support module")
        self.assertEqual(subdir_mod.file_count, 2)

    def test_pycache_is_ignored(self) -> None:
        self.create_file("main.py")
        self.create_file("__pycache__/main.cpython-310.pyc")
        self.create_file("__pycache__")

        manifest = build_port_manifest(self.root)

        self.assertEqual(manifest.total_python_files, 1)
        self.assertEqual(len(manifest.top_level_modules), 1)
        self.assertEqual(manifest.top_level_modules[0].name, "main.py")


if __name__ == "__main__":
    unittest.main()
