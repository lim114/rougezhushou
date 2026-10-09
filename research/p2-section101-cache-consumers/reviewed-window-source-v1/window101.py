"""Root-only101 real candidate MainWindow smoke; Source compiled, never run by author.

Observation only: complete/primary0 is not a product pass. Real Qt signal
exceptions and direct constructor exceptions are retained without inventing a
successful UI outcome. All persisted data is public and isolated.
"""
import argparse
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

APP_SHA = '34f0c92061460b239fd0af80ec263673765a16753826f6151fde87a88b89a35b'
VIEW_SHA = '5bef7b6f03592a5df615711568d116a0ffd9170f9be99832ca75d9eee78fcdb4'
SNACK = 'rogue_6_from_relic_13'
UNKNOWN_BOUND = 'public-unknown-char-buff-101'
UNKNOWN_PENDING = 'public-unknown-pending-buff-101'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_map(root):
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        assert (root/folder).is_dir()
        for path in sorted((root/folder).rglob('*')):
            relative = path.relative_to(root)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            assert not path.is_symlink()
            if path.is_file():result[relative.as_posix()] = sha(path.read_bytes())
    return dict(sorted(result.items()))


def write_json(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')
    os.replace(temporary, path)


def account():
    return {'id': 'mechanist', 'scope': 'operator_profile',
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1,
                       'module_id': None, 'module_level': 0, 'selected_skill': 3},
            'skill_ranks': {'1': 7, '3': 10}, 'captured_at': 1000.0,
            'sources': {}, 'field_times': {}, 'skill_times': {}}


def member(kind):
    value = {**account(), 'scope': 'run', 'present': True,
             'recruitment_kind': 'non_emergency', 'char_buff_ids': [SNACK],
             'char_buffs_complete': False, 'char_buff_absent_ids': [],
             'char_buff_pending_ids': [], 'invalid_fields': [],
             'invalid_skill_ranks': [], 'missing_fields': []}
    if kind == 'unknown-bound':value['char_buff_ids'] = [UNKNOWN_BOUND]
    if kind == 'unknown-pending':value['char_buff_pending_ids'] = [UNKNOWN_PENDING]
    return value


def run_fixture(kind):
    return {'id': 'public-charbuff101-original', 'started_at': 0.0,
            'last_read': 1000.0, 'operators': {'mechanist': member(kind)},
            'crew_count': 1, 'selected_operator': 'mechanist',
            'relics': {}, 'relic_count': 0, 'bar_signature': [],
            'inventory_verified': True, 'inventory_confirmed_at': 1000.0,
            'relic_icon_memory': None, 'history': [], 'resources': {},
            'tactical_tools': {}, 'config': {}, 'maps': {},
            'last_node_content': None, 'node_contents': []}


from native_evidence import freeze, assert_native_equal, write_record

HELPER_SHA = '96765f55f696815c44b9c3eb22b4e6247f4ffe1c9d3a064c5301cfdc33de7e3b'
TEST_SHA = 'cf8654a622f8c09d4ec41cbd1a857c9e1733c500c3fc9c93ecb495f9f36f18b8'
NATIVE_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
ORIGINAL_SHA = 'eb18f912f78fd5a90b3efdf75602726da87b03ef871bb0471dcf809d354fc171'
COUNTER_SHA = '6c06be67ea7e0e864fac28b1c697383e2782c669f72699a104ad35bfc8a91403'
PNG_CASES = {'unknown-bound': 'training101-unknown-bound.png',
             'unknown-pending': 'training101-unknown-pending.png',
             'counter-source-null': 'training101-historical-counter.png',
             'present-null': 'training101-presence-gate.png'}
ALTAR = 'rogue_6_relic_legacy_103'


