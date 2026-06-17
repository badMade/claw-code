import json
import unittest
from pathlib import Path
from unittest import mock

from src.parity_audit import _reference_surface, _snapshot_count


class TestParityAudit(unittest.TestCase):
    @mock.patch("pathlib.Path.read_text")
    def test_reference_surface_success(self, mock_read_text: mock.MagicMock) -> None:
        mock_read_text.return_value = '{"test": "data"}'
        result = _reference_surface()
        self.assertEqual(result, {"test": "data"})
        mock_read_text.assert_called_once()

    @mock.patch("pathlib.Path.read_text")
    def test_reference_surface_file_not_found(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.side_effect = FileNotFoundError("File not found")
        with self.assertRaises(FileNotFoundError):
            _reference_surface()
        mock_read_text.assert_called_once()

    @mock.patch("pathlib.Path.read_text")
    def test_reference_surface_invalid_json(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.return_value = '{"invalid": json}'
        with self.assertRaises(json.JSONDecodeError):
            _reference_surface()
        mock_read_text.assert_called_once()

    @mock.patch("pathlib.Path.read_text")
    def test_snapshot_count_success(self, mock_read_text: mock.MagicMock) -> None:
        mock_read_text.return_value = '[{"id": 1}, {"id": 2}]'
        path = Path("dummy.json")
        result = _snapshot_count(path)
        self.assertEqual(result, 2)
        mock_read_text.assert_called_once()

    @mock.patch("pathlib.Path.read_text")
    def test_snapshot_count_file_not_found(
        self, mock_read_text: mock.MagicMock
    ) -> None:
        mock_read_text.side_effect = FileNotFoundError("File not found")
        path = Path("dummy.json")
        with self.assertRaises(FileNotFoundError):
            _snapshot_count(path)
        mock_read_text.assert_called_once()

    @mock.patch("pathlib.Path.read_text")
    def test_snapshot_count_invalid_json(self, mock_read_text: mock.MagicMock) -> None:
        mock_read_text.return_value = "invalid json"
        path = Path("dummy.json")
        with self.assertRaises(json.JSONDecodeError):
            _snapshot_count(path)
        mock_read_text.assert_called_once()


if __name__ == "__main__":
    unittest.main()
