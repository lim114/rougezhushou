"""Saved-only verification: no rouge imports, API, helpers or formatters."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from native_codec092 import decode, encode


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_native(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def load_compressed(receipt):
    raw = Path(receipt['path']).read_bytes()
    assert len(raw) == receipt['compressed_bytes']
    assert sha(raw) == receipt['compressed_sha256']
    decoded = gzip.decompress(raw)
    assert len(decoded) == receipt['decoded_bytes']
    assert sha(decoded) == receipt['decoded_sha256']
    return json.loads(decoded)


freeze = json.loads((HERE / 'pre-public-freeze092.json').read_text())
for item in freeze['files']:
    raw = Path(item['source_path']).read_bytes()
    assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], item['archive_path']
inputs = json.loads((HERE / 'public-inputs092.json').read_text())
cases = {case['id']: case for case in inputs['cases']}
ledgers = {}
saved = {}
caches = {}
for variant in ('baseline', 'draft'):
    ledger = json.loads((HERE / (variant + '-actual-ledger092.json')).read_text())
    assert ledger['status'] == 'PASS'
    assert ledger['actual_public_entries'] == 4
    assert len(ledger['external_formatter_requests']) == 12
    assert len(ledger['actual_formatter_entries']) == 16
    assert len(ledger['saved_records']) == 4
    assert all(ledger[key] == 0 for key in ('explicit_external_project_helper_calls', 'Qt', 'Wine', 'tests'))
    assert ledger['source_current_730_verified_before_run']
    assert ledger['no_actual_Qt_or_app_import']
    ledgers[variant] = ledger
    saved[variant] = {}
    for receipt in ledger['saved_records']:
        record = load_compressed(receipt)
        case_id = record['case_id']
        assert case_id in cases and case_id not in saved[variant]
        assert record['variant'] == variant and record['error'] is None
        expected_input = cases[case_id]['input']
        assert record['input_before'] == encode(expected_input) == record['input_after']
        assert record['input_JSON_before'] == json_native(expected_input) == record['input_JSON_after']
        assert record['caller_unchanged']
        result = decode(record['result_native_tree'])
        assert encode(result) == record['result_native_tree'] == record['result_after_formatters_native_tree']
        assert json_native(result) == record['result_JSON']
        assert set(record['texts']) == {'estimate', 'default', 'technical'}
        assert all(isinstance(text, str) and text for text in record['texts'].values())
        assert record['texts']['estimate'] == record['texts']['default']
        assert all(value['equal_first_native_tree'] for value in record['observed_cache_state_after_call'].values())
        saved[variant][case_id] = {'record': record, 'result': result}
    assert set(saved[variant]) == set(cases)
    cache = load_compressed(ledger['saved_cache'])
    assert len(cache) == 9
    for key, value in cache.items():
        assert value['equal_complete_native_tree']
        assert value['first_native_tree'] == value['final_native_tree']
        assert encode(decode(value['first_native_tree'])) == value['first_native_tree']
        tree_hash = sha(json_native(value['first_native_tree']).encode())
        for entry in saved[variant].values():
            observed = entry['record']['observed_cache_state_after_call'].get(key)
            if observed is not None:
                assert observed['native_tree_sha256'] == tree_hash
    caches[variant] = cache
assert caches['baseline'] == caches['draft']

pair_receipts = []
for case_id, case in cases.items():
    old = saved['baseline'][case_id]
    new = saved['draft'][case_id]
    assert old['record']['input_before'] == new['record']['input_before']
    before = old['result']
    after = deepcopy(new['result'])
    old_blocks = {block['id']: block for block in before['report']['sections']}
    removed = []
    effective = before['estimate']['skill']['window_seconds']
    for block in after['report']['sections']:
        original = old_blocks[block['id']]
        extras = [row for row in block['metrics']
                  if row['key'] == 'window_seconds'
                  and not any(previous['key'] == 'window_seconds' for previous in original['metrics'])]
        for row in extras:
            assert block['id'] in ('damage', 'healing')
            label = '伤害观察窗口' if block['id'] == 'damage' else '治疗观察窗口'
            expected_row = {'key': 'window_seconds', 'label': label, 'value': effective, 'unit': '秒'}
            assert encode(row) == encode(expected_row)
            assert effective is not None
            block['metrics'].remove(row)
            removed.append({'section_id': block['id'], 'row': row,
                            'native_value': encode(row['value'])})
    assert len(removed) == 1, case_id
    assert encode(after) == old['record']['result_native_tree'], case_id
    assert json_native(after) == old['record']['result_JSON'], case_id
    text_inverse = {}
    # These added rows have unit 秒 and no range/reason. format_report.render's
    # unchanged source formats this case using value:.2f and adds the unit.
    # The two labels contain none of phrase's translation/source tokens.
    for mode in ('estimate', 'default', 'technical'):
        text = new['record']['texts'][mode]
        added_lines = [entry['row']['label'] + '：' + f"{entry['row']['value']:.2f}" + ' 秒'
                       for entry in removed]
        for line in added_lines:
            assert text.splitlines().count(line) == 1
            assert line not in old['record']['texts'][mode].splitlines()
            pieces = text.splitlines(keepends=True)
            matches = [i for i, piece in enumerate(pieces) if piece.rstrip('\r\n') == line]
            assert len(matches) == 1
            del pieces[matches[0]]
            text = ''.join(pieces)
        assert text == old['record']['texts'][mode], (case_id, mode)
        text_inverse[mode] = {'removed_lines': added_lines, 'remaining_saved_text_exact': True,
                              'baseline_sha256': sha(old['record']['texts'][mode].encode()),
                              'draft_sha256': sha(new['record']['texts'][mode].encode())}
    skill = before['estimate']['skill']
    target_section = 'damage' if case_id == 'damage-zero' else 'healing'
    metrics = next(block['metrics'] for block in new['result']['report']['sections'] if block['id'] == target_section)
    if case_id in ('damage-zero', 'finite-healing-zero'):
        assert type(effective) is float and effective == 0.0
        assert not any(row['key'] in ('window_dps', 'window_hps') for row in metrics)
    if case_id == 'friendly-healing-enemy-zero':
        assert case['input']['timing']['target_disappears_seconds'] == 0
        assert effective == 6.0 and skill['window_healing'] > 0
    if case_id == 'finite-healing-long':
        assert case['input']['window_seconds'] == 60.0
        assert effective == 30.0 == skill['duration_seconds']
    pair_receipts.append({'case_id': case_id, 'qualified_section': target_section,
                          'requested_window_native': encode(case['input']['window_seconds']),
                          'effective_window_native': encode(effective),
                          'unchanged_observed_window_damage': skill.get('window_damage'),
                          'unchanged_observed_window_healing': skill.get('window_healing'),
                          'removed_qualified_rows': removed, 'whole_native_inverse_exact': True,
                          'whole_JSON_inverse_exact': True, 'three_saved_text_inverses': text_inverse,
                          'caller_unchanged_both': True, 'result_unchanged_by_formatters_both': True})

entry_counts = Counter()
request_counts = Counter()
for ledger in ledgers.values():
    for request in ledger['external_formatter_requests']:
        request_counts[request['mode']] += 1
    for entry in ledger['actual_formatter_entries']:
        key = entry['function']
        if key == 'format_report':
            key += '_technical' if entry['technical'] else '_default'
        entry_counts[key] += 1
assert dict(request_counts) == {'estimate': 8, 'default': 8, 'technical': 8}
assert dict(entry_counts) == {'format_estimate': 8, 'format_report_default': 16, 'format_report_technical': 8}
summary = {
    'format_version': 1, 'status': 'PASS_SAVED_ONLY_STRICT_INVERSE',
    'fixed_root_commit': '59961ec3d633ac91b01014fb06b357d45e5979f7',
    'pairs': pair_receipts, 'pair_count': 4, 'saved_public_results': 8,
    'actual_public_entries': sum(ledger['actual_public_entries'] for ledger in ledgers.values()),
    'external_formatter_requests': sum(request_counts.values()),
    'external_request_modes_actual': dict(request_counts),
    'actual_internal_formatter_entries': sum(entry_counts.values()),
    'actual_internal_formatter_entries_by_function': dict(entry_counts),
    'complete_observed_cache_objects_per_variant': 9,
    'complete_observed_cache_first_final_and_across_variants_exact': True,
    'cache_scope': ledgers['baseline']['cache_scope'],
    'frozen14_files_verified_unchanged': True,
    'comparison_process_project_imports_API_helpers_formatters_tests_Qt_Wine': 0,
    'new_regression_test_methods': 0,
    'scope': 'Only one qualified report.window_seconds row per observed result differs; all other native types/values/order and JSON are exact. Each saved text differs only by the corresponding rendered added line.',
    'bounds': 'Four valid public source-qualified inputs only. Existing errors/guards statically unchanged, not fresh-tested. No actual Qt, native game clock or generic long-window clipping claim.'
}
(HERE / 'saved-comparison-summary092.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': summary['status'], 'pairs': 4, 'actual_public': 8,
                  'external_text_requests': 24, 'actual_formatter_entries': 32,
                  'saved_only_comparison_project_calls': 0}, ensure_ascii=False))
