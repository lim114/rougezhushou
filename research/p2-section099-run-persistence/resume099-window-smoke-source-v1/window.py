"""Unexecuted Source for Root's bounded real section099 Wine window smoke.

All calculations, formatters, delivery, reset, stores and OS operations delegate
to original code. The author has not imported/ran project/helper/codec/Qt/Wine.
Root must bind actual completed 098 + applied 099 source before execution.
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


CORE_SHA = '1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9'
DEADLINE_SECONDS = 300
OP = 'mechanist'
START = 1700000000
SENTINEL_BYTES = b'public run099 actual open failure barrier\n'


def write_json(path, value):
    with path.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2)
        stream.write('\n')


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
    assert guard['section'] == 99
    expected_source = guard['source_sha256']
    before_source = source_map(root)
    assert before_source == expected_source
    assert before_source['rouge/run_state.py'] == CORE_SHA
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
    run_calls = []
    save_calls = []
    numeric_calls = []
    io_calls = []
    record_refs = []
    pngs = []
    owned_parents = set()
    owned_pending = set()
    receipt = {'kind': 'ACTUAL_RUN099_BOUNDED_REAL_WINDOW_SMOKE',
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
               'game_chat_executed': False, 'capture_OCR_executed': False,
               'manual_public_delivery_only': True, 'gold_old_version_executed': False,
               'same_facts_control': 'Actual healthy MainWindow in this same applied099 source',
               'no_fake_calculation': True, 'global_profile_or_trace_installed': False}
    application = None
    module = None
    window = None
    active_folder = None
    run_path = None
    account_path = None

    def persist_progress(status):
        with lock:
            write_json(output / 'progress.json', {'status': status, 'step': current,
                       'records_completed': len(record_refs), 'fresh_windows': len(windows),
                       'elapsed_seconds': round(time.perf_counter() - started, 3)})

    def watchdog():
        if finished.wait(DEADLINE_SECONDS):return
        with lock:
            receipt.update(failure={'type': 'TimeoutError', 'message': 'Declared 300 second deadline',
                           'step': current}, primary_exit_by_watchdog=124,
                           records_completed=len(record_refs), elapsed_seconds=time.perf_counter() - started)
            write_json(output / 'receipt.json', receipt)
        os._exit(124)

    threading.Thread(target=watchdog, daemon=True, name='run099-deadline').start()
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
        assert not window.capture.stats()['collecting']
        assert not window.desktop.process and not window.desktop_request_busy
        assert not window.chat_busy and not window.busy
        assert not (active_folder / 'chat').exists()

    def filesystem(folder):
        value = []
        for file in sorted(folder.rglob('*')):
            if file.is_dir():
                value.append({'path': file.relative_to(folder).as_posix(), 'kind': 'directory'})
            else:
                raw = file.read_bytes()
                value.append({'path': file.relative_to(folder).as_posix(), 'kind': 'file',
                              'bytes': raw, 'sha256': sha256(raw)})
        return value

    def describe_io_argument(value):
        # Filesystem methods receive Path arguments. Describe them explicitly;
        # the native codec admits only exact builtins, never Path/QObject values.
        if isinstance(value, Path):
            return {'argument_kind': type(value).__name__, 'path': str(value)}
        return value

    def frame_description(frame):
        return None if frame is None else {'kind': 'public-delivery-QImage',
                                         'width': frame.width(), 'height': frame.height()}

    def snapshot():
        # The real empty overview has no selected profile. Its calculation
        # getters require an operator; describe that state without calling them.
        has_operator = window.operator.currentData() is not None
        return freeze({'run': window.run.state, 'run_save_issue': window.run.save_issue,
                       'run_preserve_unreadable': window.run.preserve_unreadable,
                       'account': window.account_cache.records,
                       'account_issues': window.account_cache.issues,
                       'account_load_issue': window.account_cache.load_issue,
                       'account_save_issue': window.account_cache.save_issue,
                       'account_preserve_original': window.account_cache.preserve_original,
                       'files': filesystem(active_folder),
                       'current_operator_state': window.current_operator_state(),
                       'training_conditions': window.training_conditions() if has_operator else None,
                       'training_getters_invoked': has_operator,
                       'training_status': window.training_status.text(),
                       'operator_summary': window.operator_summary.toPlainText(),
                       'run_summary': window.run_summary.text(),
                       'level': window.level.value(), 'skill': window.skill.currentData(),
                       'rank': window.skill_rank_value() if has_operator else None,
                       'run_priority': window.use_run_training.isChecked(),
                       'operator_observations_alias_is_records':
                           window.operator_observations is window.account_cache.records,
                       'sample_epoch': window.sample_epoch, 'last_sample_at': window.last_sample_at,
                       'observation': window.observation,
                       'map_frame': frame_description(window.map_frame),
                       'map_frames': {key: frame_description(frame)
                                      for key, frame in window.map_frames.items()},
                       'last_observed_operator': window.last_observed_operator,
                       'last_observed_stage': window.last_observed_stage,
                       'target_stage_index': window.target_stage.currentIndex(),
                       'target_enemy_index': window.target_enemy.currentIndex(),
                       'relic_context_previews': window.relic_context_previews,
                       'relic_context_text': window.relic_context.toPlainText(),
                       'target_buff_previews': window.target_buff_previews,
                       'target_preview_operator': window.target_preview_operator,
                       'target_buff_test': window.target_buff_test.isChecked(),
                       'capture_stats': window.capture.stats()})

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
        assert_native_equal(value, unchanged, 'Three original formatters preserve full numeric result')
        assert_native_equal({'run': window.run.state, 'account': window.account_cache.records,
                             'files': filesystem(active_folder)}, before,
                            'Actual manual calculation preserves accepted state and every owned file')
        return freeze({'damage_result': value, 'three_full_texts': texts,
                       'visible_damage_text': window.damage_text.toPlainText()})

    def record(label, value):
        reference = write_record(records, len(record_refs) + 1, freeze(value))
        reference['label'] = label
        record_refs.append(reference)
        persist_progress('running')

    def screenshot(label):
        for index, suffix in ((0, 'summary'), (1, 'calculation')):
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

    def fresh(folder, run_fixture=None):
        nonlocal window, active_folder, account_path, run_path
        if window is not None:
            window.close()
            application.processEvents()
        active_folder = folder
        account_path = folder / 'account.json'
        run_path = folder / 'run.json'
        if run_fixture is not None:
            account_path.write_bytes(json.dumps(public_account, ensure_ascii=True).encode('ascii'))
            run_path.write_bytes(json.dumps(run_fixture, ensure_ascii=True).encode('ascii'))
        owned_parents.add(folder)
        owned_pending.add(run_path.with_suffix('.tmp'))
        module.OPERATOR_STATE = account_path
        module.RUN_STATE = run_path
        module.SETTINGS = folder / 'settings.json'
        module.DesktopBackend = lambda _path, callback: real_backend(folder / 'chat', callback)
        window = module.MainWindow()
        windows.append(window)
        window.auto.setChecked(False)
        window.timer.stop()
        window.capture.set_collecting(False)
        window.resize(1400, 1050)
        window.show()
        window.centralWidget().setCurrentIndex(1)
        process()
        assert window.operator.currentData() == OP
        assert window.use_run_training.isChecked()
        assert window.operator_observations is window.account_cache.records
        assert not module.list_game_windows(), 'No game prerequisite used'
        assert not window.run.preserve_unreadable and window.run.save_issue is None
        return snapshot()

    def run_observation(level):
        fields = dict(public_run['operators'][OP]['fields'], level=level)
        return {'operators': [{'id': OP, 'scope': 'run', 'fields': fields,
                              'skill_ranks': {'1': 7}, 'recruitment_kind': 'non_emergency',
                              'advanced': False, 'sources': {'level': 'public-manual-run099'}}],
                'crew_count': 1, 'selected_operator': OP,
                'relics': {'ids': [], 'count': 0, 'icons': [], 'source': 'held_bar'}}

    def deliver(level, captured):
        incoming = run_observation(level)
        before = freeze(incoming)
        complete = {'captured_at': captured, 'page': 'public_manual_run_record',
                    'nodes': [], 'run': incoming, 'performance': {}}
        complete_before = freeze(complete)
        image = numpy.zeros((100, 160, 3), dtype=numpy.uint8)
        window.sample_received((image, complete))
        process()
        assert_native_equal(incoming, before, 'Run delivery caller retains all native values and aliases')
        assert_native_equal(complete, complete_before, 'Complete manual delivery caller stays unchanged')
        assert window.last_sample_at == captured and window.run.state['last_read'] == captured
        assert window.run.state['operators'][OP]['fields']['level'] == level
        assert window.current_operator_state()['fields']['level'] == level
        assert window.level.value() == level
        assert window.run_summary.text() == window.run.summary()
        assert window.operator_summary.toPlainText() == module.format_operator_observation(
            window.run.state['operators'][OP])

    def assert_failure_notice():
        assert window.run.save_issue and not window.run.preserve_unreadable
        text = window.run_summary.text()
        for fragment in ('保存未完成', '仅在当前运行有效', '可能恢复磁盘中较早的记录',
                         '不会再次写入或覆盖本局记录'):
            assert fragment in text, (fragment, text)
        assert '原本局记录无法读取' not in text
        assert '持续累积并保存' not in text

    try:
        sys.excepthook = qt_hook
        sys.path.insert(0, str(root))
        import numpy
        from PySide6.QtWidgets import QApplication, QPushButton
        import rouge.app as module
        import rouge.reporting as reporting
        import rouge.estimate as estimate
        from rouge.run_state import RunState
        real_backend = module.DesktopBackend
        for name in ('OPERATOR_STATE', 'RUN_STATE', 'SETTINGS', 'DesktopBackend'):
            restored.append((module, name, getattr(module, name)))

        def watch_run_method(name, calls):
            original = getattr(RunState, name)
            restored.append((RunState, name, original))

            @functools.wraps(original)
            def watched(instance, *positional, **keywords):
                row = {'step': current, 'method': name, 'file': str(instance.file),
                       'positional_before': freeze(positional), 'keywords_before': freeze(keywords),
                       'state_before': freeze(instance.state), 'save_issue_before': instance.save_issue,
                       'load_guard_before': instance.preserve_unreadable, 'outcome': 'pending'}
                calls.append(row)
                try:
                    value = original(instance, *positional, **keywords)
                except BaseException as error:
                    row.update(outcome='raised', error_type=type(error).__name__, error_args=error.args)
                    raise
                else:
                    row.update(outcome='returned', returned=value)
                    return value
                finally:
                    assert_native_equal(positional, row['positional_before'], 'Original run method arguments unchanged')
                    assert_native_equal(keywords, row['keywords_before'], 'Original run method keywords unchanged')
                    row.update(state_after=freeze(instance.state), save_issue_after=instance.save_issue,
                               load_guard_after=instance.preserve_unreadable)

            setattr(RunState, name, watched)

        watch_run_method('apply', run_calls)
        watch_run_method('save', save_calls)
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

        def watch_path_method(name):
            original = getattr(Path, name)
            restored.append((Path, name, original))

            @functools.wraps(original)
            def watched(path, *positional, **keywords):
                owned = path in (owned_parents if name == 'mkdir' else owned_pending)
                if not owned:return original(path, *positional, **keywords)
                row = {'step': current, 'method': name, 'path': str(path),
                       'positional_descriptions': freeze(tuple(describe_io_argument(v) for v in positional)),
                       'keyword_descriptions': freeze({k: describe_io_argument(v) for k, v in keywords.items()}),
                       'outcome': 'pending'}
                io_calls.append(row)
                try:
                    value = original(path, *positional, **keywords)
                except BaseException as error:
                    row.update(outcome='raised', error_type=type(error).__name__,
                               error_args=error.args, is_actual_oserror=isinstance(error, OSError))
                    raise
                else:
                    row.update(outcome='returned', returned_description=describe_io_argument(value))
                    return value

            setattr(Path, name, watched)

        for name in ('mkdir', 'write_text', 'replace'):watch_path_method(name)
        public_account = {OP: {'id': OP, 'scope': 'operator_profile',
                          'fields': {'elite': 2, 'level': 2, 'trust': 100, 'potential': 1,
                                     'module_id': None, 'module_level': 0},
                          'skill_ranks': {'1': 7}, 'captured_at': START + 1}}
        public_run = {'id': 'public-run099-window', 'started_at': START, 'last_read': START + 1,
                      'operators': {OP: {'id': OP, 'scope': 'run', 'present': True,
                          'fields': {'elite': 2, 'level': 1, 'trust': 60, 'potential': 2,
                                     'module_id': None, 'module_level': 0},
                          'skill_ranks': {'1': 7}, 'captured_at': START + 1,
                          'recruitment_kind': 'non_emergency', 'advanced': False}},
                      'selected_operator': OP, 'crew_count': 1, 'relics': {},
                      'history': [], 'resources': {}, 'tactical_tools': {}, 'config': {}, 'maps': {}}
        application = QApplication([])
        application.setQuitOnLastWindowClosed(False)

        current = 'healthy_same_facts_control'
        healthy_folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-run099-healthy-')))
        healthy_initial = fresh(healthy_folder, freeze(public_run))
        initial_reports = reports()
        deliver(3, START + 10)
        healthy_level3 = reports()
        healthy_state3 = freeze(window.run.state)
        assert_native_equal(json.loads(run_path.read_text(encoding='utf-8')), window.run.state,
                            'Healthy actual run save commits full accepted state')
        assert not run_path.with_suffix('.tmp').exists()
        deliver(4, START + 12)
        healthy_level4 = reports()
        healthy_state4 = freeze(window.run.state)
        assert_native_equal(json.loads(run_path.read_text(encoding='utf-8')), window.run.state,
                            'Second healthy save commits full accepted state')
        record(current, {'initial': healthy_initial, 'initial_reports': initial_reports,
                         'level3': healthy_state3, 'level3_reports': healthy_level3,
                         'level4': healthy_state4, 'level4_reports': healthy_level4, 'final': snapshot()})

        current = 'real_io_failure_and_continuing_run'
        io_folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-run099-real-io-')))
        io_initial = fresh(io_folder, freeze(public_run))
        io_original = run_path.read_bytes()
        account_original = account_path.read_bytes()
        original_run_id = window.run.state['id']
        pending = run_path.with_suffix('.tmp')
        assert pending != run_path and not pending.exists()
        # This actual fixture setup is not a product retry or permission mock.
        pending.mkdir()
        sentinel = pending / 'public-sentinel.bin'
        sentinel.write_bytes(SENTINEL_BYTES)
        io_before = snapshot()
        run_index = len(run_calls)
        save_index = len(save_calls)
        io_index = len(io_calls)
        deliver(3, START + 10)
        assert window.run.state['id'] == original_run_id
        assert_native_equal(window.run.state, healthy_state3, 'Accepted full run equals healthy same-fact memory')
        actual_failure = io_calls[io_index:]
        assert [row['method'] for row in actual_failure] == ['mkdir', 'write_text']
        assert actual_failure[0]['outcome'] == 'returned'
        assert actual_failure[1]['outcome'] == 'raised' and actual_failure[1]['is_actual_oserror']
        assert run_calls[run_index:][-1]['returned'] is True
        assert save_calls[save_index:][-1]['returned'] is False
        assert run_path.read_bytes() == io_original
        assert account_path.read_bytes() == account_original
        assert sentinel.read_bytes() == SENTINEL_BYTES and list(pending.iterdir()) == [sentinel]
        assert_failure_notice()
        io_reports3 = reports()
        assert_native_equal(io_reports3, healthy_level3, 'IO failure retains complete original math and three texts')
        before_later_io = len(io_calls)
        deliver(4, START + 12)
        assert len(io_calls) == before_later_io
        assert window.run.state['id'] == original_run_id
        assert_native_equal(window.run.state, healthy_state4, 'Later accepted facts equal healthy current run')
        assert run_path.read_bytes() == io_original and sentinel.read_bytes() == SENTINEL_BYTES
        io_reports4 = reports()
        assert_native_equal(io_reports4, healthy_level4, 'Later facts retain healthy original math and three texts')
        assert_failure_notice()
        screenshot('real-io-failure')
        record(current, {'initial': io_initial, 'before_failure': io_before,
                         'after_failure_and_later_read': snapshot(),
                         'reports3': io_reports3, 'reports4': io_reports4,
                         'actual_run_calls': run_calls[run_index:], 'actual_save_calls': save_calls[save_index:],
                         'actual_owned_IO_calls': io_calls[io_index:]})

        current = 'manual_new_run_stays_in_memory_without_retry'
        # Explicit public UI-reset preconditions; no game state or real map added.
        assert window.map_frame is not None
        window.map_frames['public-reset-precondition'] = window.map_frame
        window.relic_context_previews[(OP, 1)] = '{}'
        window.target_buff_previews[OP] = ['public-unused-preview-marker']
        window.target_preview_operator = OP
        window.target_buff_test.blockSignals(True)
        window.target_buff_test.setChecked(True)
        window.target_buff_test.blockSignals(False)
        # Queue a clearly synthetic, non-dark frame through the real public
        # buffer API. This is not capture/OCR; reset must actually discard it.
        queued_image = numpy.full((16, 32, 3), 127, dtype=numpy.uint8)
        window.capture.buffer.offer(queued_image, START + 13)
        assert window.capture.stats()['pending'] == 1
        manual_before = snapshot()
        manual_epoch = window.sample_epoch
        manual_generation = window.capture.stats()['generation']
        manual_id = window.run.state['id']
        saved_issue = window.run.save_issue
        manual_io_index = len(io_calls)
        window.centralWidget().setCurrentIndex(0)
        process()
        window.reset_run_button.click()
        process()
        assert window.sample_epoch == manual_epoch + 1
        assert window.run.state['id'] != manual_id
        assert window.run.state['operators'] == {} and window.run.state['relics'] == {}
        assert window.run.state['maps'] == {} and window.run.state['history'] == []
        assert window.run.state['last_read'] is None
        assert window.observation is None and window.map_frame is None and window.map_frames == {}
        assert window.capture.stats()['pending'] == 0
        assert window.capture.stats()['generation'] != manual_generation
        assert window.last_observed_operator is None and window.last_observed_stage is None
        assert window.target_stage.currentIndex() == 0 and window.target_enemy.currentIndex() == 0
        assert window.relic_context_previews == {} and not window.relic_context.toPlainText()
        assert window.target_buff_previews == {} and not window.target_buff_test.isChecked()
        assert len(io_calls) == manual_io_index
        assert window.run.save_issue == saved_issue and not window.run.preserve_unreadable
        assert run_path.read_bytes() == io_original and account_path.read_bytes() == account_original
        assert sentinel.read_bytes() == SENTINEL_BYTES
        assert_failure_notice()
        manual_empty = snapshot()
        new_id = window.run.state['id']
        deliver(5, window.run.state['started_at'] + 1)
        assert window.run.state['id'] == new_id and len(io_calls) == manual_io_index
        assert run_path.read_bytes() == io_original and sentinel.read_bytes() == SENTINEL_BYTES
        assert_failure_notice()
        new_run_reports = reports()
        same_new_run_facts = freeze(window.run.state)
        # A delayed prior-epoch completion with a deliberately newer timestamp
        # must not restore old-run cultivation into the accepted new run.
        stale = {'captured_at': window.run.state['last_read'] + 1,
                 'page': 'public_manual_prior_epoch', 'nodes': [],
                 'run': run_observation(9), 'performance': {},
                 '_sampling': {'epoch': manual_epoch, 'generation': manual_generation}}
        stale_caller = freeze(stale)
        prior_delivery = freeze({'run': window.run.state, 'observation': window.observation,
                                'last_sample_at': window.last_sample_at,
                                'files': filesystem(active_folder)})
        before_stale_calls = len(run_calls)
        window.sample_received((queued_image, stale))
        process()
        assert len(run_calls) == before_stale_calls and len(io_calls) == manual_io_index
        assert_native_equal(stale, stale_caller, 'Prior-epoch caller stays unchanged')
        assert_native_equal({'run': window.run.state, 'observation': window.observation,
                             'last_sample_at': window.last_sample_at,
                             'files': filesystem(active_folder)}, prior_delivery,
                            'Delayed prior-run completion cannot overwrite accepted new-run facts')
        screenshot('manual-new-run')
        record(current, {'before_manual_click': manual_before, 'after_actual_manual_click': manual_empty,
                         'after_new_run_delivery': snapshot(), 'new_run_reports': new_run_reports,
                         'synthetic_prior_epoch_delivery': stale,
                         'actual_save_calls': save_calls[save_index:],
                         'actual_owned_IO_calls_after_manual': io_calls[manual_io_index:]})

        current = 'healthy_same_new_run_facts_control'
        clone_folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-run099-new-facts-')))
        fresh(clone_folder, same_new_run_facts)
        # Clone only into a separate public healthy fixture; never overwrite or
        # restore old/new facts into the failed window's accepted memory/files.
        assert window.run.state['id'] == same_new_run_facts['id']
        assert window.current_operator_state()['fields']['level'] == 5
        assert_native_equal(reports(), new_run_reports,
                            'Healthy actual window with identical new-run facts has identical full math/three texts')
        record(current, {'new_healthy_control': snapshot(), 'original_failed_new_run_facts': same_new_run_facts})

        current = 'healthy_restart_restores_preserved_disk_record'
        restart_io_index = len(io_calls)
        fresh(io_folder)
        assert window.run.state['id'] == original_run_id
        assert window.current_operator_state()['fields']['level'] == 1
        assert window.run.save_issue is None and not window.run.preserve_unreadable
        assert run_path.read_bytes() == io_original and account_path.read_bytes() == account_original
        assert sentinel.read_bytes() == SENTINEL_BYTES and list(pending.iterdir()) == [sentinel]
        assert len(io_calls) == restart_io_index
        assert_native_equal(reports(), initial_reports,
                            'Actual new window reads original healthy disk facts and original math/three texts')
        record(current, {'actual_restart': snapshot(), 'actual_owned_IO_calls': io_calls[restart_io_index:]})
        assert len(windows) == 4 and len(record_refs) == 5 and len(pngs) == 4
        assert not qt_errors and all(row['outcome'] != 'pending'
                                    for row in run_calls + save_calls + io_calls)
        receipt.update(passed=True, workflow_complete=True)
    except BaseException as error:
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
                              'step': current, 'traceback': traceback.format_exc()}
        try:
            record('unfinished_failure', {'step': current, 'actual_run_calls': run_calls,
                    'actual_save_calls': save_calls, 'actual_numeric_calls': numeric_calls,
                    'actual_owned_IO_calls': io_calls, 'Qt_exceptions': qt_errors,
                    'state': snapshot() if window is not None else None})
        except BaseException as saving_error:
            receipt['unfinished_save_error'] = str(saving_error)
    finally:
        close_errors = []
        for item in windows:
            try:
                if not item.closing:item.close()
            except BaseException as error:
                close_errors.append({'type': type(error).__name__, 'message': str(error)})
        if application is not None:application.processEvents()
        if close_errors or qt_errors:receipt.update(passed=False, workflow_complete=False)
        for owner, name, original in reversed(restored):setattr(owner, name, original)
        sys.excepthook = previous_hook
        after_source = source_map(root)
        drift = [name for name in sorted(set(before_source) | set(after_source))
                 if before_source.get(name) != after_source.get(name)]
        if drift:receipt.update(passed=False, workflow_complete=False)
        receipt.update(source_after=after_source, source_drift=drift, fresh_windows=len(windows),
                       actual_run_calls=len(run_calls), actual_save_calls=len(save_calls),
                       actual_numeric_calls=len(numeric_calls), actual_owned_IO_calls=len(io_calls),
                       Qt_exceptions=qt_errors, close_errors=close_errors,
                       elapsed_seconds=round(time.perf_counter() - started, 3),
                       ended_at_UTC=datetime.now(timezone.utc).isoformat())
        if numeric_calls:
            receipt['complete_actual_numeric_call_evidence'] = write_record(output, 1, freeze(numeric_calls))
        folders.close()
        with lock:write_json(output / 'receipt.json', receipt)
        persist_progress('passed' if receipt['passed'] else 'failed')
        finished.set()
        print(json.dumps({'passed': receipt['passed'], 'records': len(record_refs),
                          'failure': receipt.get('failure')}, ensure_ascii=True), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
