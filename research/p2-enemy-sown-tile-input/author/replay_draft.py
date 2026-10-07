"""Replay each complete discovery input against the fixed external draft."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
package = p/'draft'
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


catalog_before, mechanics_before = strict(catalog()), strict(mechanics())
cache, isolation_errors = {}, []
calls = 0


def outcome(args):
    global calls
    key = strict(args)
    if key in cache:
        return cache[key]
    calls += 1
    before = strict(args)
    try:
        result = calculate_damage(args)
        value = {'accepted': True, 'result': result, 'formatted_report': format_report(result)}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    if strict(args) != before:
        isolation_errors.append(before)
    cache[key] = value
    return value


original = json.loads(gzip.decompress((p/'readonly-public.json.gz').read_bytes()))
records = []
for before in original['records']:
    row = {key: copy.deepcopy(value) for key, value in before.items()
           if key not in ('outcome', 'false_outcome', 'true_outcome', 'matches_false_strict_json', 'matches_true_strict_json')}
    row['outcome'] = outcome(copy.deepcopy(row['input']))
    row['false_outcome'] = outcome(copy.deepcopy(row['false_input']))
    row['true_outcome'] = outcome(copy.deepcopy(row['true_input']))
    row['matches_false_strict_json'] = strict(row['outcome']) == strict(row['false_outcome'])
    row['matches_true_strict_json'] = strict(row['outcome']) == strict(row['true_outcome'])
    records.append(row)
changed, unchanged, unexpected, bool_drift = [], [], [], []
error = {'accepted': False, 'error_type': 'ValueError',
         'error': 'enemy_on_sown_tile 不接受文本条件；请使用布尔值。'}
for before, after in zip(original['records'], records):
    assert before['key'] == after['key'] and strict(before['input']) == strict(after['input'])
    expected_change = before['group'] == 'active' and isinstance(before['input'].get('enemy_on_sown_tile'), str)
    if strict(before['outcome']) == strict(after['outcome']):
        unchanged.append(before['key'])
        if expected_change:
            unexpected.append(before['key'])
    else:
        changed.append(before['key'])
        if not expected_change or strict(after['outcome']) != strict(error):
            unexpected.append(before['key'])
    if any(strict(before[field]) != strict(after[field]) for field in ('false_outcome', 'true_outcome')):
        bool_drift.append(before['key'])
summary = {'final_baseline_head': 'f4ca1c97278c5354f32940f56db2de60bbd21423',
           'scenarios': len(records), 'draft_actual_public_calls': calls,
           'paired_actual_public_calls': original['summary']['actual_public_calls'] + calls,
           'new_active_text_errors': len(changed), 'preserved_complete_outcomes': len(unchanged),
           'unexpected_changes': unexpected, 'bool_canonical_drift': bool_drift,
           'caller_isolation_errors': isolation_errors,
           'catalog_preserved_strict_json': strict(catalog()) == catalog_before,
           'mechanics_preserved_strict_json': strict(mechanics()) == mechanics_before,
           'comparison': 'strict complete JSON including numbers/bools, formatted reports, error type/text',
           'private_state_read': False, 'native_validation': False, 'new_native_geometry_or_clock': False}
summary['passed'] = not any((unexpected, bool_drift, isolation_errors)) and summary['catalog_preserved_strict_json'] and summary['mechanics_preserved_strict_json']
raw = strict({'summary': summary, 'records': records}).encode()
destination = p/'draft-public.json.gz'
with destination.open('wb') as handle:
    with gzip.GzipFile(filename='', mode='wb', fileobj=handle, mtime=0) as zipped:
        zipped.write(raw)
assert gzip.decompress(destination.read_bytes()) == raw
summary['compressed_evidence'] = {'gzip_bytes': destination.stat().st_size,
                                  'gzip_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                                  'raw_bytes': len(raw), 'raw_sha256': hashlib.sha256(raw).hexdigest(),
                                  'decompression_verified': True}
(p/'paired-comparison.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary))
assert summary['passed']
