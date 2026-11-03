"""Run the nine actual author tests, transparently counting public invocations."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest

OUT = Path(__file__).resolve().parent
assert os.environ.get('PYTHONHASHSEED') == '0'
root = Path('/workspace/.continuation/p2-amiya-trait-scale-080/draft')
sys.path.insert(0, str(root))
freeze = json.loads((OUT / 'freeze080.json').read_text())
path = Path(freeze['new_test']['path'])
assert hashlib.sha256(path.read_bytes()).hexdigest() == freeze['new_test']['sha256']
import rouge.damage as damage
original = damage.calculate_damage
calls = 0


def counted_public_call(*args, **kwargs):
    global calls
    calls += 1
    return original(*args, **kwargs)


damage.calculate_damage = counted_public_call
spec = importlib.util.spec_from_file_location('reviewed_actual_new_tests80', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
assert suite.countTestCases() == 9
capture = io.StringIO()
result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
log = capture.getvalue()
with (OUT / 'independent-new-tests080.log').open('x', encoding='utf-8') as stream:
    stream.write(log)
receipt = {'status': 'passed' if result.wasSuccessful() else 'failed', 'tests_run': result.testsRun,
           'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
           'actual_public_calls_inside_new_tests': calls,
           'call_counter_scope': 'Transparent wrapper increments count then calls unchanged real calculate_damage; no result mocking or extra calculation.',
           'hash_seed': '0', 'test_source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'qt_executed': False, 'wine_executed': False}
with (OUT / 'independent-new-tests080.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2);stream.write('\n')
print(log)
print(json.dumps(receipt))
sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
