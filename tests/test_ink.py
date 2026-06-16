import unittest
from src.ink import render_markdown_panel


class TestInk(unittest.TestCase):
    def test_render_markdown_panel_normal(self):
        text = "Hello World"
        expected = f"{'=' * 40}\nHello World\n{'=' * 40}"
        self.assertEqual(render_markdown_panel(text), expected)

    def test_render_markdown_panel_empty(self):
        text = ""
        expected = f"{'=' * 40}\n\n{'=' * 40}"
        self.assertEqual(render_markdown_panel(text), expected)

    def test_render_markdown_panel_multiline(self):
        text = "Line 1\nLine 2\nLine 3"
        expected = f"{'=' * 40}\nLine 1\nLine 2\nLine 3\n{'=' * 40}"
        self.assertEqual(render_markdown_panel(text), expected)


if __name__ == "__main__":
    unittest.main()
