import json
import unittest
from unittest.mock import patch

from src.commands import load_command_snapshot
from src.models import PortingModule


class TestCommands(unittest.TestCase):
    def setUp(self) -> None:
        # Clear the lru_cache to ensure tests are isolated and the mocked read_text is called.
        load_command_snapshot.cache_clear()

    def tearDown(self) -> None:
        load_command_snapshot.cache_clear()

    @patch("src.commands.Path.read_text")
    def test_load_command_snapshot_success(self, mock_read_text) -> None:
        # Mock valid JSON data
        mock_data = [
            {
                "name": "test_cmd_1",
                "responsibility": "Handle test command 1",
                "source_hint": "commands/test1.ts",
            },
            {
                "name": "test_cmd_2",
                "responsibility": "Handle test command 2",
                "source_hint": "commands/test2.ts",
            },
        ]
        mock_read_text.return_value = json.dumps(mock_data)

        # Call the function
        result = load_command_snapshot()

        # Verify the result
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

        self.assertIsInstance(result[0], PortingModule)
        self.assertEqual(result[0].name, "test_cmd_1")
        self.assertEqual(result[0].responsibility, "Handle test command 1")
        self.assertEqual(result[0].source_hint, "commands/test1.ts")
        self.assertEqual(result[0].status, "mirrored")

        self.assertIsInstance(result[1], PortingModule)
        self.assertEqual(result[1].name, "test_cmd_2")
        self.assertEqual(result[1].responsibility, "Handle test command 2")
        self.assertEqual(result[1].source_hint, "commands/test2.ts")
        self.assertEqual(result[1].status, "mirrored")

        # Verify read_text was called
        mock_read_text.assert_called_once()

    @patch("src.commands.Path.read_text")
    def test_load_command_snapshot_file_not_found(self, mock_read_text) -> None:
        # Mock FileNotFoundError
        mock_read_text.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            load_command_snapshot()

    @patch("src.commands.Path.read_text")
    def test_load_command_snapshot_invalid_json(self, mock_read_text) -> None:
        # Mock Invalid JSON
        mock_read_text.return_value = "{ invalid json"

        with self.assertRaises(json.JSONDecodeError):
            load_command_snapshot()

    @patch("src.commands.Path.read_text")
    def test_load_command_snapshot_missing_key(self, mock_read_text) -> None:
        # Mock JSON with missing 'name' key
        mock_data = [
            {"responsibility": "Handle test command", "source_hint": "commands/test.ts"}
        ]
        mock_read_text.return_value = json.dumps(mock_data)

        with self.assertRaises(KeyError):
            load_command_snapshot()


if __name__ == "__main__":
    unittest.main()
