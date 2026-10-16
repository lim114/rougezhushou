"""Cache draft: manual documented-choice-item reading in an isolated native UI.

Not executable acceptance until promoted to the canonical scripts/ path.  Root
owns the actual process supervisor, final source binding, launch and closeout.
Selected-source guards do not claim the whole transitive dependency graph.
"""
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
CANONICAL = 'scripts/verify_documented_choice_item_window_295.py'
MANIFEST = 'research/p3-documented-choice-items-295/source-manifest.json'
DATA = 'rouge/data/documented-choice-items.json'
EVENT = 'community_group_021'
SIZE = (1050, 720)
CHOICE = EVENT + ':scene:0:choice:0'
ITEM = 'rogue_6_relic_final_1'
REFERENCE = CHOICE + ':documented-item:' + ITEM


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def bound_files():
    names = {CANONICAL, 'rouge/app.py', 'rouge/node_catalog_view.py',
        'rouge/documented_choice_item_view.py', 'rouge/documented_choice_items.py',
        'rouge/node_catalog.py', 'rouge/event_planning.py',
        'rouge/player_node_information.py', 'rouge/ui_state.py',
        'rouge/node_rewards.py', 'rouge/data/node-reward-reference.json',
        'rouge/event_named_reward_links.py', 'rouge/data/event-planning-reference.json',
        'scripts/build_documented_choice_items_295.py',
        'tests/test_documented_choice_items_295.py',
        'tests/test_documented_choice_item_view_295.py',
        'tests/test_documented_item_integration_295.py',
        'verification/sections/295-preparation/pre295-query-baseline.json',
        'tests/test_event_named_reward_integration_289.py',
        'tests/test_event_named_reward_links_289.py', 'tests/test_node_rewards.py',
        'tests/test_player_node_information_286.py', 'tests/test_node_catalog_view.py', MANIFEST}
    manifest = json.loads((ROOT / MANIFEST).read_bytes())
    names.update(manifest['files'])
    names.update(p.relative_to(ROOT).as_posix()
        for p in (ROOT / Path(MANIFEST).parent).rglob('*') if p.is_file())
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if (not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT)):
            raise ValueError('Selected public source must be a regular project file: ' + name)
        result[name] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=30000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt')
    if args.visible_ms <= 0:
        raise ValueError('Positive --visible-ms required')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before = {}; after = {}; checks = []; images = []; native_observations = []
    observations = []; executions = 0; failure = None; done = False
    closed = False; qpa = None; qt_exit = None
    attempts = {name: 0 for name in ('game_enumeration', 'game_connect', 'game_capture',
        'game_next_frame', 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}

    def require(value, label):
        nonlocal executions
        if not value:
            raise AssertionError(label)
        executions += 1
        if label not in checks:
            checks.append(label)

    def forbidden(name):
        def blocked(*_, **__):
            attempts[name] += 1
            raise AssertionError('Forbidden original external entry: ' + name)
        return blocked

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual native Windows required')
        if Path(__file__).resolve() != (ROOT / CANONICAL).resolve():
            raise RuntimeError('Cache draft is not executable acceptance; promote canonical script first')
        from PySide6.QtCore import Qt, QPoint, QRect, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap
        from PySide6.QtTest import QTest
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        from rouge import documented_choice_items as results
        before = bound_files()
        gui = QApplication([]); qpa = gui.platformName()
        require(qpa == 'windows', 'native_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-295-documented-item-window-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                    'OPERATOR_STATE': temporary / 'operators.json',
                    'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, key, value))
            stack.enter_context(patch.object(app_module, 'list_game_windows',
                side_effect=forbidden('game_enumeration')))
            for method, name in [('connect', 'game_connect'), ('capture', 'game_capture'),
                    ('next_frame', 'game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture, method, side_effect=forbidden(name)))
            for method, name in [('start', 'desktop_start'), ('request', 'desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend, method, side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = PublicWindow()
            window.setWindowTitle('第295节 · 线人具名物品说明（公开隔离验收）')
            window.resize(*SIZE); window.show()
            panel = window.node_catalog; tabs = window.centralWidget()
            initial_run = deepcopy(window.run.state)
            typed_before = deepcopy(catalog.event_reward_options(EVENT))
            dialog = None; parent_saved = None; reading_saved = None
            read_observations = []; refresh_rounds = 0
            role = Qt.ItemDataRole.UserRole + 1

            def isolated():
                require(not window.auto.isChecked() and not window.timer.isActive(),
                    'automatic_sampling_and_timer_disabled')
                require(window.capture.target is None and window.desktop.process is None,
                    'capture_target_and_desktop_backend_inactive')
                require(all(value == 0 for value in attempts.values()),
                    'all_eight_external_operation_attempts_zero')

            def native(widget, kind):
                hwnd = int(widget.winId())
                thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(),
                    kind + '_actual_native_HWND_visible')
                require(pid == os.getpid() and not win32gui.IsIconic(hwnd),
                    kind + '_HWND_owned_by_fixture_and_not_minimized')
                actual = [widget.width(), widget.height()]
                if kind == 'parent':
                    require(actual == list(SIZE), 'parent_actual_client_size_exact_1050x720')
                else:
                    require(actual[0] >= 850 and actual[1] >= 650,
                        'dialog_actual_client_size_at_least_850x650')
                return {'kind': kind, 'hwnd': hwnd, 'process_id': pid,
                    'thread_id': thread, 'qpa': qpa, 'client_size': actual}

            def choose(control, key):
                index = control.findData(key)
                require(index >= 0, 'requested_complete_reference_key_exists')
                control.setCurrentIndex(index)

            def event(identity):
                panel.show_directory(); choose(panel.kind, 'event')
                choose(panel.floor, None); choose(panel.node_type, None)
                panel.search.setText(catalog._event(identity)['title'])
                index = next(i for i, entry in enumerate(panel.entries)
                    if entry['kind'] == 'event' and entry['record']['id'] == identity)
                panel.list.setCurrentRow(index); tabs.setCurrentWidget(panel)
                require(panel.entries[index]['record']['id'] == identity, 'exact_event_identity_selected')

            def reader(widget):
                cursor = widget.textCursor()
                return {'text': text_sha(widget.toPlainText()), 'anchor': cursor.anchor(),
                    'position': cursor.position(), 'selected': cursor.selectedText(),
                    'vertical': widget.verticalScrollBar().value(),
                    'horizontal': widget.horizontalScrollBar().value()}

            def parent_state():
                return {'key': panel.list.selected_key(), 'tab': panel.reading_tabs.currentIndex(),
                    'scene_filter': panel.event_scene_filter.currentData(),
                    'choice_filter': panel.event_choice_filter.currentData(),
                    'stage_id': panel.event_stage.currentData(),
                    'stage_token': deepcopy(panel.event_stage.currentData(role)),
                    'search': panel.search.text(), 'search_cursor': panel.search.cursorPosition(),
                    'search_selection_start': panel.search.selectionStart(),
                    'search_selection': panel.search.selectedText(),
                    'player': reader(panel.player_detail), 'technical': reader(panel.detail)}

            def icon_empty():
                pixmap = dialog.icon.pixmap()
                return not dialog.icon.isVisible() and (pixmap is None or pixmap.isNull())

            def dialog_state():
                pixmap = dialog.icon.pixmap()
                return {'event_id': dialog.event_id, 'scope_key': deepcopy(dialog.scope_key),
                    'choice_key': dialog.choice.currentData(), 'tab': dialog.reading_tabs.currentIndex(),
                    'details_identity': deepcopy(dialog._details_identity),
                    'icon_visible': dialog.icon.isVisible(),
                    'icon_size': None if pixmap is None or pixmap.isNull() else [pixmap.width(), pixmap.height()],
                    'item': reader(dialog.item_text), 'choice': reader(dialog.choice_text),
                    'source': reader(dialog.source_text)}

            def click_visible(button, owner, label):
                gui.processEvents()
                rect = QRect(button.mapTo(owner, QPoint(0, 0)), button.size())
                require(button.isVisible() and button.isEnabled() and not button.visibleRegion().isEmpty()
                    and owner.rect().contains(rect), label + '_visible_enabled_inside_actual_client')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton, pos=button.rect().center())

            def prime(widget):
                gui.processEvents()
                require(widget.verticalScrollBar().maximum() > 0 and len(widget.toPlainText()) > 16,
                    'real_existing_document_has_nonzero_scroll_range')
                cursor = widget.textCursor(); cursor.setPosition(5)
                cursor.setPosition(16, QTextCursor.MoveMode.KeepAnchor); widget.setTextCursor(cursor)
                widget.verticalScrollBar().setValue(max(1, widget.verticalScrollBar().maximum() // 2))
                require(widget.verticalScrollBar().value() > 0 and bool(widget.textCursor().selectedText()),
                    'real_nonzero_scroll_and_nonempty_document_selection')

            def save_image(name, widget, kind):
                isolated(); handle = native(widget, kind)
                path = destination.with_name(destination.stem + '-' + name + '.png')
                if path.exists():
                    raise FileExistsError('First image must not be overwritten')
                pixels = widget.grab(); require(not pixels.isNull(), 'actual_own_window_pixels')
                require(pixels.save(str(path), 'PNG'), 'actual_own_window_PNG_saved')
                images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': handle})

            def close_owned_windows():
                if dialog is not None:
                    dialog.close()
                window.close()

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                        'traceback': traceback.format_exc()}
                done = False; close_owned_windows(); gui.exit(1)

            def later(callback, delay=200):
                def guarded():
                    try:
                        isolated(); callback()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def begin():
                nonlocal parent_saved
                event(EVENT); panel.reading_tabs.setCurrentWidget(panel.detail)
                gui.processEvents(); prime(panel.detail); panel.search.setSelection(0, 2)
                parent_saved = parent_state()
                require(panel.documented_item_window is None, 'item_dialog_not_precreated_before_real_parent_entry')
                require(panel.documented_item_button.isVisible(), 'exact_informant_event_shows_item_entry')
                require(panel.event_choice_filter.currentData() is None,
                    'parent_default_filter_does_not_implicitly_choose_documented_item')
                save_image('parent-entry', window, 'parent')
                click_visible(panel.documented_item_button, window, 'actual_parent_documented_item_QTest_click')
                later(check_opened)

            def check_opened():
                nonlocal dialog
                dialog = panel.documented_item_window
                require(dialog is not None and dialog.parent() is panel,
                    'actual_main_entry_constructed_and_retained_owned_item_dialog')
                parent_handle = native(window, 'parent'); dialog_handle = native(dialog, 'dialog')
                require(parent_handle['hwnd'] != dialog_handle['hwnd'], 'parent_and_dialog_have_distinct_owned_HWNDs')
                native_observations.extend([parent_handle, dialog_handle])
                require(dialog.event_id == EVENT and dialog.scope_key == panel.list.selected_key(),
                    'dialog_scope_is_exact_actual_parent_event_key')
                require(dialog.choice.count() == 1 and dialog.choice.currentIndex() == -1
                    and dialog.choice.currentData() is None and dialog._details_identity is None
                    and not dialog.open_item_button.isEnabled() and icon_empty(),
                    'default_dialog_has_one_reference_but_no_choice_icon_or_opened_item')
                require(dialog.choice.itemData(0) == REFERENCE,
                    'only_alpha_item_uses_exact_complete_event_scene_choice_item_identity')
                require('尚未手动打开' in dialog.item_text.toPlainText(),
                    'opening_main_dialog_does_not_automatically_open_item')
                require(parent_state() == parent_saved, 'opening_item_dialog_preserves_parent_reading_state')
                choose(dialog.choice, REFERENCE)
                require(dialog.open_item_button.isEnabled() and dialog._details_identity is None and icon_empty(),
                    'selecting_alpha_enables_manual_button_without_automatic_item_or_icon')
                require('我受雇于梅兰德' in dialog.choice_text.toPlainText()
                    and '部署费用变化是物品用途' in dialog.choice_text.toPlainText()
                    and '不是本节点的即时资源费用' in dialog.choice_text.toPlainText(),
                    'choice_reader_distinguishes_item_usage_from_immediate_node_cost')
                click_visible(dialog.open_item_button, dialog, 'actual_item_description_QTest_click')
                later(check_item)

            def check_item():
                require(dialog._details_identity == (EVENT, dialog.scope_key, REFERENCE)
                    and dialog.reading_tabs.currentWidget() is dialog.item_text,
                    'real_manual_button_opens_exact_full_identity_item_reader')
                require(dialog.icon.isVisible() and not dialog.icon.pixmap().isNull(),
                    'actual_source_item_icon_is_visible_and_nonempty')
                ref = dialog.packet['items'][0]; icon = ref['icon_reference']
                require(icon['item_id'] == ITEM and icon['icon_id'] == ITEM
                    and before[icon['file']] == icon['sha256'],
                    'shown_icon_is_bound_to_exact_documented_alpha_item_bytes')
                expected = QPixmap(str(ROOT / icon['file'])).scaledToWidth(
                    104, Qt.TransformationMode.SmoothTransformation)
                require(not expected.isNull() and dialog.icon.pixmap().toImage() == expected.toImage(),
                    'actual_dialog_pixmap_matches_exact_fixed_source_icon_scaled_image')
                text = dialog.item_text.toPlainText()
                require(all(word in text for word in ('沙盘α · 收藏品', '【用途】', '【物品说明】',
                    '【物品条目的解锁说明】', '我方单位部署费用+2', '沙盘β',
                    '来自梅兰德基金会', '完成游戏结局', '不等于本事件的完整出现条件',
                    '本账号是否解锁仍未确认', '数量、实际领取和是否持有：尚未确认')),
                    'player_item_reader_has_chinese_usage_description_unlock_and_actual_unknowns')
                require(not any(value in text for value in ('rogue_6_', 'community_group_', 'https://')),
                    'default_item_reader_has_no_raw_identifiers_or_source_URLs')
                require(ref['quantity_reference'] is None and ref['actual_reward'] is None
                    and ref['actual_selectable'] is None and ref['source_scene_link_verified'] is False
                    and ref['original_item_pointer_present'] is False and ref['original_choice_entry_bound'] is False,
                    'manual_reading_does_not_upgrade_original_entry_typed_grant_quantity_or_eligibility')
                raw_choice = catalog._event(EVENT)['scenes'][0]['choices'][0]
                require(raw_choice['key'] == CHOICE and raw_choice['game_choice_ids'] == [],
                    'existing_original_choice_identity_gap_is_retained_not_filled_from_item_document')
                read_observations.append({'reference_id': REFERENCE, 'icon_file': icon['file'],
                    'icon_sha256': icon['sha256'], 'actual_reward': None, 'actual_quantity': None,
                    'actual_selectable': None, 'original_entry_bound': False})
                save_image('alpha-item-description', dialog, 'dialog')
                later(prime_refresh)

            def prime_refresh():
                nonlocal reading_saved
                dialog.reading_tabs.setCurrentWidget(dialog.source_text); prime(dialog.source_text)
                reading_saved = dialog_state(); later(refresh_once)

            def refresh_once():
                nonlocal refresh_rounds
                panel.refresh(); dialog.refresh_reference(); gui.processEvents()
                require(dialog_state() == reading_saved,
                    'same_scope_periodic_refresh_retains_choice_tab_details_icon_text_selection_and_nonzero_scroll')
                require(parent_state() == parent_saved,
                    'same_scope_periodic_refresh_preserves_parent_filter_search_selection_tab_and_reading')
                refresh_rounds += 1
                if refresh_rounds < 3:
                    later(refresh_once)
                else:
                    later(check_source_failure)

            def check_source_failure():
                source_root = temporary / 'public-source-clone'
                manifest_raw = (ROOT / MANIFEST).read_bytes(); manifest = json.loads(manifest_raw)
                for relative in [MANIFEST, *manifest['files']]:
                    source = ROOT / relative; target = source_root / relative
                    require(source.is_file() and not source.is_symlink()
                        and source.resolve().is_relative_to(ROOT),
                        'negative_fixture_copies_only_selected_regular_public_manifest_members')
                    target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
                cloned_manifest = source_root / MANIFEST; original_manifest = cloned_manifest.read_bytes()
                require(sha(cloned_manifest) == before[MANIFEST],
                    'temporary_source_clone_manifest_starts_with_exact_public_bytes')
                with patch.object(results, 'ROOT', source_root):
                    require(results.source_data() is not None,
                        'temporary_complete_public_source_clone_validates_before_damage')
                    try:
                        cloned_manifest.write_bytes(original_manifest + b' ')
                        dialog.refresh_reference()
                        require(dialog.choice.count() == 0 and dialog.choice.currentData() is None
                            and dialog.packet is None and dialog._details_identity is None
                            and dialog._view_key is None and not dialog.open_item_button.isEnabled() and icon_empty(),
                            'real_source_hash_failure_clears_choice_old_identity_button_and_icon')
                        require(all('已清除' in widget.toPlainText() and '沙盘α' not in widget.toPlainText()
                            for widget in (dialog.item_text, dialog.choice_text, dialog.source_text)),
                            'source_failure_clears_all_three_old_reading_pages')
                        save_image('source-invalidated', dialog, 'dialog')
                    finally:
                        cloned_manifest.write_bytes(original_manifest)
                    require(sha(cloned_manifest) == before[MANIFEST],
                        'temporary_source_restored_from_true_original_manifest_bytes')
                    dialog.refresh_reference()
                    require(dialog.choice.count() == 1 and dialog.choice.currentIndex() == -1
                        and dialog.choice.currentData() is None and dialog._details_identity is None
                        and not dialog.open_item_button.isEnabled() and icon_empty(),
                        'source_recovery_does_not_automatically_restore_choice_icon_or_opened_item')
                    require('尚未手动打开' in dialog.item_text.toPlainText(),
                        'source_recovery_does_not_reopen_stale_item_description')
                later(check_changed_event)

            def check_changed_event():
                choose(dialog.choice, REFERENCE)
                click_visible(dialog.open_item_button, dialog, 'reopen_exact_item_before_event_change_QTest_click')
                require(dialog._details_identity is not None and dialog.icon.isVisible(),
                    'event_change_negative_fixture_starts_from_real_opened_item')
                event('community_group_014')
                require(not panel.documented_item_button.isVisible() and dialog.event_id is None
                    and dialog.scope_key is None and dialog.choice.count() == 0
                    and dialog._details_identity is None and not dialog.open_item_button.isEnabled()
                    and icon_empty(), 'different_parent_event_clears_scope_choice_item_and_icon')
                require(all('沙盘α' not in widget.toPlainText()
                    for widget in (dialog.item_text, dialog.choice_text, dialog.source_text)),
                    'different_event_clears_all_three_old_item_pages')
                event(EVENT)
                click_visible(panel.documented_item_button, window, 'return_main_entry_QTest_click')
                require(panel.documented_item_window is dialog and dialog.choice.currentData() is None
                    and dialog._details_identity is None and icon_empty()
                    and not dialog.open_item_button.isEnabled(),
                    'return_to_informant_reuses_dialog_without_restoring_old_choice_or_item')
                later(finish)

            def finish():
                nonlocal done
                native_observations.extend([native(window, 'parent'), native(dialog, 'dialog')])
                require(window.run.state == initial_run, 'manual_reading_never_changes_temporary_run_memory')
                require(catalog.event_reward_options(EVENT) == typed_before,
                    'item_reading_does_not_change_existing_typed_reward_query_values')
                require(refresh_rounds == 3, 'three_actual_same_scope_UI_refresh_rounds_completed')
                require(len(images) == 3, 'three_actual_entry_item_and_invalidation_PNGs_saved')
                require(bound_files() == before, 'selected_public_sources_stable_before_completion')
                observations.append({'documented_item_reads': read_observations,
                    'same_scope_refresh_rounds': refresh_rounds, 'default_choice': None,
                    'actual_game_choice': None, 'actual_inventory': None, 'actual_quantity': None,
                    'actual_item_active': None, 'original_entry_bound': False,
                    'old_typed_reward_source_sha256': before['rouge/data/node-reward-reference.json'],
                    'same_event_typed_reward_query_unchanged_during_reading': True,
                    'source_failure_is_only_an_explicit_temporary_public_clone_negative_fixture': True})
                done = True

            def close_deadline():
                nonlocal failure
                if not done and failure is None:
                    failure = {'type': 'TimeoutError', 'message': 'New UI checks not completed before deadline'}
                close_owned_windows()

            later(begin, 500); QTimer.singleShot(max(30000, args.visible_ms), close_deadline)
            qt_exit = gui.exec()
            closed = not window.isVisible() and (dialog is None or not dialog.isVisible())
            if qt_exit != 0 or not closed or not done:
                if failure is None:
                    failure = {'type': 'RuntimeError', 'message': 'Fixture checks/Qt/owned windows not closed'}
            if failure is None:
                isolated()
            after = bound_files()
            if before != after and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Selected public sources changed through actual closure'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    report = {'section': 295, 'kind': 'isolated_native_windows_documented_choice_item_reading',
        'passed': done and failure is None, 'failure': failure, 'started_at': started,
        'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(),
        'qpa': qpa, 'qt_exit_code': qt_exit, 'verification_window_closed': closed,
        'checks': checks, 'unique_checks': len(checks),
        'successful_assertion_executions_including_repeated_guards': executions,
        'requested_parent_client_size': list(SIZE), 'minimum_dialog_client_size': [850, 650],
        'native_observations': native_observations, 'screenshots': images, 'screenshot_count': len(images),
        'public_observations': observations, 'source_sha256_before': before, 'source_sha256_after': after,
        'source_guard_is_selected_not_all_transitive_dependencies': True, 'temporary_state_root': True,
        'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
        'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
        'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
        'external_entrypoints_blocked_before_original_call': True,
        'original_project_window_operated_or_restarted': False,
        'actual_process_termination_verified_by_this_script': False,
        'owned_supervisor_exit_and_cleanup_required_separately': True,
        'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID': True,
        'scope': 'Real MainWindow informant entry and manual documented alpha-item icon, usage, description and unlock reading; default unselected, three same-scope reader refreshes, actual public-source-clone invalidation and cross-event clearing. No typed grant, original-choice identity repair, inventory or qualification inference; no full rerun.'}
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
