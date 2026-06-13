from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.session_store import StoredSession, load_session, save_session, validate_session_id


class TestValidateSessionId(unittest.TestCase):
    def test_accepts_normal_identifiers(self) -> None:
        validate_session_id("abc123")
        validate_session_id("my-session")
        validate_session_id("session_2024-01-01")
        validate_session_id("UPPER_CASE")
        validate_session_id("a")

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id("")

    def test_rejects_forward_slash(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id("foo/bar")
        with self.assertRaises(ValueError):
            validate_session_id("../../etc/passwd")
        with self.assertRaises(ValueError):
            validate_session_id("/absolute")

    def test_rejects_backslash(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id("foo\\bar")
        with self.assertRaises(ValueError):
            validate_session_id("..\\..\\windows\\system32")

    def test_rejects_dot_and_dotdot(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id(".")
        with self.assertRaises(ValueError):
            validate_session_id("..")

    def test_rejects_windows_drive_prefix(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id("C:session")
        with self.assertRaises(ValueError):
            validate_session_id("C:\\session")

    def test_rejects_unc_path(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_id("\\\\server\\share")


class TestSaveAndLoadSession(unittest.TestCase):
    def _make_session(self, session_id: str = "test-session") -> StoredSession:
        return StoredSession(
            session_id=session_id,
            messages=("hello", "world"),
            input_tokens=10,
            output_tokens=20,
        )

    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            session = self._make_session()
            path = save_session(session, directory=d)
            loaded = load_session(session.session_id, directory=d)
        self.assertEqual(loaded.session_id, session.session_id)
        self.assertEqual(loaded.messages, session.messages)
        self.assertEqual(loaded.input_tokens, session.input_tokens)
        self.assertEqual(loaded.output_tokens, session.output_tokens)
        self.assertTrue(path.name.endswith(".json"))

    def test_save_rejects_traversal_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = self._make_session(session_id="../../evil")
            with self.assertRaises(ValueError):
                save_session(session, directory=Path(tmp))

    def test_load_rejects_traversal_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                load_session("../../etc/passwd", directory=Path(tmp))


if __name__ == "__main__":
    unittest.main()
