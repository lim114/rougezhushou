from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, sys, unittest

base = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--related', action='store_true')
args = parser.parse_args()
package = base / 'draft078'
sys.path.insert(0, str(package))
name = 'rouge/operator_engine.py'
start = hashlib.sha256((package / name).read_bytes()).hexdigest()
suite = unittest.TestSuite()
files = ['tests/test_mantra_manual_events.py', 'tests/test_integer_option_input_types.py',
         'tests/test_empty_enemy_scope.py', 'tests/test_s1_neural_boundary.py',
         'tests/test_neural_sources_035.py', 'tests/test_neural_relic_034.py'] if args.related else ['test_mantra_talent_qualification.py']
for filename in files:
    path = package / filename if args.related else base / filename
    spec = importlib.util.spec_from_file_location(Path(filename).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
end = hashlib.sha256((package / name).read_bytes()).hexdigest()
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'related': args.related,
       'run': result.testsRun, 'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
       'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
       'source_start_sha256': start, 'source_end_sha256': end, 'source_unchanged': start == end,
       'available_checks_passed': result.wasSuccessful()}
(base / ('related-tests078.json' if args.related else 'new-tests078.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(out)
assert start == end and result.wasSuccessful()
