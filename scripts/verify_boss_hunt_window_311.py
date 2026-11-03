"""Real Windows fixed-stage reader fixture; root alone executes after promotion."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_boss_hunt_window_311.py'
PACK = 'research/p3-boss-hunt-311'
MANIFEST = PACK + '/source-manifest.json'
DATA = 'rouge/data/boss-hunt-reference.json'
TARGETS = (('ro6_b_4', 'enemy_2145_cadejo', 0), ('ro6_b_4', 'enemy_2146_cadesd', 0),
           ('ro6_b_4', 'enemy_2137_shsdgo', 0))
PICTURE_ATTRIBUTES = ('boss_picture', 'avatar_picture', 'hound_picture')
FALSE_FLAGS = ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated',
               'inventory_updated', 'modifiers_changed', 'maps_changed')


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bound_files():
    names = {CANONICAL, MANIFEST, DATA, 'rouge/boss_hunt_reference.py', 'rouge/boss_hunt_view.py',
             'rouge/battle_view.py', 'rouge/battle_preview.py', 'rouge/enemy_skills.py',
             'rouge/view_catalog.py', 'rouge/ui_state.py', 'rouge/branch_choice.py',
             'rouge/enemy_form_reference.py', 'rouge/enemy_form_view.py',
             'rouge/boss_phase_reference.py', 'rouge/boss_phase_view.py',
             'rouge/boss_cycle_reference.py', 'rouge/boss_cycle_view.py',
             'rouge/app.py', 'rouge/capture.py', 'rouge/desktop_backend.py', 'rouge/chat.py', 'rouge/credentials.py',
             'rouge/data/battle-previews.json', 'rouge/data/view-catalog.json',
             'rouge/data/enemy-skill-references.json', 'scripts/build_boss_hunt_reference_311.py',
             'tests/test_boss_hunt_reference_311.py', 'tests/test_boss_hunt_view_311.py',
             'tests/test_boss_hunt_integration_311.py'}
    manifest = read(ROOT / MANIFEST)
    names.update(manifest['runtime_files'])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / PACK).rglob('*') if p.is_file())
    # This fixture also checks that the pre-existing phase entry stays available.
    phase_manifest = 'research/p3-boss-phase-309/source-manifest.json'
    names.add(phase_manifest)
    names.update(read(ROOT / phase_manifest)['runtime_files'])
    catalog = read(ROOT / 'rouge/data/view-catalog.json')
    for _, enemy_id, _ in TARGETS:
        portrait = catalog['enemies'][enemy_id].get('portrait')
        if portrait is None:
            raise ValueError('Exact subject portrait is absent: ' + enemy_id)
        names.add('rouge/data/' + catalog['images'][portrait]['file'])
    stages = read(ROOT / 'rouge/data/battle-previews.json')['stages']
    for stage_id in ('ro6_b_4', 'ro6_b_4_b', 'ro6_b_6'):
        names.add('rouge/data/' + stages[stage_id]['image']['file'])
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if (not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT.resolve())):
            raise ValueError('A regular selected public source is required: ' + name)
        result[name] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True, type=Path)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = args.receipt.resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first real receipt.')
    if args.visible_ms < 15000:
        raise ValueError('At least 15000 ms are needed for staged real reading.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before, after = {}, {}
    failure = None
    checks, images, windows = [], [], []
    readings, overviews, refreshes = [], [], []
    negative = None
    calls = 0
    gui = panel = None
    qpa = None
    qt_exit = None
    done = closed = False
    attempts = {name: 0 for name in ('game_enumeration', 'game_connect', 'game_capture', 'game_next_frame',
                                    'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}

    def require(value, label):
        nonlocal calls
        if not value:
            raise AssertionError(label)
        calls += 1
        if label not in checks:
            checks.append(label)

    def forbidden(name):
        def blocked(*_args, **_kwargs):
            attempts[name] += 1
            raise AssertionError('Forbidden external operation: ' + name)
        return blocked

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual Windows is required.')
        if Path(__file__).resolve() != (ROOT / CANONICAL).resolve():
            raise RuntimeError('A cache candidate must not be executed.')
        before = bound_files()
        from rouge import app as app_module, boss_hunt_reference as model
        from rouge.battle_view import BattlePreviewPanel
        from rouge.branch_choice import OVERVIEW
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process

        packets = {identity: model.hunt_reference(*identity) for identity in TARGETS}
        require(model.TARGETS == TARGETS and all(packet is not None and packet['source_valid'] is True
                                                for packet in packets.values()),
                'all_three_exact_normal_stage_entries_have_valid_fixed_sources_before_GUI')
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_native_windows_QPA')
        with tempfile.TemporaryDirectory(prefix='rouge-311-hunt-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for attribute, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                                     'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, attribute, value))
            stack.enter_context(patch.object(app_module, 'list_game_windows', side_effect=forbidden('game_enumeration')))
            for method, name in (('connect', 'game_connect'), ('capture', 'game_capture'), ('next_frame', 'game_next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, method, side_effect=forbidden(name)))
            for method, name in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(app_module.DesktopBackend, method, side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            panel = BattlePreviewPanel()
            panel.setWindowTitle('第311节 · 卡德霍与相关敌人机制资料（公开隔离验收）')
            panel.resize(1280, 900)
            panel.show()
            context_before = deepcopy(panel.context)
            entry_index = 0
            identity = TARGETS[0]
            topics = []
            saved_parent = None

            def native(widget, kind):
                hwnd = int(widget.winId())
                thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
                        and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'real_visible_owned_HWND_matches_fixture_PID')
                value = {'kind': kind, 'hwnd': hwnd, 'process_id': pid, 'thread_id': thread,
                         'qpa': qpa, 'client_size': [widget.width(), widget.height()]}
                windows.append(value)
                return value

            def choose(combo, value):
                index = next((i for i in range(combo.count()) if type(combo.itemData(i)) is type(value)
                              and combo.itemData(i) == value), -1)
                if index < 0:
                    raise AssertionError('Exact value is absent from the actual combo: ' + str(value))
                combo.setFocus()
                QTest.keyClick(combo, Qt.Key.Key_Home)
                for _ in range(index):
                    QTest.keyClick(combo, Qt.Key.Key_Down)
                QTest.keyClick(combo, Qt.Key.Key_Return)
                gui.processEvents()
                require(type(combo.currentData()) is type(value) and combo.currentData() == value,
                        'real_QTest_combo_selects_exact_source_identity')

            def reader(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value()}

            def parent_state():
                return deepcopy({'stage': panel.current_stage, 'wave': panel.wave_combo.currentData(),
                    'enemy_branch': panel.enemy_choices.branch.currentData(), 'enemy': panel.enemy_combo.currentData(),
                    'branches': panel.include_branches.isChecked(), 'technical': panel.technical.isChecked(),
                    'row': panel.grid.selected, 'tile': panel._tile_cell, 'original_row': panel.original.selected,
                    'original_cell': panel.original.reference_cell, 'context': panel.context,
                    'spawn_text': panel.spawn_detail.toPlainText(), 'enemy_text': panel.enemy_detail.toPlainText(),
                    'spawn_reading': reader(panel.spawn_detail), 'enemy_reading': reader(panel.enemy_detail)})

            def screenshot(name, widget, direct_player=True):
                path = destination.with_name('window-' + name + '.png')
                if path.exists():
                    raise FileExistsError('Preserve the first real screenshot.')
                widget.repaint()
                gui.processEvents()
                require(widget.grab().save(str(path), 'PNG'), 'actual_widget_PNG_saved')
                images.append({'name': name, 'path': str(path), 'sha256': sha(path),
                               'direct_player_text': direct_player, 'native_window': native(widget, name)})

            def close_all():
                nonlocal closed
                if panel.boss_hunt_window is not None:
                    panel.boss_hunt_window.close()
                panel.close()
                gui.processEvents()
                closed = not panel.isVisible() and (panel.boss_hunt_window is None or not panel.boss_hunt_window.isVisible())

            def fail(error):
                nonlocal failure
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                close_all()
                gui.exit(1)

            def later(function, delay=200):
                def guarded():
                    try:
                        function()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def select_identity(value):
                if panel.current_stage != value[0]:
                    panel.stage_choices.select_branch(OVERVIEW)
                    choose(panel.stage_combo, value[0])
                panel.enemy_choices.select_branch(OVERVIEW)
                choose(panel.enemy_combo, (value[1], value[2]))
                require(panel._shown_enemy == value, 'actual_enemy_combo_resolves_the_exact_selected_tuple')

            def begin():
                nonlocal identity, topics, saved_parent
                identity = TARGETS[entry_index]
                prior = panel.boss_hunt_window
                native(panel, 'battle-preview')
                if entry_index == 0:
                    require(prior is None, 'no_hunt_window_automatically_created_before_manual_entry')
                select_identity(identity)
                require(panel.boss_hunt_button.isVisible() and panel.boss_hunt_button.isEnabled(),
                        'exact_normal_stage_subject_exposes_enabled_manual_entry')
                if prior is not None:
                    require(prior.identity is None and prior.topic.count() == 0 and not prior.player.toPlainText(),
                            'switching_subject_clears_old_topic_before_manual_reopen')
                saved_parent = parent_state()
                QTest.mouseClick(panel.boss_hunt_button, Qt.MouseButton.LeftButton)
                gui.processEvents()
                dialog = panel.boss_hunt_window
                dialog.resize(1080, 760)
                gui.processEvents()
                require(dialog.identity == identity and dialog.topic.currentData() is None and not dialog.isModal(),
                        'actual_button_opens_selected_subject_modeless_overview')
                require(parent_state() == saved_parent, 'manual_open_keeps_parent_filters_map_selection_and_reading')
                pictures = [getattr(dialog, attribute) for attribute in PICTURE_ATTRIBUTES]
                require([picture.key[1] for picture in pictures] == [value[1] for value in TARGETS]
                        and all(picture.key[0] == 'enemy' and picture.image.pixmap() is not None
                                and not picture.image.pixmap().isNull() for picture in pictures),
                        'three_distinct_exact_original_portraits_loaded_without_current_state_claim')
                require(dialog.player.toPlainText() == model.reference_text(dialog.result, topic_id=None),
                        'overview_displays_the_complete_ordinary_player_reference')
                topics = dialog.result['reference']['topics']
                topic_ids = [row['id'] for row in topics]
                require(bool(topic_ids) and len(set(topic_ids)) == len(topic_ids)
                        and all(type(value) is str for value in topic_ids),
                        'all_manual_topics_come_from_current_source_not_a_hardcoded_count')
                overviews.append({'identity': list(identity), 'entry_name': dialog.result['reference']['entry_name'],
                    'topic_ids': topic_ids, 'portrait_subjects': [list(picture.key[:2]) for picture in pictures],
                    'native_window': native(dialog, 'subject-overview')})
                screenshot('subject-' + str(entry_index + 1) + '-overview-player', dialog)
                later(lambda: topic_case(0))

            def topic_case(index):
                dialog = panel.boss_hunt_window
                topic = topics[index]
                choose(dialog.topic, topic['id'])
                require(dialog.identity == identity and dialog.result['reference']['enemy_id'] == identity[1]
                        and dialog.result['reference']['entry_name'] in dialog.windowTitle()
                        and dialog.player.toPlainText() == model.reference_text(dialog.result, topic_id=topic['id'])
                        and all(value[1] not in dialog.player.toPlainText() for value in TARGETS),
                        'manual_topic_keeps_subject_identity_and_ordinary_player_text_without_raw_enemy_IDs')
                source = json.loads(dialog.technical.toPlainText())
                require(source['selected_topic_id'] == topic['id'] and source['result'] == dialog.result,
                        'technical_tab_retains_all_source_data_and_selected_topic_identity')
                require(bool(model.ACTUAL_FIELDS) and all(dialog.result[field] is None for field in model.ACTUAL_FIELDS)
                        and all(dialog.result[flag] is False for flag in FALSE_FLAGS),
                        'reading_never_applies_actual_forms_hounds_clocks_damage_inventory_or_map_changes')
                require(parent_state() == saved_parent, 'topic_reading_keeps_parent_context_filters_map_and_text')
                readings.append({'identity': list(identity), 'topic_id': topic['id'], 'name': topic['name'],
                                 'native_window': native(dialog, 'topic-reader')})
                if entry_index == 0 and index == 0:
                    screenshot('manual-topic-player', dialog)
                if index + 1 < len(topics):
                    later(lambda: topic_case(index + 1))
                else:
                    later(check_refresh)

            def check_refresh():
                nonlocal entry_index
                dialog = panel.boss_hunt_window
                richest = max(topics, key=lambda row: len(model.reference_text(dialog.result, topic_id=row['id'])))['id']
                choose(dialog.topic, richest)
                dialog.resize(980, 470)
                gui.processEvents()
                selected = dialog.topic.currentData()
                for widget in (dialog.player, dialog.technical):
                    dialog.tabs.setCurrentWidget(widget)
                    gui.processEvents()
                    cursor = widget.textCursor()
                    cursor.setPosition(2)
                    cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
                    widget.setTextCursor(cursor)
                    bar = widget.verticalScrollBar()
                    require(bar.maximum() > 0, 'real_reader_has_nonzero_scroll_without_synthetic_padding')
                    bar.setValue(min(17, bar.maximum()))
                    before_reading = reader(widget)
                    scope = dialog.scope_key
                    panel._refresh_boss_hunt()
                    gui.processEvents()
                    require(dialog.tabs.currentWidget() is widget and dialog.topic.currentData() == selected
                            and dialog.scope_key == scope and reader(widget) == before_reading,
                            'same_identity_source_and_topic_refresh_preserves_tab_cursor_selection_and_nonzero_scroll')
                    refreshes.append({'identity': list(identity), 'topic_id': selected, 'tab': dialog.tabs.indexOf(widget),
                                      'before': before_reading, 'after': reader(widget)})
                if entry_index + 1 < len(TARGETS):
                    entry_index += 1
                    later(begin)
                else:
                    later(check_negative)

            def check_negative():
                nonlocal negative
                dialog = panel.boss_hunt_window
                clone = temporary / 'public-source-clone'
                manifest = read(ROOT / MANIFEST)
                names = [MANIFEST, *manifest['runtime_files']]
                for name in names:
                    source = ROOT / name
                    target = clone / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
                damaged_relative = PACK + '/runtime-selected-authority.json'
                require(damaged_relative in names, 'negative_fixture_damages_a_real_runtime_authority_member')
                with patch.object(model, 'ROOT', clone):
                    require(model.hunt_reference(*identity)['source_valid'] is True,
                            'complete_temporary_public_source_clone_valid_before_real_byte_damage')
                    target = clone / damaged_relative
                    original = target.read_bytes()
                    target.write_bytes(original + b' ')
                    try:
                        panel._refresh_boss_hunt()
                        gui.processEvents()
                        require(not panel.boss_hunt_button.isEnabled() and dialog.identity is None
                                and dialog.result is None and dialog.topic.count() == 0 and not dialog.topic.isEnabled()
                                and not dialog.player.toPlainText() and not dialog.technical.toPlainText()
                                and all(getattr(dialog, attribute).key == (None, None, '') for attribute in PICTURE_ATTRIBUTES),
                                'actual_bad_source_clears_both_readers_all_pictures_and_topic_and_disables_entry')
                        screenshot('source-unavailable-cleared', dialog)
                    finally:
                        target.write_bytes(original)
                    panel._refresh_boss_hunt()
                    gui.processEvents()
                    require(panel.boss_hunt_button.isEnabled() and dialog.identity is None and not dialog.player.toPlainText(),
                            'source_recovery_does_not_automatically_refill_the_old_reader')
                    QTest.mouseClick(panel.boss_hunt_button, Qt.MouseButton.LeftButton)
                    gui.processEvents()
                    require(dialog.identity == identity and dialog.topic.currentData() is None,
                            'restored_source_requires_real_manual_overview_reopen')
                    negative = {'exact_copied_public_files': names, 'damaged_source': damaged_relative,
                                'restored_exact_bytes': target.read_bytes() == original,
                                'manual_reopened_identity': list(dialog.identity)}
                # The same enemy names/IDs in the distinct 痛苦将息 stage are not entries.
                select_identity(('ro6_b_4_b', TARGETS[0][1], 0))
                require(panel.boss_hunt_button.isHidden() and not panel.open_boss_hunt_reference()
                        and dialog.identity is None and not dialog.player.toPlainText()
                        and all(getattr(dialog, attribute).key == (None, None, '') for attribute in PICTURE_ATTRIBUTES),
                        'real_other_stage_with_same_enemy_names_hides_entry_and_clears_old_content')
                select_identity(('ro6_b_6', 'enemy_2150_shchmr', 0))
                require(panel.boss_hunt_button.isHidden() and panel.boss_phase_button.isEnabled(),
                        'other_boss_hides_new_entry_and_keeps_existing_phase_reader_available')
                require(panel.context == context_before and all(value == 0 for value in attempts.values()),
                        'parent_calculation_context_unchanged_and_all_eight_external_attempts_zero')
                require(all([row['topic_id'] for row in readings if row['identity'] == list(value)]
                            == [topic['id'] for topic in packets[value]['reference']['topics']] for value in TARGETS),
                        'all_three_selected_subjects_manually_read_every_dynamic_source_topic')
                later(finish)

            def finish():
                nonlocal done
                done = True
                close_all()
                gui.exit(0)

            def timeout():
                if not done:
                    fail(TimeoutError('The documentary native fixture did not finish before its deadline.'))

            try:
                later(begin, 350)
                QTimer.singleShot(args.visible_ms, timeout)
                qt_exit = gui.exec()
                require(qt_exit == 0 and done and closed, 'actual_Qt_success_and_owned_widgets_closed')
            finally:
                close_all()
        after = bound_files()
        require(before == after, 'selected_public_source_bytes_unchanged_through_real_window_close')
    except BaseException as error:
        if failure is None:
            failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if panel is not None:
            try:
                if panel.boss_hunt_window is not None:
                    panel.boss_hunt_window.close()
                panel.close()
                if gui is not None:
                    gui.processEvents()
                closed = not panel.isVisible() and (panel.boss_hunt_window is None or not panel.boss_hunt_window.isVisible())
            except BaseException as error:
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        if before and not after:
            try:
                after = bound_files()
            except BaseException:
                pass
    report = {'section': 311, 'kind': 'isolated_native_windows_boss_hunt_reader',
        'passed': done and failure is None and qt_exit == 0 and closed,
        'failure': failure, 'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
        'process_id': os.getpid(), 'qpa': qpa, 'qt_exit_code': qt_exit, 'verification_window_closed': closed,
        'checks': checks, 'unique_checks': len(checks), 'successful_assertion_executions_including_repeated_guards': calls,
        'actual_entry_overviews': overviews, 'actual_topic_readings': readings,
        'same_identity_refresh_observations': refreshes, 'source_negative_fixture': negative,
        'screenshots': images, 'screenshot_count': len(images), 'native_observations': windows,
        'source_sha256_before': before, 'source_sha256_after': after,
        'selected_sources_not_all_transitive_dependencies': True, 'temporary_state_root': True,
        'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
        'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
        'actual_hunt_avatar_hounds_rest_gate_stats_damage_time_or_server_verified': False,
        'actual_full_MainWindow_or_process_descendant_closure_claimed': False,
        'scope': 'Three exact entries in 永无安宁 and all manual documentary topics only; original portraits are not live forms. The distinct 痛苦将息关卡 is excluded. Real temporary public source damage and manual recovery; no numerical, map, inventory or run-state application.'}
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
