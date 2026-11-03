"""Unexecuted Source for Root's bounded actual section097 window smoke.

Uses real MainWindow, original calculation, original formatters and real public
filesystem failures. No project/test/Wine/codec execution by this author. Root
must first bind actual completed096 and applied097 source, review, then run.
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

CORE_SHA = '29bf05d1c7fc111b2e74977be6ca413bb0a25c50cead69fe3a04237ef5a2768e'
DEADLINE_SECONDS = 300
OP = 'mechanist'
UNKNOWN = 'public_unknown_account097'
START = 1700000000


def write_json(path, data):
    # Human-readable metadata is not authoritative native string evidence.
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
    assert guard['section'] == 97
    expected_source = guard['source_sha256']
    before_source = source_map(root)
    assert before_source == expected_source
    assert before_source['rouge/account_cache.py'] == CORE_SHA
    output.mkdir()
    records = output / 'records'
    records.mkdir()
    started = time.perf_counter()
    finished = threading.Event()
    lock = threading.Lock()
    current = 'before_import'
    windows = []
    folders = ExitStack()
    restored = []
    qt_errors = []
    account_calls = []
    numeric_calls = []
    write_calls = []
    owned_pending = set()
    record_refs = []
    pngs = []
    receipt = {'kind': 'ACTUAL_ACCOUNT097_BOUNDED_REAL_WINDOW_SMOKE',
               'passed': False, 'workflow_complete': False,
               'actual_root': str(root), 'actual_argv': list(sys.argv),
               'actual_cwd': str(Path.cwd()),
               'runner_sha256': sha256(Path(__file__).read_bytes()),
               'helper_sha256': sha256(Path(__file__).with_name('native_evidence.py').read_bytes()),
               'guard_path': str(guard_path), 'guard_sha256': sha256(guard_path.read_bytes()),
               'source_before': before_source, 'actual_records': record_refs,
               'actual_PNGs': pngs, 'deadline_seconds': DEADLINE_SECONDS,
               'started_at_UTC': datetime.now(timezone.utc).isoformat(),
               'private_state_isolated': True, 'native_windows_verified': False,
               'game_chat_executed': False, 'gold_old_version_executed': False,
               'same_facts_control': 'Actual healthy window in this same applied097 source',
               'no_fake_calculation': True, 'global_profile_or_trace_installed': False}
    application = None
    module = None
    window = None
    active_folder = account_path = run_path = None

    def persist_progress(status):
        with lock:
            write_json(output / 'progress.json', {'status': status, 'step': current,
                       'records_completed': len(record_refs), 'fresh_windows': len(windows),
                       'elapsed_seconds': round(time.perf_counter() - started, 3)})

    def watchdog():
        if finished.wait(DEADLINE_SECONDS):
            return
        with lock:
            receipt.update(failure={'type': 'TimeoutError', 'message': 'Declared 300 second deadline',
                           'step': current}, primary_exit_by_watchdog=124,
                           records_completed=len(record_refs), elapsed_seconds=time.perf_counter() - started)
            write_json(output / 'receipt.json', receipt)
        os._exit(124)

    threading.Thread(target=watchdog, daemon=True, name='account097-deadline').start()
    previous_hook = sys.excepthook

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
        for file in sorted(folder.rglob('*')):
            if file.is_dir():
                result.append({'path': file.relative_to(folder).as_posix(), 'kind': 'directory'})
            else:
                raw = file.read_bytes()
                result.append({'path': file.relative_to(folder).as_posix(), 'kind': 'file',
                               'bytes': raw, 'sha256': sha256(raw)})
        return result

    def snapshot():
        return freeze({'run': window.run.state, 'account': window.account_cache.records,
                       'issues': window.account_cache.issues,
                       'load_issue': window.account_cache.load_issue,
                       'save_issue': window.account_cache.save_issue,
                       'preserve_original': window.account_cache.preserve_original,
                       'files': filesystem(active_folder),
                       'current_operator_state': window.current_operator_state(),
                       'training_conditions': window.training_conditions(),
                       'training_status': window.training_status.text(),
                       'operator_summary': window.operator_summary.toPlainText(),
                       'run_summary': window.run_summary.text(),
                       'level': window.level.value(), 'skill': window.skill.currentData(),
                       'rank': window.skill_rank_value(),
                       'run_priority': window.use_run_training.isChecked(),
                       'operator_observations_alias_is_records':
                           window.operator_observations is window.account_cache.records})

    def reports():
        process()
        before = freeze({'run': window.run.state, 'account': window.account_cache.records,
                         'files': filesystem(active_folder)})
        index = len(numeric_calls)
        buttons = [button for button in window.findChildren(QPushButton)
                   if button.text() == '计算属性与技能预估']
        assert len(buttons) == 1
        buttons[0].click()
        process()
        assert len(numeric_calls) > index, 'Actual button must call original numeric entry'
        assert window.damage_result is not None, window.damage_text.toPlainText()
        value = window.damage_result
        unchanged = freeze(value)
        texts = {'estimate': estimate.format_estimate(value['result']),
                 'default': reporting.format_report(value['result']),
                 'technical': reporting.format_report(value['result'], technical=True)}
        assert all(texts.values()) and texts['estimate'] == texts['default']
        assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
        assert_native_equal(value, unchanged, 'Original full numeric result survives all three formatters')
        assert_native_equal({'run': window.run.state, 'account': window.account_cache.records,
                             'files': filesystem(active_folder)}, before,
                            'Actual manual calculation preserves account/run/all owned files')
        return freeze({'damage_result': value, 'three_full_texts': texts,
                       'visible_damage_text': window.damage_text.toPlainText()})

    def record(label, data):
        reference = write_record(records, len(record_refs) + 1, freeze(data))
        reference['label'] = label
        record_refs.append(reference)
        persist_progress('running')

    def screenshot(label):
        for index, suffix in ((1, 'training'), (0, 'summary')):
            window.centralWidget().setCurrentIndex(index)
            process()
            file = output / (label + '-' + suffix + '.png')
            pixmap = window.grab()
            assert not pixmap.isNull() and pixmap.save(str(file), 'PNG')
            raw = file.read_bytes()
            assert raw.startswith(b'\x89PNG\r\n\x1a\n')
            pngs.append({'path': file.name, 'bytes': len(raw), 'sha256': sha256(raw),
                         'width': pixmap.width(), 'height': pixmap.height(),
                         'root_visual_inspection_completed': False})
        window.centralWidget().setCurrentIndex(1)
        process()

    def fresh(folder, account_fixture=None):
        nonlocal window, active_folder, account_path, run_path
        if window is not None:
            window.close()
            application.processEvents()
        active_folder = folder
        account_path = folder / 'account.json'
        run_path = folder / 'run.json'
        if account_fixture is not None:
            account_path.write_bytes(json.dumps(account_fixture, ensure_ascii=True).encode('ascii'))
            run_path.write_bytes(json.dumps(public_run, ensure_ascii=True).encode('ascii'))
        module.OPERATOR_STATE = account_path
        module.RUN_STATE = run_path
        module.SETTINGS = folder / 'settings.json'
        module.DesktopBackend = lambda _path, callback: real_backend(folder / 'chat', callback)
        window = module.MainWindow()
        windows.append(window)
        window.resize(1400, 1050)
        window.show()
        window.centralWidget().setCurrentIndex(1)
        process()
        assert window.operator.currentData() == OP
        assert window.operator_observations is window.account_cache.records
        assert window.run.state['id'] == public_run['id']
        assert not module.list_game_windows(), 'No game prerequisites used'
        return snapshot()

    def observation(level, *, opaque=None):
        fields = dict(public_account[OP]['fields'], level=level)
        if opaque is not None:
            fields['opaque'] = opaque
        return {'id': OP, 'scope': 'operator_profile', 'fields': fields,
                'skill_ranks': {'1': 7}, 'sources': {'level': 'public-manual-account097'}}

    def deliver(incoming, captured):
        before = freeze(incoming)
        complete = {'captured_at': captured, 'page': 'public_manual_operator_profile',
                    'nodes': [], 'operator': incoming, 'performance': {}}
        complete_before = freeze(complete)
        module_image = numpy.zeros((100, 160, 3), dtype=numpy.uint8)
        # This is manually constructed delivery, not capture/OCR or live game.
        window.sample_received((module_image, complete))
        process()
        assert_native_equal(incoming, before, 'Account caller retains all values/types/aliases')
        assert_native_equal(complete, complete_before, 'Manual delivery caller remains unchanged')
        assert window.last_sample_at == captured
        assert window.account_cache.view(OP)['fields']['level'] == incoming['fields']['level']
        body = module.format_operator_observation(window.account_cache.view(OP))
        notice = window.account_cache.notice(OP)
        assert window.operator_summary.toPlainText() == body + ('\n' + notice if notice else '')

    def priority_pair(expected_level):
        unchanged_run = freeze(window.run.state)
        unchanged_file = run_path.read_bytes()
        window.use_run_training.setChecked(True)
        process()
        assert window.current_operator_state()['fields']['level'] == 1
        assert window.level.value() == 1
        run_reports = reports()
        window.use_run_training.setChecked(False)
        process()
        assert window.current_operator_state()['fields']['level'] == expected_level
        assert window.level.value() == expected_level
        account_reports = reports()
        window.use_run_training.setChecked(True)
        process()
        assert_native_equal(window.run.state, unchanged_run, 'Priority controls do not reset or edit current run')
        assert run_path.read_bytes() == unchanged_file
        return {'run': run_reports, 'account': account_reports}

    try:
        sys.excepthook = qt_hook
        sys.path.insert(0, str(root))
        import numpy
        from PySide6.QtWidgets import QApplication, QPushButton
        import rouge.app as module
        import rouge.reporting as reporting
        import rouge.estimate as estimate
        from rouge.account_cache import AccountCache
        real_backend = module.DesktopBackend
        for name in ('OPERATOR_STATE', 'RUN_STATE', 'SETTINGS', 'DesktopBackend'):
            restored.append((module, name, getattr(module, name)))
        original_observe = AccountCache.observe
        restored.append((AccountCache, 'observe', original_observe))

        @functools.wraps(original_observe)
        def watched_observe(instance, operator, captured_at):
            before = freeze(operator)
            row = {'step': current, 'caller_before': before, 'captured_at': captured_at,
                   'account_before': freeze(instance.records), 'outcome': 'pending'}
            account_calls.append(row)
            try:
                returned = original_observe(instance, operator, captured_at)
            except BaseException as error:
                row.update(outcome='raised', error_type=type(error).__name__, error_args=error.args)
                raise
            else:
                row.update(outcome='returned', returned=returned)
                return returned
            finally:
                assert_native_equal(operator, before, 'Original AccountCache.observe caller unchanged')
                complete = freeze({**row, 'caller_after': operator, 'account_after': instance.records})
                row.clear()
                row.update(complete)

        AccountCache.observe = watched_observe
        original_damage = module.calculate_damage
        restored.append((module, 'calculate_damage', original_damage))

        @functools.wraps(original_damage)
        def watched_damage(scenario):
            before = freeze(scenario)
            result = original_damage(scenario)
            assert_native_equal(scenario, before, 'Original numerical scenario caller unchanged')
            numeric_calls.append(freeze({'step': current, 'caller_before': before,
                                        'caller_after': scenario, 'returned': result}))
            return result

        module.calculate_damage = watched_damage
        original_write = Path.write_text
        restored.append((Path, 'write_text', original_write))

        @functools.wraps(original_write)
        def watched_write(path, text, *positional, **keywords):
            if path not in owned_pending:
                return original_write(path, text, *positional, **keywords)
            row = {'step': current, 'role': 'owned_distinct_account_tmp',
                   'text': text, 'positional': positional, 'keywords': keywords,
                   'outcome': 'pending'}
            write_calls.append(row)
            try:
                value = original_write(path, text, *positional, **keywords)
            except BaseException as error:
                row.update(outcome='raised', error_type=type(error).__name__,
                           error_args=error.args, is_actual_oserror=isinstance(error, OSError))
                raise
            else:
                row.update(outcome='returned', returned=value)
                return value

        Path.write_text = watched_write
        public_account = {OP: {'id': OP, 'scope': 'operator_profile',
                          'fields': {'elite': 2, 'level': 2, 'trust': 100, 'potential': 1,
                                     'module_id': None, 'module_level': 0},
                          'skill_ranks': {'1': 7}, 'captured_at': START + 1},
                          UNKNOWN: {'label': '中文', 'emoji': '\U0001f642', 'literal': '\\ud800'}}
        public_run = {'id': 'public-account097-run', 'started_at': START, 'last_read': START + 1,
                      'operators': {OP: {'id': OP, 'scope': 'run', 'present': True,
                          'fields': {'elite': 2, 'level': 1, 'trust': 60, 'potential': 2,
                                     'module_id': None, 'module_level': 0},
                          'skill_ranks': {'1': 7}, 'captured_at': START + 1,
                          'recruitment_kind': 'non_emergency', 'advanced': False}},
                      'selected_operator': OP, 'crew_count': 1, 'relics': {},
                      'history': [], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}}
        application = QApplication([])
        application.setQuitOnLastWindowClosed(False)
        controls = {}
        io_folder = None
        for kind in ('healthy', 'real_io_failure', 'lone_surrogate', 'native_pair'):
            current = kind
            persist_progress('running')
            folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-account097-' + kind + '-')))
            fixture = freeze(public_account)
            if kind == 'lone_surrogate':
                fixture[UNKNOWN]['opaque'] = '\ud800x\udc00'
            before_window = fresh(folder, fixture)
            if kind == 'healthy':
                controls['initial_level2'] = priority_pair(2)
            pending = account_path.with_suffix('.tmp')
            assert pending != account_path and not pending.exists()
            owned_pending.add(pending)
            before_target = account_path.read_bytes()
            before_run = freeze(window.run.state)
            before_run_file = run_path.read_bytes()
            call_index = len(account_calls)
            write_index = len(write_calls)
            if kind == 'real_io_failure':
                pending.mkdir()
                (pending / 'public-sentinel.bin').write_bytes(b'public account097 directory IO barrier\n')
                io_folder = folder
            elif kind == 'native_pair':
                pending.write_bytes(b'public preexisting tmp must survive pair refusal\n')
            before_action = snapshot()
            if kind == 'native_pair':
                incoming = observation(3, opaque='\ud800\udc00')
                caller = freeze(incoming)
                window.apply_operator_observation(incoming, START + 10)
                process()
                assert_native_equal(incoming, caller, 'Native pair accepted caller stays two exact code points')
                assert [ord(c) for c in window.account_cache.view(OP)['fields']['opaque']] == [0xd800, 0xdc00]
                assert len(write_calls) == write_index
                # Ordinary following delivery reaches second visible consumer;
                # avoids sending raw surrogate units into Qt observed_text.
                deliver(observation(3), START + 11)
            else:
                deliver(observation(3), START + 10)
            assert account_calls[call_index:]
            assert all(row['outcome'] == 'returned' and row['returned'] is True
                       for row in account_calls[call_index:])
            assert_native_equal(window.run.state, before_run, 'Account observation does not alter current run')
            assert run_path.read_bytes() == before_run_file
            failed = kind in ('real_io_failure', 'native_pair')
            if failed:
                assert window.account_cache.preserve_original and window.account_cache.save_issue
                assert window.account_cache.load_issue is None
                assert account_path.read_bytes() == before_target
                for text in (window.training_status.text(), window.operator_summary.toPlainText()):
                    assert '保存未完成' in text and '新的读取未保存到账号档案' in text
                if kind == 'real_io_failure':
                    assert len(write_calls) == write_index + 1
                    assert write_calls[-1]['outcome'] == 'raised' and write_calls[-1]['is_actual_oserror']
                    assert (pending / 'public-sentinel.bin').read_bytes() == b'public account097 directory IO barrier\n'
                else:
                    assert len(write_calls) == write_index
                    assert pending.read_bytes() == b'public preexisting tmp must survive pair refusal\n'
            else:
                assert not window.account_cache.preserve_original and window.account_cache.save_issue is None
                assert len(write_calls) == write_index + 1 and write_calls[-1]['outcome'] == 'returned'
                assert not pending.exists()
                assert_native_equal(json.loads(account_path.read_text(encoding='utf-8')),
                                    window.account_cache.records, 'Actual saved file decoded values exact')
            paired = priority_pair(3)
            if kind == 'healthy':
                controls['level3'] = freeze(paired)
            else:
                assert_native_equal(paired, controls['level3'],
                    'Same accepted effective facts retain complete original math and all three texts')
            after_action = snapshot()
            if kind == 'healthy':
                deliver(observation(4), START + 12)
                controls['level4'] = priority_pair(4)
            if failed:
                # Remove owned IO fixture barrier explicitly, without product
                # retry, deletion or replay; protected object must remain sticky.
                if kind == 'real_io_failure':
                    pending.rename(folder / 'retained-io-barrier')
                new_index = len(write_calls)
                deliver(observation(4), START + 12)
                assert len(write_calls) == new_index
                assert window.account_cache.preserve_original
                assert account_path.read_bytes() == before_target
                assert_native_equal(priority_pair(4), controls['level4'],
                    'Changed read after fault removal stays in memory with unchanged original arithmetic')
                screenshot(kind)
            record(kind, {'fixture': fixture, 'window_before': before_window,
                          'before_action': before_action, 'after_action': after_action,
                          'final': snapshot(), 'complete_reports': paired,
                          'actual_observe_calls': account_calls[call_index:],
                          'actual_write_calls': write_calls[write_index:]})
        current = 'healthy_new_session_after_real_io_failure'
        assert io_folder is not None
        fresh(io_folder)
        assert not window.account_cache.preserve_original and window.account_cache.save_issue is None
        assert window.account_cache.view(OP)['fields']['level'] == 2
        reopened = priority_pair(2)
        assert_native_equal(reopened, controls['initial_level2'], 'New actual window reads preserved original healthy account')
        record(current, {'new_session': snapshot(), 'complete_reports': reopened})
        assert len(record_refs) == 5 and len(pngs) == 4
        assert not qt_errors and all(row['outcome'] != 'pending' for row in account_calls + write_calls)
        receipt.update(passed=True, workflow_complete=True)
    except BaseException as error:
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
                              'step': current, 'traceback': traceback.format_exc()}
        try:
            record('unfinished_failure', {'step': current, 'actual_account_calls': account_calls,
                    'actual_numeric_calls': numeric_calls, 'actual_write_calls': write_calls,
                    'Qt_exceptions': qt_errors, 'state': snapshot() if window is not None else None})
        except BaseException as saving_error:
            receipt['unfinished_save_error'] = str(saving_error)
    finally:
        close_errors = []
        for item in windows:
            try:
                if not item.closing:
                    item.close()
            except BaseException as error:
                close_errors.append({'type': type(error).__name__, 'message': str(error)})
        if application is not None:
            application.processEvents()
        if close_errors or qt_errors:
            receipt.update(passed=False, workflow_complete=False)
        for owner, name, original in reversed(restored):
            setattr(owner, name, original)
        sys.excepthook = previous_hook
        after_source = source_map(root)
        drift = [name for name in sorted(set(before_source) | set(after_source))
                 if before_source.get(name) != after_source.get(name)]
        if drift:
            receipt.update(passed=False, workflow_complete=False)
        receipt.update(source_after=after_source, source_drift=drift,
                       fresh_windows=len(windows), actual_account_calls=len(account_calls),
                       actual_numeric_calls=len(numeric_calls), actual_account_tmp_write_calls=len(write_calls),
                       Qt_exceptions=qt_errors, close_errors=close_errors,
                       elapsed_seconds=round(time.perf_counter() - started, 3),
                       ended_at_UTC=datetime.now(timezone.utc).isoformat())
        if numeric_calls:
            receipt['complete_actual_numeric_call_evidence'] = write_record(output, 1, freeze(numeric_calls))
        folders.close()
        with lock:
            write_json(output / 'receipt.json', receipt)
        persist_progress('passed' if receipt['passed'] else 'failed')
        finished.set()
        print(json.dumps({'passed': receipt['passed'], 'records': len(record_refs),
                          'failure': receipt.get('failure')}, ensure_ascii=True), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
