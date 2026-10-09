"""Root executes this independent stdlib-only saved-output audit after full115."""
import argparse
import ast
import copy
import datetime
import gzip
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re

INDICES = (18, 19, 20, 21, 38, 39, 40, 41, 44, 45)
METRICS = ('window_seconds', 'window_dps', 'window_hps')
ADMISSION_SHA113 = 'a32b857a4b9241a55714c7027bb537f04fec0918e442d94e40dd098fc0ebdacf'
BRIDGE_SHA = 'e054ed7e7fa81ee2a3187f7710017940b63b07fc275d262bcc482bba60304c1a'
FUNCTIONAL_TRY_SHA = '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
ASSERT_AST_SHA = '39e4e712593b1576a96f7355d0ce9ee2e4f801aa366da6bd9dc22b8f405f1916'
SUPERVISOR_SHA = '705e2be5804663754119d64caefa2b171e5879997e2cdbf882688c14128fe782'
LAUNCHER_TEMPLATE_SHA = '3b23065af979f846120e841ea34512dcbf178f9219580f68e9908d22180cfaac'
TUPLE_SEAMS21 = (('external_event_reference', 'parameter_rows', 0),
                 ('external_event_reference', 'window_reference', 'parameter_rows', 0))
PROOFS = {'original_primary', 'candidate_primary', 'original_receipt', 'candidate_receipt',
          'original_guard', 'candidate_guard', 'pair_audit'}
PNG_NAMES = ('wine-sown-tile-control-100.png', 'wine-movement-reference-100.png',
             'wine-medical-trait-100.png', 'wine-window-100.png')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')

def digest(value):
    return sha(encoded(value))

def strict_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)

def check_tag(tag, projected):
    kind = tag['type']
    if kind == 'NoneType':
        assert projected is None and tag['value'] is None
    elif kind in ('bool', 'int', 'str'):
        expected = {'bool': bool, 'int': int, 'str': str}[kind]
        assert type(projected) is expected and tag['value'] == projected
    elif kind == 'float':
        assert type(projected) is float and math.isfinite(projected)
        assert float.fromhex(tag['hex']).hex() == projected.hex()
    elif kind in ('list', 'tuple'):
        # JSON represents both as lists. The original native type stays in tag.
        assert type(projected) is list and len(tag['items']) == len(projected)
        for child, value in zip(tag['items'], projected):
            check_tag(child, value)
    elif kind == 'dict':
        assert type(projected) is dict and len(tag['items']) == len(projected)
        for (key_tag, value_tag), (key, value) in zip(tag['items'], projected.items()):
            check_tag(key_tag, key); check_tag(value_tag, value)
    else:
        raise AssertionError('Unknown saved type: ' + kind)

def tagged(value):
    kind = type(value).__name__
    if value is None or type(value) in (bool, int, str):
        return {'type': kind, 'value': value}
    if type(value) is float:
        assert math.isfinite(value)
        return {'type': 'float', 'hex': value.hex()}
    if type(value) in (list, tuple):
        return {'type': kind, 'items': [tagged(item) for item in value]}
    assert type(value) is dict
    return {'type': 'dict', 'items': [[tagged(key), tagged(item)] for key, item in value.items()]}

def field(tag, key):
    assert tag['type'] == 'dict'
    found = [value for name, value in tag['items'] if name == tagged(key)]
    assert len(found) == 1
    return found[0]

def at(tag, path):
    for key in path:
        if type(key) is int:
            assert tag['type'] in ('list', 'tuple'); tag = tag['items'][key]
        else:
            tag = field(tag, key)
    return tag

def projection(result):
    keys = ['attack', 'total_damage', 'components', 'attack_speed', 'base_attack_speed', 'interval_seconds', 'timing']
    if 'total_healing' in result:
        keys.append('total_healing')
    keys.extend(key for key in result if key.endswith('_reference'))
    value = {key: result[key] for key in dict.fromkeys(keys)}
    value['estimate'] = {key: result['estimate'][key] for key in ('training', 'base_stats', 'skill')}
    return value

