import unittest
from pathlib import Path
from src.prefetch import (
    PrefetchResult,
    start_mdm_raw_read,
    start_keychain_prefetch,
    start_project_scan,
)


class TestPrefetch(unittest.TestCase):
    def test_start_mdm_raw_read(self):
        result = start_mdm_raw_read()
        self.assertIsInstance(result, PrefetchResult)
        self.assertEqual(result.name, "mdm_raw_read")
        self.assertTrue(result.started)
        self.assertEqual(
            result.detail, "Simulated MDM raw-read prefetch for workspace bootstrap"
        )

    def test_start_keychain_prefetch(self):
        result = start_keychain_prefetch()
        self.assertIsInstance(result, PrefetchResult)
        self.assertEqual(result.name, "keychain_prefetch")
        self.assertTrue(result.started)
        self.assertEqual(
            result.detail, "Simulated keychain prefetch for trusted startup path"
        )

    def test_start_project_scan(self):
        path = Path("/test/path")
        result = start_project_scan(path)
        self.assertIsInstance(result, PrefetchResult)
        self.assertEqual(result.name, "project_scan")
        self.assertTrue(result.started)
        self.assertEqual(result.detail, "Scanned project root /test/path")


if __name__ == "__main__":
    unittest.main()
