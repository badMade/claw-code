import unittest
from src.interactiveHelpers import bulletize

class TestInteractiveHelpers(unittest.TestCase):
    def test_bulletize_empty_list(self):
        self.assertEqual(bulletize([]), "")

    def test_bulletize_single_item(self):
        self.assertEqual(bulletize(["apple"]), "- apple")

    def test_bulletize_multiple_items(self):
        self.assertEqual(bulletize(["apple", "banana", "cherry"]), "- apple\n- banana\n- cherry")

    def test_bulletize_with_special_characters(self):
        self.assertEqual(bulletize(["apple pie", "banana-split", "!@#$"]), "- apple pie\n- banana-split\n- !@#$")

if __name__ == '__main__':
    unittest.main()
