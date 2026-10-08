"""Strict saved-only comparison; no project imports or new product requests."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
sha = lambda b: hashlib.sha256(b).hexdigest()


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def decode(t):
    kind = t['type']
    if kind == 'dict':
        value = {decode(k): decode(v) for k, v in t['items']}
    elif kind in ('list', 'tuple'):
        value = [decode(v) for v in t['items']]
        if kind == 'tuple':
            value = tuple(value)
    elif kind == 'float':
        value = float.fromhex(t['hex'])
    else:
        assert kind in ('str', 'bool', 'int', 'NoneType')
        value = t['value']
        assert type(value).__name__ == kind
    assert canon(typed(value)) == canon(t)
    return value


freeze = json.loads((OUT / 'formal-execution-freeze088.json').read_bytes())
plan_path = OUT / 'formal-risk-plan088.json'
assert sha(plan_path.read_bytes()) == freeze['plan_sha256']
cases = json.loads(plan_path.read_bytes())['cases']
all_rows = {}
summaries = {}
for side in ('baseline', 'draft'):
    path = OUT / (side + '-risks088.jsonl.gz')
    compressed = path.read_bytes()
    raw = gzip.decompress(compressed)
    summary = json.loads((OUT / (side + '-risks088-summary.json')).read_bytes())
    assert summary['gzip_sha256'] == sha(compressed) and summary['gzip_bytes'] == len(compressed)
    assert summary['decoded_sha256'] == sha(raw) and summary['decoded_bytes'] == len(raw)
    rows = [json.loads(line) for line in raw.splitlines()]
    assert len(rows) == summary['risk_inputs'] == 8
    assert summary['counts']['explicit_public_requests'] == summary['counts']['public_function_entries'] == 8
    for case, row in zip(cases, rows):
        assert row['case'] == case['case']
        assert row['input_typed_before'] == row['input_typed_after'] == case['input_typed']
        assert canon(decode(row['input_typed_before'])) == canon(row['input'])
        assert row['catalog_native_sha256_before'] == row['catalog_native_sha256_after']
        if row['outcome'] == 'accepted':
            assert canon(decode(row['result_typed'])) == canon(row['result'])
            assert set(row['reports']) == {'estimate', 'user', 'technical'}
            assert all(type(value) is str for value in row['reports'].values())
        else:
            assert row['outcome'] == 'error' and type(row['error_message']) is str
    assert summary['accepted'] == sum(r['outcome'] == 'accepted' for r in rows)
    all_rows[side] = rows
    summaries[side] = summary

outcomes = Counter()
details = []
for case, old, new in zip(cases, all_rows['baseline'], all_rows['draft']):
    expectation = case['expected']
    if expectation == 'whole_unchanged':
        assert old['outcome'] == new['outcome'] == 'accepted'
        assert canon(old['result_typed']) == canon(new['result_typed'])
        assert canon(old['result']) == canon(new['result'])
        assert old['reports'] == new['reports']
    elif expectation == 'new_text_error':
        assert old['outcome'] == 'accepted' and new['outcome'] == 'error'
        assert new['error_type'] == 'ValueError'
        assert new['error_message'] == 'continuous_attacks 不接受文本条件；请使用布尔值。'
    else:
        assert expectation == 'old_error_unchanged'
        assert old['outcome'] == new['outcome'] == 'error'
        expected = case['expected_old_error']
        assert {k: old[k] for k in expected} == {k: new[k] for k in expected} == expected
    outcomes[expectation] += 1
    details.append({'case': case['case'], 'label': case['label'], 'verified': expectation,
                    'old_outcome': old['outcome'], 'draft_outcome': new['outcome']})
assert dict(outcomes) == {'whole_unchanged': 5, 'new_text_error': 2, 'old_error_unchanged': 1}

# Bind the corrected public qualification to actual accepted results, not labels.
for side in ('baseline', 'draft'):
    for index in (0, 1):
        result = all_rows[side][index]['result']
        assert result['relic_resolution']['rules'] == []
        assert result['applied_effects'] == []
        records = result['relic_resolution']['records']
        assert len(records) == 1
        assert records[0]['id'] == 'rogue_6_relic_legacy_118'
        assert records[0]['status'] == 'reference_only' and records[0]['applied'] == []
        assert records[0]['reference_effects']
        assert 'sp_events' not in result['estimate']
    assert type(decode(all_rows[side][5]['input_typed_before'])['continuous_attacks']) is tuple
amiya = all_rows['baseline'][2]['result']['amiya_continuous_reference']
assert amiya['enemy_source_excluded'] is True and amiya['attack_sp_enabled_in_reference'] is True
assert amiya['native_clock_binding_verified'] is False
assert all_rows['baseline'][2]['result']['estimate']['skill']['cycle_seconds'] is None
counts = {
    'explicit_public_requests': sum(v['counts']['explicit_public_requests'] for v in summaries.values()),
    'public_function_entries': sum(v['counts']['public_function_entries'] for v in summaries.values()),
    'explicit_three_text_requests': sum(v['counts']['explicit_three_text_requests'] for v in summaries.values()),
    'format_estimate_function_entries': sum(v['counts']['actual_formatter_entries']['format_estimate'] for v in summaries.values()),
    'format_report_function_entries': sum(v['counts']['actual_formatter_entries']['format_report'] for v in summaries.values()),
    'explicit_catalog_native_reads': sum(v['counts']['explicit_catalog_native_reads'] for v in summaries.values())
}
assert counts['explicit_public_requests'] == counts['public_function_entries'] == 16
assert counts['explicit_three_text_requests'] == 36
assert counts['format_estimate_function_entries'] == 12 and counts['format_report_function_entries'] == 36
target = OUT / 'independent-risk-comparison088.json'
assert not target.exists()
receipt = {'format_version': 1, 'status': 'PASS_UNIQUE_EIGHT_RISK_PAIRS',
           'risk_pairs': 8, 'outcomes': dict(outcomes), 'details': details, 'counts': counts,
           'native_before_JSON_full_tree_verified': True, 'whole_JSON_three_texts_verified': True,
           'native_tuple_input_before_JSON_preserved': True, 'caller_catalog_native_unchanged': True,
           'retired_event_public_controls_reference_only': True,
           'native0_ready_wait_tail_scope': 'Final frozen unit helper test; no public activation claimed.',
           'Amiya_E0_empty_scope_condition_reference_consumed': True,
           'parameter_or_actual_clock_changed': False, 'saved_compare_new_project_calls': 0,
           'old_sources16_or_author60_repeated': False, 'normalization': None,
           'formatter_entries_measured_not_derived': True}
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'outcomes': receipt['outcomes'], 'counts': counts}))