def cases(counter):
    values = [{'id': identity, 'fixture': run_fixture(identity),
               'unknown': identity.startswith('unknown-'), 'sp': 28}
              for identity in ('healthy-snack', 'unknown-bound', 'unknown-pending')]
    for identity, count in (('stored-count-text', '0'), ('stored-count-null', None), ('stored-count-zero', 0)):
        fixture = run_fixture('healthy-snack');fixture['relic_count'] = count
        values.append({'id': identity, 'fixture': fixture, 'sp': 28, 'apply_unread': True})
    for identity, present, expected in (('present-text', 'yes', 28), ('present-null', None, 35)):
        fixture = run_fixture('healthy-snack');fixture['operators']['mechanist']['present'] = present
        values.append({'id': identity, 'fixture': fixture, 'sp': expected,
                       'summary_members': 1 if present else 0})
    fixture = run_fixture('healthy-snack')
    fixture['resources'] = {'public_counter': {'value': 1, 'captured_at': 0,
                            'source': 'held_card_counter', 'counter_evidence': {'id': []}}}
    values.append({'id': 'counter-list-id', 'fixture': fixture, 'sp': 28, 'withheld': 'public_counter'})
    for identity, provenance in (('healthy-counter', 'held_full_name_usage_and_public_probe'),
                                 ('counter-source-null', None), ('counter-source-list', []),
                                 ('counter-source-number', 1)):
        fixture = run_fixture('healthy-snack');record = freeze(counter)
        record['counter_evidence']['source'] = provenance
        fixture['resources'] = {'altar_stacks': record}
        fixture['relics'] = {ALTAR: {'held': True}}
        fixture['relic_count'] = 1;fixture['bar_signature'] = [[ALTAR]]
        values.append({'id': identity, 'fixture': fixture, 'sp': 28,
                       'withheld': None if identity=='healthy-counter' else 'altar_stacks',
                       'usable_counter': identity=='healthy-counter'})
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--original', required=True)
    parser.add_argument('--original-exit', required=True)
    parser.add_argument('--counter-evidence', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve();output = Path(args.out).resolve()
    assert not output.exists() and output != root and root not in output.parents
    guard_path = Path(args.guard).resolve();guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw);expected = guard.get('source_sha256', guard.get('source_sha256_after'))
    assert type(expected) is dict and len(expected)==745
    assert source_map(root)==expected
    assert expected['rouge/run_metadata_view.py']==HELPER_SHA
    assert expected['tests/test_cache_consumers_101.py']==TEST_SHA
    assert expected['rouge/training_view.py']==VIEW_SHA
    assert sha(Path(__file__).with_name('native_evidence.py').read_bytes())==NATIVE_SHA
    original_path = Path(args.original);original_raw = original_path.read_bytes()
    assert sha(original_raw)==ORIGINAL_SHA
    original = json.loads(original_raw)
    assert original['observation_complete'] is True and original['product_pass'] is False
    assert original['runner_sha256']=='933b8181cf70cb5ddb666c0be6d614a6be02153ff9a74b5af8cbce477755f471'
    assert int(Path(args.original_exit).read_text())==0
    assert original['source_before']['rouge/app.py']==APP_SHA
    assert set(expected)-set(original['source_before'])=={'rouge/run_metadata_view.py','tests/test_cache_consumers_101.py'}
    assert not set(original['source_before'])-set(expected)
    changed={key for key in original['source_before'] if expected[key]!=original['source_before'][key]}
    assert changed=={'rouge/run_state.py','rouge/app.py','rouge/relic_counter_semantics.py','scripts/verify_cloud.py'}
    old_rows={row['id']:row for row in original['rows']}
    assert set(old_rows)=={'healthy-snack','unknown-bound','unknown-pending'}
    assert old_rows['healthy-snack']['constructor_returned'] is True
    assert not old_rows['healthy-snack']['Qt_signal_exceptions']
    for identity in ('unknown-bound','unknown-pending'):
        assert old_rows[identity]['constructor_returned'] is False
        assert old_rows[identity]['direct_exception']['type']=='KeyError'
        assert len(old_rows[identity]['Qt_signal_exceptions'])==1
        assert old_rows[identity]['original_disks_unchanged'] is True
    counter_raw = Path(args.counter_evidence).read_bytes()
    assert sha(counter_raw)==COUNTER_SHA
    counter_evidence = json.loads(counter_raw)
    healthy_counter = next(row for row in counter_evidence['cases'] if row['id']=='healthy-text')
    assert healthy_counter['accepted_without_rejection'] is True
    counter = healthy_counter['fixture_JSON']['resources']['altar_stacks']
    output.mkdir(parents=True);(output/'records').mkdir();(output/'public-state').mkdir()
    rows=[];records=[];pngs=[];qt_errors=[];call_records=[];active={'id':'preimport'}
    finished=threading.Event();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_101_REAL_MAINWINDOW_CANDIDATE', 'passed':False,
             'workflow_complete':False,'source_before':expected,'source_guard_sha256':sha(guard_raw),
             'runner_sha256':sha(Path(__file__).read_bytes()),'native_helper_sha256':NATIVE_SHA,
             'actual_original_observation_sha256':ORIGINAL_SHA,'counter_evidence_sha256':COUNTER_SHA,
             'original_primary_exit':0,'rows':rows,'records':records,'pngs':pngs,'Qt_errors':qt_errors,
             'calculate_call_records':call_records,'deadline_seconds':450,
             'private_state_access':False,'game_chat_sampling_executed':False,
             'native_windows_verified':False,
             'healthy_baseline_scope':'Same actual original fixture disk hashes, JSON values and UI text; original probe stored JSON, not native alias evidence. Candidate native arguments/results/three-text views are separately retained.',
             'started_at_UTC':datetime.now(timezone.utc).isoformat()}
    old_hook=sys.excepthook;application=None;module=None;original_backend=None;original_calc=None;window=None

    def deadline():
        if not finished.wait(450):
            write_json(output/'timeout.json',{'passed':False,'workflow_complete':False,
                       'active_case':active['id'],'elapsed':time.perf_counter()-started})
            os._exit(124)

    def observed_exception(kind,error,trace):
        qt_errors.append({'case':active['id'],'type':kind.__name__,'message':str(error),
                          'traceback':''.join(traceback.format_exception(kind,error,trace))})
        old_hook(kind,error,trace)

    def save(kind,value):
        row=write_record(output/'records',len(records)+1,{'kind':kind,'case':active['id'],**value})
        row.update(kind=kind,case=active['id']);records.append(row)
        return row

    threading.Thread(target=deadline,daemon=True).start();sys.excepthook=observed_exception
    try:
        sys.path.insert(0,str(root))
        from PySide6 import __version__ as pyside_version
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.run_state import RunState
        application=QApplication.instance() or QApplication([])
        assert pyside_version=='6.9.3' and qVersion()=='6.9.3'
        receipt.update(python=sys.version,sys_platform=sys.platform,pyside=pyside_version,qt=qVersion())
        original_backend=module.DesktopBackend;original_calc=module.calculate_damage

        def observed_calculation(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:
                value=original_calc(*positional,**keywords)
            except BaseException as error:
                assert_native_equal({'args':positional,'kwargs':keywords},before,'Failing numeric API preserves original caller')
                row=save('actual_calculate_exception',{'before':before,'after':freeze({'args':positional,'kwargs':keywords}),
                         'exception':{'type':type(error).__name__,'message':str(error)}})
                row.update(exception_type=type(error).__name__,exception_message=str(error),
                           operator=before['args'][0].get('operator') if len(before['args'])==1 else None)
                if active['id'] in ('unknown-bound','unknown-pending') and row['operator']=='mechanist':
                    assert len(before['args'])==1 and not before['kwargs']
                    expected_member=member(active['id']);actual_input=before['args'][0]
                    assert_native_equal(actual_input['char_buff_ids'],expected_member['char_buff_ids'],
                                        'Original positive IDs reach the actual numeric API unchanged')
                    assert_native_equal(actual_input['char_buff_pending_ids'],expected_member['char_buff_pending_ids'],
                                        'Original pending IDs reach the actual numeric API unchanged')
                call_records.append(row)
                raise
            assert_native_equal({'args':positional,'kwargs':keywords},before,'Successful numeric API preserves original caller')
            row=save('actual_calculate_result',{'before':before,'after':freeze({'args':positional,'kwargs':keywords}),
                                               'result':freeze(value)})
            row['operator']=before['args'][0].get('operator') if len(before['args'])==1 else None
            call_records.append(row)
            return value

        module.calculate_damage=observed_calculation
        for case in cases(counter):
            active['id']=case['id'];first_call=len(call_records)
            with tempfile.TemporaryDirectory(prefix='public-window101-',dir=output/'public-state') as directory:
                folder=Path(directory);account_path=folder/'account.json';run_path=folder/'run.json'
                account_raw=(json.dumps({'mechanist':account()},ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                run_raw=(json.dumps(case['fixture'],ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_path.write_bytes(account_raw);run_path.write_bytes(run_raw)
                module.OPERATOR_STATE=account_path;module.RUN_STATE=run_path;module.SETTINGS=folder/'settings.json'
                module.DesktopBackend=lambda _path,callback,public=folder:original_backend(public/'chat',callback)
                window=module.MainWindow();window.resize(1400,1050);window.show();window.centralWidget().setCurrentIndex(1)

                def idle():
                    application.processEvents()
                    assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending
                    assert not qt_errors,qt_errors

                def durable():
                    return {'run':window.run.state,'account':window.account_cache.records}

                def disks():
                    return {'account':account_path.read_bytes(),'run':run_path.read_bytes(),
                            'account_tmp':account_path.with_suffix('.tmp').exists(),
                            'run_tmp':run_path.with_suffix('.tmp').exists()}

                def original_disks():
                    assert_native_equal(disks(),{'account':account_raw,'run':run_raw,'account_tmp':False,'run_tmp':False},
                                        'Pure UI/view consumers retain original public disk bytes')

                def action(label,function):
                    state=freeze(durable());disk=freeze(disks())
                    function();idle()
                    assert_native_equal(durable(),state,'Pure UI preserves native loaded records: '+label)
                    assert_native_equal(disks(),disk,'Pure UI preserves native public disks: '+label)

                def snapshot():
                    state=freeze(durable());disk=freeze(disks());value=window.damage_result
                    texts=None
                    if value is not None:
                        before=freeze(value);result=value['result']
                        texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                               'technical':reporting.format_report(result,technical=True)}
                        assert texts['estimate']==texts['default']
                        assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                        assert_native_equal(value,before,'Three report formatters retain actual native result')
                    result={'damage_result':value,'three_texts':texts,'damage_text':window.damage_text.toPlainText(),
                            'buff_status':window.target_buff_status.text(),'summary':window.run.summary(),
                            'run_metadata':window.current_run_operator_state(),
                            'usable_resources':window.run.calculation_resources()}
                    assert_native_equal(durable(),state,'Formatting/metadata/resource views retain loaded caller')
                    assert_native_equal(disks(),disk,'Formatting/metadata/resource views retain native disks')
                    return result

                idle();original_disks()
                assert isinstance(window.run,RunState) and not window.run.preserve_unreadable
                action('same selected operator',lambda:window.operator_choices.select_value('mechanist'))
                index=window.skill.findData(3);assert index>=0
                action('actual S3 combo',lambda:window.skill.setCurrentIndex(index))
                action('actual calculate',window.calculate)
                view=snapshot();original_disks()
                row={'id':case['id'],'constructor_returned':True,'snapshot_record':save('actual_window_snapshot',
                      {'view':view,'durable':freeze(durable()),'disks':freeze(disks())}),
                     'original_disk_sha256':{'account':sha(account_raw),'run':sha(run_raw)},'steps':[]}
                if case['id'] in old_rows:
                    assert old_rows[case['id']]['original_disk_sha256']==row['original_disk_sha256']
                if case.get('unknown'):
                    assert window.damage_result is None
                    assert '暂不可确认' in view['buff_status']
                    assert '已确认' not in view['buff_status'] and '已核对' not in view['buff_status']
                    metadata=view['run_metadata'];original_member=case['fixture']['operators']['mechanist']
                    assert_native_equal(metadata,original_member,'Original unknown IDs/metadata must not be filtered')
                    this_calls=[record for record in call_records[first_call:] if record['operator']=='mechanist']
                    assert this_calls and all(r['kind']=='actual_calculate_exception' and r['exception_type']=='ValueError'
                                              for r in this_calls)
                    expected_error='未知干员定向强化' if case['id']=='unknown-bound' else '待更新的个人强化'
                    assert expected_error in view['damage_text']
                    row['original_numeric_ValueError_retained']=True
                else:
                    assert window.damage_result['result']['estimate']['skill']['sp_cost']==case['sp']
                if case['id']=='healthy-snack':
                    actual_json=json.loads(json.dumps(window.damage_result,ensure_ascii=False,allow_nan=False))
                    assert_native_equal(actual_json,old_rows['healthy-snack']['damage_result'],
                                        'Healthy actual original JSON values equal; this comparison does not prove original aliases')
                    assert view['damage_text']==old_rows['healthy-snack']['damage_text']
                    row['actual_original_JSON_values_and_UI_text_equal']=True
                if 'summary_members' in case:
                    assert f"当前已识别 {case['summary_members']} /" in view['summary']
                    assert_native_equal(window.run.state['operators']['mechanist']['present'],
                                        case['fixture']['operators']['mechanist']['present'],'Stored presence remains exact')
                if case.get('withheld'):
                    key=case['withheld'];assert key not in view['usable_resources']
                    assert key not in window.damage_result['scenario'].get('relic_context',{})
                    assert '历史值，当前层数待确认' in view['summary']
                    assert_native_equal(window.run.state['resources'],case['fixture']['resources'],'Bad proof remains original history')
                if case.get('usable_counter'):
                    assert view['usable_resources']['altar_stacks']['value']==1
                    assert window.damage_result['scenario']['relic_context']['altar_stacks']==1
                if case['id'] in PNG_CASES:
                    idle();path=output/PNG_CASES[case['id']];assert window.grab().save(str(path),'PNG')
                    raw=path.read_bytes();pngs.append({'path':str(path),'bytes':len(raw),'sha256':sha(raw)})
                if case.get('apply_unread'):
                    observed={'operators':[]};caller=freeze(observed);old_count=freeze(window.run.state['relic_count'])
                    assert window.apply_run_observation(observed,1001.0) is True
                    idle();assert_native_equal(observed,caller,'Actual observation caller is unchanged')
                    assert_native_equal(window.run.state['relic_count'],old_count,'Unread page does not rewrite opaque count')
                    assert window.run.save_issue is None and not window.run.preserve_unreadable
                    saved=json.loads(run_path.read_bytes());assert_native_equal(saved['relic_count'],old_count,'Legitimate save preserves count type/value')
                    assert account_path.read_bytes()==account_raw
                    assert not run_path.with_suffix('.tmp').exists() and not account_path.with_suffix('.tmp').exists()
                    phase_disk=freeze(disks());restored=RunState(run_path)
                    assert_native_equal(restored.state['relic_count'],old_count,'Actual restart preserves opaque count type/value')
                    assert_native_equal(disks(),phase_disk,'Restart does not rewrite accepted observation file')
                    row['steps'].append('actual unread observation+authorized save+restart; original count preserved')
                    row['post_observation_record']=save('actual_after_authorized_observation',
                                                       {'view':snapshot(),'durable':freeze(durable()),'disks':freeze(disks())})
                state=freeze(durable());disk=freeze(disks())
                window.close();application.processEvents()
                assert_native_equal(durable(),state,'Actual close retains native loaded state')
                assert_native_equal(disks(),disk,'Actual close retains its current authorized disk phase')
                if not case.get('apply_unread'):original_disks()
                window.deleteLater();application.processEvents();window=None
                row['calculate_call_records']=call_records[first_call:];rows.append(row)
                write_json(output/'progress.json',{'completed':len(rows),'active_case':case['id'],'Qt_errors':qt_errors})
                print(json.dumps({'completed_case':case['id'],'completed':len(rows)},ensure_ascii=False),flush=True)
        assert len(rows)==13 and len(pngs)==4 and not qt_errors
        assert source_map(root)==expected
        receipt.update(passed=True,workflow_complete=True,elapsed_seconds=time.perf_counter()-started,
                       finished_at_UTC=datetime.now(timezone.utc).isoformat())
        return 0
    except BaseException as error:
        receipt['failure']={'case':active['id'],'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        raise
    finally:
        if window is not None:
            try:window.close();application.processEvents()
            except BaseException as error:receipt['close_failure']={'type':type(error).__name__,'message':str(error)}
        if module is not None:
            if original_backend is not None:module.DesktopBackend=original_backend
            if original_calc is not None:module.calculate_damage=original_calc
        sys.excepthook=old_hook;write_json(output/'receipt.json',receipt);finished.set()


if __name__=='__main__':
    raise SystemExit(main())
