"""Unexecuted Source; Root-only Saved audit, without project/API/Qt reexecution."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import threading
import time
import traceback

sys.dont_write_bytecode = True
import native_evidence as native

HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
WINDOW_SHA = 'da217e2296d5f6347b6431010f50f8c185acb61a9a5cab127eaab295305ea30f'
SU, AM = 'char_298_susuro', 'char_002_amiya'
PATCHES = ('char_1001_amiya2', 'char_1037_amiya3')
CONTEXTS = ('core', 'H', 'I', 'J', 'K', 'unsafe')
NOTICE = '已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
RESET_NOTICE = '等待本局页面读取；同一局记忆仅在手动开始新局后清空。'
MANUAL_LABEL = '所选技能等级（已选账号参考，局外模拟）'
RUN_KEYS = ('id', 'started_at', 'last_read', 'operators', 'crew_count', 'selected_operator',
            'relics', 'relic_count', 'bar_signature', 'inventory_verified', 'inventory_confirmed_at',
            'relic_icon_memory', 'history', 'resources', 'tactical_tools', 'config', 'maps',
            'last_node_content', 'node_contents', 'notice')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def same(left, right, label):
    native.assert_native_equal(left, right, label)


def copied_without(value, keys):
    result = native.freeze(value)
    for key in keys:
        result.pop(key)
    return result


def specifications():
    values = {}
    def add(identity, context, op, skill, rank, elite, source, manual=False, mode='frames', numeric=True):
        assert identity not in values
        values[identity] = dict(context=context, operator=op, skill=skill, rank=rank,
                                elite=elite, source=source, manual=manual, mode=mode, numeric=numeric)
    for mode in ('frames', 'continuous'):
        for letter, rank, manual in (('A', 5, False), ('B', 3, True), ('C', 5, False), ('D', 7, True)):
            add(letter+'-'+mode, 'core', SU, 1, rank, 1,
                'manual_account_reference' if manual else 'run_confirmed', manual, mode)
    for identity, op, skill, rank, source, manual in (
        ('E-skill-switch-clear', SU, 2, 4, 'run_confirmed', False),
        ('E-skill2-reference-before-owner', SU, 2, 7, 'manual_account_reference', True),
        ('F-owner-switch-clear', AM, 1, 2, 'run_confirmed', False),
        ('G-return-without-reference', SU, 1, 3, 'run_confirmed', False),
        ('M-account-only', SU, 1, 7, 'account_reference', False),
        ('M-run-mode-restore', SU, 1, 3, 'run_confirmed', False),
        ('M-departed-account-reference', 'char_196_sunbr', 1, 7, 'account_reference', False),
        ('L-before-real-new-run', SU, 1, 7, 'manual_account_reference', True),
        ('L-after-real-reset-same-skill', SU, 1, 7, 'account_reference', False)):
        add(identity, 'core', op, skill, rank, 1, source, manual)
    for op in PATCHES:
        for skill in (1, 2):
            add('N-missing-patch-'+op+'-S'+str(skill), 'core', op, skill, 10, 2, 'run_confirmed')
    add('O-unimplemented-no-skill', 'core', 'char_285_medic2', None, None, None, None, numeric=False)
    add('O-empty-new-run-overview', 'core', None, None, None, None, None, numeric=False)
    add('H-before-incompatible-read', 'H', SU, 1, 7, 1, 'manual_account_reference', True)
    add('H-incompatible-mastered-account', 'H', SU, 1, 3, 1, 'run_confirmed')
    for context in ('I', 'J', 'K'):
        rank = 7 if context in ('I', 'K') else 5
        selected = 10 if context == 'I' else 7 if context == 'J' else 3
        elite = 2 if context == 'I' else 0 if context == 'J' else 1
        source = 'preview_unconfirmed' if context == 'K' else 'run_confirmed'
        for mode in ('frames', 'continuous'):
            for part in ('default', 'reference', 'cancel'):
                manual = part == 'reference'
                add(context+'-'+part+'-'+mode, context, SU, 1, selected if manual else rank, elite,
                    'manual_account_reference' if manual else source, manual, mode)
    for mode in ('frames', 'continuous'):
        add('unsafe-original-run-retained-'+mode, 'unsafe', SU, 1, 3, 1, 'account_reference', mode=mode)
    return values


def main():
    parser = argparse.ArgumentParser()
    for name in ('root', 'guard', 'window', 'window-exit', 'runner', 'out'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--source-count', type=int, required=True)
    args = parser.parse_args()
    root, folder, out = (Path(value).resolve() for value in (args.root, args.window, args.out))
    guard_path, runner, exit_path = (Path(value).resolve() for value in (args.guard, args.runner, args.window_exit))
    assert not out.exists() and root not in out.parents and out not in (root, folder)
    assert pin(Path(__file__).with_name('native_evidence.py'))['sha256'] == HELPER_SHA
    assert pin(runner)['sha256'] == WINDOW_SHA and exit_path.read_bytes() == b'0\n'
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected, extra = guard['source_sha256'], guard['source_additional_sha256']
    assert type(guard['section']) is int and guard['section'] == 118
    assert args.source_count == len(expected) and native.source_map(root) == expected
    assert set(extra) == {'CORE_0.70_VERIFICATION.json'}
    assert {name: sha((root/name).read_bytes()) for name in extra} == extra
    original_raw = (root/'rouge/data/skill-cultivation-reference.json').read_bytes()
    assert sha(original_raw) == expected['rouge/data/skill-cultivation-reference.json']
    original = json.loads(original_raw)
    input_path = folder/'receipt.json'
    receipt_raw, exit_raw = input_path.read_bytes(), exit_path.read_bytes()
    window = json.loads(receipt_raw)
    assert window['kind'] == 'ROOT_ACTUAL_118_REAL_MAINWINDOW' and window['section'] == 118
    assert window['passed'] is True and window['workflow_complete'] is True and not window.get('failure')
    assert window['runner_sha256'] == WINDOW_SHA and window['native_helper_sha256'] == HELPER_SHA
    assert window['source_guard_sha256'] == sha(guard_raw) and window['source_count'] == args.source_count
    assert window['source_before'] == window['source_after'] == expected and window['source_drift'] == []
    assert window['source_additional_before'] == window['source_additional_after'] == extra
    assert window['Qt_errors'] == [] and window['actual_windows'] == len(CONTEXTS)
    assert window['private_state_access'] is False and window['native_windows_verified'] is False
    assert window['game_chat_sampling_executed'] is False
    assert type(window['deadline_seconds']) is int and 1 <= window['deadline_seconds'] <= 1200
    assert 0 <= window['elapsed_seconds'] < window['deadline_seconds']
    out.mkdir()
    (out/'native-verified').mkdir()
    started, done = time.perf_counter(), threading.Event()
    frozen = {input_path: receipt_raw, guard_path: guard_raw, exit_path: exit_raw, runner: runner.read_bytes()}
    proof = {'kind': 'ROOT_ACTUAL118_SKILL_SOURCE_WINDOW_SAVED_AUDIT', 'passed': False,
             'workflow_complete': False, 'source_before': expected, 'source_additional_before': extra,
             'auditor': pin(Path(__file__)), 'window_runner': pin(runner), 'window_receipt': pin(input_path),
             'guard': pin(guard_path), 'window_exit': pin(exit_path), 'native_helper_sha256': HELPER_SHA,
             'source_drift': [], 'snapshots': [], 'pairs': [], 'close_reloads': [], 'PNGs': [],
             'intentional_public_transitions': [], 'intentional_reentrant_calculations': [],
             'intentional_brackets': [], 'full_native_records_retained': [],
             'no_project_API_formatter_Qt_Wine_reexecution': True, 'private_state_access': False,
             'native_windows_game_chat_verified': False, 'PNG_pixels_viewed_by_this_auditor': False,
             'formatter_scope': 'Complete three-formatter group native purity and all three complete strings; no per-formatter isolated purity claim.',
             'technical_intermediate_display_independently_saved': False,
             'technical_scope': 'Exact runner and raw0 bind real technical display assertions; Saved independently compares toggle graph purity. Numeric snapshots do not store the intermediate QTextEdit display string.',
             'non_numeric_scope': 'Actual saved no-API UI step and complete public joint/display. Hidden row and disabled source assertions are bound to the exact runner/raw0 rather than separate unsaved widget flags.',
             'intentional_chronology_scope': 'Only three exact snapshot-to-unique-receipt brackets admit reentrant numeric calls at explicitly enumerated complete public graph stages. Every calculation remains whole caller/joint pure, stage order cannot regress, final ingress/reset scope is independently checked, and all records outside these intervals must match current complete graph.',
             'reload_scope': 'Complete live graph/account/disks; independently derive only the old constructor notice presentation transition. No other leaf/type/order/alias change admitted.',
             'game_scope': 'Read-source selection, original training/cap references and old numeric API agreement do not prove E0 actual game use.'}

    def timeout():
        if not done.wait(180):
            (out/'timeout.json').write_text('{"passed":false,"deadline_seconds":180}\n')
            os._exit(124)
    threading.Thread(target=timeout, daemon=True).start()
    try:
        refs = window['records']
        names = [ref['path'] for ref in refs]
        assert names == [f'{i:06d}.pickle.gz' for i in range(1, len(names)+1)]
        assert not (folder/'records').is_symlink()
        assert {path.name for path in (folder/'records').iterdir()} == set(names)
        ledger, decoded, positions = {}, {}, {}
        for index, ref in enumerate(refs):
            value = native.read_record(folder/'records', ref)
            for key in ('kind', 'context', 'case', 'phase'):
                same(value[key], ref[key], 'complete saved record metadata '+key)
            assert value['context'] in CONTEXTS
            name = ref['path']
            ledger[name], decoded[name], positions[name] = ref, value, index
            source_path = folder/'records'/name
            raw = source_path.read_bytes()
            frozen[source_path] = raw
            with (out/'native-verified'/name).open('xb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            assert (out/'native-verified'/name).read_bytes() == raw
            proof['full_native_records_retained'].append(ref)
        def get(ref, kind):
            name = ref['path']
            same(ref, ledger[name], 'complete reference metadata')
            value = decoded[name]
            assert value['kind'] == kind
            return value
        # The producer appends an intentional receipt only after its real method
        # and any reentrant calculate callbacks finish. Identify those narrow
        # intervals using the exact sealed runner's preceding snapshot, exact
        # active metadata tuple, and unique final receipt. A later ordinary pure
        # control may retain that active tuple; it is outside this interval and
        # receives the ordinary current-graph check without any exception.
        rows_by_id = {row['id']: row for row in window['rows']}
        assert len(rows_by_id) == len(window['rows'])
        intentional_contracts = (
            ('core', 'D-public-observation', 'intentional_public_fixture_update',
             'actual_explicit_public_observation_ingress', 'C-continuous'),
            ('H', 'H-new-account-mastery', 'intentional_public_account_observation',
             'actual_explicit_public_account_ingress', 'H-before-incompatible-read'),
            ('core', 'L-real-reset', 'explicit_user_reset',
             'actual_explicit_new_run', 'L-before-real-new-run'),
        )
        bracket_calls, bracket_endings = {}, {}
        for context, case, phase, ending_kind, anchor_id in intentional_contracts:
            ending_names = [name for name in names if decoded[name]['kind'] == ending_kind]
            assert len(ending_names) == 1
            ending_name = ending_names[0]
            ending = decoded[ending_name]
            assert (ending['context'], ending['case'], ending['phase']) == (context, case, phase)
            anchor_ref = rows_by_id[anchor_id]['snapshot']
            anchor = get(anchor_ref, 'actual_window_snapshot')
            assert (anchor['context'], anchor['case'], anchor['phase']) == (context, anchor_id, 'actual_snapshot')
            first, stop = positions[anchor_ref['path']]+1, positions[ending_name]
            assert first <= stop
            stages = [('before', ending['before'])]
            if case == 'D-public-observation':
                # AccountCache.observe saves before show_observed_operator's
                # calculate; RunState.apply saves before later UI recalculates.
                account_saved = native.freeze(ending['before'])
                account_saved['account'] = native.freeze(ending['after']['account'])
                account_saved['disks']['account.json'] = ending['after']['disks']['account.json']
                stages.append(('account_saved_run_unchanged', account_saved))
            stages.append(('final_after', ending['after']))
            bracket = {'context': context, 'case': case, 'phase': phase,
                       'anchor': anchor_ref, 'ending': ledger[ending_name],
                       'first': first, 'stop': stop, 'stages': stages, 'last_stage': -1}
            assert ending_name not in bracket_endings
            bracket_endings[ending_name] = bracket
            for index in range(first, stop):
                name = names[index]
                value = decoded[name]
                assert value['kind'] == 'actual_calculate_result'
                assert (value['context'], value['case'], value['phase']) == (context, case, phase)
                assert name not in bracket_calls
                bracket_calls[name] = bracket
            proof['intentional_brackets'].append({
                'context': context, 'case': case, 'phase': phase, 'anchor': anchor_ref,
                'ending': ledger[ending_name], 'actual_reentrant_record_count': stop-first,
                'allowed_complete_graph_stages': [label for label, _ in stages],
            })
        initial = {value['context']: value for value in decoded.values() if value['kind'] == 'actual_public_fixture_loaded'}
        assert set(initial) == set(CONTEXTS)
        current = {context: value['value'] for context, value in initial.items()}
        kinds, numeric, fresh = {}, [], []
        for context, value in initial.items():
            joint = value['value']
            same(joint['disks']['run.json'], value['run_bytes'], 'original public run bytes')
            same(joint['disks']['account.json'], value['account_bytes'], 'original public account bytes')
            raw_run, account = json.loads(value['run_bytes']), json.loads(value['account_bytes'])
            same(account, joint['account'], 'complete original public account')
            loaded = {key: raw_run[key] for key in RUN_KEYS if key != 'notice'}
            loaded['notice'] = NOTICE
            for key, item in raw_run.items():
                if key not in loaded: loaded[key] = item
            same(joint['run'], loaded, 'complete accepted public RunState constructor graph/order')
            assert joint['run']['id'] == 'public118-'+context
            same(joint['run']['public_opaque'], {'signed_zero': -0.0, 'nullable': None}, 'opaque public signed-zero graph')
        for name in names:
            value = decoded[name]
            kind, context = value['kind'], value['context']
            kinds[kind] = kinds.get(kind, 0)+1
            joint = current[context]
            if kind == 'actual_calculate_result':
                same(value['after'], value['before'], 'complete actual numeric caller/joint purity')
                if name in bracket_calls:
                    bracket = bracket_calls[name]
                    ending = decoded[bracket['ending']['path']]
                    same(ending['before'], joint, 'intentional bracket begins at current complete public graph')
                    assert 'joint' in value['before']
                    candidates = []
                    for stage_index, (_, stage) in enumerate(bracket['stages']):
                        try:
                            same(value['before']['joint'], stage, 'reentrant complete graph must equal one declared exact stage')
                        except AssertionError:
                            continue
                        candidates.append(stage_index)
                    candidates = [index for index in candidates if index >= bracket['last_stage']]
                    assert candidates, 'Reentrant calculation has no exact non-regressing intentional graph stage'
                    stage_index = min(candidates)
                    bracket['last_stage'] = stage_index
                    proof['intentional_reentrant_calculations'].append({
                        'native': ledger[name], 'ending': bracket['ending'],
                        'complete_graph_stage': bracket['stages'][stage_index][0],
                        'complete_caller_joint_before_after_pure': True,
                    })
                elif 'joint' in value['before']:
                    same(value['before']['joint'], joint, 'actual numeric current public graph')
                else:
                    assert value['case'] == context+'-constructor'
                numeric.append(value)
            elif kind == 'actual_UI_step':
                same(value['before']['joint'], joint, 'UI begins at current public graph')
                same(value['after']['joint'], joint, 'UI preserves current public graph')
                if value['label'] in ('actual technical checkbox', 'ordinary report restore', 'show source checkbox viewport'):
                    same(value['after'], value['before'], 'actual display-only control whole graph purity')
            elif kind == 'actual_reference_API_before_after_result':
                same(value['after'], value['before'], 'fresh original reference complete caller/joint purity')
                same(value['before']['joint'], joint, 'fresh API current public graph')
                fresh.append(value)
            elif kind == 'actual_three_formatter_group':
                same(value['after'], value['before'], 'complete three formatter group purity')
                same(value['before']['joint'], joint, 'formatter current public graph')
            elif kind in ('actual_window_snapshot', 'actual_non_numeric_window_snapshot'):
                same(value['value']['state_and_disks'] if kind == 'actual_window_snapshot' else value['joint'], joint, 'snapshot current public graph')
            elif kind in ('actual_explicit_public_observation_ingress', 'actual_explicit_public_account_ingress'):
                before, after = value['before'], value['after']
                same(before, joint, 'intentional observation current input graph')
                account_input = value['account_input'] if kind == 'actual_explicit_public_observation_ingress' else value['input']
                assert account_input['id'] == SU and account_input['scope'] == 'operator_profile'
                same(copied_without(after['account'], (SU,)), copied_without(before['account'], (SU,)), 'observation leaves every other account unchanged')
                observed = after['account'][SU]
                same(observed['fields'], account_input['fields'], 'intentional public account fields')
                same(observed['skill_ranks'], account_input['skill_ranks'], 'intentional public account ranks')
                assert observed['captured_at'] == 2000.0
                same(copied_without(after['disks'], ('account.json', 'run.json') if context == 'core' else ('account.json',)),
                     copied_without(before['disks'], ('account.json', 'run.json') if context == 'core' else ('account.json',)), 'intentional observation only declared public file deltas')
                if context == 'core':
                    assert value['case'] == 'D-public-observation'
                    member = value['run_input']; assert member['id'] == SU and member['scope'] == 'run'
                    same(copied_without(after['run'], ('operators', 'history', 'last_read')),
                         copied_without(before['run'], ('operators', 'history', 'last_read')), 'D only declared member/history/read-time run deltas')
                    same(copied_without(after['run']['operators'], (SU,)), copied_without(before['run']['operators'], (SU,)), 'D leaves every other run member unchanged')
                    updated = after['run']['operators'][SU]
                    same(updated['fields'], member['fields'], 'D actual public member fields')
                    same(updated['skill_ranks'], member['skill_ranks'], 'D actual public member grades')
                    same(updated['char_buff_ids'], before['run']['operators'][SU]['char_buff_ids'], 'D independent buff evidence retained')
                    assert updated['recruitment_kind'] == 'non_emergency' and after['run']['last_read'] == 2000.0
                    same(after['run']['history'][:len(before['run']['history'])], before['run']['history'], 'D prior history preserved')
                else:
                    assert context == 'H' and value['case'] == 'H-new-account-mastery'
                    same(after['run'], before['run'], 'H account observation retains whole run graph')
                current[context] = after
                proof['intentional_public_transitions'].append(ledger[name])
            elif kind == 'actual_explicit_new_run':
                assert context == 'core' and value['case'] == 'L-real-reset'
                before, after = value['before'], value['after']
                same(before, joint, 'real reset current input graph')
                same(after['account'], before['account'], 'real reset retains every account leaf/type/order/alias')
                same(copied_without(after['disks'], ('run.json',)), copied_without(before['disks'], ('run.json',)), 'real reset changes only its public run file')
                reset = after['run']
                assert tuple(reset) == RUN_KEYS and type(reset['id']) is str and reset['id'] != before['run']['id']
                assert type(reset['started_at']) is float and math.isfinite(reset['started_at']) and reset['started_at'] > 0
                assert reset['notice'] == RESET_NOTICE and reset['operators'] == {} and reset['last_read'] is None
                for key in ('relics', 'resources', 'tactical_tools', 'config', 'maps'): assert reset[key] == {}
                for key in ('history', 'node_contents'): assert reset[key] == []
                for key in ('crew_count', 'selected_operator', 'relic_count', 'bar_signature', 'inventory_confirmed_at', 'relic_icon_memory', 'last_node_content'): assert reset[key] is None
                assert reset['inventory_verified'] is False
                current[context] = after
                proof['intentional_public_transitions'].append(ledger[name])
            elif kind == 'actual_close_RunState_AccountCache_reload':
                same(value['live_before'], joint, 'real close current complete graph')
                restart = native.freeze(joint['run']); restart['notice'] = NOTICE
                same(value['expected_restart_state'], restart, 'independent existing notice-only reload expectation')
                same(value['restart_state'], restart, 'whole actual RunState reload with old notice-only transition')
                same(value['account_restart_records'], joint['account'], 'whole actual AccountCache reload')
                same(value['disks_after'], joint['disks'], 'real close and both reloads preserve every raw public byte')
                transition = value['existing_constructor_notice_transition']
                assert transition['before'] == joint['run']['notice'] and transition['after'] == NOTICE
            else:
                assert kind in ('actual_public_fixture_loaded', 'actual_PNG_source_form_scope')
        assert len(proof['intentional_reentrant_calculations']) == len(bracket_calls)
        assert len(proof['intentional_brackets']) == len(intentional_contracts)
        assert {ref['path'] for ref in proof['intentional_public_transitions']} == set(bracket_endings)
        assert len(numeric) == window['actual_numeric_calls'] and len(fresh) == window['fresh_reference_API_calls']
        cases = specifications()
        actual_ids = [row['id'] for row in window['rows']]
        assert len(actual_ids) == len(set(actual_ids)) and set(actual_ids) == set(cases)
        assert set(window['required_case_ids']) <= set(actual_ids)
        snapshots = {}
        for row in window['rows']:
            identity, spec = row['id'], cases[row['id']]
            saved = get(row['snapshot'], 'actual_window_snapshot' if spec['numeric'] else 'actual_non_numeric_window_snapshot')
            assert saved['case'] == identity and saved['context'] == spec['context']
            index = positions[row['snapshot']['path']]
            if not spec['numeric']:
                assert row['numeric'] is None and index > 0
                step = decoded[names[index-1]]
                assert step['kind'] == 'actual_UI_step' and step['case'] == identity and step['label'] == 'MainWindow.calculate'
                assert step['after']['damage_result'] is None and saved['operator'] == spec['operator'] and saved['skill'] is None
                # Active case labels persist during later owner selection.
                # Bound the no-call claim to this direct calculate interval.
                assert index >= 2
                preceding = decoded[names[index-2]]
                assert preceding['kind'] == 'actual_UI_step'
                assert preceding['label'] == ('actual timing checkbox' if identity == 'O-unimplemented-no-skill' else 'empty actual run overview')
                assert preceding['after']['damage_result'] is None
                assert type(saved['display']) is str
                if spec['operator'] is not None: assert '未知伤害' in saved['display']
                proof['snapshots'].append({'id': identity, 'numeric': False, 'snapshot': row['snapshot']})
                continue
            snapshot = saved['value']; snapshots[identity] = snapshot
            call = get(row['numeric'], 'actual_calculate_result')
            reference = get(row['reference_numeric'], 'actual_reference_API_before_after_result')
            assert index >= 6 and names[index-6] == row['numeric']['path'] and names[index-4] == row['reference_numeric']['path']
            step, group, technical, ordinary = (decoded[names[index-offset]] for offset in (5, 3, 2, 1))
            assert step['kind'] == 'actual_UI_step' and step['label'] == 'MainWindow.calculate'
            assert group['kind'] == 'actual_three_formatter_group'
            assert technical['label'] == 'actual technical checkbox' and ordinary['label'] == 'ordinary report restore'
            assert all(value['case'] == identity for value in (call, reference, step, group, technical, ordinary))
            caller, result = snapshot['caller'], snapshot['damage_result']['result']
            same(caller, call['before']['args'][0], 'complete saved actual numeric caller')
            assert len(call['before']['args']) == 1 and call['before']['kwargs'] == {}
            same(snapshot['damage_result']['scenario'], caller, 'complete actual GUI scenario')
            same(result, call['result'], 'complete original return/actual GUI result')
            same(reference['before']['caller'], caller, 'complete fresh reference caller')
            same(reference['result'], result, 'full actual GUI result/fresh original API reference result')
            for key in ('operator', 'skill', 'elite'): same(caller[key], spec[key], 'case fixed '+key)
            assert caller['skill_rank'] == spec['rank'] and caller['timing_mode'] == spec['mode']
            assert row['rank'] == spec['rank'] and row['rank_source'] == spec['source'] and row['mode'] == spec['mode']
            assert 'base_attack' not in caller and 'target_enemy' not in caller
            assert (caller['window_seconds'], caller['trust'], caller['potential']) == (10, 0, 1)
            assert caller['module_id'] is None and caller['module_level'] == 0 and caller['relic_ids'] == []
            assert (MANUAL_LABEL in caller['unconfirmed_training']) is spec['manual']
            selection = snapshot['selection_row']
            assert (selection['operator'], selection['skill'], selection['elite'], selection['rank']) == (spec['operator'], spec['skill'], spec['elite'], spec['rank'])
            assert selection['rank_source'] == spec['source'] and selection['manual_reference_applied'] is spec['manual']
            assert selection['arithmetic_changed_by_explanation'] is False and selection['actual_activation_verified'] is None
            assert snapshot['checkbox_checked'] is spec['manual']
            if spec['manual']:
                assert snapshot['checkbox_enabled'] is True and '局外模拟' in snapshot['rank_label'] and '本局未确认' in snapshot['explanation_text']
            else:
                expected_label = ('等级 '+str(spec['rank']) if spec['rank'] <= 7 else '专精 '+str(spec['rank']-7)) + ('（未确认，档案预览）' if spec['source'] == 'preview_unconfirmed' else '（读取）')
                assert snapshot['rank_label'] == expected_label
            if identity == 'H-incompatible-mastered-account': assert snapshot['checkbox_enabled'] is False
            if spec['operator'] in PATCHES:
                assert selection['original_source_status'] == 'missing' and selection['training_requirement'] is None
                assert '不借用其他职业' in snapshot['explanation_text']
            else:
                source = original['operators'][spec['operator']]
                assert selection['original_source_status'] == 'located'
                requirement = source['allSkillLvlup'][spec['rank']-2]['unlockCond'] if spec['rank'] <= 7 else source['skills'][spec['skill']-1]['levelUpCostCond'][spec['rank']-8]['unlockCond']
                same(selection['training_requirement']['raw'], requirement, 'physical original training requirement')
            same(selection['recruit_upper_bounds'], original['recruit_upper_bounds']['rogue_6'], 'physical raw recruit cap reference')
            if spec['elite'] == 0:
                assert selection['e0_common_use_verified'] is None and '仍未核验' in snapshot['explanation_text']
            if spec['context'] == 'K': assert snapshot['state_and_disks']['run']['operators'][SU]['invalid_skill_ranks'] == ['1']
            if spec['context'] == 'unsafe': assert snapshot['state_and_disks']['run']['operators'][SU]['fields']['elite'] == []
            same(group['before']['damage_result'], snapshot['damage_result'], 'formatter complete input result')
            same(group['before']['joint'], snapshot['state_and_disks'], 'formatter complete public graph')
            same(group['texts'], snapshot['texts'], 'all three complete native report strings')
            assert tuple(snapshot['texts']) == ('estimate', 'default', 'technical') and all(type(text) is str and text for text in snapshot['texts'].values())
            assert snapshot['texts']['estimate'] == snapshot['texts']['default']
            same(technical['before'], {'joint': group['after']['joint'], 'damage_result': group['after']['damage_result']}, 'complete technical toggle order/input')
            same(ordinary['before'], technical['after'], 'ordinary toggle follows complete technical graph')
            proof['snapshots'].append({'id': identity, 'numeric': row['numeric'], 'reference_numeric': row['reference_numeric'], 'snapshot': row['snapshot'], 'three_text_record': ledger[names[index-3]], 'complete_caller_result_texts_public_graph_verified': True})
        for pair in window['pairs']:
            if pair['id'].startswith('cancel-'):
                mode = pair['id'][len('cancel-'):]
                expected_ids = tuple(letter+'-'+mode for letter in ('A', 'B', 'C'))
            else:
                context, suffix = pair['id'].split('-cancel-', 1)
                assert context in ('I', 'J', 'K')
                expected_ids = tuple(context+'-'+part+'-'+suffix for part in ('default', 'reference', 'cancel'))
            originals = [get(pair[key], 'actual_window_snapshot') for key in ('before', 'selected', 'restored')]
            assert tuple(value['case'] for value in originals) == expected_ids
            a, b, c = (value['value'] for value in originals)
            same(a['damage_result'], c['damage_result'], 'cancel restores complete caller and result')
            same(a['texts'], c['texts'], 'cancel restores all complete texts')
            same(a['state_and_disks'], b['state_and_disks'], 'reference preserves all current public leaves')
            same(a['state_and_disks'], c['state_and_disks'], 'cancel preserves all current public leaves')
            expected_caller = native.freeze(a['caller']); expected_caller['skill_rank'] = b['caller']['skill_rank']
            labels = list(expected_caller['unconfirmed_training'])
            if '所选技能等级' in labels: labels[labels.index('所选技能等级')] = MANUAL_LABEL
            else: labels.insert(0, MANUAL_LABEL)  # All bound pair fixtures provide the five base fields.
            expected_caller['unconfirmed_training'] = labels
            same(b['caller'], expected_caller, 'reference changes only rank and exact explicit source label')
            proof['pairs'].append(pair)
        expected_pairs = {'cancel-'+mode for mode in ('frames', 'continuous')}
        expected_pairs.update(context+'-cancel-'+mode for context in ('I', 'J', 'K') for mode in ('frames', 'continuous'))
        assert {pair['id'] for pair in window['pairs']} == expected_pairs and len(window['pairs']) == len(expected_pairs)
        assert [row['context'] for row in window['close_reloads']] == list(CONTEXTS)
        for row in window['close_reloads']:
            close = get(row['native'], 'actual_close_RunState_AccountCache_reload')
            assert close['context'] == row['context']
            proof['close_reloads'].append(row)
        expected_pngs = (('account-reference-lower-rank.png', 'B-frames'), ('e0-read-reference-use-unknown.png', 'J-reference-frames'))
        assert tuple(row['path'] for row in window['pngs']) == tuple(name for name, _ in expected_pngs)
        for row, (name, case) in zip(window['pngs'], expected_pngs):
            path = folder/name; raw = path.read_bytes(); assert not path.is_symlink()
            frozen[path] = raw
            assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
            assert raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR'
            width, height = struct.unpack('>II', raw[16:24]); assert width > 0 and height > 0
            visual = get(row['visual'], 'actual_PNG_source_form_scope')
            assert visual['case'] == case and visual['entire_explanation_claimed_visible'] is False and visual['checked'] is True
            same(visual['text'], snapshots[case]['explanation_text'], 'full PNG-bound source text')
            assert visual['rank_label'] == snapshots[case]['rank_label']
            vx, vy, vw, vh = visual['viewport']; assert vw > 0 and vh > 0
            for key, metric in visual['widget_rectangles'].items():
                x, y, w, h = metric['rect']; ix, iy, iw, ih = metric['intersection']
                assert all(type(v) is int for v in (x, y, w, h, ix, iy, iw, ih)) and w > 0 and h > 0
                fully = vx <= x and vy <= y and x+w <= vx+vw and y+h <= vy+vh
                assert metric['entire_widget_visible'] is fully
                if iw > 0 and ih > 0:
                    assert ix == max(x, vx) and iy == max(y, vy)
                    assert iw == min(x+w, vx+vw)-ix and ih == min(y+h, vy+vh)-iy
            assert visual['widget_rectangles']['checkbox']['entire_widget_visible'] is True
            assert visual['widget_rectangles']['explanation']['intersection'][2] > 0 and visual['widget_rectangles']['explanation']['intersection'][3] > 0
            with (out/name).open('xb') as stream: stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            assert (out/name).read_bytes() == raw
            proof['PNGs'].append({'input_metadata': row, 'visual': visual, 'width': width, 'height': height,
                                  'complete_explanation_visibility_claimed': False, 'pixels_viewed': False})
        assert kinds.get('actual_public_fixture_loaded') == len(CONTEXTS)
        assert kinds.get('actual_close_RunState_AccountCache_reload') == len(CONTEXTS)
        assert kinds.get('actual_window_snapshot') == sum(spec['numeric'] for spec in cases.values())
        assert kinds.get('actual_non_numeric_window_snapshot') == sum(not spec['numeric'] for spec in cases.values())
        assert kinds.get('actual_three_formatter_group') == len(snapshots) and len(fresh) == len(snapshots)
        assert len(proof['intentional_public_transitions']) == 3
        with (out/'original-window-receipt.json').open('xb') as stream: stream.write(receipt_raw); stream.flush(); os.fsync(stream.fileno())
        with (out/'original-window-exit-code').open('xb') as stream: stream.write(exit_raw); stream.flush(); os.fsync(stream.fileno())
        proof.update(passed=True, workflow_complete=True, actual_native_records_decoded=len(names),
                     actual_complete_states=len(window['rows']), actual_numeric_states=len(snapshots),
                     actual_non_numeric_states=len(cases)-len(snapshots), actual_numeric_calls=len(numeric),
                     actual_fresh_reference_API_records=len(fresh), actual_three_formatter_groups=len(snapshots),
                     actual_complete_formatter_strings=sum(len(value['texts']) for value in snapshots.values()),
                     actual_complete_close_reloads=len(window['close_reloads']), actual_cancellation_pairs=len(window['pairs']),
                     actual_PNG_hash_intersection_gates=len(window['pngs']), record_kinds=kinds)
    except BaseException as error:
        proof['failure'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        proof['source_after'] = native.source_map(root)
        proof['source_additional_after'] = {name: sha((root/name).read_bytes()) for name in extra}
        proof['source_drift'] = [name for name in set(expected)|set(proof['source_after']) if expected.get(name) != proof['source_after'].get(name)]
        if proof['source_drift'] or proof['source_additional_after'] != extra or any(path.read_bytes() != raw for path, raw in frozen.items()):
            proof.update(passed=False, workflow_complete=False)
        proof['elapsed_seconds'] = time.perf_counter()-started
        with (out/'receipt.json').open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(proof, ensure_ascii=False, indent=2)+'\n'); stream.flush(); os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed': proof['passed'], 'decoded': proof.get('actual_native_records_decoded', 0), 'states': proof.get('actual_complete_states', 0)}))
    return 0 if proof['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
