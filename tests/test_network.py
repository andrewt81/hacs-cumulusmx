import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'custom_components/cumulusmx/network.py'
spec = importlib.util.spec_from_file_location('network', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NetworkTest(unittest.TestCase):
    def test_source_addresses(self):
        self.assertEqual(module.parse_bind_addresses('192.168.1.5, 10.0.0.2; 192.168.1.5'), ('192.168.1.5', '10.0.0.2'))
        self.assertEqual(module.parse_bind_addresses(''), ())
        with self.assertRaises(ValueError):
            module.parse_bind_addresses('eth0')


if __name__ == '__main__':
    unittest.main()
