"""Run the author's eight frozen methods once with explicit/entry ledgers."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest

OUT = Path(__file__).resolve().parent
freeze = json.loads((OUT / 'formal-execution-freeze088.json').read_bytes())
assert freeze['status'] == 'AUTHOR_FINAL_AND_INDEPENDENT_EXECUTION_FROZEN'
REPO = Path(freeze['draft_execution_root'])
path = REPO / 'tests/test_continuous_attacks_text_input.py'
assert hashlib.sha256(path.read_bytes()).hexdigest() == freeze['new_test_sha256']
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location('independent_original_section088_tests', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.sp_events import charge
from rouge.estimate import format_estimate
from rouge.reporting import format_report


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


counts = {'public_function_entries': 0, 'explicit_test_public_requests': 0,
          'explicit_test_context_helper_requests': 0, 'standalone_charge_function_entries': 0,
          'named_condition_leaf_entries': {}, 'actual_formatter_entries': {'format_estimate': 0, 'format_report': 0},
          'explicit_catalog_native_reads': 0, 'all_project_function_entries_instrumented': False}
lock = threading.Lock()
leaf = str(REPO / 'rouge/condition_inputs.py')
test = str(path)
inflight = {}
events = []
resets = []


def profile(frame, event, arg):
    code = frame.f_code
    parent = frame.f_back
    direct = parent is not None and parent.f_code.co_filename == test
    with lock:
        if event == 'call':
            if code is calculate_damage.__code__:
                counts['public_function_entries'] += 1
                if direct:
                    counts['explicit_test_public_requests'] += 1
                inflight[id(frame)] = typed(frame.f_locals['scenario'])
            elif code is charge.__code__:
                counts['standalone_charge_function_entries'] += 1
                if direct:
                    counts['explicit_test_context_helper_requests'] += 1
            elif code.co_filename == leaf:
                data = counts['named_condition_leaf_entries']
                data[code.co_name] = data.get(code.co_name, 0) + 1
                if direct:
                    counts['explicit_test_context_helper_requests'] += 1
            elif code is format_estimate.__code__:
                counts['actual_formatter_entries']['format_estimate'] += 1
            elif code is format_report.__code__:
                counts['actual_formatter_entries']['format_report'] += 1
        elif event == 'return':
            if code is calculate_damage.__code__:
                before = inflight.pop(id(frame))
                after = typed(frame.f_locals['scenario'])
                assert before == after
                events.append({'caller_input_typed_before': before, 'caller_input_typed_after': after,
                               'result_typed_if_returned': typed(arg) if isinstance(arg, dict) else None,
                               'direct_test_request': direct})
            elif code.co_filename == leaf and code.co_name == 'isolated':
                resets.append({'caller': parent.f_code.co_name if parent else None,
                               'pending_restored_after_return': frame.f_globals['_pending'].get(),
                               'thread_name': threading.current_thread().name})


def catalog_sha():
    counts['explicit_catalog_native_reads'] += 1
    return hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()


before_catalog = catalog_sha()
sys.setprofile(profile)
threading.setprofile(profile)
try:
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    assert suite.countTestCases() == 8
    result = unittest.TextTestRunner(verbosity=2).run(suite)
finally:
    threading.setprofile(None)
    sys.setprofile(None)
after_catalog = catalog_sha()
assert before_catalog == after_catalog
assert not inflight
assert counts['public_function_entries'] <= 32
assert counts['explicit_test_context_helper_requests'] <= 32
assert hashlib.sha256(path.read_bytes()).hexdigest() == freeze['new_test_sha256']
for binding in freeze['draft_source_bindings']:
    data = (REPO / binding['path']).read_bytes()
    assert len(data) == binding['bytes'] and hashlib.sha256(data).hexdigest() == binding['sha256']
native = {'public_call_return_events': events, 'context_reset_return_observations': resets,
          'catalog_native_sha256_before': before_catalog, 'catalog_native_sha256_after': after_catalog}
decoded = json.dumps(native, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
native_path = OUT / 'new-tests-native-evidence088.json.gz'
with native_path.open('xb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as stream:
    stream.write(decoded)
receipt = {'format_version': 1, 'status': 'PASS' if result.wasSuccessful() else 'FAIL',
           'methods_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skips': len(result.skipped), 'counts': counts,
           'failure_details': [(str(test), trace) for test, trace in result.failures],
           'error_details': [(str(test), trace) for test, trace in result.errors],
           'new_test_frozen_sha256': freeze['new_test_sha256'], 'caller_catalog_native_unchanged': True,
           'native_evidence_gzip_sha256': hashlib.sha256(native_path.read_bytes()).hexdigest(),
           'native_evidence_gzip_bytes': native_path.stat().st_size,
           'native_evidence_decoded_sha256': hashlib.sha256(decoded).hexdigest(), 'native_evidence_decoded_bytes': len(decoded),
           'source_bytes_unchanged': True, 'explicit_formatter_requests': 0,
           'tests_scope': 'Author original eight methods once; no old tests and no test expectation/body edits.',
           'source_parse_download_Qt_Wine_tracked': 0}
(OUT / 'new-tests-independent-receipt088.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
