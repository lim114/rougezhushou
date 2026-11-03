"""Actual common-event current catalogue, with temporary public state only."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_event_directory as model, expansion_reference as version
    for provider in [model, version, *model.providers().values()]:
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/build_current_event_directory_372.py', 'scripts/verify_current_event_directory_window_372.py',
                  'tests/test_current_event_directory_372.py', 'tests/test_current_event_directory_view_372.py', 'scripts/verify_full_available.py'))
    return {n: sha256((ROOT / n).read_bytes()).hexdigest() for n in sorted(names)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=180000); args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite an actual receipt')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks = []; images = []; observations = []; filters = []; refreshes = []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False

    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)

    def forbidden(name):
        def fail(*a, **kw): calls[name] += 1; raise AssertionError('Forbidden real operation: ' + name)
        return fail

    try:
        before = bound_files()
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_event_directory as model
        from tests.test_current_event_directory_372 import clone
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge372-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for name, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                                'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, name, value))
            backend = app_module.DesktopBackend
            stack.enter_context(patch.object(app_module, 'DesktopBackend', lambda _path, callback: backend(temporary / 'chat', callback)))
            stack.enter_context(patch.object(app_module, 'list_game_windows', return_value=[]))
            for name, key in (('connect', 'game_connect'), ('capture', 'capture'), ('next_frame', 'next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, name, side_effect=forbidden(key)))
            for name, key in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(backend, name, side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = app_module.MainWindow(); window.resize(1260, 900); window.setWindowTitle('第372节 · 当前节点事件目录（公开隔离验收）')
            window.show(); gui.processEvents(); state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)
            common = None; dialog = None; panel = None

            def native(widget):
                owner = widget.window(); hwnd = int(owner.winId()); pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(), 'visible_owned_native_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [owner.width(), owner.height()]}

            def shot(label, widget):
                gui.processEvents(); path = dest.with_name('window-' + label + '.png')
                if path.exists(): raise FileExistsError('Never overwrite an actual image')
                require(widget.grab().save(str(path), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest(), 'native': native(widget)})

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'visible_enabled_button_before_actual_mouse_click')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()

            def select(widget, key):
                rows = [i for i in range(widget.count()) if widget.item(i).data(Qt.ItemDataRole.UserRole) == key]
                require(len(rows) == 1, 'unique_exact_list_target')
                item = widget.item(rows[0]); widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center()); gui.processEvents()
                require(widget.currentItem().data(Qt.ItemDataRole.UserRole) == key, 'actual_mouse_selects_exact_list_target')

            def choose(combo, value):
                index = combo.findData(value); require(index >= 0, 'exact_filter_value_exists')
                combo.setCurrentIndex(index); gui.processEvents(); require(combo.currentData() == value, 'real_combobox_filter_changed')

            def ordinary():
                nonlocal common, dialog, panel
                common = window.reference_panel('scenes'); gui.processEvents()
                require(window.centralWidget().currentWidget() is common and common.full_catalog and common.scope.isHidden(), 'ordinary_events_page_not_separate_version_tab')
                require(common.event_directory_button.isVisible(), 'ordinary_events_page_exposes_current_catalogue')
                click(common.event_directory_button); dialog = common.event_directory_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.result is not None, 'actual_owned_event_directory_visible')
                return panel

            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(), 'scroll': widget.verticalScrollBar().value()}

            def exercise():
                nonlocal done, failure, dialog, panel
                try:
                    ordinary(); require(panel.events.count() == 39 and panel.events.currentItem() is None and not panel.open_button.isEnabled(), '39_current_events_without_default_selection')
                    rows = model.packet()['data']['rows']
                    require(len(rows) == 39 and sum(len(r['catalogue_groups']) for r in rows) == 38, '38_legacy_groups_preserved_in39_current_readers')
                    require(sum(len(r['entries']) for r in rows) == 277 and all(e['choice_id'] in r['scenes'][e['scene_id']]['choice_ids'] for r in rows for e in r['entries']), 'all277_exact_dialogue_choice_memberships_checked_not277_windows')
                    require(all(r['actual_eligible'] is None and r['actual_node'] is None for r in rows), 'no_event_marked_actually_eligible')
                    shot('overview', panel)
                    panel.query.setText('生命蓝图'); gui.processEvents()
                    require(panel.events.count() == 1 and '制图桌' in panel.events.item(0).text(), 'search_in_exact_related_item_hint_not_title_only')
                    panel.query.clear(); choose(panel.node_type, 'unclassified')
                    unclassified = [panel.events.item(i).text() for i in range(panel.events.count())]
                    require(panel.events.count() == 4 and all(any(t in s for s in unclassified) for t in ('安眠一隅', '大红按钮', '制图桌', '手术祭坛')), 'four_unclassified_events_not_forced_into_encounter')
                    shot('unclassified', panel); choose(panel.node_type, None)
                    for topic, _ in model.TOPICS:
                        choose(panel.topic, topic); values = [panel.events.item(i).data(Qt.ItemDataRole.UserRole) for i in range(panel.events.count())]
                        require(values and all(topic in r['topics'] for r in panel.result['rows']), 'all_eight_literal_topic_filters_keep_only_cited_content')
                        filters.append({'topic': topic, 'event_ids': values, 'actual_eligible': None})
                    choose(panel.topic, None); panel.query.setText('笼控器'); gui.processEvents()
                    require(any('黑诞' in panel.events.item(i).text() for i in range(panel.events.count())), 'search_across_options_preserves_required_item_context')
                    shot('item-search', panel); panel.query.clear()
                    seen = set()
                    for row in rows:
                        if row['reader'] in seen: continue
                        seen.add(row['reader']); select(panel.events, row['id']); entry = row['entries'][-1]; select(panel.entries, entry['key']); click(panel.open_button); child = panel.event_dialog
                        require(child is not None and child.isVisible(), 'all21_reader_kinds_open_owned_native_windows')
                        require((child.panel.event_id, child.panel.scene_id, child.panel.choice_id) == (row['event_id'], entry['scene_id'], entry['choice_id']), 'all21_exact_event_scene_choice_targets_without_name_substitution')
                        require(child.panel.result.get('actual_eligible') is None and child.panel.result.get('run_updated') is False, 'reader_open_does_not_claim_live_eligibility_or_update_run')
                        observations.append({'reader': row['reader'], 'event_id': row['event_id'], 'scene_id': child.panel.scene_id, 'choice_id': child.panel.choice_id, 'native': native(child)})
                    require(len(seen) == 21 and len(observations) == 21, 'exactly21_distinct_reader_families_exercised')
                    select(panel.events, 'flows321:button'); row = panel.result['selected']; entry = next(e for e in row['entries'] if e['choice_id'] == 'choice_ro6_end4_3')
                    select(panel.entries, entry['key']); click(panel.open_button); child = panel.event_dialog
                    require(child.panel.battle_button.isVisible() and child.panel.battle_button.isEnabled(), 'big_button_exact_full_dialogue_has_existing_fixed_battle_entry')
                    click(child.panel.battle_button); battle = child.panel.battle_dialog
                    require(battle is not None and battle.isVisible() and battle.panel.stage_id == 'ro6_s_1', 'big_button_existing_exact_fixed_map_reference_opens_without_game')
                    shot('button-dialogue', child.panel); select(panel.events, 'rest:三重身')
                    require(not child.isVisible() and not battle.isVisible() and child.panel.result is None, 'event_change_clears_and_closes_old_flow_battle_tree')
                    require(len(panel.result['selected']['catalogue_groups']) == 3 and '三' in panel.player.toPlainText(), 'three_travel_source_groups_retained_without_guessing_actual_variant')
                    shot('same-name-sources', panel)
                    select(panel.events, 'memory336:memorytree'); row = panel.result['selected']; entry = next(e for e in row['entries'] if e['choice_id'] == 'choice_ro6_normal5_3')
                    select(panel.entries, entry['key']); click(panel.open_button); child = panel.event_dialog
                    require(child.panel.result['declared']['source_key'] is None and child.panel.result['declared']['controller'] is None, 'opening_exact_choice_keeps_item_declarations_unknown')
                    dialog.resize(720, 420); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor(); cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        require(reader.verticalScrollBar().maximum() > 0, 'real_nonzero_scroll_range_for_both_readers')
                        reader.verticalScrollBar().setValue(min(3, reader.verticalScrollBar().maximum())); prior = reading(reader); tab = panel.tabs.currentIndex()
                        require(common.refresh_reference(), 'actual_common_parent_refresh'); gui.processEvents()
                        require(reading(reader) == prior and panel.tabs.currentIndex() == tab and panel.event_id == row['id'] and panel.entry_key == entry['key'], 'both_nonzero_readings_tab_event_choice_kept_after_real_parent_refresh')
                        refreshes.append({'reader': 'player' if reader is panel.player else 'technical', 'before': prior, 'after': reading(reader)})
                    require(panel.event_dialog is child and child.isVisible(), 'parent_refresh_keeps_exact_owned_reader')
                    panel.tabs.setCurrentIndex(0); shot('exact-choice-reading', panel)
                    old = child; panel.query.setText('制图桌'); gui.processEvents()
                    require(not old.isVisible() and old.panel.result is None and panel.event_id is None and panel.entry_key is None, 'search_change_clears_old_choice_and_owned_actual_data')
                    panel.query.clear(); select(panel.events, 'flows321:button'); click(panel.open_button); child = panel.event_dialog
                    damaged = clone(temporary / 'damaged'); path = damaged / model.DATA; raw = path.read_bytes()
                    with patch.object(model, 'ROOT', damaged):
                        path.write_bytes(raw + b'x'); require(common.refresh_reference(), 'ordinary_events_parent_survives_new_directory_source_loss'); gui.processEvents()
                        require(panel.result is None and panel.events.count() == 0 and panel.entries.count() == 0 and panel.technical.toPlainText() == '' and panel.player.toPlainText() == model.UNAVAILABLE and child.panel.result is None and not child.isVisible() and not dialog.isVisible(), 'bad_source_clears_actual_directory_and_all_owned_readers')
                        shot('source-loss', common); path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.event_id is None and panel.events.currentItem() is None and not panel.open_button.isEnabled(), 'source_repair_requires_manual_reselection')
                    ordinary(); select(panel.events, 'flows321:button'); click(panel.open_button); child = panel.event_dialog
                    window.reference_panel('squads'); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and panel.result is None and child.panel.result is None, 'common_page_switch_closes_directory_actual_reader_tree')
                    ordinary(); select(panel.events, 'flows321:button'); click(panel.open_button); child = panel.event_dialog
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_calculation_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero')
                    require(len(images) == 7, 'seven_actual_native_screenshots_recorded'); native(window); window.close(); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and panel.result is None and child.panel.result is None, 'actual_MainWindow_close_clears_and_closes_whole_tree')
                    done = True; gui.exit(0)
                except BaseException as error:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)

            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, lambda: gui.exit(2) if not done else None)
            exitcode = gui.exec(); require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    try: after = bound_files()
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    result = {'section': 372, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None, 'qt_exit_code': exitcode,
              'configured_visible_ms': args.visible_ms, 'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'actual_readings': observations, 'actual_filter_observations': filters,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after, 'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True, 'private_contents_read_copied_or_restored': False,
              'game_operated': False, 'chat_sent': False, 'current_server_or_original_runtime_validated': False,
              'feature_section_published_or_completed_by_this_script': False, 'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
