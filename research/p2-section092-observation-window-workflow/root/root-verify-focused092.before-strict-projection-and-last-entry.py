"""Verify the actual saved window receipt, complete typed records and source freeze."""
from pathlib import Path
import gzip
import hashlib
import json
from collections import Counter

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
def sha(data):
    return hashlib.sha256(data).hexdigest()
def encode(value):
    if value is None or type(value) in (bool, int, str):
        return {'type': type(value).__name__, 'value': value}
    if type(value) is float:
        return {'type': 'float', 'hex': value.hex()}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [encode(item) for item in value]}
    if type(value) is dict:
        return {'type': 'dict', 'items': [[encode(key), encode(item)] for key, item in value.items()]}
    raise TypeError(type(value).__name__)
def decode(node):
    kind = node['type']
    if kind in ('NoneType', 'bool', 'int', 'str'):
        value = node['value']
        assert type(value).__name__ == kind
        return value
    if kind == 'float':
        return float.fromhex(node['hex'])
    if kind in ('list', 'tuple'):
        values = [decode(item) for item in node['items']]
        return values if kind == 'list' else tuple(values)
    if kind == 'dict':
        pairs = [(decode(key), decode(item)) for key, item in node['items']]
        value = dict(pairs)
        assert len(value) == len(pairs)
        return value
    raise ValueError(kind)
def native_json_pair(node, projection):
    value = decode(node)
    assert encode(value) == node
    assert json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False)) == projection
    return value

receipt_path = OUT / 'wine-focused-window-092.json'
receipt = json.loads(receipt_path.read_bytes())
assert receipt['passed'] is True and receipt['focused_window_complete'] is True
assert receipt['source_drift'] == [] and receipt['game_capture_requests'] == receipt['chat_requests'] == 0
assert receipt['native_game_clock_certified'] is False and receipt['old91_or_full90_replayed'] is False
root_source = json.loads((LOCAL / 'root-source-092.json').read_bytes())
assert root_source['passed'] is True
assert receipt['source_sha256_before'] == receipt['source_sha256_after'] == root_source['source_sha256_after']
for name, digest in root_source['source_sha256_after'].items():
    assert sha((ROOT / name).read_bytes()) == digest, name
lossless = receipt['lossless_records']
compressed = (OUT / lossless['file']).read_bytes()
assert len(compressed) == lossless['bytes'] and sha(compressed) == lossless['sha256']
decoded = gzip.decompress(compressed)
assert len(decoded) == lossless['decoded_bytes'] and sha(decoded) == lossless['decoded_sha256']
records = json.loads(decoded)
assert records['passed'] is True
plan = json.loads((LOCAL / 'ui-092-focused-final/wine-focused-window-092-plan.json').read_bytes())
states = records['states']
assert len(states) == len(plan['rows']) == len(records['checks']) == len(receipt['checks']) == 19
assert records['checks'] == receipt['checks'] and all(row['passed'] is True for row in records['checks'])
assert [row['id'] for row in states] == [row['id'] for row in plan['rows']]
text_count = numeric_count = error_count = 0
results = {}
callers = {}
for state, expected in zip(states, plan['rows']):
    assert state['planned'] == expected and state['passed'] is True
    if 'error' in expected:
        error_count += 1
        assert state['result'] is None and state['visible_error'] == expected['error']
        assert state['three_texts'] == 'inapplicable: existing error has no numerical result'
        continue
    numeric_count += 1
    caller = native_json_pair(state['scenario_native'], state['scenario'])
    result = native_json_pair(state['result_native'], state['result'])
    results[state['id']] = result
    callers[state['id']] = caller
    texts = state['reports']
    assert set(texts) == {'estimate', 'default', 'technical'}
    assert all(type(text) is str and text for text in texts.values())
    assert texts['estimate'] == texts['default']
    text_count += 3
    assert ('window_seconds' in caller) is expected['limit']
    if expected['limit']:
        assert type(caller['window_seconds']) is float and caller['window_seconds'] == expected['seconds']
    if 'effective' in expected:
        effective = expected['effective']
        assert result['estimate']['skill']['window_seconds'] == effective
        sections = {section['id']: section for section in result['report']['sections']}
        for kind in ('damage', 'healing'):
            if kind not in sections:
                continue
            metrics = {item['key']: item['value'] for item in sections[kind]['metrics']}
            assert metrics['window_seconds'] == effective
            average = 'window_dps' if kind == 'damage' else 'window_hps'
            assert (average in metrics) is bool(effective)
    if expected.get('same_native_result_as'):
        other = expected['same_native_result_as']
        assert state['scenario_native'] == encode(callers[other])
        assert state['result_native'] == encode(results[other])
    if expected.get('same_components_as'):
        assert encode(result['components']) == encode(results[expected['same_components_as']]['components'])
    if expected.get('positive_healing'):
        assert result['total_healing'] > 0 and result['estimate']['skill']['window_healing'] > 0
    if state['id'].startswith('kaltsit-S3-friendly'):
        assert result['total_damage'] == 0
        assert any('真实友方获取时钟未核验' in text for text in result['estimate']['notes'])
        if expected['mode'] == 'frames':
            assert any(stream['target_scope'] == 'friendly' for stream in result['timing']['streams'])
