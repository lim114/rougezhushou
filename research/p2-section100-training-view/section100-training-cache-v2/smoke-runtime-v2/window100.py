"""Root-only real MainWindow smoke; author compiled but did not execute it.

Gold exercises five healthy controls on actual post99/pre100 source. Candidate
repeats them with exact native outputs/three-text comparison, then exercises the
new UI safety boundary and independently retained recruitment/buff evidence.
All state is public temporary disk data. Sampling/desktop requests/game/chat are
off. Root must bind an actual source guard and capture genuine primary exits.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, source_map, write_record, read_record

HELPER_SHA = '5bef7b6f03592a5df615711568d116a0ffd9170f9be99832ca75d9eee78fcdb4'
TEST_SHA = 'f5a11226278b1295acb09deec4d5596e61bb4e483ef50eeeee849e2b92981814'
NATIVE_HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
OP = 'mechanist'
SNACK = 'rogue_6_from_relic_13'
CARGO = 'rogue_6_relic_cargo_10'
HEALTHY_IDS = ['healthy-full', 'healthy-mixed', 'healthy-masked', 'healthy-none-time', 'healthy-float-clamp']
PNG_CASES = {'healthy-masked': 'training100-masked.png',
             'healthy-float-clamp': 'training100-float-clamp.png',
             'unsafe-elite': 'training100-safe-fallback-and-buff.png',
             'manual-level-override': 'training100-manual-level-override.png'}
DEADLINE_SECONDS = 450


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_info(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def account_record(op=OP):
    return {'id': op, 'scope': 'operator_profile',
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1,
                       'module_id': None, 'module_level': 0, 'selected_skill': 3},
            'skill_ranks': {'1': 7, '3': 10}, 'captured_at': 1000.0,
            'sources': {}, 'field_times': {}, 'skill_times': {}}


def member_record(op=OP):
    return {**account_record(op), 'scope': 'run', 'present': True,
            'recruitment_kind': 'non_emergency', 'char_buff_ids': [SNACK],
            'char_buffs_complete': True, 'char_buff_absent_ids': [], 'char_buff_pending_ids': [],
            'invalid_fields': [], 'invalid_skill_ranks': [], 'missing_fields': []}


def run_fixture(member, op=OP):
    # Same explicit public disk bytes in gold/candidate. No UUID/time rewrite.
    return {'id': 'public-training100-same-facts', 'started_at': 0.0, 'last_read': None,
            'operators': {op: member}, 'crew_count': 1, 'selected_operator': op,
            'relics': {CARGO: {'id': CARGO, 'held': True, 'captured_at': 1000.0,
                               'source': 'public-held-card', 'icon_evidence': {}}},
            'relic_count': 1, 'bar_signature': [[CARGO]],
            'inventory_verified': True, 'inventory_confirmed_at': 1000.0,
            'relic_icon_memory': None, 'history': [], 'resources': {},
            'tactical_tools': {}, 'config': {}, 'maps': {},
            'last_node_content': None, 'node_contents': [], 'notice': '公开临时同局夹具'}


def cases():
    result = []
    result.append({'id': 'healthy-full', 'member': member_record(), 'account': {OP: account_record()}, 'level': 80})
    member = member_record();member['fields'] = {'potential': 6, 'level': 60}
    result.append({'id': 'healthy-mixed', 'member': member, 'account': {OP: account_record()}, 'level': 60})
    member = member_record();member['fields'] = {'elite': [], 'level': 'ignored', 'potential': 6}
    member['invalid_fields'] = ['elite', 'level'];member['skill_ranks']['1'] = []
    member['invalid_skill_ranks'] = ['1']
    result.append({'id': 'healthy-masked', 'member': member, 'account': {OP: account_record()}, 'level': 80})
    member = member_record();member['captured_at'] = None
    result.append({'id': 'healthy-none-time', 'member': member, 'account': {OP: account_record()}, 'level': 80})
    member = member_record();member['fields']['level'] = 91.9
    result.append({'id': 'healthy-float-clamp', 'member': member, 'account': {OP: account_record()}, 'level': 90})
    for identity, change in [('unsafe-elite', ('fields', 'elite', [])),
                             ('unsafe-active-rank', ('skill_ranks', '3', 'bad rank')),
                             ('unsafe-giant-level', ('fields', 'level', 10 ** 100))]:
        member = member_record();member[change[0]][change[1]] = change[2]
        result.append({'id': identity, 'member': member, 'account': {OP: account_record()}, 'level': 80})
    member = member_record();member['captured_at'] = 'bad'
    result.append({'id': 'unsafe-time', 'member': member, 'account': {OP: account_record()}, 'level': 80})
    member = member_record();member['fields']['elite'] = []
    result.append({'id': 'unsafe-without-account', 'member': member, 'account': {}, 'level': 90})
    member = member_record();member['fields']['level'] = None;member['fields']['potential'] = 6
    result.append({'id': 'manual-level-override', 'member': member, 'account': {OP: account_record()}, 'level': 80})
    account = account_record();account['fields'] = {'elite': 1, 'level': 60};account['skill_ranks'] = {'1': 7}
    member = member_record();member['fields'] = {'potential': 6};member['skill_ranks'] = {'1': 8, '3': 10}
    result.append({'id': 'incompatible-account-fill', 'member': member, 'account': {OP: account}, 'level': 90})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--mode', choices=('gold', 'candidate'), required=True)
    parser.add_argument('--baseline')
    parser.add_argument('--baseline-exit')
    args = parser.parse_args()
    root = Path(args.root).resolve();output = Path(args.out).resolve()
    assert not output.exists(), 'Every attempt uses a fresh absent output directory'
    assert output != root and root not in output.parents
    guard_path = Path(args.guard).resolve();guard = json.loads(guard_path.read_text(encoding='utf-8'))
    expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and expected
    assert source_map(root) == expected, 'Actual maintained source must match Root guard'
    here = Path(__file__).resolve().parent
    assert sha((here/'native_evidence.py').read_bytes()) == NATIVE_HELPER_SHA
    if args.mode == 'candidate':
        assert sha((root/'rouge/training_view.py').read_bytes()) == HELPER_SHA
        assert args.baseline and args.baseline_exit
        assert int(Path(args.baseline_exit).read_text(encoding='utf-8')) == 0
        baseline_dir = Path(args.baseline).resolve()
        baseline = json.loads((baseline_dir/'receipt.json').read_text(encoding='utf-8'))
        assert baseline['mode'] == 'gold' and baseline['passed'] is True and baseline['workflow_complete'] is True
        assert baseline['healthy_case_ids'] == HEALTHY_IDS
        assert baseline['runner_sha256'] == sha(Path(__file__).read_bytes())
        gold_source=baseline['source_before']
        assert set(expected)-set(gold_source)=={'rouge/training_view.py','tests/test_training_view_100.py'}
        assert not set(gold_source)-set(expected)
        changed={path for path in gold_source if expected[path]!=gold_source[path]}
        assert changed <= {'rouge/app.py','scripts/verify_cloud.py'} and 'rouge/app.py' in changed
        assert expected['tests/test_training_view_100.py']==TEST_SHA
    else:
        assert not args.baseline and not args.baseline_exit
        assert 'rouge/training_view.py' not in expected and not (root/'rouge/training_view.py').exists()
        baseline_dir = None;baseline = None
    output.mkdir(parents=True);(output/'records').mkdir();(output/'public-state').mkdir()
    started = time.perf_counter();finished = threading.Event();case_rows = [];record_rows = []
    png_rows = [];qt_errors = [];active_case = {'id': 'preimport'};numeric_calls = []
    receipt = {'kind': 'ACTUAL_TRAINING100_BOUNDED_REAL_MAINWINDOW', 'mode': args.mode,
               'passed': False, 'workflow_complete': False,
               'root': str(root), 'argv': list(sys.argv), 'cwd': str(Path.cwd()),
               'runner_sha256': sha(Path(__file__).read_bytes()), 'native_helper_sha256': NATIVE_HELPER_SHA,
               'actual_source_guard': file_info(guard_path), 'source_before': expected,
               'started_at_UTC': datetime.now(timezone.utc).isoformat(),
               'healthy_case_ids': HEALTHY_IDS, 'cases': case_rows, 'records': record_rows,
               'pngs': png_rows, 'Qt_exceptions': qt_errors, 'numeric_calls': numeric_calls,
               'private_state_isolated': True, 'game_chat_sampling_executed': False,
               'native_windows_verified': False, 'deadline_seconds': DEADLINE_SECONDS}

    def deadline():
        if not finished.wait(DEADLINE_SECONDS):
            timeout = {'passed': False, 'workflow_complete': False, 'reason': 'Root-declared450sbudget',
                       'active_case': active_case['id'], 'elapsed': time.perf_counter()-started}
            write_json(output/'timeout.json', timeout)
            os._exit(124)

    threading.Thread(target=deadline, daemon=True).start()
    old_hook = sys.excepthook

    def observed_exception(kind, error, trace):
        qt_errors.append({'case': active_case['id'], 'type': kind.__name__, 'message': str(error),
                          'traceback': ''.join(traceback.format_exception(kind, error, trace))})
        old_hook(kind, error, trace)

    sys.excepthook = observed_exception
    window = None;application = None;module = None;original_calc = None;original_backend = None
    folders = ExitStack()
    try:
        sys.path.insert(0, str(root))
        from PySide6 import __version__ as pyside_version
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication, QPushButton
        from rouge import app as module, estimate, reporting
        from rouge.relics import mechanics
        from rouge.run_state import RunState
        application = QApplication.instance() or QApplication([])
        receipt.update(python=sys.version, sys_platform=sys.platform,
                       pyside=pyside_version, qt=qVersion())
        assert pyside_version=='6.9.3' and qVersion()=='6.9.3', 'Root probes bind this actual Qt version'
        original_calc = module.calculate_damage;original_backend = module.DesktopBackend

        def observed_calculation(*positional, **keywords):
            before = freeze({'args': positional, 'kwargs': keywords})
            value = original_calc(*positional, **keywords)
            assert_native_equal({'args': positional, 'kwargs': keywords}, before, 'Native calculation caller unchanged')
            row = write_record(output/'records', len(record_rows)+1,
                               {'kind': 'actual_calculate_damage', 'case': active_case['id'],
                                'before': before, 'after': freeze({'args': positional, 'kwargs': keywords}),
                                'result': freeze(value)})
            row.update(kind='actual_calculate_damage', case=active_case['id'])
            record_rows.append(row);numeric_calls.append(row['path'])
            return value

        module.calculate_damage = observed_calculation

        def idle():
            application.processEvents()
            assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
            assert not window.busy and not window.chat_busy and not window.desktop_request_busy
            assert window.desktop.process is None and not window.desktop.pending
            assert not qt_errors, qt_errors

        def durable():
            return {'run': window.run.state, 'account': window.account_cache.records}

        def disks(account_path, run_path):
            return {'account': account_path.read_bytes(), 'run': run_path.read_bytes(),
                    'account_tmp': account_path.with_suffix('.tmp').exists(),
                    'run_tmp': run_path.with_suffix('.tmp').exists()}

        def step(label, action, account_path, run_path):
            caller = freeze(durable());disk = freeze(disks(account_path, run_path))
            action();idle()
            assert_native_equal(durable(), caller, 'UI/formatter leaves native run/account caller unchanged: '+label)
            assert_native_equal(disks(account_path, run_path), disk, 'UI does not write original temporary disks: '+label)

        def report_snapshot():
            before_state = freeze(durable())
            before_disk = freeze(disks(account_path, run_path))
            value = window.damage_result
            assert type(value) is dict, window.damage_text.toPlainText()
            before = freeze(value);result = value['result']
            texts = {'estimate': estimate.format_estimate(result),
                     'default': reporting.format_report(result),
                     'technical': reporting.format_report(result, technical=True)}
            assert texts['estimate'] == texts['default']
            assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
            assert_native_equal(value, before, 'Three actual formatting calls do not mutate native report')
            snapshot = {'damage_result': value, 'three_texts': texts, 'level': window.level.value(),
                        'skill': window.skill.currentData(), 'cultivation': window.training_conditions(),
                        'ranks': window.current_operator_state().get('skill_ranks', {})}
            assert_native_equal(durable(), before_state, 'Actual formatting/training views preserve native durable state')
            assert_native_equal(disks(account_path, run_path), before_disk,
                                'Actual formatting/training views preserve native public disks')
            assert_native_equal(disks(account_path, run_path),
                                {'account': account_bytes, 'run': run_bytes,
                                 'account_tmp': False, 'run_tmp': False},
                                'Original public account/run disk bytes and tmp absence remain exact')
            return snapshot

        def cargo_applied():
            result=window.damage_result['result']
            record=next(item for item in result['relic_resolution']['records'] if item['id']==CARGO)
            return record, [(effect['kind'], effect['value']) for effect in record['applied']]

        for case in cases():
            if args.mode == 'gold' and case['id'] not in HEALTHY_IDS:continue
            active_case['id'] = case['id']
            folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-training100-', dir=output/'public-state')))
            account_path = folder/'account.json';run_path = folder/'run.json'
            account_bytes = (json.dumps(case['account'], ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
            run_bytes = (json.dumps(run_fixture(case['member']), ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
            account_path.write_bytes(account_bytes);run_path.write_bytes(run_bytes)
            module.OPERATOR_STATE = account_path;module.RUN_STATE = run_path;module.SETTINGS = folder/'settings.json'
            module.DesktopBackend = lambda _path, callback, public=folder: original_backend(public/'chat', callback)
            window = module.MainWindow();window.resize(1400, 1050);window.show()
            window.centralWidget().setCurrentIndex(1);application.processEvents()
            assert type(window.run) is RunState
            assert window.operator_observations is window.account_cache.records
            idle()
            assert window.auto_relics.isChecked() and not window.target_buff_test.isChecked()
            assert disks(account_path, run_path)['account'] == account_bytes
            assert disks(account_path, run_path)['run'] == run_bytes
            step('select same known operator', lambda: window.operator_choices.select_value(OP), account_path, run_path)
            skill_index = window.skill.findData(3);assert skill_index >= 0
            step('select actual S3 combo', lambda: window.skill.setCurrentIndex(skill_index), account_path, run_path)
            step('actual calculate', window.calculate, account_path, run_path)
            snapshot = report_snapshot()
            assert snapshot['level'] == case['level']
            assert snapshot['damage_result']['result']['estimate']['skill']['sp_cost'] == 28
            assert cargo_applied()[1] == [('attack_pct', 0.0), ('hp_pct', 0.0), ('defense_pct', 0.0)]
            assert mechanics()['char_buffs'][SNACK]['name'] in window.target_buff_status.text()
            row = {'id': case['id'], 'disk_sha256': {'account': sha(account_bytes), 'run': sha(run_bytes)},
                   'initial_level': window.level.value(), 'status': window.training_status.text(),
                   'target_buff_status': window.target_buff_status.text(), 'steps': []}
            record = write_record(output/'records', len(record_rows)+1,
                                  {'kind': 'window_snapshot', 'case': case['id'], 'comparable': snapshot,
                                   'durable': freeze(durable()), 'disks': freeze(disks(account_path, run_path)),
                                   'training_status': window.training_status.text()})
            record.update(kind='window_snapshot', case=case['id']);record_rows.append(record)
            row['snapshot_record'] = record
            if case['id'] in HEALTHY_IDS and args.mode == 'candidate':
                gold_row = next(r for r in baseline['cases'] if r['id']==case['id'])
                assert gold_row['disk_sha256'] == row['disk_sha256']
                saved = read_record(baseline_dir/'records', gold_row['snapshot_record'])
                assert_native_equal(snapshot, saved['comparable'], 'Same healthy facts retain native result and all three texts')
                row['actual_gold_native_and_three_texts_equal'] = True
            state = window.current_operator_state()
            if args.mode == 'candidate':
                metadata = window.current_run_operator_state()
                assert metadata is window.run.state['operators'][OP]
                assert metadata['char_buff_ids'] == [SNACK]
                if case['id'].startswith('unsafe-') or case['id']=='manual-level-override':
                    assert '不可用' in window.training_status.text()
                    assert state.get('scope') != 'run', 'Unsafe training does not claim current-run confirmation'
                if case['id']=='healthy-masked':
                    assert 'elite' not in state['run_confirmed_fields'] and 'level' not in state['run_confirmed_fields']
                    assert '1' not in state['skill_ranks'] and state['fields']['potential']==6
                if case['id']=='unsafe-without-account':
                    assert state == {} and '档案预览' in window.training_status.text()
                    scenario=snapshot['damage_result']['scenario']
                    assert '精英阶段' in scenario['unconfirmed_training'] and '当前等级' in scenario['unconfirmed_training']
                if case['id']=='incompatible-account-fill':
                    assert state['fields'] == {'potential':6} and '不兼容' in window.training_status.text()
                    assert window.training_conditions()['elite']==2
                if case['id']=='unsafe-elite':
                    window.run.state['operators'][OP]['recruitment_kind']='emergency_hire'
                    step('same bad cultivation with confirmed emergency source', window.calculate, account_path, run_path)
                    assert cargo_applied()[1] == [('attack_pct', .4), ('hp_pct', .4), ('defense_pct', .4)]
                    assert report_snapshot()['damage_result']['result']['estimate']['skill']['sp_cost']==28
                    window.run.state['operators'][OP]['recruitment_kind']='non_emergency'
                    step('restore exact ordinary recruitment source', window.calculate, account_path, run_path)
                    assert cargo_applied()[1] == [('attack_pct', 0.0), ('hp_pct', 0.0), ('defense_pct', 0.0)]
                    step('actual run-training toggle off', lambda: window.use_run_training.setChecked(False), account_path, run_path)
                    assert window.current_run_operator_state()=={}
                    assert report_snapshot()['damage_result']['result']['estimate']['skill']['sp_cost']==35
                    assert cargo_applied()[0]['missing_conditions']==['emergency_hire']
                    step('actual run-training toggle on', lambda: window.use_run_training.setChecked(True), account_path, run_path)
                    assert report_snapshot()['damage_result']['result']['estimate']['skill']['sp_cost']==28
                    window.run.state['operators'][OP]['present']=False
                    step('departed original gate', window.update_operator, account_path, run_path)
                    assert window.current_run_operator_state()=={}
                    assert report_snapshot()['damage_result']['result']['estimate']['skill']['sp_cost']==35
                    window.run.state['operators'][OP]['present']=True
                    step('present original gate', window.update_operator, account_path, run_path)
                    assert report_snapshot()['damage_result']['result']['estimate']['skill']['sp_cost']==28
                    assert disks(account_path, run_path)['run']==run_bytes
                    row['steps'].extend(['confirmed-emergency/ordinary40percent/0percent',
                                         'run-toggle-off-on35/28','departed-present35/28'])
                if case['id']=='manual-level-override':
                    step('actual manual level valueChanged', lambda: window.level.setValue(17), account_path, run_path)
                    assert window.level_override is True
                    step('actual preserve_level=True', lambda: window.update_operator(preserve_level=True), account_path, run_path)
                    manual_state=window.current_operator_state()
                    assert manual_state['fields']['level'] is None and manual_state['fields']['potential']==6
                    assert window.level.value()==17 and window.training_conditions()['potential']==6
                    report_snapshot();row['steps'].append('saved None unused while manual level17/potential6 confirmed')
            if args.mode == 'candidate' and case['id'] in PNG_CASES:
                idle();png=output/PNG_CASES[case['id']]
                assert window.grab().save(str(png), 'PNG')
                png_rows.append(file_info(png))
            if args.mode=='candidate' and case['id']=='manual-level-override':
                buttons=[button for button in window.findChildren(QPushButton) if button.text()=='使用读取等级']
                assert len(buttons)==1
                step('actual restore-level button click', buttons[0].click, account_path, run_path)
                assert window.level.value()==80 and window.training_conditions()['potential']==1
                assert '不可用' in window.training_status.text()
                report_snapshot();row['steps'].append('restore button retries actual setter path and safely falls back')
            caller=freeze(durable());disk=freeze(disks(account_path, run_path))
            window.close();application.processEvents()
            assert_native_equal(durable(), caller, 'Real close preserves native durable state')
            assert_native_equal(disks(account_path, run_path), disk, 'Real close preserves original public disks')
            assert_native_equal(disks(account_path, run_path),
                                {'account': account_bytes, 'run': run_bytes,
                                 'account_tmp': False, 'run_tmp': False},
                                'Real close preserves original bytes across the complete public case')
            window.deleteLater();application.processEvents();window=None
            case_rows.append(row)
            write_json(output/'progress.json', {'mode':args.mode,'case':case['id'],'completed':len(case_rows),
                                               'elapsed_seconds':time.perf_counter()-started,'Qt_exceptions':qt_errors})
            print(json.dumps({'completed_case':case['id'],'completed':len(case_rows)}, ensure_ascii=False), flush=True)
        assert len(case_rows)==(5 if args.mode=='gold' else 12)
        assert len(png_rows)==(0 if args.mode=='gold' else 4)
        assert not qt_errors
        assert source_map(root)==expected
        receipt.update(passed=True, workflow_complete=True,
                       healthy_native_three_text_pairs=(0 if args.mode=='gold' else 5),
                       finished_at_UTC=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter()-started)
        return 0
    except BaseException as error:
        receipt['failure']={'active_case':active_case['id'],'type':type(error).__name__, 'message':str(error),
                            'traceback':traceback.format_exc()}
        raise
    finally:
        if window is not None:
            try:window.close();application.processEvents()
            except BaseException as error:receipt['close_failure']={'type':type(error).__name__,'message':str(error)}
        if module is not None:
            if original_calc is not None:module.calculate_damage=original_calc
            if original_backend is not None:module.DesktopBackend=original_backend
        folders.close();sys.excepthook=old_hook
        write_json(output/'receipt.json', receipt);finished.set()


if __name__=='__main__':
    raise SystemExit(main())
