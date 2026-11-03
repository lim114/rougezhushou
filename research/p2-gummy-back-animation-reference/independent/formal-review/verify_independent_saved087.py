"""Strict saved-only comparison. Zero new API, formatter, helper or reader calls."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def typed(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(typed(x, y) for x, y in zip(a, b))
    return a == b

def load(side):
    path = ROOT / ('independent-' + side + '-results087.json.gz')
    raw = gzip.decompress(path.read_bytes())
    result = json.loads(raw)
    summary = json.loads((ROOT / ('independent-' + side + '-summary087.json')).read_text())
    assert path.stat().st_size == summary['bytes'] and sha(path.read_bytes()) == summary['sha256']
    assert len(raw) == summary['decompressed_result_bytes'] and sha(raw) == summary['decompressed_result_sha256']
    assert typed(summary['public_entry_counts'], result['public_entry_counts'])
    assert result['actual_public_API_calls'] == result['public_entry_counts']['calculate_damage'] == len(result['items']) == summary['actual_public_API_calls']
    assert result['native_before_JSON_saved'] is True
    assert len(result['native_trees_content_addressed_complete']) == summary['native_tree_file_count']
    return result, {'source_path': str(path), 'archive_path': path.name,
        'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes()),
        'decoded_bytes': len(raw), 'decoded_sha256': sha(raw)}

before, b_input = load('baseline')
after, d_input = load('draft')
tests, t_input = load('newtests')
native_type_counts = Counter()
native_checked = {}
def validate_native_binding(binding):
    path = ROOT / binding['archive_path']
    assert str(path) == binding['source_path']
    assert path.stat().st_size == binding['bytes'] and sha(path.read_bytes()) == binding['sha256']
    raw = gzip.decompress(path.read_bytes())
    assert len(raw) == binding['decoded_native_tree_bytes'] and sha(raw) == binding['decoded_native_tree_sha256']
    if path not in native_checked:
        tree = json.loads(raw)
        def walk(node):
            assert isinstance(node, dict) and type(node['type']) is str
            name = node['type']
            native_type_counts[name] += 1
            if name == 'builtins.dict':
                assert list(node) == ['items', 'type'] and isinstance(node['items'], list)
                for item in node['items']:
                    assert set(item) == {'key', 'value'}
                    walk(item['key']); walk(item['value'])
            elif name in ['builtins.list', 'builtins.tuple']:
                assert isinstance(node['items'], list)
                for value in node['items']:
                    walk(value)
            elif name == 'builtins.NoneType':
                assert node['value'] is None
            elif name == 'builtins.bool':
                assert type(node['value']) is bool
            elif name == 'builtins.int':
                assert type(node['value_decimal']) is str
            elif name == 'builtins.float':
                assert type(node['value_hex']) is str
            elif name == 'builtins.str':
                assert type(node['value']) is str
            else:
                raise AssertionError('Unexpected native tree type: ' + name)
        walk(tree)
        native_checked[path] = binding

for collection in [before, after, tests]:
    for binding in collection['native_trees_content_addressed_complete']:
        validate_native_binding(binding)
    for item in collection['items']:
        assert item['caller_unchanged'] is True
        assert item['caller_before_native_tree']['decoded_native_tree_sha256'] == item['caller_after_native_tree']['decoded_native_tree_sha256']
        validate_native_binding(item['caller_before_native_tree']); validate_native_binding(item['caller_after_native_tree'])
        if 'cached_data_before_native_trees' in item:
            assert item['cached_data_unchanged'] is True
            for key in ['catalog', 'operator_profiles', 'animation_references']:
                b = item['cached_data_before_native_trees'][key]
                d = item['cached_data_after_native_trees'][key]
                assert b['decoded_native_tree_sha256'] == d['decoded_native_tree_sha256']
                validate_native_binding(b); validate_native_binding(d)
        if item['accepted']:
            validate_native_binding(item['native_result_tree_before_JSON'])

cases = json.loads((ROOT / 'independent12-cases087.json').read_text())['cases']
assert len(cases) == len(before['items']) == len(after['items']) == 12
assert len({json.dumps(case['scenario'], ensure_ascii=False, sort_keys=True) for case in cases}) == 12
counts = {'whole_native_and_JSON_and_3texts_same': 0, 'exact_old_errors': 0, 'new_explicit_Back_successes': 0}
details = []
ref_error = '原版动画参考与当前干员/技能不符，或该动作不适合常规逐击参考。'
for case, b, d in zip(cases, before['items'], after['items']):
    assert b['label'] == d['label'] == case['label']
    assert b['expect'] == d['expect'] == case['expect']
    assert typed(b['scenario'], d['scenario']) and typed(b['scenario'], case['scenario'])
    assert b['caller_before_native_tree']['decoded_native_tree_sha256'] == d['caller_before_native_tree']['decoded_native_tree_sha256']
    if case['expect'] == 'unchanged':
        assert b['accepted'] is True and d['accepted'] is True
        assert typed(b['result'], d['result']) and typed(b['texts'], d['texts'])
        assert b['native_result_tree_before_JSON']['decoded_native_tree_sha256'] == d['native_result_tree_before_JSON']['decoded_native_tree_sha256']
        counts['whole_native_and_JSON_and_3texts_same'] += 1
    elif case['expect'] == 'exact_error':
        assert b['accepted'] is False and d['accepted'] is False
        assert b['error_type'] == d['error_type'] == 'ValueError' and b['error'] == d['error']
        counts['exact_old_errors'] += 1
    else:
        assert b['accepted'] is False and b['error_type'] == 'ValueError' and b['error'] == ref_error
        assert d['accepted'] is True
        result = d['result']
        assert result['timing']['complete'] is False
        for stream in result['timing']['streams']:
            assert stream['exact_binding'] is False
            if 'original_animation_reference' in stream:
                assert stream['original_animation_reference']['runtime_binding_verified'] is False
                assert stream['original_animation_reference']['source_sha256'] == '09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
        counts['new_explicit_Back_successes'] += 1
    for item in [b, d]:
        if item['accepted']:
            assert set(item['texts']) == {'plain', 'technical', 'estimate'}
            assert item['texts']['plain'] == item['texts']['estimate']
    details.append({'label': case['label'], 'passed': True, 'expect': case['expect']})
assert counts == {'whole_native_and_JSON_and_3texts_same': 6, 'exact_old_errors': 2, 'new_explicit_Back_successes': 4}

new_rows = {item['label']: item for item in after['items']}
friendly = new_rows['back_s2_both_empty_enemy']['result']
assert friendly['total_healing'] == 1800
stream = friendly['timing']['streams'][0]
assert stream['target_scope'] == 'friendly' and stream['start_frames'] == [300] and stream['release_frames'] == [316]
assert stream['reference_binding'] is True and stream['exact_binding'] is False
assert new_rows['back_s2_manual_half_open']['result']['total_healing'] == 0
assert new_rows['back_normal_continuous_zero_recipient']['result']['total_healing'] == 0
unknown = new_rows['back_s1_both_unknown']['result']
assert unknown['total_healing'] is None and unknown['timing']['streams'] == []
for key in ['recharge_seconds', 'cycle_seconds', 'cycle_healing', 'cycle_hps']:
    assert unknown['estimate']['skill'][key] is None
assert new_rows['invalid_elite_before_recovered_reference']['error'] == '精英阶段需要为 0、1 或 2。'
assert new_rows['invalid_potential_before_generic_reference']['error'] == '潜能需要为 1–6。'
assert tests['actual_public_API_calls'] == 11 and tests['test_summary'] == {'tests_run': 7,
    'passed': True, 'failure_count': 0, 'error_count': 0, 'skipped_count': 0}
assert before['actual_public_API_calls'] + after['actual_public_API_calls'] + tests['actual_public_API_calls'] == 35
assert before['three_text_requests'] + after['three_text_requests'] == 48
assert tests['three_text_requests'] == 0
formatter_counts = {key: before['public_entry_counts'][key] + after['public_entry_counts'][key] + tests['public_entry_counts'][key]
    for key in ['format_estimate', 'format_report_default', 'format_report_technical']}
assert formatter_counts == {'format_estimate': 16, 'format_report_default': 32, 'format_report_technical': 16}
assert sum(formatter_counts.values()) == 64
assert before['direct_cache_snapshot_helper_requests_separate_from_production_body_entries'] == after['direct_cache_snapshot_helper_requests_separate_from_production_body_entries'] == 6

receipt = {'version': 1, 'status': 'PASS_INDEPENDENT12_PAIRS_AND_7_NEW_TESTS',
    'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'input_bindings': [b_input, d_input, t_input],
    'independent_unique_pairs': 12, 'counts': counts, 'details': details,
    'API_ledger': {'baseline': 12, 'draft': 12, 'new7tests': 11, 'total_actual_fresh_public_API_calls': 35,
        'actual_profiled_public_entries': 35, 'repeated_author35_pairs': 0},
    'three_text_requests': 48, 'actual_profiled_formatter_entries': formatter_counts,
    'actual_total_formatter_entries': 64, 'test_formatter_entries': 0,
    'direct_cache_snapshot_source_helper_requests': 12,
    'production_reference_helper_body_entries_separately_recorded': {side['mode']: side['public_entry_counts'] for side in [before, after, tests]},
    'native_before_JSON_result_type_and_value_trees_saved': True,
    'complete_native_tree_artifact_files_verified': len(native_checked),
    'native_type_nodes_observed_across_distinct_tree_files': dict(native_type_counts),
    'whole_native_results_identical_on_six_unchanged_pairs': True,
    'caller_native_type_values_unchanged_on_all35_fresh_calls': True,
    'same_process_catalog_profiles_references_native_type_values_unchanged_on_all24_pair_calls': True,
    'friendly_scope_and_half_open_manual_preview_isolation_verified': True,
    'zero_recipient_and_S1_lifecycle_unknowns_preserved': True,
    'new_tests_actual_result': tests['test_summary'],
    'author_saved35_boundary': 'Separate saved proof has exact decoded JSON type/value and three text strings only, no native before-JSON tree. Its126 is text request count, not an instrumented formatter total.',
    'new_source_parser_network_Qt_Wine_tracked_changes': 0,
    'comparator_application_API_helper_formatter_tests_calls': 0,
    'root86_transport_boundary': 'New pairs/tests used frozen author9ef baseline/draft. Root86 must integrate only approved data/tests/one registry line; root combined regression remains root-owned.',
    'runtime_native_game_clock_binding_inferred': False, 'EOF_render_or_historical_parser_rootcause_inferred': False}
path = ROOT / 'independent-numeric-and-test-review087.json'
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'receipt_sha256': sha(path.read_bytes()),
    'fresh_API_calls': 35, 'pair_counts': counts, 'formatter_entries': 64,
    'native_tree_artifacts': len(native_checked)}))
