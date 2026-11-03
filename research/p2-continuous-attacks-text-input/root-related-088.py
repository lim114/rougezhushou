import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('/workspace/rougezhushou')))
modules = [
    'tests.test_continuous_attacks_text_input',
    'tests.test_amiya_continuous_lifetime',
    'tests.test_charge_reference',
    'tests.test_wine_timing',
    'tests.test_timing',
    'tests.test_remaining_boolean_condition_text_input',
]
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
