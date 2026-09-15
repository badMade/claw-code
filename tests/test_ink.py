import unittest
from src.ink import render_markdown_panel

class TestInk(unittest.TestCase):
    def test_render_markdown_panel_short_text(self):
        text = "Short text"
        result = render_markdown_panel(text)
        expected = "========================================\nShort text\n========================================"
        self.assertEqual(result, expected)

    def test_render_markdown_panel_long_text(self):
        text = "This is a much longer text that definitely exceeds the default 40 characters width."
        result = render_markdown_panel(text)
        border = '=' * len(text)
        expected = f"{border}\n{text}\n{border}"
        self.assertEqual(result, expected)

    def test_render_markdown_panel_ansi_text(self):
        # The visual length is "Hello World" which is 11 chars. So border should be 40.
        text = "\x1b[31mHello World\x1b[0m"
        result = render_markdown_panel(text)
        expected = "========================================\n\x1b[31mHello World\x1b[0m\n========================================"
        self.assertEqual(result, expected)

    def test_render_markdown_panel_multiline(self):
        text = "Short text\nAnother line that is also short"
        result = render_markdown_panel(text)
        expected = "========================================\nShort text\nAnother line that is also short\n========================================"
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
