from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from src._archive_helper import load_archive_metadata


class TestArchiveHelper(unittest.TestCase):
    def test_load_archive_metadata_success(self) -> None:
        # Load a known, real package "cli"
        metadata = load_archive_metadata("cli")
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get("package_name"), "cli")
        self.assertEqual(metadata.get("archive_name"), "cli")
        self.assertIn("module_count", metadata)

    def test_load_archive_metadata_not_found(self) -> None:
        # Test loading a non-existent package
        with self.assertRaises(FileNotFoundError):
            load_archive_metadata("this_package_does_not_exist_123")

    @patch("src._archive_helper.Path.read_text")
    def test_load_archive_metadata_invalid_json(self, mock_read_text) -> None:
        # Mock read_text to return invalid json
        mock_read_text.return_value = "{ invalid json"
        with self.assertRaises(json.JSONDecodeError):
            load_archive_metadata("dummy_package")


if __name__ == "__main__":
    unittest.main()
