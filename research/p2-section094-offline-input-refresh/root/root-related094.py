"""Fresh existing regressions for the complete thirteen-control refresh group."""
import sys
import unittest
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
sys.path.insert(0, str(ROOT))
modules = ('tests.test_charge_reference', 'tests.test_shield_break_reference',
           'tests.test_myrtle_healing_targets', 'tests.test_training_input_types',
           'tests.test_healing_subtotal_scaling')
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in modules)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