def projection_tags(result, native):
    value = projection(result)
    rows = [[tagged(key), field(native, key)] for key in value if key != 'estimate']
    estimate = field(native, 'estimate')
    rows.append([tagged('estimate'), {'type': 'dict', 'items': [
        [tagged(key), field(estimate, key)] for key in ('training', 'base_stats', 'skill')]}])
    return {'type': 'dict', 'items': rows}

def scalar(present, value):
    assert type(present) is bool
    if not present:
        return {'present': False, 'python_type': None, 'value': None, 'float_hex': None}
    assert value is None or type(value) in (int, float)
    assert type(value) is not float or math.isfinite(value)
    return {'present': True, 'python_type': type(value).__name__, 'value': value,
            'float_hex': value.hex() if type(value) is float else None}

def leaves(row):
    metrics = row['metric_leaf_admission']
    assert tuple(metrics) == tuple('estimate.skill.' + key for key in METRICS)
    output = {}; changed = []
    for path, leaf in metrics.items():
        old = scalar(leaf['old_present'], leaf['old_source_value'])
        new = scalar(leaf['actual_candidate_present'], leaf['actual_candidate_value'])
        assert old['present'] is new['present'] and old['python_type'] == new['python_type']
        assert leaf['old_python_type'] == old['python_type'] and leaf['old_float_hex'] == old['float_hex']
        assert leaf['actual_candidate_python_type'] == new['python_type'] and leaf['actual_candidate_float_hex'] == new['float_hex']
        assert type(leaf['actual_changed']) is bool and leaf['actual_changed'] is (encoded(old) != encoded(new))
        output[path] = {'old_source': old, 'actual_new': new, 'actual_changed': leaf['actual_changed']}
        if leaf['actual_changed']:
            changed.append(path)
    assert changed and changed[0] == 'estimate.skill.window_seconds'
    assert set(changed) <= {'estimate.skill.window_seconds', 'estimate.skill.window_dps'}
    return output, changed

def plain_json(path, frozen):
    path = Path(path).resolve(); raw = path.read_bytes(); frozen[path] = raw
    return json.loads(raw), raw

def regular_leaf(base, name):
    assert type(name) is str and name == Path(name).name and name not in ('', '.', '..')
    path = Path(base) / name; assert not path.is_symlink() and path.is_file()
    return path

