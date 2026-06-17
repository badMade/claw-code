from __future__ import annotations

import unittest
from src.remote_runtime import (
    RuntimeModeReport,
    run_remote_mode,
    run_ssh_mode,
    run_teleport_mode
)

class TestRemoteRuntime(unittest.TestCase):
    def test_runtime_mode_report_as_text(self):
        report = RuntimeModeReport('test_mode', True, 'Some detail here')
        expected_text = 'mode=test_mode\nconnected=True\ndetail=Some detail here'
        self.assertEqual(report.as_text(), expected_text)

        report_false = RuntimeModeReport('offline', False, 'Disconnected')
        expected_text_false = 'mode=offline\nconnected=False\ndetail=Disconnected'
        self.assertEqual(report_false.as_text(), expected_text_false)

    def test_run_remote_mode(self):
        target = 'server-01'
        report = run_remote_mode(target)
        self.assertEqual(report.mode, 'remote')
        self.assertTrue(report.connected)
        self.assertEqual(report.detail, 'Remote control placeholder prepared for server-01')
        self.assertIsInstance(report, RuntimeModeReport)

    def test_run_ssh_mode(self):
        target = 'server-02'
        report = run_ssh_mode(target)
        self.assertEqual(report.mode, 'ssh')
        self.assertTrue(report.connected)
        self.assertEqual(report.detail, 'SSH proxy placeholder prepared for server-02')
        self.assertIsInstance(report, RuntimeModeReport)

    def test_run_teleport_mode(self):
        target = 'server-03'
        report = run_teleport_mode(target)
        self.assertEqual(report.mode, 'teleport')
        self.assertTrue(report.connected)
        self.assertEqual(report.detail, 'Teleport resume/create placeholder prepared for server-03')
        self.assertIsInstance(report, RuntimeModeReport)

if __name__ == '__main__':
    unittest.main()
