import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('/workspace/rougezhushou')))
modules = [
    'tests.test_run_crew_count_boolean_input',
    'tests.test_run_reuse_guards_032',
    'tests.test_origin_discovery_055',
    'tests.test_inventory_snapshot_051',
    'tests.test_run_config_validation',
]
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
