"""Source only: bounded real MainWindow checks for applied section 098.

The author has not imported/executed the project, tests, this native helper,
Qt, Wine or Git. Root must bind its actual applied-098 full source guard,
independently review this Source, and execute on isolated public state.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import functools
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, sha256, source_map, write_record

CORE_SHA = 'ca338423cdce026293d0987365eefac7a16fe3769f6b2dff9d4e0faf1b956363'
DEADLINE_SECONDS = 300
OP = 'mechanist'
RELICS = ('rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26')
TOOL = 'rogue_6_active_tool_5'
START = 1700000000
MISSING = object()


def write_json(path, data):
    with path.open('w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=True, indent=2)
        handle.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--source-guard', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.out).resolve()
    guard_path = Path(args.source_guard).resolve()
    assert root.is_dir() and not output.exists()
    assert output != root and root not in output.parents
    guard = json.loads(guard_path.read_text(encoding='utf-8'))
    assert guard['section'] == 98
    before_source = source_map(root)
    assert before_source == guard['source_sha256']
    assert before_source['rouge/run_state.py'] == CORE_SHA
    assert "member.get('fields',{}).items()" in (root / 'rouge/app.py').read_text(encoding='utf-8')
    output.mkdir()
    records = output / 'records'
    records.mkdir()
    started = time.perf_counter()
    current = 'before_import'
    lock = threading.Lock()
    finished = threading.Event()
    folders = ExitStack()
    originals = []
    qt_errors = []
    all_windows = []
    record_refs = []
    pngs = []
    explicit_numeric = []
    automatic_numeric_calls = 0
    capture_numeric = False
    window = None
    application = None
    module = None
    active_folder = None
    run_path = None
    account_path = None
    previous_hook = sys.excepthook
    receipt = {'kind': 'ACTUAL_RUNSTATE098_BOUNDED_REAL_WINDOW_SMOKE',
        'passed': False, 'workflow_complete': False,
        'actual_root': str(root), 'actual_argv': list(sys.argv),
        'actual_cwd': str(Path.cwd()), 'source_before': before_source,
        'guard_path': str(guard_path), 'guard_sha256': sha256(guard_path.read_bytes()),
        'runner_sha256': sha256(Path(__file__).read_bytes()),
        'helper_sha256': sha256(Path(__file__).with_name('native_evidence.py').read_bytes()),
        'started_at_UTC': datetime.now(timezone.utc).isoformat(),
        'deadline_seconds': DEADLINE_SECONDS, 'actual_records': record_refs,
        'actual_PNGs': pngs, 'native_windows_verified': False,
        'private_state_isolated': True, 'game_chat_executed': False,
        'global_profile_or_trace_installed': False,
        'full095_UI_restart_attempt': False,
        'math_control': 'Unchanged original calculator and original history notice on each button scenario; same-raw bool/None pairs',
        'numeric_recording_scope': 'Explicit manual button calls only; automatic calls counted without full native copies'}

    def progress(status='running'):
        with lock:
            write_json(output / 'progress.json', {'status': status, 'step': current,
                'fresh_windows': len(all_windows), 'records_completed': len(record_refs),
                'explicit_numeric_calls': len(explicit_numeric), 'PNGs': len(pngs),
                'elapsed_seconds': round(time.perf_counter() - started, 3)})

    def watchdog():
        if finished.wait(DEADLINE_SECONDS):return
        with lock:
            receipt.update(failure={'type': 'TimeoutError', 'message': 'Declared 300 second deadline',
                'step': current}, primary_exit_by_watchdog=124,
                elapsed_seconds=time.perf_counter() - started)
            write_json(output / 'receipt.json', receipt)
        os._exit(124)

    threading.Thread(target=watchdog, daemon=True, name='runstate098-deadline').start()

    def qt_hook(kind, error, tb):
        qt_errors.append({'step': current, 'type': kind.__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(kind, error, tb))})

    def process():
        application.processEvents()
        assert time.perf_counter() - started < DEADLINE_SECONDS
        assert not qt_errors, qt_errors
        assert window.isVisible() and not window.auto.isChecked()
        assert not window.timer.isActive() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not window.chat_busy and not window.busy
        assert not (active_folder / 'chat').exists()

    def filesystem(folder):
        result = []
        for path in sorted(folder.rglob('*')):
            if path.is_dir():
                result.append({'path': path.relative_to(folder).as_posix(), 'kind': 'directory'})
            else:
                raw = path.read_bytes()
                result.append({'path': path.relative_to(folder).as_posix(), 'kind': 'file',
                    'bytes': raw, 'sha256': sha256(raw)})
        return result

    def snapshot():
        selected = window.operator.currentData()
        return freeze({'run': window.run.state, 'protected': window.run.preserve_unreadable,
            'account': window.account_cache.records, 'files': filesystem(active_folder),
            'run_summary': window.run_summary.text(), 'inventory_status': window.run.inventory_status(),
            'held_relics': window.run.held_relic_ids(), 'held_tools': window.run.held_tool_ids(),
            'current_operator_state': window.current_operator_state(),
            'training_conditions': window.training_conditions() if selected is not None else None,
            'training_status': window.training_status.text(), 'selected_operator': selected,
            'level': window.level.value(), 'skill': window.skill.currentData(),
            'run_training_enabled': window.use_run_training.isChecked(),
            'operator_summary': window.operator_summary.toPlainText(),
            'map_mode': window.map_mode.text(), 'map_content': window.map_content.text(),
            'map_text': window.map_text.toPlainText(),
            'account_alias': window.operator_observations is window.account_cache.records})

    def record(label, value):
        row = write_record(records, len(record_refs) + 1, freeze(value))
        row['label'] = label
        record_refs.append(row)
        progress()

    def screenshot(label, tab):
        window.centralWidget().setCurrentIndex(tab)
        process()
        path = output / (label + '.png')
        pixmap = window.grab()
        assert not pixmap.isNull() and pixmap.save(str(path), 'PNG')
        raw = path.read_bytes()
        assert raw.startswith(b'\x89PNG\r\n\x1a\n')
        pngs.append({'path': path.name, 'bytes': len(raw), 'sha256': sha256(raw),
            'width': pixmap.width(), 'height': pixmap.height(),
            'root_visual_inspection_completed': False})
        window.centralWidget().setCurrentIndex(1)
        process()

    def close_current():
        nonlocal window
        if window is None:return
        before = freeze(filesystem(active_folder))
        window.close()
        application.processEvents()
        assert_native_equal(filesystem(active_folder), before, 'Real close preserves all owned files')
        assert window.closing and not window.timer.isActive() and window.capture.target is None
        window.deleteLater()
        application.processEvents()
        window = None

    def fresh(raw=None, *, folder=None):
        nonlocal window, active_folder, run_path, account_path
        close_current()
        if folder is None:
            folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-runstate098-')))
        active_folder = folder
        run_path = folder / 'run.json'
        account_path = folder / 'account.json'
        if raw is not None:
            run_path.write_bytes(raw)
            account_path.write_bytes(account_raw)
            (folder / 'other-run.bin').write_bytes(b'public companion run must stay untouched\n')
        module.RUN_STATE = run_path
        module.OPERATOR_STATE = account_path
        module.SETTINGS = folder / 'settings.json'
        module.DesktopBackend = lambda _path, callback: real_backend(folder / 'chat', callback)
        window = module.MainWindow()
        all_windows.append(window)
        window.resize(1400, 1050)
        window.show()
        window.centralWidget().setCurrentIndex(1)
        window.auto.setEnabled(False)
        window.connect_button.setEnabled(False)
        window.sample_button.setEnabled(False)
        process()
        assert not module.list_game_windows(), 'No live game prerequisite used'
        assert window.operator_observations is window.account_cache.records
        assert account_path.read_bytes() == account_raw
        assert (folder / 'other-run.bin').read_bytes() == b'public companion run must stay untouched\n'
        assert not module.SETTINGS.exists()
        return snapshot()

    def select_owner():
        assert window.select_operator(OP)
        process()
        assert window.operator.currentData() == OP

    def reports():
        nonlocal capture_numeric
        process()
        before = freeze({'run': window.run.state, 'account': window.account_cache.records,
            'files': filesystem(active_folder)})
        window.raw_damage.setChecked(False)
        window.damage_technical.setChecked(False)
        buttons = [button for button in window.findChildren(QPushButton)
            if button.text() == '计算属性与技能预估']
        assert len(buttons) == 1
        index = len(explicit_numeric)
        capture_numeric = True
        try:
            buttons[0].click()
            process()
        finally:
            capture_numeric = False
        assert len(explicit_numeric) == index + 1
        actual = explicit_numeric[-1]
        assert window.damage_result is not None, window.damage_text.toPlainText()
        value = window.damage_result
        before_result = freeze(value)
        direct_scenario = freeze(actual['scenario'])
        direct = original_damage(direct_scenario)
        module.apply_relic_history_notice(direct_scenario, direct)
        assert not window.target_buff_test.isChecked()
        assert_native_equal(direct, value['result'], 'Actual button equals unchanged original calculator on exact scenario')
        texts = {'estimate': estimate.format_estimate(value['result']),
            'default': reporting.format_report(value['result']),
            'technical': reporting.format_report(value['result'], technical=True)}
        assert all(texts.values()) and texts['estimate'] == texts['default']
        assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
        window.damage_technical.setChecked(True)
        process()
        assert window.damage_text.toPlainText() == texts['technical'].replace(chr(160), ' ')
        window.raw_damage.setChecked(True)
        process()
        raw_text = json.dumps(value, ensure_ascii=False, indent=2)
        assert window.damage_text.toPlainText() == raw_text.replace(chr(160), ' ')
        window.raw_damage.setChecked(False)
        window.damage_technical.setChecked(False)
        process()
        assert_native_equal(value, before_result, 'Three formatters and real render toggles preserve numeric result')
        assert_native_equal({'run': window.run.state, 'account': window.account_cache.records,
            'files': filesystem(active_folder)}, before, 'Explicit reports preserve all owned durable/native state')
        return freeze({'damage_result': value, 'texts': texts,
            'structured_visible_text': raw_text, 'visible_default': window.damage_text.toPlainText(),
            'actual_button_scenario': actual['scenario'], 'original_direct_result': direct})

    def priority_pair(run_level, account_level=2):
        select_owner()
        before = freeze(window.run.state)
        raw = run_path.read_bytes()
        window.use_run_training.setChecked(True)
        process()
        assert window.current_operator_state()['fields']['level'] == run_level
        assert window.level.value() == run_level
        run_reports = reports()
        window.use_run_training.setChecked(False)
        process()
        assert window.current_operator_state()['fields']['level'] == account_level
        assert window.level.value() == account_level
        account_reports = reports()
        window.use_run_training.setChecked(True)
        process()
        assert_native_equal(window.run.state, before, 'Priority toggles do not edit run state')
        assert run_path.read_bytes() == raw and account_path.read_bytes() == account_raw
        return {'run': run_reports, 'account': account_reports}

    def icon(identity):
        return {'id': identity, 'candidates': [identity], 'confirmed': True}

    def bar(count=MISSING, *, one=False):
        relics = {'ids': [], 'icons': [icon(RELICS[0])] if one else [], 'source': 'held_bar'}
        if count is not MISSING:relics['count'] = count
        shared = [None, False, 0, -0.0, ('public', 1), b'public']
        cycle = []
        cycle.append(cycle)
        return {'relics': relics, 'operators': [],
            'public_opaque': {'first': shared, 'same': shared, 'cycle': cycle}}

    def deliver(observed, at):
        caller = freeze(observed)
        before = snapshot()
        returned = window.apply_run_observation(observed, at)
        process()
        assert returned is True
        assert_native_equal(observed, caller, 'Caller types/keys/order/float bits/aliases unchanged')
        assert window.run_summary.text() == window.run.summary()
        return {'caller_before': caller, 'caller_after': freeze(observed),
            'captured_at': at, 'returned': returned, 'before': before, 'after': snapshot()}

    try:
        sys.excepthook = qt_hook
        sys.path.insert(0, str(root))
        from PySide6.QtWidgets import QApplication, QPushButton
        import rouge.app as module
        import rouge.reporting as reporting
        import rouge.estimate as estimate
        real_backend = module.DesktopBackend
        original_damage = module.calculate_damage
        for name in ('RUN_STATE', 'OPERATOR_STATE', 'SETTINGS', 'DesktopBackend', 'calculate_damage'):
            originals.append((module, name, getattr(module, name)))

        @functools.wraps(original_damage)
        def watched_damage(scenario):
            nonlocal automatic_numeric_calls
            if not capture_numeric:
                automatic_numeric_calls += 1
                return original_damage(scenario)
            before = freeze(scenario)
            result = original_damage(scenario)
            assert_native_equal(scenario, before, 'Original explicit numerical caller unchanged')
            explicit_numeric.append(freeze({'step': current, 'scenario': before, 'result': result}))
            return result

        module.calculate_damage = watched_damage
        application = QApplication([])
        application.setQuitOnLastWindowClosed(False)
        account_fixture = {OP: {'id': OP, 'scope': 'operator_profile',
            'fields': {'elite': 2, 'level': 2, 'trust': 100, 'potential': 1,
                'module_id': None, 'module_level': 0},
            'skill_ranks': {'1': 7}, 'captured_at': START + 1},
            'public_unknown_account098': {'opaque': [None, {'label': '保留'}]}}
        account_raw = json.dumps(account_fixture, ensure_ascii=True, indent=2).encode('ascii')
        member = {'id': OP, 'scope': 'run', 'present': True,
            'fields': {'elite': 2, 'level': 1, 'trust': 60, 'potential': 2,
                'module_id': None, 'module_level': 0},
            'skill_ranks': {'1': 7}, 'captured_at': START + 1,
            'recruitment_kind': 'non_emergency', 'advanced': False}
        public_run = {'id': 'public-runstate098-window', 'started_at': START,
            'last_read': START + 1, 'operators': {OP: member}, 'selected_operator': OP,
            'crew_count': 1, 'relics': {}, 'history': [], 'resources': {},
            'tactical_tools': {}, 'config': {}, 'maps': {},
            'public_opaque': {'nullable': None, 'nested': [None, {'kept': True}]}}
        healthy_raw = json.dumps(public_run, ensure_ascii=True, indent=2).encode('ascii')
        current = 'healthy_startup'
        progress()
        before = fresh(healthy_raw)
        assert not window.run.preserve_unreadable and run_path.read_bytes() == healthy_raw
        healthy_reports = priority_pair(1)
        screenshot('healthy-training', 1)
        record(current, {'original_raw': healthy_raw, 'before': before,
            'after': snapshot(), 'complete_reports': healthy_reports})
        healthy_folder = active_folder
        current = 'healthy_close_reopen'
        progress()
        reopened = fresh(folder=healthy_folder)
        assert not window.run.preserve_unreadable and run_path.read_bytes() == healthy_raw
        assert_native_equal(priority_pair(1), healthy_reports, 'Healthy real restart preserves full math and reports')
        record(current, {'reopened': reopened, 'after': snapshot(), 'original_raw': healthy_raw})

        templates = json.loads((root / 'rouge/data/map-templates.json').read_text(encoding='utf-8'))
        template = next(item for item in templates['templates'] if item['id'] == '1a')
        valid_graph = {'status': 'matched', 'zone_id': template['zone_id'], 'template_id': template['id'],
            'grid': {'rows': template['rows'], 'cols': template['cols']},
            'edges': freeze(template['edges']), 'source': freeze(templates['source']),
            'nodes': [{**freeze(node), 'template_type': node['fixed_type'], 'observed_type': None,
                'visible': False, 'prediction': None} for node in template['nodes']]}
        assert template['rows'] == 3
        content_graph = freeze(valid_graph)
        content_graph['nodes'][0]['content'] = {'public_opaque': None}
        coordinate_graph = freeze(valid_graph)
        coordinate_graph['nodes'][0]['row'] = 3
        faults = (
            ('maps_outer_array', {'maps': []}),
            ('history_nonlist', {'history': None}),
            ('nested_member_fields', {'operators': {OP: {**member, 'fields': None}}}),
            ('icons_missing_candidates', {'relic_icon_memory': {'icons': [{'id': RELICS[0]}]}}),
            ('node_content_missing_title', {'maps': {template['zone_id']: content_graph}}),
            ('grid_row_outside_three_rows', {'maps': {template['zone_id']: coordinate_graph}}),
        )
        for name, change in faults:
            current = name
            progress()
            bad = {**freeze(public_run), **freeze(change)}
            raw = json.dumps(bad, ensure_ascii=True, indent=2).encode('ascii')
            before = fresh(raw)
            assert window.run.preserve_unreadable and run_path.read_bytes() == raw
            assert window.run.state['id'] != public_run['id']
            assert window.run.state['operators'] == {} and window.run.state['maps'] == {}
            assert 'public_opaque' not in window.run.state
            assert '原本局记录无法读取' in window.run_summary.text()
            assert window.reset_run_button.isEnabled()
            incoming = {'operators': [freeze(member)], 'selected_operator': OP, 'crew_count': 1}
            applied = deliver(incoming, window.run.state['started_at'] + 1)
            assert window.run.preserve_unreadable and run_path.read_bytes() == raw
            assert not run_path.with_suffix('.tmp').exists()
            paired = priority_pair(1)
            record(current, {'original_raw': raw, 'startup': before, 'actual_apply': applied,
                'complete_reports': paired, 'protected_after': snapshot()})
            if name == 'maps_outer_array':
                screenshot('protected-cache-summary', 0)
                before_reset = snapshot()
                previous_id = window.run.state['id']
                window.centralWidget().setCurrentIndex(0)
                window.reset_run_button.click()
                process()
                assert not window.run.preserve_unreadable
                assert window.run.state['id'] != previous_id and window.run.state['operators'] == {}
                assert window.run.state['history'] == [] and run_path.read_bytes() != raw
                assert account_path.read_bytes() == account_raw
                assert (active_folder / 'other-run.bin').read_bytes() == b'public companion run must stay untouched\n'
                reset_raw = run_path.read_bytes()
                reset_id = window.run.state['id']
                screenshot('manual-reset-summary', 0)
                reset_folder = active_folder
                after_reset = snapshot()
                fresh(folder=reset_folder)
                assert not window.run.preserve_unreadable and window.run.state['id'] == reset_id
                assert run_path.read_bytes() == reset_raw and window.run.state['operators'] == {}
                record('actual_manual_reset_and_reopen', {'before': before_reset,
                    'after': after_reset, 'reopened': snapshot(), 'actual_reset_raw': reset_raw})

        current = 'accepted_old_member_missing_fields'
        progress()
        missing = freeze(public_run)
        missing['operators'][OP].pop('fields')
        raw = json.dumps(missing, ensure_ascii=True, indent=2).encode('ascii')
        before = fresh(raw)
        assert not window.run.preserve_unreadable and run_path.read_bytes() == raw
        assert 'fields' not in window.run.state['operators'][OP]
        effective = window.current_operator_state()
        assert effective['fields']['level'] == 2 and effective['run_confirmed_fields'] == []
        assert '账号档案参考，本局未确认' in window.elite.text()
        missing_reports = priority_pair(2)
        folder = active_folder
        fresh(folder=folder)
        assert not window.run.preserve_unreadable and run_path.read_bytes() == raw
        assert_native_equal(priority_pair(2), missing_reports, 'Missing fields safe consumer survives actual restart')
        record(current, {'original_raw': raw, 'startup': before, 'after_restart': snapshot(),
            'complete_reports': missing_reports})

        current = 'real_positive_inventory_seed'
        progress()
        fresh(healthy_raw)
        positive = {'relics': {'ids': list(RELICS), 'count': 3,
            'icons': [icon(identity) for identity in (*RELICS, TOOL)], 'source': 'held_bar'},
            'tactical_tools': {'ids': [TOOL], 'source': 'held_bar'}, 'operators': []}
        seed_action = deliver(positive, START + 2)
        assert window.run.inventory_status()['complete'] and window.run.state['relic_count'] == 3
        seed_raw = run_path.read_bytes()
        record(current, {'actual_seed_action': seed_action, 'actual_persisted_raw': seed_raw})
        controls = {}
        for label, count, one in (
            ('none_empty_control', None, False), ('none_one_control', None, True),
            ('false_empty_unknown', False, False), ('true_one_unknown', True, True),
            ('missing_count_unknown', MISSING, False),
            ('integer_zero_explicit_empty', 0, False), ('integer_one_explicit_one', 1, True),
        ):
            current = label
            progress()
            fresh(seed_raw)
            observed = bar(count, one=one)
            applied = deliver(observed, START + 3)
            status = window.run.inventory_status()
            paired = priority_pair(1)
            result = {'state': freeze(window.run.state), 'raw_after': run_path.read_bytes(),
                'inventory': status, 'held_relics': window.run.held_relic_ids(),
                'held_tools': window.run.held_tool_ids(), 'complete_reports': paired}
            if count is None:
                controls[one] = freeze(result)
            elif type(count) is bool or count is MISSING:
                assert_native_equal(result, controls[one], 'Incoming unknown bool/missing retains exact None outcome')
                assert type(window.run.state['relic_count']) is int and window.run.state['relic_count'] == 3
                assert window.run.held_relic_ids() == list(RELICS) and window.run.held_tool_ids() == [TOOL]
                if type(count) is bool:assert observed['relics']['count'] is count
                if label == 'false_empty_unknown':screenshot('bool-inventory-preserved', 0)
            else:
                assert type(window.run.state['relic_count']) is int and window.run.state['relic_count'] == count
                assert status['complete']
                assert window.run.held_tool_ids() == []
                assert window.run.held_relic_ids() == ([RELICS[0]] if one else [])
            record(current, {'same_original_seed_raw': seed_raw, 'actual_apply': applied,
                'actual_outcome': result})
        current = 'bool_no_prior_count_remains_unknown'
        progress()
        fresh(healthy_raw)
        applied = deliver(bar(True, one=True), START + 2)
        assert window.run.state['relic_count'] is None
        assert not window.run.inventory_status()['complete']
        assert window.run.held_relic_ids() == [RELICS[0]]
        assert '/ 未确认 件' in window.run_summary.text()
        record(current, {'actual_apply': applied, 'complete_reports': priority_pair(1), 'after': snapshot()})
        assert len(pngs) == 4
        assert not qt_errors and explicit_numeric
        receipt.update(passed=True, workflow_complete=True)
    except BaseException as error:
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
            'step': current, 'traceback': traceback.format_exc()}
        try:
            record('unfinished_failure', {'step': current, 'Qt_errors': qt_errors,
                'actual_state': snapshot() if window is not None else None,
                'explicit_numeric_so_far': explicit_numeric})
        except BaseException as saving_error:
            receipt['unfinished_native_save_error'] = str(saving_error)
    finally:
        try:
            close_current()
        except BaseException as error:
            receipt.update(passed=False, workflow_complete=False,
                close_error={'type': type(error).__name__, 'message': str(error)})
        if application is not None:application.processEvents()
        if qt_errors:receipt.update(passed=False, workflow_complete=False)
        for owner, name, original in reversed(originals):setattr(owner, name, original)
        sys.excepthook = previous_hook
        after_source = source_map(root)
        drift = [name for name in sorted(set(before_source) | set(after_source))
            if before_source.get(name) != after_source.get(name)]
        if drift:receipt.update(passed=False, workflow_complete=False)
        receipt.update(source_after=after_source, source_drift=drift, fresh_windows=len(all_windows),
            explicit_numeric_calls=len(explicit_numeric), automatic_numeric_calls=automatic_numeric_calls,
            Qt_errors=qt_errors, elapsed_seconds=round(time.perf_counter() - started, 3),
            ended_at_UTC=datetime.now(timezone.utc).isoformat())
        if explicit_numeric:
            receipt['complete_explicit_numeric_evidence'] = write_record(output, 1, freeze(explicit_numeric))
        folders.close()
        with lock:write_json(output / 'receipt.json', receipt)
        progress('passed' if receipt['passed'] else 'failed')
        finished.set()
        print(json.dumps({'passed': receipt['passed'], 'records': len(record_refs),
            'failure': receipt.get('failure')}, ensure_ascii=True), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
