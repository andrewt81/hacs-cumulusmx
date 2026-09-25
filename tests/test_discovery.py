import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'custom_components/cumulusmx/discovery.py'
spec = importlib.util.spec_from_file_location('discovery', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DiscoveryTest(unittest.TestCase):
    def test_partial_payload_and_later_sensor(self):
        first = {'temp': '18,4', 'UV': '*** web tag error - see MXdiags file ***', 'SolarRad': ''}
        self.assertEqual(module.available_tags(first, ['temp', 'UV', 'SolarRad']), {'temp'})
        later = {**first, 'UV': '0', 'SolarRad': '350'}
        self.assertEqual(module.available_tags(later, ['temp', 'UV', 'SolarRad']), {'temp', 'UV', 'SolarRad'})

    def test_rejects_missing_and_invalid_values(self):
        for value in ('-999', 'NaN', 'Infinity', None, ''):
            self.assertIsNone(module.numeric_value({'temp': value}, 'temp'))


if __name__ == '__main__':
    unittest.main()
