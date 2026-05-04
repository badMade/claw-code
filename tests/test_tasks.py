from __future__ import annotations

import sys
import unittest
from unittest import mock

class TestTasks(unittest.TestCase):
    def setUp(self) -> None:
        # Save original sys.modules to prevent test pollution
        self.original_modules = sys.modules.copy()

        # Mock src.task before importing src.tasks to prevent circular import error
        self.mock_task_module = mock.MagicMock()

        class MockPortingTask:
            def __init__(self, name: str, description: str):
                self.name = name
                self.description = description

        self.mock_task_module.PortingTask = MockPortingTask
        sys.modules['src.task'] = self.mock_task_module

    def tearDown(self) -> None:
        # Restore sys.modules to prevent test pollution
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_default_tasks_returns_list_of_porting_tasks(self) -> None:
        # Import inside the test to use the mocked module
        from src.tasks import default_tasks

        tasks = default_tasks()
        self.assertIsInstance(tasks, list)
        self.assertTrue(len(tasks) > 0)
        for task in tasks:
            self.assertIsInstance(task, self.mock_task_module.PortingTask)

    def test_default_tasks_contains_expected_tasks(self) -> None:
        # Import inside the test to use the mocked module
        from src.tasks import default_tasks

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