def proof_files(admission, folder, frozen):
    pins = admission['proof_files']; assert set(pins) == PROOFS
    parts_all = []; raw_files = {}
    reserved = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)), *(f'lpt{i}' for i in range(1, 10))}
    for name, pin in pins.items():
        assert set(pin) == {'path', 'bytes', 'sha256'}
        text = pin['path']; relative = PurePosixPath(text); parts = relative.parts
        assert type(text) is str and '\\' not in text and ':' not in text and not relative.is_absolute()
        assert len(parts) >= 2 and parts[0] == 'proofs' and '/'.join(parts) == text
        for part in parts:
            assert re.fullmatch(r'[a-z0-9][a-z0-9._-]*', part) and not part.endswith('.')
            assert part.split('.', 1)[0] not in reserved
        folded = tuple(part.casefold() for part in parts)
        for prior in parts_all:
            assert prior[:len(folded)] != folded and folded[:len(prior)] != prior
        parts_all.append(folded); path = Path(folder)
        assert not path.is_symlink()
        for part in parts:
            path = path / part; assert not path.is_symlink()
        assert path.is_file() and path.resolve().is_relative_to(Path(folder).resolve())
        raw = path.read_bytes(); frozen[path.resolve()] = raw
        assert type(pin['bytes']) is int and pin['bytes'] >= 0 and len(raw) == pin['bytes'] and sha(raw) == pin['sha256']
        raw_files[name] = raw
    for name in ('original_primary', 'candidate_primary'):
        assert raw_files[name] == b'0\n'
    for name, key in (('original_guard', 'actual113_original_guard_sha256'), ('candidate_guard', 'actual113_candidate_guard_sha256'),
        ('original_primary', 'Root_actual_original_primary_exit_sha256'), ('candidate_primary', 'Root_actual_candidate_primary_exit_sha256')):
        assert admission[key] == pins[name]['sha256']
    audit = json.loads(raw_files['pair_audit'])
    assert audit['kind'] == 'ROOT_ACTUAL_113_SAME_INPUT_PROJECTION_AUDIT' and audit['passed'] is True
    assert audit['literal_indices'] == list(INDICES)
    for key in ('same_full_callers', 'only_measured_window_metric_leaves_changed', 'caller_and_three_formatter_purity', 'whole_source_and_CORE_stable'):
        assert audit[key] is True
    assert len(audit['rows']) == 10
    for admitted, proved in zip(admission['rows'], audit['rows']):
        for key in ('literal_index', 'full_source_row_sha256_json_ordered', 'input_sha256_json_ordered',
            'original_projection_native090_sha256', 'candidate_projection_native090_sha256',
            'original_caller_native090_sha256', 'candidate_caller_native090_sha256'):
            assert type(admitted[key]) is type(proved[key]) and admitted[key] == proved[key]
        assert proved['metric_leaf_admission_sha256'] == digest(admitted['metric_leaf_admission'])
        paths = ['.'.join(map(str, path)) for path in TUPLE_SEAMS21] if admitted['literal_index'] == 21 else []
        assert proved['qualified_historical_JSON_tuple_list_paths'] == paths
        for key, name in (('Root_actual_original_receipt_sha256', 'original_receipt'),
            ('Root_actual_candidate_receipt_sha256', 'candidate_receipt'), ('Root_actual_pair_audit_sha256', 'pair_audit')):
            assert admitted[key] == pins[name]['sha256']
    return audit

def source_maps(root, guard):
    found = {}
    for name in ('rouge', 'tests', 'scripts'):
        folder = root / name; assert folder.is_dir()
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(root)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            assert not path.is_symlink()
            if path.is_file():
                found[relative.as_posix()] = sha(path.read_bytes())
    assert dict(sorted(found.items())) == guard['source_sha256']
    assert 'CORE_0.70_VERIFICATION.json' in guard['source_additional_sha256']
    for name, expected in guard['source_additional_sha256'].items():
        path = root / name
        assert not Path(name).is_absolute() and '..' not in Path(name).parts and not path.is_symlink()
        assert path.resolve().is_relative_to(root) and sha(path.read_bytes()) == expected

