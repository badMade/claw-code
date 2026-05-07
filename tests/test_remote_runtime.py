import unittest
from src.remote_runtime import (
    RuntimeModeReport,
    run_remote_mode,
    run_ssh_mode,
    run_teleport_mode,
)

class TestRemoteRuntime(unittest.TestCase):
    def test_runtime_mode_report_as_text(self) -> None:
        report = RuntimeModeReport(mode='test', connected=True, detail='test detail')
        expected = "mode=test\nconnected=True\ndetail=test detail"
        self.assertEqual(report.as_text(), expected)

    def test_run_remote_mode(self) -> None:
        target = "test-target"
        report = run_remote_mode(target)
        self.assertEqual(report.mode, 'remote')
        self.assertTrue(report.connected)
        self.assertIn(target, report.detail)

    def test_run_ssh_mode(self) -> None:
        target = "ssh-target"
        report = run_ssh_mode(target)
        self.assertEqual(report.mode, 'ssh')
        self.assertTrue(report.connected)
        self.assertIn(target, report.detail)

    def test_run_teleport_mode(self) -> None:
        target = "teleport-target"
        report = run_teleport_mode(target)
        self.assertEqual(report.mode, 'teleport')
        self.assertTrue(report.connected)
        self.assertIn(target, report.detail)

if __name__ == '__main__':
    unittest.main()
