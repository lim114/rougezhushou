"""Run new public contract tests against either sealed package without copying fixtures."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
PACKAGE = Path(sys.argv[1]).resolve()
OUTPUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PACKAGE))
spec = importlib.util.spec_from_file_location('public_contract_059',
    ROOT / 'draft/tests/test_damage_subtotal_sources.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
receipt = {'package_directory': str(PACKAGE), 'tests_run': result.testsRun,
    'failures': len(result.failures), 'errors': len(result.errors),
    'skipped': len(result.skipped), 'passed': result.wasSuccessful(),
    'native_windows_or_game_validation': False}
OUTPUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
