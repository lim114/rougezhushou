"""Independent readback of actual full261 states and frozen evidence, no rerun.

Decode tagged captured Python values, preserve float.hex and tuple types, and
check roundtrip/ordered plain JSON. The native090 codec records Python values;
it is not native game execution. Do not dump captured scenario/results to chat.
"""
import argparse
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

CODEC_SHA = 'ec8c1e37d372c5ec81de99c2d6cbeb18fe4763ba211d4f01a83a04fd1a6ae7c7'
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ordered(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def encode(value):
    kind = type(value).__name__
    if value is None or type(value) in (bool, int, str):
        return {'type': kind, 'value': value}
    if type(value) is float:
        return {'type': 'float', 'hex': value.hex()}
    if type(value) in (list, tuple):
        return {'type': kind, 'items': [encode(v) for v in value]}
    if type(value) is dict:
        return {'type': 'dict', 'items': [[encode(k), encode(v)] for k, v in value.items()]}
    raise ValueError('Unexpected captured value type')


def decode(node, counts):
    assert type(node) is dict
    kind = node['type']
    counts[kind] += 1
    if kind in ('NoneType', 'bool', 'int', 'str'):
        assert set(node) == {'type', 'value'}
        expected = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str}[kind]
        assert type(node['value']) is expected
        return node['value']
    if kind == 'float':
        assert set(node) == {'type', 'hex'} and type(node['hex']) is str
        value = float.fromhex(node['hex'])
        assert value.hex() == node['hex']
        return value
    if kind in ('list', 'tuple', 'dict'):
        assert set(node) == {'type', 'items'} and type(node['items']) is list
        if kind == 'dict':
            assert all(type(pair) is list and len(pair) == 2 for pair in node['items'])
            pairs = [(decode(k, counts), decode(v, counts)) for k, v in node['items']]
            result = dict(pairs)
            assert len(result) == len(pairs)
            return result
        values = [decode(item, counts) for item in node['items']]
        return tuple(values) if kind == 'tuple' else values
    raise ValueError('Unknown captured codec tag')


