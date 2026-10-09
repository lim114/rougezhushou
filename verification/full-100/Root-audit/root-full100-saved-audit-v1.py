"""Root independent saved-output verification; no project/helper imports."""
import argparse
import ast
import datetime
import gzip
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_tag(tag, projected):
    kind = tag['type']
    if kind == 'NoneType':
        assert projected is None and tag['value'] is None
    elif kind in ('bool', 'int', 'str'):
        expected = {'bool': bool, 'int': int, 'str': str}[kind]
        assert type(projected) is expected and tag['value'] == projected
    elif kind == 'float':
        assert type(projected) is float and float.fromhex(tag['hex']).hex() == projected.hex()
    elif kind in ('list', 'tuple'):
        assert type(projected) is list and len(tag['items']) == len(projected)
        for child, value in zip(tag['items'], projected):
            check_tag(child, value)
    elif kind == 'dict':
        assert type(projected) is dict and len(tag['items']) == len(projected)
        for (key_tag, value_tag), (key, value) in zip(tag['items'], projected.items()):
            check_tag(key_tag, key)
            check_tag(value_tag, value)
    else:
        raise AssertionError('Unknown saved type: ' + kind)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--runner', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--primary', required=True)
    parser.add_argument('--supervisor', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    receipt = json.loads((output/'wine-ui-100.json').read_bytes())
    guard_raw = Path(args.guard).read_bytes()
    guard = json.loads(guard_raw)
    supervisor = json.loads(Path(args.supervisor).read_bytes())
    assert Path(args.primary).read_bytes() == b'0\n'
    assert supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0
    assert supervisor['timed_out'] is False
    assert supervisor['owned_session_closure']['no_live_owned_execution_verified'] is True
    assert receipt['passed'] is True and receipt['complete_ui_validation'] is True
    assert receipt['total_actual_checks'] == len(receipt['checks']) == 4283
    assert not receipt['source_drift'] and not receipt['source_additional_drift']
    assert receipt['source_sha256'] == receipt['source_sha256_after'] == guard['source_sha256']
    assert receipt['source_additional_sha256'] == receipt['source_additional_sha256_after'] == guard['source_additional_sha256']
    assert receipt['source100_guard_sha256'] == sha(guard_raw)
    runner_raw = Path(args.runner).read_bytes()
    assert receipt['runner_sha256'] == sha(runner_raw)
    matrix = None
    for node in ast.walk(ast.parse(runner_raw)):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'rows090' for t in node.targets):
            assert matrix is None
            matrix = ast.literal_eval(node.value)
    assert matrix is not None and len(matrix) == 52
    archived = receipt['new_state_archive090']
    packed = (output/archived['file']).read_bytes()
    decoded = gzip.decompress(packed)
    assert len(packed) == archived['bytes'] and sha(packed) == archived['sha256']
    assert len(decoded) == archived['decoded_bytes'] and sha(decoded) == archived['decoded_sha256']
    saved = json.loads(decoded)
    states = saved['actual_new_window_states']
    assert saved['passed'] is True and saved['actual_main_window_execution_only'] is True
    assert saved['expected_UI_state_rows'] == archived['records'] == len(states) == 52
    saved_digests = []
    for actual, expected in zip(states, matrix):
        assert actual['pair_id'] == expected['pair_id'] and actual['section'] == expected['section']
        assert type(actual['widget_checked']) is bool and actual['widget_checked'] is expected['widget_checked']
        assert actual['passed'] is True
        check_tag(actual['scenario_native'], actual['scenario'])
        check_tag(actual['result_native'], actual['result'])
        result = actual['result']
        keys = ['attack', 'total_damage', 'components', 'attack_speed', 'base_attack_speed', 'interval_seconds', 'timing']
        if 'total_healing' in result:
            keys.append('total_healing')
        keys.extend(key for key in result if key.endswith('_reference'))
        projection = {key: result[key] for key in dict.fromkeys(keys)}
        projection['estimate'] = {key: result['estimate'][key] for key in ('training', 'base_stats', 'skill')}
        assert json.dumps(projection, ensure_ascii=False, sort_keys=True, allow_nan=False) == json.dumps(expected['expected_public_projection'], ensure_ascii=False, sort_keys=True, allow_nan=False)
        assert set(actual['reports']) == {'estimate', 'default', 'technical'}
        for text in actual['reports'].values():
            assert type(text) is str and text
        assert actual['reports']['estimate'] == actual['reports']['default']
        assert actual['explicit_three_text_requests'] == 3
        saved_digests.append({'pair_id': actual['pair_id'], 'widget_checked': actual['widget_checked'],
                              'saved_complete_result_tagged_sha256': sha(json.dumps(actual['result_native'], ensure_ascii=False, allow_nan=False).encode()),
                              'three_full_text_sha256': {key: sha(value.encode()) for key, value in actual['reports'].items()}})
    screenshots = receipt['screenshots100']
    assert len(screenshots) == 4
    for row in screenshots:
        raw = (output/row['file']).read_bytes()
        assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw) == row['bytes']
        assert sha(raw) == row['sha256']
    repository = Path('/workspace/rougezhushou')
    for name in ('source_sha256', 'source_additional_sha256'):
        for relative, value in guard[name].items():
            assert sha((repository/relative).read_bytes()) == value
    audit = {
        'kind': 'ROOT_ACTUAL_SAVED_OUTPUT_AUDIT',
        'verified_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'passed': True, 'actual_gui_checks': 4283, 'saved_states': 52,
        'main_source_files': len(guard['source_sha256']),
        'selected_public_projections_equal_original_matrix': 52,
        'complete_saved_result_and_three_text_digests': saved_digests,
        'full_result_equality_to_old_gold_verified': False,
        'baseline_scope': 'Original runner compares its explicit public projection; legacy source-only full-result hash fields have no bound current full-result comparison contract.',
        'three_full_texts_retained_per_state': True,
        'tagged_native_scope': 'Exact represented type, dictionary order and finite float hex; this legacy codec has no container-alias representation.',
        'native_aliases_verified_by_this_audit': False,
        'old095_complete_function_vector_measured': False,
        'png_hashes_checked': screenshots,
        'pngs_visually_inspected_by_this_script': False,
        'primary_exit': 0,
        'no_live_owned_execution_verified': True,
        'owned_session_absence_verified': supervisor['owned_session_closure']['owned_session_absence_verified'],
        'native_windows_game_chat_verified': False,
        'audit_script_sha256': sha(Path(__file__).read_bytes()),
        'saved_archive_sha256': sha(packed),
    }
    with Path(args.receipt).open('x', encoding='utf-8') as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({k: audit[k] for k in ('passed', 'actual_gui_checks', 'saved_states', 'selected_public_projections_equal_original_matrix')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
