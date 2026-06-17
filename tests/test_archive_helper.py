import json
import unittest
from unittest import mock

from src._archive_helper import load_archive_metadata


class TestArchiveHelper(unittest.TestCase):
    @mock.patch("pathlib.Path.read_text")
    def test_load_archive_metadata_success(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.return_value = '{"foo": "bar"}'
        result = load_archive_metadata("my_package")
        self.assertEqual(result, {"foo": "bar"})

    @mock.patch("pathlib.Path.read_text")
    def test_load_archive_metadata_file_not_found(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.side_effect = FileNotFoundError("No such file or directory")
        with self.assertRaises(FileNotFoundError):
            load_archive_metadata("my_package")

    @mock.patch("pathlib.Path.read_text")
    def test_load_archive_metadata_invalid_json(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.return_value = '{"foo": '
        with self.assertRaises(json.JSONDecodeError):
            load_archive_metadata("my_package")
