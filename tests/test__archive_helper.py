from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from src._archive_helper import load_archive_metadata


class TestArchiveHelper(unittest.TestCase):
    @patch("src._archive_helper.Path.read_text")
    def test_load_archive_metadata_success(self, mock_read_text):
        """Test that load_archive_metadata correctly loads and parses JSON."""
        mock_read_text.return_value = '{"key": "value", "id": 123}'

        result = load_archive_metadata("test_package")

        self.assertEqual(result, {"key": "value", "id": 123})
        mock_read_text.assert_called_once()

    @patch("src._archive_helper.Path.read_text")
    def test_load_archive_metadata_file_not_found(self, mock_read_text):
        """Test that load_archive_metadata raises FileNotFoundError when the file is missing."""
        mock_read_text.side_effect = FileNotFoundError("No such file or directory")

        with self.assertRaises(FileNotFoundError):
            load_archive_metadata("missing_package")

        mock_read_text.assert_called_once()

    @patch("src._archive_helper.Path.read_text")
    def test_load_archive_metadata_invalid_json(self, mock_read_text):
        """Test that load_archive_metadata raises JSONDecodeError when the file contains invalid JSON."""
        mock_read_text.return_value = '{"key": "value", invalid}'

        with self.assertRaises(json.JSONDecodeError):
            load_archive_metadata("corrupt_package")

        mock_read_text.assert_called_once()


if __name__ == "__main__":
    unittest.main()
