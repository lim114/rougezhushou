"""Independently read/reencode all saved60; never run product or author checker."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
SNAP = OUT / 'snapshots'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def tree(value):
    kind = type(value)
    if kind is dict:
        return {'type': 'dict', 'items': [[tree(k), tree(v)] for k, v in value.items()]}
    if kind in (list, tuple):
        return {'type': kind.__name__, 'items': [tree(v) for v in value]}
    if kind is float:
        return {'type': 'float', 'hex': value.hex()}
    assert kind in (str, int, bool, type(None)), kind
    return {'type': kind.__name__, 'value': value}

node_counts = Counter()
def rebuild(encoded):
    kind = encoded['type']
    node_counts[kind] += 1
    if kind == 'dict':
        assert set(encoded) == {'type', 'items'}
        pairs = [(rebuild(k), rebuild(v)) for k, v in encoded['items']]
        result = dict(pairs)
        assert len(result) == len(pairs)
        return result
    if kind in ('list', 'tuple'):
        assert set(encoded) == {'type', 'items'}
        result = [rebuild(v) for v in encoded['items']]
        return tuple(result) if kind == 'tuple' else result
    if kind == 'float':
        assert set(encoded) == {'type', 'hex'}
        result = float.fromhex(encoded['hex'])
        assert result.hex() == encoded['hex']
        return result
    assert kind in ('str', 'int', 'bool', 'NoneType')
    assert set(encoded) == {'type', 'value'}
    result = encoded['value']
    assert type(result).__name__ == kind
    return result

plan_bytes = (SNAP / 'matrix-plan088.json').read_bytes()
plan = json.loads(plan_bytes)
assert len(plan) == 60 and [case['case'] for case in plan] == list(range(1, 61))
assert len({json.dumps(case['input'], sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    for case in plan}) == 60
records, summaries, bindings = {}, {}, []
for side in ('baseline', 'draft'):
    summary = json.loads((SNAP / (side + '-public60-summary.json')).read_bytes())
    compressed = (SNAP / (side + '-public60.jsonl.gz')).read_bytes()
    decoded = gzip.decompress(compressed)
    assert len(compressed) == summary['gzip_bytes'] and sha(compressed) == summary['gzip_sha256']
    assert len(decoded) == summary['decoded_bytes'] and sha(decoded) == summary['decoded_sha256']
    assert sha(plan_bytes) == summary['plan_sha256']
    rows = [json.loads(line) for line in decoded.splitlines()]
    assert len(rows) == summary['unique_inputs'] == summary['actual_public_calls'] == 60
    accepted = 0
    for expected, row in zip(plan, rows):
        assert row['case'] == expected['case'] and row['label'] == expected['label']
        assert tree(row['input']) == tree(expected['input'])
        assert row['input_typed_before'] == row['input_typed_after'] == tree(row['input'])
        assert row['catalog_native_sha256_before'] == row['catalog_native_sha256_after']
        assert len(row['catalog_native_sha256_before']) == 64
        if row['outcome'] == 'accepted':
            accepted += 1
            native_result = rebuild(row['result_typed'])
            assert tree(native_result) == row['result_typed']
            projected = json.loads(json.dumps(native_result, ensure_ascii=False, allow_nan=False))
            assert tree(projected) == tree(row['result'])
            assert list(row['reports']) == ['estimate', 'user', 'technical']
            assert all(type(value) is str for value in row['reports'].values())
            assert row['reports']['estimate'] == row['reports']['user']
        else:
            assert row['outcome'] == 'error'
            assert type(row['error_type']) is type(row['error_message']) is str
    assert accepted == summary['accepted']
    assert len(rows) - accepted == summary['errors']
    assert summary['explicit_report_requests'] == accepted * 3
    assert summary['explicit_format_estimate_requests'] == accepted
    assert summary['explicit_format_report_requests'] == accepted * 2
    assert summary['instrumented_format_function_entries'] == {'format_estimate': accepted, 'format_report': accepted * 3}
    assert summary['explicit_catalog_native_isolation_cache_reads'] == 61
    records[side], summaries[side] = rows, summary
    bindings.append({'side': side, 'gzip_bytes': len(compressed), 'gzip_sha256': sha(compressed),
        'decoded_bytes': len(decoded), 'decoded_sha256': sha(decoded)})

changed, same, older, pair_receipts = [], [], [], []
for expected, old, new in zip(plan, records['baseline'], records['draft']):
    assert old['input_typed_before'] == new['input_typed_before'] == tree(expected['input'])
    assert old['catalog_native_sha256_before'] == new['catalog_native_sha256_before']
    trace = new['actual_observer_return_trace']
    assert all(item['pending'] is None or type(item['pending']) is bool for item in trace)
    for item in trace:
        assert tree(rebuild(item['value'])) == item['value']
    if old['outcome'] == 'error':
        assert new['outcome'] == 'error'
        assert (old['error_type'], old['error_message']) == (new['error_type'], new['error_message'])
        older.append({'case': old['case'], 'type': old['error_type'], 'message': old['error_message']})
        category = 'old_error_type_message_exact'
    elif new['outcome'] == 'error':
        assert type(expected['input']['continuous_attacks']) is str
        assert (new['error_type'], new['error_message']) == ('ValueError', 'continuous_attacks 不接受文本条件；请使用布尔值。')
        assert any(item['pending'] is True for item in trace)
        changed.append(new['case'])
        category = 'qualified_text_rejection'
    else:
        assert old['result_typed'] == new['result_typed']
        assert tree(old['result']) == tree(new['result'])
        assert tree(old['reports']) == tree(new['reports'])
        assert not any(item['pending'] is True for item in trace)
        same.append(new['case'])
        category = 'full_beforeJSON_native_JSON_three_strings_exact'
    pair_receipts.append({'case': expected['case'], 'label': expected['label'],
        'category': category, 'trace_pending_true': any(item['pending'] is True for item in trace),
        'observer_returns': len(trace), 'caller_native_exact': True, 'catalog_native_hash_unchanged': True})
assert len(changed) == 23 and len(same) == 32 and len(older) == 5
for case in (19, 20, 21, 22, 41, 42, 43, 44):
    old, new = records['baseline'][case - 1], records['draft'][case - 1]
    assert case in same and not new['actual_observer_return_trace']
    resolution = old['result']['relic_resolution']
    assert resolution['rules'] == []
    assert all(record['applied'] == [] and record['status'] == 'reference_only' for record in resolution['records'])
for case in (39, 40):
    assert case in same and records['draft'][case - 1]['actual_observer_return_trace'] == []
    assert any(rule['kind'] == 'periodic_sp' for rule in records['baseline'][case - 1]['result']['relic_resolution']['rules'])
for case in (15, 16, 17, 18):
    reference = records['baseline'][case - 1]['result']['amiya_continuous_reference']
    assert reference['native_clock_binding_verified'] is False
    for key in ('actual_acquisition_times_seconds', 'actual_impact_times_seconds',
                'actual_recharge_seconds', 'actual_cycle_seconds'):
        assert reference[key] is None
for case in (31, 32):
    assert case in changed
    assert any(rule['kind'] == 'attack_sp' for rule in records['baseline'][case - 1]['result']['relic_resolution']['rules'])
assert 56 in changed and records['baseline'][55]['outcome'] == 'accepted'
assert {row['case'] for row in older} == {55, 57, 58, 59, 60}
success_total = sum(summary['accepted'] for summary in summaries.values())
assert success_total == 87
receipt = {'status': 'PASS_INDEPENDENT_SAVED60_BEFOREJSON_NATIVE_JSON_TEXT_ERROR_CALLER_AND_CATALOG_HASH',
    'pairs': 60, 'new_rejections': 23, 'whole_native_JSON_three_text_same': 32, 'exact_old_errors': 5,
    'changed_cases': changed, 'same_cases': same, 'olderrors': older, 'pair_receipts': pair_receipts,
    'decoded_native_node_counts': dict(node_counts), 'native_decode_reencode_exact': True,
    'no_normalization_or_tolerances': True, 'caller_whole_native_same': True,
    'catalog_scope': 'Actual full-native catalog hash before/after and across sides is preserved; raw catalog object tree was not separately saved.',
    'saved_bindings': bindings,
    'author_calls_only': {'public': 120, 'successful': 87, 'explicit_three_text_requests': 261,
        'instrumented_formatter_entries': 348, 'estimate_entries': 87, 'report_entries': 261,
        'explicit_catalog_cache_reads': 122},
    'actual_boundaries': {'Gummy_Bloom_and_incoming_event_controls': 'Current reference_only/applied=[]/rules=[]; do not prove publicevent-SP tail.',
        'periodic_defensive39_40': 'Active periodic rules with no condition observer; incoming priority unchanged.',
        'Chen3_31_32': 'Real applied attack_sp and text rejection.',
        'Amiya15_18': 'Report reference actually consumed but original four actual-clock fields stayNone/nativeFalse.',
        'case56': 'Baseline accepts healing_targets=True; new text rejection, not oldcount error.',
        'event_tail': 'Only original final8 scoped internal charge tests establish readiness/wait controls; no publicnativeclock conclusion.'},
    'new_calls_this_review': {'calculate_API': 0, 'production_helper': 0, 'formatter': 0, 'tests': 0,
        'network': 0, 'binary_source_parser': 0, 'Qt': 0, 'Wine': 0, 'tracked': 0},
    'author_comparator_not_executed': True, 'source16_not_decoded_or_repeated': True}
with (OUT / 'saved60-review088.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'pairs': 60, 'new_rejections': 23,
    'whole_same': 32, 'oldexact': 5, 'new_calls': 0}))
