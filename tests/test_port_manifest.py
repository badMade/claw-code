import unittest
from pathlib import Path
import tempfile

from src.port_manifest import build_port_manifest, PortManifest
from src.models import Subsystem

class TestPortManifest(unittest.TestCase):
    def test_build_port_manifest_default(self):
        manifest = build_port_manifest()
        self.assertIsInstance(manifest, PortManifest)
        self.assertTrue(manifest.total_python_files > 0)
        self.assertTrue(len(manifest.top_level_modules) > 0)

    def test_build_port_manifest_custom_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create some mock files
            (tmp_path / 'main.py').touch()
            (tmp_path / '__init__.py').touch()
            (tmp_path / 'other.txt').touch()  # Should be ignored (not .py)

            # Create a module subdirectory
            module_dir = tmp_path / 'module_a'
            module_dir.mkdir()
            (module_dir / '__init__.py').touch()
            (module_dir / 'a.py').touch()

            # Create a __pycache__ directory with a .py file
            pycache_dir = tmp_path / '__pycache__'
            pycache_dir.mkdir()
            (pycache_dir / 'compiled.py').touch()

            # Create a file literally named __pycache__ inside another module to test ignore logic
            (module_dir / '__pycache__').touch()

            manifest = build_port_manifest(src_root=tmp_path)

            # total files should be 5 (.py files) because it uses root.rglob('*.py')
            # main.py, __init__.py, module_a/__init__.py, module_a/a.py, __pycache__/compiled.py
            # Note: The codebase counter explicitly ignores path.name == '__pycache__'
            # But the 'total files' calculation is just len(files) from root.rglob('*.py')
            # so the total_python_files logic includes '__pycache__/compiled.py'
            self.assertEqual(manifest.total_python_files, 5)

            # check the counter logic
            module_names = {m.name for m in manifest.top_level_modules}
            self.assertIn('main.py', module_names)
            self.assertIn('__init__.py', module_names)
            self.assertIn('module_a', module_names)
            # The current counter logic counts paths.relative_to(root).parts[0].
            # So __pycache__ should also be a module name because compiled.py is inside it
            # The codebase logic filters "path.name != '__pycache__'".
            # `path.name` of '__pycache__/compiled.py' is 'compiled.py'
            # So compiled.py is counted under __pycache__ part[0]
            self.assertIn('__pycache__', module_names)

            # check notes logic in most_common modules
            main_module = next(m for m in manifest.top_level_modules if m.name == 'main.py')
            self.assertEqual(main_module.notes, 'CLI entrypoint')
            self.assertEqual(main_module.file_count, 1)

            init_module = next(m for m in manifest.top_level_modules if m.name == '__init__.py')
            self.assertEqual(init_module.notes, 'package export surface')

            module_a = next(m for m in manifest.top_level_modules if m.name == 'module_a')
            self.assertEqual(module_a.file_count, 2)
            self.assertEqual(module_a.notes, 'Python port support module')

    def test_port_manifest_to_markdown(self):
        manifest = PortManifest(
            src_root=Path('/test/root'),
            total_python_files=42,
            top_level_modules=(
                Subsystem(name='test_module', path='src/test_module', file_count=10, notes='Test notes'),
            )
        )
        md = manifest.to_markdown()
        self.assertIn('Port root: `/test/root`', md)
        self.assertIn('Total Python files: **42**', md)
        self.assertIn('- `test_module` (10 files) — Test notes', md)

if __name__ == '__main__':
    unittest.main()