def audit(root, container, bundle, freeze):
    actual = container / 'actual'
    receipt_raw = (actual / 'wine-ui-100.json').read_bytes()
    receipt = json.loads(receipt_raw)
    guard_raw = (bundle / 'current-source-guard.json').read_bytes()
    guard = json.loads(guard_raw)
    static = json.loads((bundle / 'static-preservation.json').read_bytes())
    closure = json.loads((actual / 'full125-bridge-closure.json').read_bytes())
    ledger_raw = (actual / 'full125-113-bridge-ledger.json').read_bytes()
    ledger = json.loads(ledger_raw)
    mapping_raw = (bundle / 'expected-map125.json').read_bytes()
    mapping = json.loads(mapping_raw)
    supervisor = json.loads((container / 'supervisor.json').read_bytes())
    process_exit = int((container / 'process.exit').read_text().strip())
    assert process_exit == supervisor['supervisor_exit'] == supervisor['child_primary_exit'] == 0
    assert supervisor['status'] == 'completed' and supervisor['timed_out'] is False
    assert receipt['passed'] is True and receipt['complete_ui_validation'] is True
    assert receipt['source_drift'] == receipt['source_additional_drift'] == []
    assert receipt['total_actual_checks'] == 4283 and len(receipt['checks']) == 4283
    assert sum(r.get('passed') is True for r in receipt['checks']) == 4281
    assert sum('passed' not in r for r in receipt['checks']) == 2
    assert receipt['new_explicit_damage_button_requests090'] == 52
    assert receipt['new_explicit_three_text_requests090'] == 156
    assert static['current_assertions'] == 862 and static['unchanged_original_assertions_outside_helpers'] == 807
    assert static['original_functional_try_assertions'] == 552
    assert static['functional_try_bytes_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
    assert receipt['source100_guard_sha256'] == digest(guard_raw)
    drift = []
    for kind in ('source_sha256', 'source_additional_sha256'):
        for relative, expected in guard[kind].items():
            p = root / relative
            if p.is_symlink() or digest(p.read_bytes()) != expected:
                drift.append(relative)
    assert drift == []
    root_freeze = json.loads(freeze.read_bytes())
    frozen = root_freeze['source_sha256']
    common = set(frozen) & set(guard['source_sha256'])
    assert all(frozen[p] == guard['source_sha256'][p] for p in common)
    assert set(frozen) - set(common) == {'CORE_0.70_VERIFICATION.json'}
    assert guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json'] == frozen['CORE_0.70_VERIFICATION.json']
    assert set(guard['source_sha256']) - set(common) == {'tests/offline_scope_retirement.py'}
    window_raw = (bundle / 'window.py').read_bytes()
    tree = ast.parse(window_raw.decode('utf-8'))
    codec = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'native090')
    assert digest(ast.get_source_segment(window_raw.decode('utf-8'), codec).encode()) == CODEC_SHA
    archive_metadata = receipt['new_state_archive090']
    archive_name = archive_metadata['file']
    assert archive_name == 'wine-ui-new-states-100.json.gz'
    compressed = (actual / archive_name).read_bytes()
    decoded = gzip.decompress(compressed)
    assert len(compressed) == archive_metadata['bytes'] and digest(compressed) == archive_metadata['sha256']
    assert len(decoded) == archive_metadata['decoded_bytes'] and digest(decoded) == archive_metadata['decoded_sha256']
    archive = json.loads(decoded)
    rows = archive['actual_new_window_states']
    assert archive['passed'] is True and archive['actual_main_window_execution_only'] is True
    assert archive['expected_UI_state_rows'] == archive_metadata['records'] == len(rows) == 52
    assert Counter(r['section'] for r in rows) == {86: 44, 88: 8}
    assert len({(r['section'], r['pair_id'], r['widget_checked']) for r in rows}) == 52
    trace_counts = Counter(); tags = Counter(); row_audit = []
    for i, row in enumerate(rows):
        assert row['passed'] is True and type(row['widget_checked']) is bool
        assert row['explicit_three_text_requests'] == 3
        assert row['actual_entries']['calculate_damage'] == 1
        assert row['actual_entries']['RunState.__init__'] == 0
        assert row['actual_entries']['format_estimate'] == 1
        assert set(row['reports']) == {'estimate', 'default', 'technical'}
        assert row['reports']['estimate'] == row['reports']['default']
        assert all(type(value) is str and value for value in row['reports'].values())
        for name in ('scenario', 'result'):
            native = row[name + '_native']
            value = decode(native, tags)
            assert encode(value) == native
            assert ordered(value) == ordered(row[name])
        trace_counts[ordered(row['actual_same_call_readonly_trace'])] += 1
        row_audit.append({'index': i, 'section': row['section'], 'pair_id': row['pair_id'],
                          'checked': row['widget_checked'],
                          'scenario_native_sha256_json_ordered': digest(ordered(row['scenario_native']).encode()),
                          'result_native_sha256_json_ordered': digest(ordered(row['result_native']).encode()),
                          'actual_entries': row['actual_entries']})
    admissions = sorted(ledger['actual_admissions'], key=lambda r: r['literal_index'])
    assert ledger['all10_admitted'] is True and len(admissions) == 10
    assert ledger['expected_literal_indices'] == [r['literal_index'] for r in admissions] == INDICES
    assert ledger['mapping_sha256'] == digest(mapping_raw)
    saved_by_identity = {(r['section'], r['pair_id'], r['widget_checked']): r for r in rows}
    for actual_row, proved in zip(admissions, mapping['rows']):
        for key in ('literal_index', 'section', 'pair_id', 'widget_checked',
                    'full_source_row_sha256_json_ordered', 'input_sha256_json_ordered'):
            assert type(actual_row[key]) is type(proved[key]) and actual_row[key] == proved[key]
        assert actual_row['raw_result_and_caller_unchanged'] is True
        saved = saved_by_identity[actual_row['section'], actual_row['pair_id'], actual_row['widget_checked']]
        assert digest(ordered(saved['scenario_native']).encode()) == actual_row['actual_caller_native090_sha256']
        assert actual_row['actual_caller_native090_sha256'] == actual_row['Root_original_caller_native090_sha256']
    assert closure['passed'] is True and closure['workflow_complete'] is True
    assert closure['source_drift'] == closure['source_additional_drift'] == []
    assert closure['window_primary_code'] == 0 and closure['window_receipt_sha256'] == digest(receipt_raw)
    assert closure['ledger_sha256'] == digest(ledger_raw) and closure['guard_sha256'] == digest(guard_raw)
    assert closure['window_sha256'] == digest(window_raw)
    assert closure['launcher_sha256'] == digest((bundle / 'launcher125.py').read_bytes())
    return {'kind': 'INDEPENDENT_FULL261_COMPLETE_WINDOW_READBACK', 'passed': True,
            'section': 261, 'actual_attempt': guard['actual_full261_attempt'], 'process_exit': process_exit,
            'child_primary_exit': supervisor['child_primary_exit'], 'supervisor_exit': supervisor['supervisor_exit'],
            'actual_runtime_seconds': supervisor['elapsed_seconds'], 'timeout': False,
            'complete_runtime_checks': 4283, 'passed_flag_records': 4281, 'metadata_records': 2,
            'current_revised_assertions': 862, 'original_assertions_outside_two_helpers': 807,
            'historical831_unchanged_claimed': False, 'original552_maintry_sha256': static['functional_try_bytes_sha256'],
            'saved_rows': 52, 'row_sections': {'86': 44, '88': 8},
            'codec_exact_typed_roundtrip': True, 'codec_plain_JSON_order_and_values_match': True,
            'codec_tag_counts': dict(tags), 'native_codec_source_sha256': CODEC_SHA,
            'native_codec_is_capture_serializer_not_native_game_execution': True,
            'readonly_trace_variants_preserved': dict(trace_counts), 'readonly_trace_empty_rows_not_invented': trace_counts['[]'],
            'compressed_archive_sha256': digest(compressed), 'decoded_archive_sha256': digest(decoded),
            'archive_declared_hash_and_size_match': True,
            'exact_ten_admission_indices': INDICES, 'exact_ten_identity_types_input_and_full_row_hash_match': True,
            'maintained_source_count': len(guard['source_sha256']), 'additional_source_count': len(guard['source_additional_sha256']),
            'source_and_additional_drift': drift, 'root_freeze_common_source_count': len(common),
            'root_freeze_CORE_protected_by_additional': True,
            'guard_extra_source_preserved': 'tests/offline_scope_retirement.py',
            'native_windows_verified': False, 'game_actions': 0, 'chat_requests': 0,
            'PNG_visual_inspection_claimed_by_this_readback': False, 'rows': row_audit}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--container', required=True, type=Path)
    p.add_argument('--bundle', required=True, type=Path)
    p.add_argument('--freeze', required=True, type=Path)
    args = p.parse_args()
    record = audit(args.root.resolve(), args.container.resolve(), args.bundle.resolve(), args.freeze.resolve())
    out = args.container / 'independent-saved-readback-audit.json'
    with out.open('x', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({k: v for k, v in record.items() if k not in ('rows', 'readonly_trace_variants_preserved')}, ensure_ascii=False))
