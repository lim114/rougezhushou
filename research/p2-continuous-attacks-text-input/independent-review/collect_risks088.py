"""Collect one authorized side once, preserving native inputs and results."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('side', choices=('baseline', 'draft'))
parser.add_argument('--repo', required=True)
args = parser.parse_args()
OUT = Path(__file__).resolve().parent
REPO = Path(args.repo).resolve()
freeze = json.loads((OUT / 'formal-execution-freeze088.json').read_bytes())
assert freeze['status'] == 'AUTHOR_FINAL_AND_INDEPENDENT_EXECUTION_FROZEN'
plan_path = OUT / 'formal-risk-plan088.json'
assert hashlib.sha256(plan_path.read_bytes()).hexdigest() == freeze['plan_sha256']
for binding in freeze[args.side + '_source_bindings']:
    path = REPO / binding['path']
    data = path.read_bytes()
    assert len(data) == binding['bytes'] and hashlib.sha256(data).hexdigest() == binding['sha256']
sys.path.insert(0, str(REPO))


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


def decode(t):
    kind = t['type']
    if kind == 'dict':
        v = {decode(k): decode(x) for k, x in t['items']}
    elif kind in ('list', 'tuple'):
        v = [decode(x) for x in t['items']]
        if kind == 'tuple':
            v = tuple(v)
    elif kind == 'float':
        v = float.fromhex(t['hex'])
    else:
        assert kind in ('str', 'bool', 'int', 'NoneType')
        v = t['value']
        assert type(v).__name__ == kind
    assert canon(typed(v)) == canon(t)
    return v


from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

counts = {'public_function_entries': 0, 'explicit_public_requests': 0,
          'explicit_three_text_requests': 0, 'actual_formatter_entries': {'format_estimate': 0, 'format_report': 0},
          'named_condition_leaf_entries': {}, 'explicit_catalog_native_reads': 0,
          'all_project_helpers_instrumented': False}
trace = []


def profile(frame, event, arg):
    code = frame.f_code
    if event == 'call':
        if code is calculate_damage.__code__:
            counts['public_function_entries'] += 1
        elif code is format_estimate.__code__:
            counts['actual_formatter_entries']['format_estimate'] += 1
        elif code is format_report.__code__:
            counts['actual_formatter_entries']['format_report'] += 1
        elif code.co_filename == str(REPO / 'rouge/condition_inputs.py'):
            leaves = counts['named_condition_leaf_entries']
            leaves[code.co_name] = leaves.get(code.co_name, 0) + 1
    elif event == 'return' and code.co_name == 'observe_continuous_attacks' and code.co_filename == str(REPO / 'rouge/condition_inputs.py'):
        trace.append({'caller_function': frame.f_back.f_code.co_name,
                      'caller_line': frame.f_back.f_lineno, 'value_typed': typed(arg),
                      'pending': frame.f_globals['_pending'].get()})


def catalog_sha():
    counts['explicit_catalog_native_reads'] += 1
    return hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()


plan = json.loads(plan_path.read_bytes())
assert len(plan['cases']) == 8
before_catalog = catalog_sha()
path = OUT / (args.side + '-risks088.jsonl.gz')
assert not path.exists()
decoded_hash = hashlib.sha256()
decoded_bytes = accepted = errors = 0
sys.setprofile(profile)
try:
    with path.open('xb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as stream:
        for case in plan['cases']:
            request = copy.deepcopy(decode(case['input_typed']))
            before = typed(request)
            assert before == case['input_typed']
            row = {'case': case['case'], 'label': case['label'], 'expected': case['expected'],
                   'input': request, 'input_typed_before': before}
            trace = []
            counts['explicit_public_requests'] += 1
            try:
                result = calculate_damage(request)
            except Exception as exc:
                errors += 1
                row.update(outcome='error', error_type=type(exc).__name__, error_message=str(exc))
            else:
                accepted += 1
                native = typed(result)
                reports = {'estimate': format_estimate(result), 'user': format_report(result),
                           'technical': format_report(result, technical=True)}
                counts['explicit_three_text_requests'] += 3
                row.update(outcome='accepted', result=result, result_typed=native, reports=reports)
            row.update(input_typed_after=typed(request), observer_return_trace=trace,
                       catalog_native_sha256_before=before_catalog, catalog_native_sha256_after=catalog_sha())
            assert row['input_typed_before'] == row['input_typed_after']
            assert row['catalog_native_sha256_before'] == row['catalog_native_sha256_after']
            data = json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode() + b'\n'
            decoded_hash.update(data)
            decoded_bytes += len(data)
            stream.write(data)
finally:
    sys.setprofile(None)
assert counts['explicit_public_requests'] == counts['public_function_entries'] == 8
for binding in freeze[args.side + '_source_bindings']:
    data = (REPO / binding['path']).read_bytes()
    assert len(data) == binding['bytes'] and hashlib.sha256(data).hexdigest() == binding['sha256']
receipt = {'format_version': 1, 'status': 'CAPTURED_ONCE_PENDING_SAVED_COMPARISON',
           'side': args.side, 'risk_inputs': 8, 'accepted': accepted, 'errors': errors,
           'counts': counts, 'native_before_JSON_saved': True, 'caller_catalog_unchanged': True,
           'source_bytes_before_after_unchanged': True, 'plan_sha256': freeze['plan_sha256'],
           'gzip_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'gzip_bytes': path.stat().st_size,
           'decoded_sha256': decoded_hash.hexdigest(), 'decoded_bytes': decoded_bytes,
           'format_estimate_delegation_included_in_measured_entries': True,
           'explicit_prepare_core_helper_requests': 0, 'tests': 0, 'Qt': 0, 'Wine': 0}
(OUT / (args.side + '-risks088-summary.json')).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