assert (numeric_count, error_count, text_count) == (15, 4, 45)
assert receipt['numeric_state_success_count'] == numeric_count
assert receipt['expected_error_state_count'] == error_count
assert receipt['explicit_button_requests'] == records['explicit_buttons'] == 2
assert receipt['explicit_three_text_requests'] == records['explicit_three_text_requests'] == 45
API = records['API_entries']
assert [row['sequence'] for row in API] == list(range(1, len(API) + 1))
outcomes = Counter()
for entry in API:
    outcomes[entry['outcome']] += 1
    assert entry['caller_native_unchanged'] is True
    assert entry['caller_native_before'] == entry['caller_native_after']
    native_json_pair(entry['caller_native_before'], entry['scenario'])
    if entry['outcome'] == 'returned_dict':
        native_json_pair(entry['result_native'], entry['result'])
    else:
        assert entry['outcome'] == 'raised_exception'
        assert entry['exception_events'][-1]['type'] == 'ValueError'
assert outcomes['raised_exception'] == 3
assert receipt['all_API_outcomes'] == {name: outcomes[name] for name in ('returned_dict', 'raised_exception', 'returned_non_dict_or_unobserved_unwind')}
counts = records['actual_python_entries']
assert receipt['actual_main_thread_function_entries'] == counts
assert counts['calculate_damage'] == len(API)
assert counts['MainWindow.calculate'] == len(records['MainWindow_calculate_entries'])
assert receipt['all_rouge_main_thread_entries'] == records['all_rouge_main_thread_entries']
assert receipt['focused_actual_entries']['calculate_damage'] == sum(row['step'] != 'startup' for row in API)
assert receipt['focused_automatic_numeric_entries'] == receipt['focused_actual_entries']['calculate_damage'] - 2
assert receipt['focused_API_success_entries'] == sum(row['step'] != 'startup' and row['outcome'] == 'returned_dict' for row in API)
screenshots = []
for row in plan['rows']:
    if 'screenshot' in row:
        path = OUT / row['screenshot']
        data = path.read_bytes()
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        screenshots.append({'file': path.name, 'bytes': len(data), 'sha256': sha(data), 'actual_viewed_by_root': False})
assert len(screenshots) == 2
summary = {
    'format_version': 1,
    'passed': True,
    'status': 'SAVED_ACTUAL_WINDOW_RECORDS_VERIFIED_PNG_VISUAL_REVIEW_PENDING',
    'states': 19, 'numeric_states': 15, 'expected_error_states': 4,
    'explicit_buttons': 2, 'explicit_three_text_requests': 45,
    'API_entries': len(API), 'API_outcomes': dict(outcomes),
    'actual_main_thread_function_entries': counts,
    'startup_actual_entries': receipt['startup_actual_entries'],
    'startup_and_common_actual_entries': receipt['startup_and_common_actual_entries'],
    'focused_actual_entries': receipt['focused_actual_entries'],
    'focused_automatic_API_entries_including_expected_errors': receipt['focused_automatic_numeric_entries'],
    'all_typed_native_JSON_and_caller_bindings_verified': True,
    'source730_current_and_unchanged_after_actual_window': True,
    'receipt_sha256': sha(receipt_path.read_bytes()),
    'lossless_records': lossless,
    'screenshots': screenshots,
    'project_calls_during_saved_only_verification': 0,
    'native_windows_game_verified': False,
}
with (LOCAL / 'root-focused092-saved-verification.json').open('xb') as stream:
    stream.write((json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps(summary, ensure_ascii=False))
