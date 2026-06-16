import unittest

from src.cost_tracker import CostTracker
from src.costHook import apply_cost_hook

class TestCostHook(unittest.TestCase):
    def test_apply_cost_hook_success(self):
        tracker = CostTracker()
        result = apply_cost_hook(tracker, "test_label", 10)

        self.assertIs(result, tracker)
        self.assertEqual(tracker.total_units, 10)
        self.assertEqual(tracker.events, ["test_label:10"])

    def test_apply_cost_hook_multiple_calls(self):
        tracker = CostTracker()
        apply_cost_hook(tracker, "first_label", 5)
        apply_cost_hook(tracker, "second_label", 15)

        self.assertEqual(tracker.total_units, 20)
        self.assertEqual(tracker.events, ["first_label:5", "second_label:15"])
