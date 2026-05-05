from __future__ import annotations

import sys
import unittest

from src.task import PortingTask
from src.tasks import default_tasks


class TestTasks(unittest.TestCase):
    def test_imports_use_real_modules(self) -> None:
        self.assertIn('src.task', sys.modules)
        self.assertIn('src.tasks', sys.modules)

    def test_default_tasks_returns_list_of_porting_tasks(self) -> None:
        tasks = default_tasks()
        self.assertIsInstance(tasks, list)
        self.assertTrue(len(tasks) > 0)
        for task in tasks:
            self.assertIsInstance(task, PortingTask)

    def test_default_tasks_contains_expected_tasks(self) -> None:
        tasks = default_tasks()
        task_names = [task.name for task in tasks]

        expected_names = [
            'root-module-parity',
            'directory-parity',
            'parity-audit'
        ]

        for name in expected_names:
            self.assertIn(name, task_names)

        # Verify specific descriptions
        for task in tasks:
            if task.name == 'root-module-parity':
                self.assertEqual(task.description, 'Mirror the root module surface of the archived snapshot')
            elif task.name == 'directory-parity':
                self.assertEqual(task.description, 'Mirror top-level subsystem names as Python packages')
            elif task.name == 'parity-audit':
                self.assertEqual(task.description, 'Continuously measure parity against the local archive')

if __name__ == '__main__':
    unittest.main()
