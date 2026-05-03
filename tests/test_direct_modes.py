from __future__ import annotations

import unittest
from src.direct_modes import DirectModeReport, run_direct_connect, run_deep_link

class TestDirectModes(unittest.TestCase):
    def test_direct_mode_report_as_text(self):
        report = DirectModeReport(mode='direct-connect', target='abc', active=True)
        self.assertEqual(report.as_text(), 'mode=direct-connect\ntarget=abc\nactive=True')

        report2 = DirectModeReport(mode='deep-link', target='xyz', active=False)
        self.assertEqual(report2.as_text(), 'mode=deep-link\ntarget=xyz\nactive=False')

    def test_run_direct_connect(self):
        report = run_direct_connect('test-target')
        self.assertIsInstance(report, DirectModeReport)
        self.assertEqual(report.mode, 'direct-connect')
        self.assertEqual(report.target, 'test-target')
        self.assertTrue(report.active)

    def test_run_deep_link(self):
        report = run_deep_link('another-target')
        self.assertIsInstance(report, DirectModeReport)
        self.assertEqual(report.mode, 'deep-link')
        self.assertEqual(report.target, 'another-target')
        self.assertTrue(report.active)

if __name__ == '__main__':
    unittest.main()
