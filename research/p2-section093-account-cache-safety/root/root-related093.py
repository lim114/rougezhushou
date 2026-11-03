"""Existing training/run contracts plus the source-reviewed account cache boundary."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path('/workspace/rougezhushou')
sys.path.insert(0, str(ROOT))
suite = unittest.TestSuite()
for name in ('test_account_cache_093', 'test_training_input_types',
             'test_run_config_validation', 'test_run_crew_count_boolean_input'):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tests' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
