"""Run only public tests against an explicitly selected frozen package."""
import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
parser.add_argument('--new-only', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parent
package = Path(args.package).resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(package))
assert package in (root / 'frozen', root / 'draft')
files = [root / 'draft/tests/test_emergency_recruitment_condition.py']
if not args.new_only:
    files += [package / ('tests/' + name + '.py') for name in (
        'test_relics', 'test_relic_scope_052', 'test_offline_relics_031',
        'test_relic_resolution_052')]
suite = unittest.TestSuite()
for number, path in enumerate(files):
    spec = importlib.util.spec_from_file_location('public_tests_' + str(number), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
import rouge.damage
assert Path(rouge.damage.__file__).resolve().is_relative_to(package)
print(json.dumps({'package': str(package), 'damage_import': rouge.damage.__file__,
                  'new_only': args.new_only, 'tests_run': result.testsRun,
                  'skipped': len(result.skipped), 'failures': len(result.failures),
                  'errors': len(result.errors), 'passed': result.wasSuccessful()},
                 ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
