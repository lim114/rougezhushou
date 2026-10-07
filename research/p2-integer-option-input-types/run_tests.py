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
OUT = Path(__file__).resolve().parent
package = Path(args.package).resolve()
assert package in (OUT / 'frozen', OUT / 'draft')
sys.dont_write_bytecode = True
sys.path.insert(0, str(package))
paths = [OUT / 'draft/tests/test_integer_option_input_types.py']
if not args.new_only:
    paths += [package / ('tests/' + name + '.py') for name in (
        'test_target_count_input_types', 'test_declared_count_input_types',
        'test_token_manual_attributes', 'test_empty_enemy_scope')]
suite = unittest.TestSuite()
for number, path in enumerate(paths):
    spec = importlib.util.spec_from_file_location('public_type_tests_' + str(number), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
import rouge.operator_engine
assert Path(rouge.operator_engine.__file__).resolve().is_relative_to(package)
print(json.dumps({'package': str(package), 'operator_engine_import': rouge.operator_engine.__file__,
                  'new_only': args.new_only, 'tests_run': result.testsRun,
                  'skipped': len(result.skipped), 'failures': len(result.failures),
                  'errors': len(result.errors), 'passed': result.wasSuccessful()}))
sys.exit(0 if result.wasSuccessful() else 1)