def main():
    parser = argparse.ArgumentParser()
    for name in ('out', 'runner', 'guard', 'primary', 'supervisor', 'supervisor-source', 'receipt', 'launcher', 'bridge-source', 'admission'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--source-count', type=int, required=True)
    parser.add_argument('--root', default='/workspace/rougezhushou')
    args = parser.parse_args(); output = Path(args.out).resolve(); root = Path(args.root).resolve()
    target = Path(args.receipt).resolve(); assert not target.exists() and target != root and root not in target.parents
    frozen = {}; receipt, receipt_raw = plain_json(output / 'wine-ui-100.json', frozen)
    guard, guard_raw = plain_json(args.guard, frozen); supervisor, supervisor_raw = plain_json(args.supervisor, frozen)
    closure, closure_raw = plain_json(output / 'full115-bridge-closure.json', frozen)
    ledger, ledger_raw = plain_json(output / 'full115-113-bridge-ledger.json', frozen)
    admission, admission_raw = plain_json(args.admission, frozen)
    for key, code in (('child_primary_exit', supervisor['child_primary_exit']), ('supervisor_exit', supervisor['supervisor_exit'])):
        assert type(code) is int and code == 0
    primary = Path(args.primary).resolve(); primary_raw = primary.read_bytes(); frozen[primary] = primary_raw
    assert primary_raw == b'0\n' and supervisor['timed_out'] is False and supervisor['status'] == 'completed'
    assert supervisor['after_section'] == 115 and supervisor['global_wineserver_terminated'] is False
    owned = supervisor['owned_session_closure']; members = owned['owned_session_members_after_completion']
    assert owned['proc_entries_unreadable'] == [] and owned['no_live_owned_execution_verified'] is True
    assert owned['potentially_live_owned_session_pids_after_completion'] == []
    assert all(type(member['pid']) is int and member['state'] == 'Z' for member in members)
    assert owned['owned_session_pids_after_completion'] == [member['pid'] for member in members]
    assert owned['zombie_owned_session_pids_after_completion'] == [member['pid'] for member in members]
    assert owned['owned_session_absence_verified'] is (not members) and owned['retained_zombies_reaped_by_supervisor'] is False
    for key in ('stdout', 'stderr'):
        log = regular_leaf(Path(args.supervisor).resolve().parent, supervisor[key]['file']); raw = log.read_bytes(); frozen[log.resolve()] = raw
        assert len(raw) == supervisor[key]['bytes'] and sha(raw) == supervisor[key]['sha256']
    assert receipt['passed'] is True and receipt['complete_ui_validation'] is True and not receipt.get('failure')
    assert type(guard['section']) is int and guard['section'] == receipt['after_section'] == 115
    assert args.source_count == len(guard['source_sha256']) == receipt['current_maintained_source_count_expected']
    assert receipt['total_actual_checks'] == len(receipt['checks']) == 4283
    assert all(type(check) is dict and type(check['scope']) is str and check.get('passed', True) is True for check in receipt['checks'])
    assert receipt['new_explicit_damage_button_requests090'] == 52 and receipt['new_explicit_three_text_requests090'] == 156
    assert receipt['native_windows_verified'] is False and receipt['game_captures'] == receipt['chat_requests'] == 0
    assert receipt['private_state_isolated'] is True and receipt['old095_complete_function_vector_measured'] is False
    assert receipt['source_drift'] == receipt['source_additional_drift'] == []
    assert receipt['source_sha256'] == receipt['source_sha256_after'] == guard['source_sha256']
    assert receipt['source_additional_sha256'] == receipt['source_additional_sha256_after'] == guard['source_additional_sha256']
    assert receipt['source100_guard_sha256'] == sha(guard_raw)
    assert (output / 'source100-guard-input.json').read_bytes() == guard_raw
    source_maps(root, guard)
    artifacts = {}
    for name, value in (('window.py', args.runner), ('launcher115.py', args.launcher), ('bridge115.py', args.bridge_source), ('supervisor115.py', args.supervisor_source)):
        path = Path(value).resolve(); assert not path.is_symlink(); raw = path.read_bytes(); frozen[path] = raw; artifacts[name] = raw
    assert all(Path(value).resolve().parent == Path(args.runner).resolve().parent for value in (args.launcher, args.bridge_source, args.admission, args.supervisor_source))
    assert receipt['runner_sha256'] == sha(artifacts['window.py'])
    assert supervisor['supervisor_sha256'] == sha(artifacts['supervisor115.py']) == SUPERVISOR_SHA
    assert sha(artifacts['bridge115.py']) == BRIDGE_SHA and sha(admission_raw) == ADMISSION_SHA113
    assert guard['full115_113_bridge_sha256'] == {'bridge115.py': BRIDGE_SHA, 'expected-map115.json': ADMISSION_SHA113}
    launcher = artifacts['launcher115.py'].decode()
    for name, value in (('WINDOW_SHA256', sha(artifacts['window.py'])), ('SOURCE115_GUARD_SHA256', sha(guard_raw))):
        active = name + ' = ' + repr(value)
        assert launcher.count(active) == 1; launcher = launcher.replace(active, name + ' = None')
    assert sha(launcher.encode()) == LAUNCHER_TEMPLATE_SHA
    runner_tree = ast.parse(artifacts['window.py']); original_asserts = [ast.dump(n, include_attributes=False) for n in ast.walk(runner_tree) if isinstance(n, ast.Assert)]
    assert len(original_asserts) == 831 and sha(json.dumps(original_asserts, separators=(',', ':')).encode()) == ASSERT_AST_SHA
    functional = max((n for n in ast.walk(runner_tree) if isinstance(n, ast.Try)), key=lambda n: n.end_lineno - n.lineno)
    functional_raw = ast.get_source_segment(artifacts['window.py'].decode(), functional).encode()
    assert len(functional_raw) == 593858 and sha(functional_raw) == FUNCTIONAL_TRY_SHA
    matrices = [ast.literal_eval(n.value) for n in ast.walk(runner_tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'rows090' for t in n.targets)]
    assert len(matrices) == 1 and len(matrices[0]) == 52; matrix = matrices[0]
    assert admission['kind'] == 'ROOT_ACTUAL_113_NARROW_WINDOW_METRIC_ADMISSION' and admission['ready'] is True
    assert tuple(row['literal_index'] for row in admission['rows']) == INDICES and admission['future_actual115_guard_sha256'] is None
    pair_audit = proof_files(admission, Path(args.admission).resolve().parent, frozen)
    assert ledger['kind'] == 'ACTUAL_FULL115_COMPARISON_ONLY_BRIDGE_LEDGER' and ledger['mapping_sha256'] == ADMISSION_SHA113
    assert ledger['Root_actual_pair_audit_sha256'] == admission['proof_files']['pair_audit']['sha256']
    assert ledger['expected_literal_indices'] == list(INDICES) and ledger['all10_admitted'] is True
    assert ledger['project_or_full_window_pass_claimed'] is False
    actual_admissions = ledger['actual_admissions']; assert tuple(row['literal_index'] for row in actual_admissions) == INDICES
    assert closure['kind'] == 'ROOT_ACTUAL_FULL115_WINDOW_BRIDGE_CLOSURE' and closure['passed'] is True and closure['workflow_complete'] is True
    assert type(closure['window_primary_code']) is int and closure['window_primary_code'] == 0
    assert closure['source_drift'] == closure['source_additional_drift'] == [] and closure['Saved_and_PNG_inspection_claimed'] is False
    for key, expected in (('window_receipt_sha256', sha(receipt_raw)), ('ledger_sha256', sha(ledger_raw)),
        ('launcher_sha256', sha(artifacts['launcher115.py'])), ('window_sha256', sha(artifacts['window.py'])), ('guard_sha256', sha(guard_raw))):
        assert closure[key] == expected
    archived = receipt['new_state_archive090']; packed_path = regular_leaf(output, archived['file']); packed = packed_path.read_bytes(); frozen[packed_path.resolve()] = packed
    decoded = gzip.decompress(packed)
    assert len(packed) == archived['bytes'] and sha(packed) == archived['sha256']
    assert len(decoded) == archived['decoded_bytes'] and sha(decoded) == archived['decoded_sha256']
    saved = json.loads(decoded); states = saved['actual_new_window_states']
    assert saved['passed'] is True and saved['actual_main_window_execution_only'] is True
    assert saved['expected_UI_state_rows'] == archived['records'] == len(states) == 52
    digests = []; isolated_rows = []; identities = set()
    admitted_by_index = dict(zip(INDICES, admission['rows'])); ledger_by_index = dict(zip(INDICES, actual_admissions))
    for index, (actual, expected) in enumerate(zip(states, matrix)):
        identity = (actual['section'], actual['pair_id'], actual['widget_checked']); assert identity not in identities; identities.add(identity)
        for key in ('section', 'pair_id', 'widget_checked'):
            assert type(actual[key]) is type(expected[key]) and actual[key] == expected[key]
        assert type(actual['widget_checked']) is bool and actual['passed'] is True
        check_tag(actual['scenario_native'], actual['scenario']); check_tag(actual['result_native'], actual['result'])
        assert 'base_attack' not in actual['scenario']
        for key, value in expected['input'].items():
            assert field(actual['scenario_native'], key) == tagged(value)
        public = projection(actual['result']); public_native = projection_tags(actual['result'], actual['result_native'])
        if index not in admitted_by_index:
            assert strict_json(public) == strict_json(expected['expected_public_projection'])
        else:
            admitted = admitted_by_index[index]; entry = ledger_by_index[index]
            assert admitted['expected_mapping_ready'] is True and digest(expected) == admitted['full_source_row_sha256_json_ordered']
            assert digest(expected['input']) == admitted['input_sha256_json_ordered']
            assert digest(public_native) == admitted['candidate_projection_native090_sha256']
            assert digest(actual['scenario_native']) == admitted['candidate_caller_native090_sha256'] == admitted['original_caller_native090_sha256']
            measured, changed = leaves(admitted); historical = copy.deepcopy(public); historical_native = copy.deepcopy(public_native)
            old_skill = expected['expected_public_projection']['estimate']['skill']; new_skill = public['estimate']['skill']
            for path, leaf in measured.items():
                name = path.rsplit('.', 1)[1]
                assert encoded(scalar(name in old_skill, old_skill.get(name))) == encoded(leaf['old_source'])
                assert encoded(scalar(name in new_skill, new_skill.get(name))) == encoded(leaf['actual_new'])
                if leaf['actual_changed']:
                    historical['estimate']['skill'][name] = old_skill[name]
                    native_leaf = at(historical_native, ('estimate', 'skill', name)); native_leaf.clear(); native_leaf.update(tagged(old_skill[name]))
            assert digest(historical_native) == admitted['original_projection_native090_sha256']
            assert strict_json(historical) == strict_json(expected['expected_public_projection'])
            qualified = copy.deepcopy(historical_native)
            if index == 21:
                for path in TUPLE_SEAMS21:
                    seam = at(qualified, path); literal = at(tagged(expected['expected_public_projection']), path)
                    assert seam['type'] == 'tuple' and literal['type'] == 'list' and len(seam['items']) == len(literal['items']) == 3
                    assert tuple(item['type'] for item in seam['items']) == ('str', 'float', 'str')
                    assert encoded(seam['items']) == encoded(literal['items']); seam['type'] = 'list'
            assert encoded(qualified) == encoded(tagged(expected['expected_public_projection']))
            for key in ('literal_index', 'section', 'pair_id', 'widget_checked', 'full_source_row_sha256_json_ordered', 'input_sha256_json_ordered'):
                assert type(entry[key]) is type(admitted[key]) and entry[key] == admitted[key]
            assert entry['actual_candidate_projection_native090_sha256'] == digest(public_native)
            assert entry['actual_caller_native090_sha256'] == digest(actual['scenario_native'])
            assert entry['Root_original_caller_native090_sha256'] == admitted['original_caller_native090_sha256']
            assert entry['comparison_only_exceptions'] == changed and encoded(entry['metric_leaves']) == encoded(measured)
            assert entry['raw_result_and_caller_unchanged'] is True and entry['mapping_sha256'] == ADMISSION_SHA113
            assert entry['Root_actual_pair_audit_sha256'] == admission['proof_files']['pair_audit']['sha256']
            isolated_rows.append({'literal_index': index, 'comparison_only_exceptions': changed,
                'candidate_projection_native090_sha256': digest(public_native), 'original_restored_projection_native090_sha256': digest(historical_native),
                'actual_caller_native090_sha256': digest(actual['scenario_native']), 'qualified_historical_JSON_tuple_list_paths': ['.'.join(map(str, p)) for p in TUPLE_SEAMS21] if index == 21 else []})
        assert set(actual['reports']) == {'estimate', 'default', 'technical'}
        assert all(type(text) is str and text for text in actual['reports'].values())
        assert actual['reports']['estimate'] == actual['reports']['default'] and actual['explicit_three_text_requests'] == 3
        corresponding = [check for check in receipt['checks'] if check.get('scope') in ('actual_boolean_checkbox_and_public_readonly_source090', 'actual_continuous_checkbox_and_JSON_editor_source088')
            and check.get('section') == actual['section'] and check.get('pair_id') == actual['pair_id'] and check.get('checked') is actual['widget_checked']]
        assert len(corresponding) == 1 and corresponding[0]['passed'] is True and corresponding[0]['three_texts_match_own_result'] is True
        digests.append({'pair_id': actual['pair_id'], 'widget_checked': actual['widget_checked'],
            'saved_complete_result_tagged_sha256': sha(json.dumps(actual['result_native'], ensure_ascii=False, allow_nan=False).encode()),
            'saved_complete_caller_native090_sha256': digest(actual['scenario_native']),
            'three_full_text_sha256': {key: sha(value.encode()) for key, value in actual['reports'].items()}})
    assert tuple(row['literal_index'] for row in isolated_rows) == INDICES
    screenshots = receipt['screenshots100']; assert tuple(row['file'] for row in screenshots) == PNG_NAMES
    for row in screenshots:
        path = regular_leaf(output, row['file']); raw = path.read_bytes(); frozen[path.resolve()] = raw
        assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw) == row['bytes'] and sha(raw) == row['sha256']
    source_maps(root, guard)
    assert all(path.read_bytes() == raw for path, raw in frozen.items())
    audit = {'kind': 'ROOT_ACTUAL_FULL115_SAVED_OUTPUT_AUDIT', 'after_section': 115,
        'workflow_complete': True, 'source_drift': [], 'passed': True,
        'verified_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'actual_gui_checks': 4283, 'saved_states': 52, 'main_source_files': args.source_count,
        'original_831_Assert_AST_order_same': True, 'whole_functional_Try_byte_same': True,
        'selected_public_projections_equal_original_matrix_without_exceptions': 42,
        'ten_admitted_projection_comparison_copies_equal_original_matrix': 10,
        'only_actual_measured_window_seconds_and_window_dps_exceptions': isolated_rows,
        'window_hps_exception_allowed': False, 'complete_saved_result_and_three_text_digests': digests,
        'full_result_equality_to_old_gold_verified': False,
        'baseline_scope': '42 original explicit JSON public projections and10 complete typed projections bound to actual113 original/candidate proof. Legacy source-only full-result hash fields have no bound current full-result comparison contract.',
        'three_full_current_texts_retained_per_state': True,
        'runner_full_result_caller_and_three_formatter_purity_assertions_completed': True,
        'formatter_purity_scope': 'Bound unchanged functional runner actual0 checked full native result/caller before and after current formatters and real technical toggles; legacy saved states have no separate after-formatter graph for independent saved re-comparison.',
        'tagged_native_scope': 'Exact represented type, dictionary order and finite float hex; legacy codec has no container-alias or cycle identity representation.',
        'native_aliases_verified_by_this_audit': False, 'old095_complete_function_vector_measured': False,
        'png_hashes_checked': screenshots, 'pngs_visually_inspected_by_this_script': False,
        'primary_exit': 0, 'child_primary_exit': supervisor['child_primary_exit'], 'supervisor_exit': supervisor['supervisor_exit'],
        'no_live_owned_execution_verified': True, 'owned_session_absence_verified': owned['owned_session_absence_verified'],
        'retained_zombie_members': members, 'retained_zombies_reaped_by_supervisor': False,
        'native_windows_game_chat_verified': False, 'audit_script_sha256': sha(Path(__file__).read_bytes()),
        'saved_archive_sha256': sha(packed), 'source_guard_sha256': sha(guard_raw), 'bridge_closure_sha256': sha(closure_raw),
        'bridge_ledger_sha256': sha(ledger_raw), 'admission_map_sha256': ADMISSION_SHA113,
        'supervisor_receipt_sha256': sha(supervisor_raw), 'Root_actual113_pair_audit_sha256': admission['proof_files']['pair_audit']['sha256']}
    with target.open('x', encoding='utf-8') as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    print(json.dumps({key: audit[key] for key in ('passed', 'actual_gui_checks', 'saved_states', 'selected_public_projections_equal_original_matrix_without_exceptions')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
