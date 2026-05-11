import unittest
from src.prefetch import start_mdm_raw_read

class TestPrefetch(unittest.TestCase):
    def test_start_mdm_raw_read(self):
        result = start_mdm_raw_read()
        self.assertEqual(result.name, 'mdm_raw_read')
        self.assertTrue(result.started)
        self.assertEqual(result.detail, 'Simulated MDM raw-read prefetch for workspace bootstrap')

if __name__ == '__main__':
    unittest.main()
