"""Existing regression covering reporting, timing and friendly/hostile windows."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
sys.path.insert(0, str(ROOT))
suite = unittest.TestSuite()
for name in ('test_report', 'test_friendly_scope_report', 'test_timing',
             'test_gnosis_target_lifetime', 'test_amiya_continuous_lifetime',
             'test_healing_subtotal_scaling'):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tests' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
