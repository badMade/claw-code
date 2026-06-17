from __future__ import annotations

import unittest
from src.ink import render_markdown_panel


class TestInk(unittest.TestCase):
    def test_render_markdown_panel_simple(self):
        text = "Hello world"
        result = render_markdown_panel(text)
        expected = f"{'=' * 40}\nHello world\n{'=' * 40}"
        self.assertEqual(result, expected)

    def test_render_markdown_panel_empty(self):
        text = ""
        result = render_markdown_panel(text)
        expected = f"{'=' * 40}\n\n{'=' * 40}"
        self.assertEqual(result, expected)

    def test_render_markdown_panel_multiline(self):
        text = "Line 1\nLine 2\nLine 3"
        result = render_markdown_panel(text)
        expected = f"{'=' * 40}\nLine 1\nLine 2\nLine 3\n{'=' * 40}"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
