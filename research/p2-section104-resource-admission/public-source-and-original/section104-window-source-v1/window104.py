"""Root-only actual MainWindow resource admission Gold/candidate verification.

The author only reads and compiles Source. Public constructed API inputs do not
claim a natural OCR failure. Numeric calls pass through the original calculator.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, read_record, write_record, source_map


HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
ORIGINAL_SHA = '6cc40a282005aec7d201bc6aeec4608f83e1b96954055bdd7cc75059e7c0cb7f'
OWNER = 'mechanist'
GOLD = 'rogue_6_relic_legacy_60'
HEALTHY_COUNT = 9
CASE_COUNT = 18


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def account():
    return {'id': OWNER, 'scope': 'operator_profile',
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1,
                       'module_id': None, 'module_level': 0, 'selected_skill': 3},
            'skill_ranks': {'1': 7, '3': 10}, 'captured_at': 1000.0,
            'sources': {}, 'field_times': {}, 'skill_times': {}}


def record(value, *, parts=False):
    result = {'value': value, 'source': 'public-resource104',
              'public_opaque': {'nullable': None, 'negative_zero': -0.0}}
    if parts:
        result['capacity'] = 12
    return result


def fixture(identity, old, *, held=True):
    member = {**account(), 'scope': 'run', 'present': True,
              'recruitment_kind': 'non_emergency', 'char_buff_ids': [],
              'char_buffs_complete': False, 'char_buff_absent_ids': [],
              'char_buff_pending_ids': [], 'missing_fields': [],
              'invalid_fields': [], 'invalid_skill_ranks': []}
    relics = {GOLD: {'held': True, 'captured_at': 1000.0,
                    'source': 'public-resource104-held', 'icon_evidence': {}}} if held else {}
    return {'id': 'public-window104-' + identity, 'started_at': 0.0,
            'last_read': 1000.0, 'operators': {OWNER: member}, 'crew_count': 1,
            'selected_operator': OWNER, 'relics': relics, 'tactical_tools': {},
            'relic_count': 1 if held else 0, 'inventory_verified': True,
            'inventory_confirmed_at': 1000.0,
            'bar_signature': [[GOLD]] if held else [], 'relic_icon_memory': None,
            'history': [], 'resources': deepcopy(old), 'config': {}, 'maps': {},
            'last_node_content': None, 'node_contents': [],
            'public_opaque': {'negative_zero': -0.0, 'nullable': None}}


def old_records(gold=25, parts=3):
    return {'gold': {**record(gold), 'captured_at': 1000.0},
            'parts_count': {**record(parts, parts=True), 'captured_at': 1000.0}}


def read(resources, **other):
    return {'operators': [], 'relics': {'ids': [], 'icons': [], 'count': None,
            'source': 'public-resource104'}, 'resources': resources, **other}


def row(identity, old, observed, expected, *, healthy=False, held=True,
        events=(), difficulty=None, stable=False, failed_io=False, followup=None):
    return {'id': identity, 'healthy': healthy, 'saved': fixture(identity, old, held=held),
            'observed': observed, 'expected_resources': expected, 'events': list(events),
            'difficulty': difficulty, 'stable_math': stable, 'failed_io': failed_io,
            'followup': followup}


def cases(phase):
    positive = old_records()
    zero = old_records(0, 0)
    updated = {'gold': {**record(26), 'captured_at': 1001.0},
               'parts_count': {**record(4, parts=True), 'captured_at': 1001.0}}
    rows = [row('healthy-zero', zero, read({}), zero, healthy=True, stable=True),
            row('healthy-positive-update', positive,
                read({'gold': record(26), 'parts_count': record(4, parts=True)}),
                updated, healthy=True, events=(('gold', 26), ('parts_count', 4))),
            row('healthy-unread-positive', positive, read({}), positive,
                healthy=True, stable=True)]
    for identity, old_value, fresh_value in (('healthy-float-unconsumed', 8.0, 8.0),
                                           ('healthy-null-unconsumed', None, None),
                                           ('healthy-bool-unconsumed', True, False),
                                           ('healthy-text-unconsumed', '8', '9')):
        old = {'gold': {**record(old_value), 'captured_at': 1000.0}}
        expected = {'gold': {**record(fresh_value), 'captured_at': 1001.0}}
        events = (('gold', fresh_value),) if old_value != fresh_value else ()
        rows.append(row(identity, old, read({'gold': record(fresh_value)}), expected,
                        healthy=True, held=False, events=events))
    shared = {'public': [None, -0.0]}
    cycle = []
    cycle.append(cycle)
    aliases = {**record(25), 'public_left': shared, 'public_right': shared}
    alias_expected = {'gold': {**aliases, 'captured_at': 1001.0},
                      'parts_count': positive['parts_count']}
    rows.append(row('healthy-unused-opaque-alias', positive,
                    read({'gold': aliases}, public_opaque={'left': shared, 'right': shared,
                                                          'unused_cycle': cycle}),
                    alias_expected, healthy=True, stable=True))
    failed_expected = {'gold': {**record(26), 'captured_at': 1001.0},
                       'parts_count': positive['parts_count']}
    rows.append(row('healthy-actual-IO-memory', positive, read({'gold': record(26)}),
                    failed_expected, healthy=True, events=(('gold', 26),), failed_io=True))
    assert len(rows) == HEALTHY_COUNT
    if phase == 'candidate':
        null = old_records(None, None)
        peer_parts = {**record(4, parts=True), 'captured_at': 1001.0}
        peers = {'gold': positive['gold'], 'parts_count': peer_parts}
        rows.extend([
            row('bad-no-old-missing-both', {}, read({'gold': {}, 'parts_count': {}}),
                {}, held=False, stable=True),
            row('bad-old-null-missing-both', null,
                read({'gold': {}, 'parts_count': {}}), null, held=False, stable=True),
            row('bad-old-positive-missing-both', positive,
                read({'gold': {}, 'parts_count': {}}), positive, stable=True),
            row('bad-null-record-with-peer-and-config', positive,
                read({'gold': None, 'parts_count': record(4, parts=True)},
                     config={'difficulty': {'value': 2, 'source': 'public-peer104'}}),
                peers, events=(('parts_count', 4),), difficulty=2),
            row('bad-container-null', positive, read(None), positive, stable=True),
            row('bad-container-list', positive, read([]), positive, stable=True),
            row('bad-record-list', positive,
                read({'gold': [], 'parts_count': []}), positive, stable=True),
            row('bad-unknown-counter-with-good-gold', positive,
                read({'public-unknown-counter104': None, 'gold': record(26)}),
                failed_expected, events=(('gold', 26),)),
            row('bad-read-after-actual-IO-memory', positive,
                read({'gold': record(26)}), failed_expected, events=(('gold', 26),),
                failed_io=True, followup=read({'gold': {}, 'parts_count': None}))])
    assert len(rows) == (HEALTHY_COUNT if phase == 'gold' else CASE_COUNT)
    return rows


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}


def main():
    parser = argparse.ArgumentParser()
    for name in ('root', 'guard', 'out', 'phase', 'original'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--gold')
    parser.add_argument('--gold-exit')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    artifact = Path(__file__).resolve().parent
    assert args.phase in ('gold', 'candidate') and not out.exists()
    assert out != root and root not in out.parents and root not in artifact.parents and artifact != root
    assert sha((artifact / 'native_evidence.py').read_bytes()) == HELPER_SHA
    original_path = Path(args.original).resolve()
    original_raw = original_path.read_bytes()
    assert sha(original_raw) == ORIGINAL_SHA
    original = json.loads(original_raw)
    assert original['observation_complete'] is True and original['product_pass'] is False
    assert original['observation_only'] is True and original['case_count'] == len(original['rows']) == 44
    assert len(original['source_before']) == 746 and original['source_before'] == original['source_after']
    assert original['source_drift'] == [] and original['CORE_drift'] is False
    guard_path = Path(args.guard).resolve()
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected = guard['source_sha256']
    extra = guard['source_additional_sha256']
    assert len(expected) == (747 if args.phase == 'gold' else 748)
    assert source_map(root) == expected
    assert 'CORE_0.70_VERIFICATION.json' in extra
    assert original['CORE_before'] == original['CORE_after'] == extra['CORE_0.70_VERIFICATION.json']
    for name, want in extra.items():
        assert sha((root / name).read_bytes()) == want
    assert set(expected) - set(original['source_before']) == (
        {'tests/test_cache_recovery_103.py'} if args.phase == 'gold' else
        {'tests/test_cache_recovery_103.py', 'tests/test_resource_observation_104.py'})
    assert not set(original['source_before']) - set(expected)
    gold = None
    gold_raw = None
    if args.phase == 'candidate':
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_text().strip() == '0'
        gold_dir = Path(args.gold).resolve()
        gold_raw = (gold_dir / 'receipt.json').read_bytes()
        gold = json.loads(gold_raw)
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['phase'] == 'gold'
        assert gold['runner_sha256'] == sha(Path(__file__).read_bytes())
        assert gold['native_helper_sha256'] == HELPER_SHA and gold['original_receipt_sha256'] == ORIGINAL_SHA
        assert len(gold['rows']) == HEALTHY_COUNT and gold['Qt_errors'] == []
        assert len(gold['source_before']) == 747 and gold['source_before'] == gold['source_after']
        assert gold['source_drift'] == [] and gold['source_additional_before'] == gold['source_additional_after'] == extra
        assert set(expected) - set(gold['source_before']) == {'tests/test_resource_observation_104.py'}
        assert not set(gold['source_before']) - set(expected)
        assert {name for name in gold['source_before'] if gold['source_before'][name] != expected[name]} == {
            'rouge/run_state.py', 'scripts/verify_cloud.py'}
        assert gold['native_windows_verified'] is False
    out.mkdir()
    (out / 'records').mkdir()
    (out / 'public-state').mkdir()
    rows = []
    records = []
    pngs = []
    qt_errors = []
    calls = []
    active = {'case': 'preimport', 'phase': 'preimport'}
    done = threading.Event()
    started = time.perf_counter()
    receipt = {'kind': 'ROOT_ACTUAL_104_REAL_MAINWINDOW', 'phase': args.phase,
               'passed': False, 'workflow_complete': False, 'rows': rows, 'records': records,
               'pngs': pngs, 'Qt_errors': qt_errors, 'deadline_seconds': 450,
               'source_before': expected, 'source_additional_before': extra,
               'source_guard_sha256': sha(guard_raw), 'runner_sha256': sha(Path(__file__).read_bytes()),
               'native_helper_sha256': HELPER_SHA, 'original_receipt_sha256': ORIGINAL_SHA,
               'original_receipt_path': str(original_path), 'original_case_count': 44,
               'native_windows_verified': False, 'natural_OCR_producer_verified': False,
               'private_state_access': False, 'game_chat_sampling_executed': False,
               'restart_scope': 'Actual close and direct RunState reload; no second MainWindow',
               'numeric_comparison_scope': 'All 9 healthy initial/post graphs and three complete texts against actual completed103 Gold; candidate bad reads retain exact facts/times and explicit stable-math checks',
               'source_hash_frequency': 'One full pre-import and one full final scan; none in window loop'}
    window = None
    application = None
    module = None
    backend = None
    calculator = None
    original_globals = None
    old_hook = sys.excepthook

    def save(kind, value):
        metadata = write_record(out / 'records', len(records) + 1,
                                {'kind': kind, 'case': active['case'], 'phase': active['phase'], **value})
        metadata.update(kind=kind, case=active['case'], phase=active['phase'])
        records.append(metadata)
        return metadata

    def deadline():
        if not done.wait(450):
            (out / 'timeout.json').write_text(json.dumps({'passed': False, 'active': active,
                                                         'deadline_seconds': 450}) + '\n')
            os._exit(124)

    def hook(kind, value, tb):
        qt_errors.append({'case': active['case'], 'phase': active['phase'],
                          'type': kind.__name__, 'message': str(value)})
        old_hook(kind, value, tb)

    threading.Thread(target=deadline, daemon=True).start()
    sys.excepthook = hook
    try:
        sys.path.insert(0, str(root))
        from PySide6 import __version__
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.run_state import RunState
        assert __version__ == qVersion() == '6.9.3'
        application = QApplication.instance() or QApplication([])
        receipt.update(python=sys.version, qt=qVersion())
        backend = module.DesktopBackend
        calculator = module.calculate_damage
        original_globals = (module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS)

        def observe_calculation(*positional, **keywords):
            before = freeze({'args': positional, 'kwargs': keywords})
            try:
                result = calculator(*positional, **keywords)
            except Exception as error:
                assert_native_equal({'args': positional, 'kwargs': keywords}, before,
                                    'Original failed calculator caller unchanged')
                details = error_record(error)
                calls.append({'case': active['case'], 'caller': before, 'error': details})
                save('actual_calculate_exception', {'before': before,
                     'after': freeze({'args': positional, 'kwargs': keywords}), 'error': details})
                raise
            assert_native_equal({'args': positional, 'kwargs': keywords}, before,
                                'Original successful calculator caller unchanged')
            calls.append({'case': active['case'], 'caller': before, 'error': None})
            save('actual_calculate_result', {'before': before,
                 'after': freeze({'args': positional, 'kwargs': keywords}), 'result': result})
            return result

        module.calculate_damage = observe_calculation
        for case in cases(args.phase):
            active.update(case=case['id'], phase='constructor')
            with tempfile.TemporaryDirectory(prefix='public104-', dir=out / 'public-state') as directory:
                folder = Path(directory)
                run_path = folder / 'run.json'
                account_path = folder / 'account.json'
                temporary = run_path.with_suffix('.tmp')
                saved = deepcopy(case['saved'])
                raw = (json.dumps(saved, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
                account_raw = (json.dumps({OWNER: account()}, ensure_ascii=False,
                                         allow_nan=False, indent=2) + '\n').encode()
                run_path.write_bytes(raw)
                account_path.write_bytes(account_raw)
                module.RUN_STATE = run_path
                module.OPERATOR_STATE = account_path
                module.SETTINGS = folder / 'settings.json'
                module.DesktopBackend = lambda _path, callback, public=folder: backend(public / 'chat', callback)
                window = module.MainWindow()
                window.resize(1400, 1050)
                window.show()
                window.centralWidget().setCurrentIndex(1)

                def idle():
                    application.processEvents()
                    assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending and not qt_errors

                def durable():
                    return {'run': window.run.state, 'account': window.account_cache.records,
                            'run_save_issue': window.run.save_issue,
                            'run_preserve_unreadable': window.run.preserve_unreadable}

                def disk(path):
                    if not path.exists():
                        return {'exists': False, 'kind': None, 'bytes': None}
                    if path.is_dir():
                        return {'exists': True, 'kind': 'directory',
                                'children': sorted(p.name for p in path.iterdir()),
                                'marker': (path / 'public-marker').read_bytes()}
                    return {'exists': True, 'kind': 'file', 'bytes': path.read_bytes()}

                def disks():
                    return {'run': disk(run_path), 'account': disk(account_path),
                            'run_tmp': disk(temporary), 'account_tmp': disk(account_path.with_suffix('.tmp'))}

                def unchanged(label, action):
                    before = freeze(durable())
                    before_disk = freeze(disks())
                    action()
                    idle()
                    assert_native_equal(durable(), before, label + ' raw state')
                    assert_native_equal(disks(), before_disk, label + ' disk bytes')

                def snapshot():
                    before = freeze(durable())
                    before_disk = freeze(disks())
                    result = window.damage_result
                    last = next(call for call in reversed(calls) if call['case'] == case['id'])
                    assert result is not None and last['error'] is None
                    assert result['scenario']['operator'] == OWNER and result['scenario']['skill'] == 3
                    assert last['caller']['args'][0]['operator'] == OWNER
                    assert last['caller']['args'][0]['skill'] == 3
                    original_result = freeze(result)
                    texts = {'estimate': estimate.format_estimate(result['result']),
                             'default': reporting.format_report(result['result']),
                             'technical': reporting.format_report(result['result'], technical=True)}
                    assert texts['estimate'] == texts['default']
                    assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
                    assert_native_equal(result, original_result, 'All actual formatter callers unchanged')
                    resources = window.run.calculation_resources()
                    summary = window.run.summary()
                    assert window.run_summary.text() == summary
                    value = {'view': {'damage_result': result, 'three_texts': texts,
                                      'displayed_damage': window.damage_text.toPlainText(),
                                      'summary': summary, 'resource_view': resources,
                                      'calculation_caller': last['caller']},
                             'durable': freeze(durable()), 'disks': freeze(disks())}
                    assert_native_equal(durable(), before, 'Summary/resources/math formatting raw-state read only')
                    assert_native_equal(disks(), before_disk, 'Summary/resources/math formatting disk read only')
                    return value

                def picture(name, tab):
                    unchanged('Show actual screenshot tab', lambda: window.centralWidget().setCurrentIndex(tab))
                    path = out / (name + '.png')
                    assert window.grab().save(str(path), 'PNG')
                    pngs.append({'case': case['id'], 'phase': active['phase'], 'tab_index': tab,
                                 'file': path.name, 'bytes': path.stat().st_size,
                                 'sha256': sha(path.read_bytes())})

                def match_gold(value, original_row, key):
                    evidence = read_record(gold_dir / 'records', original_row[key])
                    assert evidence['case'] == case['id']
                    assert evidence['kind'] == ('actual_initial_snapshot' if key == 'before' else 'actual_post_snapshot')
                    original_value = {name: evidence[name] for name in ('view', 'durable', 'disks')}
                    assert_native_equal(value, original_value,
                                        'Complete healthy native result/three texts/raw state and disk equal actual103 Gold')

                idle()
                assert run_path.read_bytes() == raw and account_path.read_bytes() == account_raw
                assert not temporary.exists() and not account_path.with_suffix('.tmp').exists()
                assert window.run.preserve_unreadable is False and window.run.save_issue is None
                assert window.run.state['id'] == saved['id']
                assert_native_equal(window.run.state['resources'], saved['resources'], 'Initial complete resource facts')
                active['phase'] = 'actual-initial-view'
                unchanged('Select actual mechanist', lambda: window.operator_choices.select_value(OWNER))
                skill_index = window.skill.findData(3)
                assert skill_index >= 0
                unchanged('Select actual S3', lambda: window.skill.setCurrentIndex(skill_index))
                unchanged('Calculate actual initial values', window.calculate)
                before = snapshot()
                result_row = {'id': case['id'], 'constructor_returned': True,
                              'before': save('actual_initial_snapshot', before)}
                original_row = None
                if case['healthy'] and args.phase == 'candidate':
                    original_row = next(item for item in gold['rows'] if item['id'] == case['id'])
                    match_gold(before, original_row, 'before')
                if case['failed_io']:
                    temporary.mkdir()
                    (temporary / 'public-marker').write_bytes(b'public-resource104-nonempty-temporary')
                active['phase'] = 'actual-observation-save'
                observed = deepcopy(case['observed'])
                caller = freeze((observed, 1001.0))
                assert window.apply_run_observation(observed, 1001.0) is True
                idle()
                assert_native_equal((observed, 1001.0), caller, 'Actual observation caller graph unchanged')
                assert window.run.preserve_unreadable is False
                assert_native_equal(window.run.state['resources'], case['expected_resources'],
                                    'Complete expected resource facts, types, float bits, order, aliases and times')
                events = [(event['resource'], event['value']) for event in window.run.state['history']
                          if event.get('kind') == 'resource_updated']
                assert_native_equal(events, case['events'], 'Actual resource history only for changed complete values')
                if case['difficulty'] is not None:
                    assert window.run.state['config']['difficulty'] == {
                        'value': 2, 'source': 'public-peer104', 'captured_at': 1001.0}
                    assert window.difficulty.currentData() == 2 and not window.difficulty.isEnabled()
                    assert [event['field'] for event in window.run.state['history']
                            if event.get('kind') == 'config_updated'] == ['difficulty']
                if case['failed_io']:
                    assert window.run.save_issue == '本局记录保存未完成'
                    assert '仅在当前运行有效' in window.run_summary.text()
                    assert run_path.read_bytes() == raw
                    assert (temporary / 'public-marker').read_bytes() == b'public-resource104-nonempty-temporary'
                else:
                    assert window.run.save_issue is None and not temporary.exists()
                if case['followup'] is not None:
                    active['phase'] = 'actual-unread-after-IO-failure'
                    issue = window.run.save_issue
                    original_resources = freeze(window.run.state['resources'])
                    followup = deepcopy(case['followup'])
                    second_caller = freeze((followup, 1002.0))
                    assert window.apply_run_observation(followup, 1002.0) is True
                    idle()
                    assert_native_equal((followup, 1002.0), second_caller, 'Post-IO unread caller unchanged')
                    assert_native_equal(window.run.state['resources'], original_resources,
                                        'Post-IO unread keeps original live fact and timestamp')
                    assert window.run.save_issue == issue and run_path.read_bytes() == raw
                    assert (temporary / 'public-marker').read_bytes() == b'public-resource104-nonempty-temporary'
                    result_row['post_IO_unread'] = save('actual_post_IO_unread', {
                        'caller_before': second_caller, 'caller_after': (followup, 1002.0),
                        'durable': freeze(durable()), 'disks': freeze(disks())})
                unchanged('Recalculate actual resource consumption', window.calculate)
                after = snapshot()
                if case['stable_math']:
                    assert_native_equal(after['view']['damage_result'], before['view']['damage_result'],
                                        'Unread or metadata-only observation keeps complete actual math graph')
                    assert_native_equal(after['view']['three_texts'], before['view']['three_texts'],
                                        'Unread or metadata-only observation keeps three complete reports')
                if case['id'] == 'healthy-unread-positive':
                    assert after['view']['damage_result']['result']['estimate']['base_stats']['attack_speed'] == 135
                    assert after['view']['damage_result']['scenario']['relic_context']['gold'] == 25
                if case['id'] == 'healthy-zero':
                    assert type(after['view']['damage_result']['scenario']['relic_context']['gold']) is int
                    assert after['view']['damage_result']['scenario']['relic_context']['gold'] == 0
                    assert window.run.state['resources']['gold']['captured_at'] == 1000.0
                if case['id'] == 'bad-no-old-missing-both':
                    assert window.run.state['resources'] == {}
                    assert '源石锭/零件数尚未确认' in window.run_summary.text()
                if case['id'] == 'bad-unknown-counter-with-good-gold':
                    assert 'public-unknown-counter104' not in window.run.state['resources']
                result_row['after'] = save('actual_post_snapshot', after)
                if original_row is not None:
                    match_gold(after, original_row, 'after')
                    result_row['complete_healthy_native_initial_post_and_three_texts_equal_Gold'] = True
                if args.phase == 'candidate':
                    if case['id'] == 'healthy-zero':
                        picture('resource-zero-confirmed', 0)
                    elif case['id'] == 'bad-null-record-with-peer-and-config':
                        picture('resource-unread-good-peer-and-config', 0)
                    elif case['id'] == 'bad-container-list':
                        picture('resource-unread-keeps-real-calculation', 1)
                    elif case['id'] == 'bad-read-after-actual-IO-memory':
                        picture('resource-save-failure-memory-scope', 0)
                active['phase'] = 'actual-close-and-restart'
                state_before_close = freeze(durable())
                disk_before_close = freeze(disks())
                window.close()
                application.processEvents()
                assert_native_equal(durable(), state_before_close, 'Actual close keeps live resource state')
                assert_native_equal(disks(), disk_before_close, 'Actual close keeps disk/temporary bytes')
                restarted = RunState(run_path)
                assert restarted.preserve_unreadable is False and restarted.save_issue is None
                assert restarted.state['id'] == saved['id']
                restart_state = freeze(restarted.state)
                restart_summary = restarted.summary()
                restart_resources = restarted.calculation_resources()
                assert_native_equal(restarted.state, restart_state, 'Actual restart views leave raw state unchanged')
                assert_native_equal(disks(), disk_before_close, 'Actual restart views leave old disk/temporary bytes')
                if case['failed_io']:
                    assert_native_equal(restarted.state['resources'], saved['resources'],
                                        'Actual failed IO reload restores older disk facts and original times')
                    assert '仅在当前运行有效' not in restart_summary
                    oracle = 'Actual older public disk; live unsaved fields were not persisted'
                else:
                    persisted = json.loads(run_path.read_text(encoding='utf-8'))
                    assert_native_equal(restarted.state, persisted, 'Actual saved JSON full native graph restores')
                    assert_native_equal(restart_resources, json.loads(json.dumps(after['view']['resource_view'])),
                                        'Actual resources restore through original JSON policy')
                    assert restart_summary == after['view']['summary']
                    if case['difficulty'] is not None:
                        assert restarted.state['config']['difficulty'] == window.run.state['config']['difficulty']
                    oracle = 'Actual persisted JSON graph; JSON does not preserve live aliases'
                result_row['restart'] = save('actual_restart', {
                    'state': restarted.state, 'summary': restart_summary, 'resource_view': restart_resources,
                    'oracle': oracle, 'live_before_close': state_before_close,
                    'disks': freeze(disks()), 'caller_before': caller, 'caller_after': (observed, 1001.0)})
                window.deleteLater()
                application.processEvents()
                window = None
                rows.append(result_row)
                print(json.dumps({'completed': len(rows), 'case': case['id']}), flush=True)
        assert len(rows) == (HEALTHY_COUNT if args.phase == 'gold' else CASE_COUNT)
        assert len(pngs) == (0 if args.phase == 'gold' else 4) and not qt_errors
        receipt.update(passed=True, workflow_complete=True)
    except BaseException as error:
        receipt['failure'] = error_record(error)
    finally:
        if window is not None:
            try:
                window.close()
                if application is not None:
                    application.processEvents()
            except BaseException as error:
                receipt['cleanup_error'] = error_record(error)
                receipt.update(passed=False, workflow_complete=False)
        if module is not None:
            if backend is not None:
                module.DesktopBackend = backend
            if calculator is not None:
                module.calculate_damage = calculator
            if original_globals is not None:
                module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS = original_globals
        sys.excepthook = old_hook
        receipt['calculate_call_count'] = len(calls)
        receipt['source_after'] = source_map(root)
        receipt['source_drift'] = [name for name in set(expected) | set(receipt['source_after'])
                                  if expected.get(name) != receipt['source_after'].get(name)]
        receipt['source_additional_after'] = {name: sha((root / name).read_bytes()) for name in extra}
        if (receipt['source_drift'] or receipt['source_additional_after'] != extra
                or guard_path.read_bytes() != guard_raw or qt_errors):
            receipt.update(passed=False, workflow_complete=False)
        if args.phase == 'candidate':
            receipt['actual_gold_receipt_sha256'] = sha(gold_raw)
        receipt['elapsed_seconds'] = time.perf_counter() - started
        (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
        done.set()
    print(json.dumps({'passed': receipt['passed'], 'windows': len(rows),
                      'records': len(records), 'elapsed_seconds': receipt['elapsed_seconds']}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
