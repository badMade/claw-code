import unittest
from src.tasks import default_tasks
from src.task import PortingTask

class TestTasks(unittest.TestCase):
    def test_default_tasks_returns_expected_list(self):
        tasks = default_tasks()

        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 3)

        self.assertIsInstance(tasks[0], PortingTask)
        self.assertEqual(tasks[0].name, 'root-module-parity')
        self.assertEqual(tasks[0].description, 'Mirror the root module surface of the archived snapshot')

        self.assertIsInstance(tasks[1], PortingTask)
        self.assertEqual(tasks[1].name, 'directory-parity')
        self.assertEqual(tasks[1].description, 'Mirror top-level subsystem names as Python packages')

        self.assertIsInstance(tasks[2], PortingTask)
        self.assertEqual(tasks[2].name, 'parity-audit')
        self.assertEqual(tasks[2].description, 'Continuously measure parity against the local archive')

if __name__ == '__main__':
    unittest.main()
