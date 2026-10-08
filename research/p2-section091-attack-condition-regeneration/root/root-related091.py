"""Run the six relevant existing regression modules once on applied root."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
sys.path.insert(0, str(ROOT))
suite = unittest.TestSuite()
for name in ('test_continuous_attacks_text_input', 'test_sp_sources_066',
             'test_summon_count_reporting', 'test_summon_modules_038',
             'test_report', 'test_healing_subtotal_scaling'):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tests'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
