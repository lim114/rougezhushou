"""Native ordinary-page non-event source exercise; cache preparation is not execution."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_non_event_origins as model, expansion_reference as version
    from rouge import current_recruit_tickets as recruit, current_rest_travel as rest
    for provider in (model, version, recruit, rest):
        names.add(provider.MANIFEST)
        names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/verify_current_non_event_origins_window_363.py',
                  'scripts/build_current_non_event_origins_363.py', 'scripts/verify_full_available.py',
                  'tests/test_current_non_event_origins_363.py', 'tests/test_current_non_event_origins_view_363.py'))
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=300000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite actual native evidence')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks, images, readings, source_reads, item_reads, reverse_reads, refreshes = [], [], [], [], [], [], []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False

    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)

    def forbidden(name):
        def fail(*args, **kwargs):
            calls[name] += 1; raise AssertionError('Forbidden real operation: ' + name)
        return fail

    try:
        before = bound_files()
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_non_event_origins as model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge363-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for name, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                                'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, name, value))
            backend = app_module.DesktopBackend
            stack.enter_context(patch.object(app_module, 'DesktopBackend',
                lambda _path, callback: backend(temporary / 'chat', callback)))
            stack.enter_context(patch.object(app_module, 'list_game_windows', return_value=[]))
            for name, key in (('connect', 'game_connect'), ('capture', 'capture'), ('next_frame', 'next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, name, side_effect=forbidden(key)))
            for name, key in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(backend, name, side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = app_module.MainWindow(); window.resize(1240, 880)
            window.setWindowTitle('第363节 · 具名物品与非事件来源（公开隔离验收）')
            window.show(); gui.processEvents(); tabs = window.centralWidget()
            state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)

            def native(widget):
                owner = widget.window(); hwnd = int(owner.winId()); pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'visible_owned_native_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [owner.width(), owner.height()]}

            def shot(label, widget):
                gui.processEvents(); path = dest.with_name('window-' + label + '.png')
                if path.exists(): raise FileExistsError('Never overwrite a native screenshot')
                require(widget.grab().save(str(path), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest(), 'native': native(widget)})

            def reading(widget):
                c = widget.textCursor()
                return {'anchor': c.anchor(), 'position': c.position(), 'selection': c.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}

            def choose(combo, value):
                index = combo.findData(value); require(index >= 0, 'actual_filter_branch_value_exists')
                combo.setCurrentIndex(index); gui.processEvents()

            def select(widget, identity):
                item = next((widget.item(i) for i in range(widget.count())
                             if widget.item(i).data(Qt.ItemDataRole.UserRole) == identity), None)
                require(item is not None, 'exact_original_id_list_item_exists')
                widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())
                gui.processEvents()
                require(widget.currentItem() is not None and widget.currentItem().data(Qt.ItemDataRole.UserRole) == identity,
                        'real_exact_item_mouse_selection')

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'actual_usable_reference_button')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()

            def ordinary(category):
                page = window.reference_panel(category); gui.processEvents()
                require(page is not None and tabs.currentWidget() is page and page.category.currentData() == category,
                        'actual_ordinary_category_page_opened')
                page.search.clear()
                if category == 'relics': choose(page.item_kind, 'RELIC')
                return page

            def exercise():
                nonlocal done, failure
                dialog = None
                try:
                    common = ordinary('squads')
                    require(common.named_sources_button.isVisible() and common.named_sources_button.isEnabled(),
                            'ordinary_exploration_squad_source_directory_entry')
                    shot('ordinary-squad-entry', common)
                    click(common.named_sources_button); dialog = common.named_sources_dialog; panel = dialog.panel
                    require(dialog.isVisible() and panel.entries.count() == 10 and panel.identity is None and panel.source_request is None,
                            'actual_directory_all10_manual_unselected')
                    require((panel.kind.count(), panel.timing.count()) == (3, 3), 'separate_source_kind_and_timing_branches')
                    require(not panel.source_button.isVisible() and not panel.item_button.isVisible(), 'overview_has_no_invented_origin_target')
                    shot('ten-source-directory', panel)
                    prior = dialog; click(common.named_sources_button); dialog = common.named_sources_dialog; panel = dialog.panel
                    require(dialog is not prior and dialog.isVisible() and not prior.isVisible() and panel.identity is None,
                            'repeated_directory_entry_closes_previous_owned_window')
                    originals = deepcopy(model.reference()['rows'])
                    require(len(originals) == 10 and sum(r['kind'] == 'squad' for r in originals) == 8
                            and sum(r['kind'] == 'relic' for r in originals) == 2, 'complete_eight_squad_two_mark_fixed_scope')
                    for row in originals:
                        select(panel.entries, row['id']); text = panel.player.toPlainText()
                        require(panel.identity == row['id'] and panel.result['selected'] == row, 'every_exact_source_record_selected')
                        require(model.version._plain(row['source_item']['usage']) in text
                                and model.version._plain(row['item']['usage']) in text, 'all10_own_full_source_and_item_usage_visible')
                        require(all(panel.result[k] is None for k in ('actual_eligible', 'actual_source_active', 'actual_received',
                                'actual_quantity', 'actual_candidate', 'actual_cultivation', 'actual_cost'))
                                and not panel.result['run_updated'] and not panel.result['calculation_applied'],
                                'all10_actual_eligibility_quantity_recipient_cultivation_unknown')
                        if row['kind'] == 'squad':
                            require(row['time'] == 'initial' and '文献明确：初始携带' in text
                                    and '同名的其它档位不能自动继承' in text, 'eight_source_timing_and_exact_grade_boundaries')
                        else:
                            require(row['time'] == 'unspecified' and '具体时点尚未核验' in text and '水月主题' in text
                                    and '首次招募即相当于已进阶' in text, 'two_marks_keep_theme_timing_and_direct_promotion_boundaries')
                        if row['source_id'] == 'rogue_6_band_27':
                            require(row['reference_quantity'] == 3 and '不在这里再加1' in text, 'initial_three_not_shop_trigger_plus_one')
                            shot('trade-three-boundary', panel)
                        if row['source_id'] == 'rogue_6_band_26':
                            require(row['reference_quantity'] == 1 and '不加到旅行绒数量里' in text, 'named_travel_item_not_random_pool_sum')
                        if row['source_id'] == 'rogue_6_band_21':
                            require('两个依据分开保留' in text, 'geology_original_pointer_separate_from_documented_start_timing')
                        if row['source_id'] == 'rogue_6_relic_legacy_133': shot('silver-mark-timing-unknown', panel)
                        readings.append({'identity': row['id'], 'source_id': row['source_id'], 'item_id': row['item_id'],
                                         'reference_quantity': row['reference_quantity'], 'documented_time': row['time'],
                                         'actual_quantity': None, 'actual_received': None})
                        click(panel.source_button); child = panel.original_dialog
                        require(child.isVisible() and child.panel.category.currentData() == row['source_category']
                                and child.panel.result['row']['id'] == row['source_id'], 'all10_exact_source_original_readers_opened')
                        source_reads.append({'identity': row['id'], 'category': child.panel.category.currentData(),
                                             'key': child.panel.result['row']['id']})
                        previous = child; click(panel.item_button); child = panel.original_dialog
                        require(not previous.isVisible() and child.isVisible(), 'side_switch_closes_previous_original_reader')
                        if row['item_category'] == 'recruit_tickets':
                            stars = 5 if row['source_id'] == model.RELICS[0] else 6
                            require(child.panel.ticket_id == row['item_id'] and child.panel.entries.count() == 47
                                    and child.panel.result['selected']['stars'] == [stars]
                                    and child.panel.result['actual_recruited'] is None, 'two_mark_items_open_exact_actual_random_promoted_ticket')
                            if stars == 6: shot('exact-six-star-random-ticket', child.panel)
                        else:
                            require(child.panel.category.currentData() == row['item_category']
                                    and child.panel.result['row']['id'] == row['item_id'], 'eight_exact_original_item_readers_opened')
                        item_reads.append({'identity': row['id'], 'category': row['item_category'], 'key': row['item_id']})
                        child.close(); gui.processEvents()
                    require({r['identity'] for r in readings} == {r['id'] for r in originals}
                            and len(source_reads) == len(item_reads) == 10, 'ten_complete_source_item_readings_completed')
                    choose(panel.kind, 'relic'); choose(panel.timing, 'initial')
                    require(panel.entries.count() == 0 and panel.identity is None, 'marks_not_listed_as_proven_initial_rewards')
                    choose(panel.timing, 'unspecified'); require(panel.entries.count() == 2, 'unknown_timing_marks_separate_branch')
                    choose(panel.kind, None); choose(panel.timing, 'initial'); require(panel.entries.count() == 8, 'eight_initial_squad_sources_separate_branch')
                    choose(panel.timing, None); panel.search.setText('枯苔藓球')
                    require(panel.entries.count() == 1 and panel.source_request is None, 'exact_chinese_item_search_not_inherited_reverse_request')
                    select(panel.entries, next(r['id'] for r in originals if r['source_id'] == 'rogue_6_band_27'))
                    click(panel.item_button); previous = panel.original_dialog
                    require(common.refresh_reference() and panel.search.text() == '枯苔藓球' and previous.isVisible(),
                            'ordinary_parent_refresh_preserves_changed_search_selected_item_child')
                    dialog.close(); gui.processEvents()

                    # Both sides for eight squads; the two marks have real ordinary source items.
                    for row in originals:
                        destinations = [(row['source_category'], row['source_id'])]
                        if row['kind'] == 'squad': destinations.append((row['item_category'], row['item_id']))
                        for category, identity in destinations:
                            common = ordinary(category); select(common.entries, identity)
                            require(common.named_sources_item_button.isVisible(), 'ordinary_exact_source_or_item_reverse_entry_visible')
                            click(common.named_sources_item_button); dialog = common.named_sources_dialog; panel = dialog.panel
                            request = {'category': category, 'key': identity}
                            require(dialog.isVisible() and panel.identity == row['id'] and panel.source_request == request
                                    and panel.result['selected'] == row, 'all18_reverse_entries_keep_exact_category_id_and_source_record')
                            reverse_reads.append({'identity': row['id'], 'request': request})
                            dialog.close(); gui.processEvents()
                    require(len(reverse_reads) == 18, 'eight_source_item_pairs_plus_two_real_mark_source_entries_completed')
                    common = ordinary('squads'); select(common.entries, 'rogue_6_band_4')
                    require(not common.named_sources_item_button.isVisible() and not common.open_named_sources(from_item=True),
                            'same_name_logistics_base_does_not_borrow_upgraded_source')

                    # Keep an exact reverse request and two nonzero readings through the true parent.
                    trade = next(r for r in originals if r['source_id'] == 'rogue_6_band_27')
                    common = ordinary('scrap'); require(common.named_sources_button.isVisible(), 'ordinary_items_directory_entry_visible')
                    select(common.entries, trade['item_id']); click(common.named_sources_item_button)
                    dialog = common.named_sources_dialog; panel = dialog.panel
                    shot('exact-scrap-reverse', panel); click(panel.source_button); child = panel.original_dialog
                    dialog.resize(800, 470); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(4); cursor.setPosition(20, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'two_actual_nonzero_reading_ranges')
                        scroll.setValue(min(4, scroll.maximum())); prior_reading = reading(reader)
                        identity, tab, request, filters = panel.identity, panel.tabs.currentIndex(), deepcopy(panel.source_request), panel._filters()
                        require(common.refresh_reference(), 'actual_item_parent_refresh_for_reverse_selection'); gui.processEvents()
                        require(reading(reader) == prior_reading and panel.identity == identity and panel.tabs.currentIndex() == tab
                                and panel.source_request == request and panel._filters() == filters and child.isVisible()
                                and child.panel.result['row']['id'] == trade['source_id'],
                                'two_nonzero_readings_exact_reverse_request_selection_tab_and_source_child_preserved')
                        refreshes.append({'reader': 'player' if reader is panel.player else 'technical',
                                          'before': prior_reading, 'after': reading(reader), 'request': request})
                    valid_target = model.locate('scrap', trade['item_id'])
                    forged = deepcopy(valid_target); forged['identity'] = originals[0]['id']
                    require(not panel.open_target(forged) and panel.identity == trade['id'], 'forged_cross_original_reverse_target_refused')

                    damaged = temporary / 'damaged'; manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((model.ROOT / name).read_bytes())
                    path = damaged / model.DATA; raw = path.read_bytes()
                    with patch.object(model, 'ROOT', damaged):
                        path.write_bytes(raw + b'x'); require(common.refresh_reference(), 'independent_item_parent_survives_source_loss')
                        gui.processEvents()
                        require(panel.result is None and panel.identity is None and panel.source_request is None
                                and panel.source_identity is None and panel.entries.count() == 0
                                and panel.player.toPlainText() == '' and panel.technical.toPlainText() == ''
                                and not panel.source_button.isEnabled() and not panel.item_button.isEnabled() and not child.isVisible(),
                                'actual_bad_member_clears_list_readers_requests_both_links_and_original_child')
                        shot('source-loss', panel); path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.identity is None and panel.source_request is None
                                and panel.entries.currentItem() is None and panel.entries.count() == 10,
                                'source_recovery_requires_manual_record_and_does_not_restore_old_reverse_request')
                    dialog.close(); gui.processEvents()

                    # Both original-reader families own their deeper readers and close with the parent.
                    silver = next(r for r in originals if r['source_id'] == 'rogue_6_relic_legacy_133')
                    common = ordinary('relics'); select(common.entries, silver['source_id']); click(common.named_sources_item_button)
                    dialog = common.named_sources_dialog; panel = dialog.panel; click(panel.item_button)
                    ticket = panel.original_dialog; require(ticket.panel.open_event('rest'), 'actual_random_ticket_nested_document_opened')
                    nested = ticket.panel.event_dialog; gui.processEvents()
                    require(all(d.isVisible() for d in (dialog, ticket, nested)), 'three_level_exact_ticket_original_tree_visible')
                    window.reference_panel('squads'); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, ticket, nested)), 'ordinary_page_switch_closes_ticket_original_tree')
                    common = ordinary('relics'); select(common.entries, silver['source_id']); click(common.named_sources_item_button)
                    dialog = common.named_sources_dialog; panel = dialog.panel; click(panel.source_button)
                    original = panel.original_dialog
                    require(original.panel.open_recruit_tickets(), 'actual_relic_original_nested_recruit_reader_opened')
                    recruit = original.panel.tickets_dialog; require(recruit.panel.open_event('rest'), 'actual_relic_original_nested_document_opened')
                    nested = recruit.panel.event_dialog; gui.processEvents()
                    require(all(d.isVisible() for d in (dialog, original, recruit, nested)), 'four_level_exact_relic_original_tree_visible')
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_calculation_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero')
                    require(len(images) == 7, 'seven_actual_native_screenshots_recorded')
                    native(window); window.close(); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, original, recruit, nested)), 'actual_MainWindow_closes_complete_source_original_tree')
                    done = True; gui.exit(0)
                except BaseException as error:
                    failure = failure or {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)

            def timeout():
                nonlocal failure
                if not done:
                    failure = failure or {'type': 'TimeoutError', 'message': f'Native exercise did not finish within configured {args.visible_ms} ms', 'traceback': None}
                    window.close(); gui.exit(2)

            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, timeout); exitcode = gui.exec()
            require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    try:
        after = bound_files()
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    result = {'section': 363, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'all10_readings': readings,
              'all10_source_originals': source_reads, 'all10_item_originals': item_reads,
              'ordinary_reverse_entry_observations': reverse_reads,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True,
              'private_contents_read_copied_or_restored': False, 'game_operated': False, 'chat_sent': False,
              'current_server_or_original_runtime_validated': False,
              'recruit_directory_reverse_UI_not_part_of_this_adapter': True,
              'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
