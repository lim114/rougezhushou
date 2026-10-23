"""Native MainWindow upgrade-ticket exercise; prepared only, not yet executed."""
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
    from rouge import current_upgrade_tickets as model, expansion_reference as version
    from rouge import current_rest_travel as rest, current_recruit_tickets as recruit
    for provider in (model, version, rest, recruit):
        names.add(provider.MANIFEST)
        names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/verify_current_upgrade_tickets_window_360.py',
                  'scripts/build_current_upgrade_tickets_360.py',
                  'scripts/verify_full_available.py',
                  'tests/test_current_upgrade_tickets_360.py',
                  'tests/test_current_upgrade_tickets_view_360.py'))
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite a native receipt')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks, images, observations, source_reads, reverse_reads, refreshes = [], [], [], [], [], []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False

    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)

    def forbidden(name):
        def fail(*args, **kwargs):
            calls[name] += 1
            raise AssertionError('Forbidden real operation: ' + name)
        return fail

    try:
        before = bound_files()
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_upgrade_tickets as model
        gui = QApplication([])
        require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge360-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第360节 · 进阶券范围与准确来源（公开隔离验收）')
            window.show(); gui.processEvents()
            tabs = window.centralWidget(); common = window.reference_panel('relics')
            state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)

            def native(widget):
                owner = widget.window(); hwnd = int(owner.winId())
                pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'visible_owned_native_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [owner.width(), owner.height()]}

            def shot(label, widget):
                gui.processEvents(); path = dest.with_name('window-' + label + '.png')
                if path.exists(): raise FileExistsError('Never overwrite an actual screenshot')
                require(widget.grab().save(str(path), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest(),
                               'native': native(widget)})

            def reading(widget):
                c = widget.textCursor()
                return {'anchor': c.anchor(), 'position': c.position(), 'selection': c.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}

            def choose(combo, value):
                index = combo.findData(value)
                require(index >= 0, 'real_separate_filter_branch_value_exists')
                combo.setCurrentIndex(index); gui.processEvents()

            def select(widget, identity):
                item = next((widget.item(i) for i in range(widget.count())
                             if widget.item(i).data(Qt.ItemDataRole.UserRole) == identity), None)
                require(item is not None, 'exact_original_id_list_item_exists')
                widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())
                gui.processEvents()
                require(widget.currentItem() is not None and widget.currentItem().data(Qt.ItemDataRole.UserRole) == identity,
                        'real_exact_list_item_mouse_selection')

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'actual_usable_reference_button')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()

            def exercise():
                nonlocal done, failure
                dialog = None
                try:
                    bar = tabs.tabBar(); index = tabs.indexOf(common)
                    QTest.mouseClick(bar, Qt.MouseButton.LeftButton, pos=bar.tabRect(index).center()); gui.processEvents()
                    require(tabs.currentWidget() is common, 'actual_MainWindow_common_items_page')
                    require(common.upgrade_tickets_button.isVisible() and common.upgrade_tickets_button.isEnabled(),
                            'ordinary_items_upgrade_directory_entry_visible')
                    shot('common-entry', common)
                    click(common.upgrade_tickets_button); dialog = common.upgrade_tickets_dialog; panel = dialog.panel
                    require(dialog.isVisible() and panel.entries.count() == 18 and panel.ticket_id is None,
                            'actual_common_entry_opens_all18_manual_directory')
                    require((panel.profession.count(), panel.kind.count(), panel.star.count()) == (9, 4, 7),
                            'three_actual_profession_kind_star_branches')
                    require(not panel.source_button.isVisible(), 'overview_does_not_invent_a_source')
                    shot('all18-directory', panel)
                    previous = dialog
                    click(common.upgrade_tickets_button); dialog = common.upgrade_tickets_dialog; panel = dialog.panel
                    require(dialog is not previous and dialog.isVisible() and not previous.isVisible()
                            and panel.entries.count() == 18 and panel.ticket_id is None,
                            'repeated_ordinary_entry_replaces_owned_directory_without_auto_selection')
                    originals = deepcopy(model.reference()['rows'])
                    require(len(originals) == 18 and len({r['name'] for r in originals}) == 10,
                            'eighteen_originals_not_eighteen_independent_names')
                    for row in originals:
                        select(panel.entries, row['id'])
                        text = panel.player.toPlainText(); link = model.destination(row['id'])
                        require(panel.ticket_id == row['id'] and panel.result['selected'] == row,
                                'every_original_id_selected_without_name_merge')
                        require(model.version._plain(row['item']['usage']) in text and all(str(s) + '★' in text for s in row['stars']),
                                'all18_own_usage_and_original_star_ranges_visible')
                        require(panel.source_button.isVisible() == (link is not None),
                                'source_button_only_for_exact_proven_origin')
                        require(all(panel.result[k] is None for k in ('actual_owned', 'actual_candidates', 'actual_eligible',
                                'actual_cost', 'actual_upgraded', 'actual_cultivation')) and not panel.result['run_updated']
                                and not panel.result['calculation_applied'], 'all18_keep_actual_inventory_candidates_cost_cultivation_unknown')
                        observations.append({'id': row['id'], 'name': row['name'], 'kind': row['kind'],
                                             'stars': row['stars'], 'professions': row['professions'], 'source_available': link is not None})
                        if row['relic_origin']:
                            origin = row['relic_origin']; click(panel.source_button); child = panel.source_dialog
                            require(child.isVisible() and child.panel.result['row']['category'] == 'relics'
                                    and child.panel.result['row']['id'] == origin['id'], 'all_eight_full_relic_originals_open_by_exact_id')
                            require(model.version._plain(origin['item']['usage']) in child.panel.player.toPlainText(),
                                    'all_eight_source_readers_contain_their_own_full_usage')
                            require(origin['reference_count'] == 1 and origin['actual_recipient'] is None,
                                    'one_documented_ticket_never_actual_recipient')
                            source_reads.append({'ticket_id': row['id'], 'relic_id': origin['id'], 'name': origin['item']['name'],
                                                 'actual_quantity_received': None, 'actual_recipient': None})
                            if row['id'] == 'rogue_6_upgrade_ticket_pioneer_from_relic':
                                shot('new-training-original', child.panel)
                            child.close(); gui.processEvents()
                        elif link is None:
                            require(not panel.open_source(), 'ordinary_same_name_and_temporary_ticket_do_not_borrow_source')
                            require('不自动借用同名券的来源' in text, 'unproven_source_boundary_visible')
                    require({r['id'] for r in observations} == {r['id'] for r in originals} and len(source_reads) == 8,
                            'all18_and_eight_exact_source_readings_completed')

                    # Exercise actual branch controls, including the 5/6-star boundary.
                    choose(panel.profession, 'PIONEER'); choose(panel.kind, 'relic'); choose(panel.star, 6)
                    require(panel.entries.count() == 1 and panel.ticket_id is None, 'profession_kind_star_intersection_not_actual_candidate')
                    select(panel.entries, 'rogue_6_upgrade_ticket_pioneer_from_relic')
                    require('不证明对应星级' in panel.player.toPlainText(), 'star_range_not_promotion_eligibility')
                    shot('profession-kind-star', panel)
                    choose(panel.profession, None); choose(panel.kind, 'general'); choose(panel.star, 5)
                    require(panel.entries.count() == 2, 'five_star_range_both_general_ticket_originals')
                    choose(panel.star, 6)
                    require(panel.entries.count() == 1 and panel.entries.item(0).data(Qt.ItemDataRole.UserRole) == 'rogue_6_upgrade_ticket_all',
                            'six_star_excludes_five_star_general_ticket')
                    choose(panel.kind, None); choose(panel.star, None)

                    # The rest origin uses its documentary id; never compare it to a native choice id.
                    select(panel.entries, 'rogue_6_upgrade_ticket_all'); click(panel.source_button)
                    child = panel.source_dialog; link = model.destination(panel.ticket_id)
                    require(child.isVisible() and child.panel.source_request == {'category': 'choices', 'key': model.REST_CHOICE}
                            and child.panel.scene_id == link['target']['scene_id'] and child.panel.choice_id == link['target']['choice_id'],
                            'advanced_ticket_exact_rest_document_scene_and_choice')
                    require(link['original_quantity'] is None and child.panel.result['actual_received'] is None,
                            'rest_origin_quantity_and_actual_receipt_remain_unknown')
                    shot('exact-rest-original', child.panel)

                    # Two actual nonzero readings survive the real parent refresh.
                    panel.search.setText('钝爪'); select(panel.entries, 'rogue_6_upgrade_ticket_pioneer_from_relic')
                    require(not child.isVisible(), 'changing_selected_ticket_closes_old_source_reader')
                    click(panel.source_button); child = panel.source_dialog
                    dialog.resize(800, 470); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents()
                        cursor = reader.textCursor(); cursor.setPosition(3)
                        cursor.setPosition(19, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'two_actual_nonzero_reading_ranges')
                        scroll.setValue(min(4, scroll.maximum())); prior = reading(reader)
                        selected, tab, filters = panel.ticket_id, panel.tabs.currentIndex(), panel._filters()
                        require(common.refresh_reference(), 'actual_common_items_parent_refresh')
                        gui.processEvents()
                        require(reading(reader) == prior and panel.ticket_id == selected and panel.tabs.currentIndex() == tab
                                and panel._filters() == filters and child.isVisible()
                                and child.panel.result['row']['id'] == 'rogue_6_relic_assign_1',
                                'two_nonzero_readings_filters_selection_tab_and_exact_child_preserved')
                        refreshes.append({'reader': 'player' if reader is panel.player else 'technical',
                                          'before': prior, 'after': reading(reader), 'ticket': selected, 'filters': filters})

                    # Actual corruption only in a copy of public sources; no private snapshot is read.
                    damaged = temporary / 'damaged'; manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes((model.ROOT / name).read_bytes())
                    path = damaged / model.DATA; raw = path.read_bytes()
                    with patch.object(model, 'ROOT', damaged):
                        path.write_bytes(raw + b'x')
                        require(common.refresh_reference(), 'independent_items_parent_survives_upgrade_source_loss')
                        gui.processEvents()
                        require(panel.result is None and panel.ticket_id is None and panel.source_identity is None
                                and panel.entries.count() == 0 and panel.player.toPlainText() == '' and panel.technical.toPlainText() == ''
                                and not panel.source_button.isEnabled() and not panel.recruit_button.isEnabled() and not child.isVisible(),
                                'actual_damaged_member_clears_old_content_links_and_owned_original')
                        shot('source-loss', panel)
                        path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.ticket_id is None and panel.entries.currentItem() is None,
                                'source_recovery_requires_manual_ticket_selection')

                    # Reverse links are tested only for eight real relic catalog items.
                    # upgradeTickets themselves are not in the existing relics table.
                    dialog.close(); gui.processEvents(); common.search.clear()
                    choose(common.item_kind, 'RELIC')
                    relic_rows = [r for r in originals if r['relic_origin']]
                    for row in relic_rows:
                        origin = row['relic_origin']; select(common.entries, origin['id'])
                        require(common.upgrade_tickets_item_button.isVisible(), 'eight_real_new_training_reverse_entries_visible')
                        click(common.upgrade_tickets_item_button); dialog = common.upgrade_tickets_dialog; panel = dialog.panel
                        require(dialog.isVisible() and panel.ticket_id == row['id'] and panel.result['selected'] == row,
                                'all_eight_reverse_entries_select_exact_attached_ticket')
                        reverse_reads.append({'relic_id': origin['id'], 'ticket_id': panel.ticket_id})
                        if origin['id'] == 'rogue_6_relic_assign_1': shot('exact-reverse-entry', panel)
                        dialog.close(); gui.processEvents()
                    require(len(reverse_reads) == 8 and {r['ticket_id'] for r in reverse_reads} == {r['id'] for r in relic_rows},
                            'eight_reverse_original_id_pairs_completed')
                    other = next(common.entries.item(i).data(Qt.ItemDataRole.UserRole) for i in range(common.entries.count())
                                 if common.entries.item(i).data(Qt.ItemDataRole.UserRole) not in {r['relic_origin']['id'] for r in relic_rows})
                    select(common.entries, other)
                    require(not common.upgrade_tickets_item_button.isVisible() and not common.open_upgrade_tickets(from_item=True),
                            'unrelated_relic_never_shows_or_opens_training_ticket')

                    # Selection and page navigation close the reader plus every owned original tree.
                    first = relic_rows[0]; select(common.entries, first['relic_origin']['id'])
                    click(common.upgrade_tickets_item_button); dialog = common.upgrade_tickets_dialog; panel = dialog.panel
                    click(panel.source_button); source = panel.source_dialog
                    require(source.panel.open_recruit_tickets(), 'actual_nested_original_recruit_reader_opened')
                    recruit = source.panel.tickets_dialog
                    require(recruit.panel.open_event('rest'), 'actual_nested_recruit_document_opened')
                    nested = recruit.panel.event_dialog; gui.processEvents()
                    require(all(d.isVisible() for d in (dialog, source, recruit, nested)), 'four_level_owned_reference_tree_visible')
                    window.reference_panel('scenes'); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, source, recruit, nested)),
                            'ordinary_page_switch_closes_full_owned_original_tree')
                    common_again = window.reference_panel('relics'); select(common_again.entries, first['relic_origin']['id'])
                    click(common_again.upgrade_tickets_item_button); dialog = common_again.upgrade_tickets_dialog; panel = dialog.panel
                    click(panel.source_button); source = panel.source_dialog
                    require(source.panel.open_recruit_tickets(), 'nested_original_reopened_for_MainWindow_close')
                    recruit = source.panel.tickets_dialog; require(recruit.panel.open_event('rest'), 'nested_document_reopened_for_MainWindow_close')
                    nested = recruit.panel.event_dialog; gui.processEvents()
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_calculation_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero')
                    require(len(images) == 7, 'seven_actual_native_screenshots_recorded')
                    native(window); window.close(); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, source, recruit, nested)), 'actual_MainWindow_closes_full_owned_reference_tree')
                    done = True; gui.exit(0)
                except BaseException as error:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)

            def timeout():
                nonlocal failure
                if not done:
                    failure = failure or {'type': 'TimeoutError', 'message': f'Native exercise did not finish within configured {args.visible_ms} ms',
                                          'traceback': None}
                    window.close(); gui.exit(2)

            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, timeout)
            exitcode = gui.exec()
            require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:
            failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    try:
        after = bound_files()
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    result = {'section': 360, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'all18_original_readings': observations,
              'eight_exact_relic_originals': source_reads, 'eight_reverse_original_pairs': reverse_reads,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True,
              'private_contents_read_copied_or_restored': False, 'game_operated': False, 'chat_sent': False,
              'current_server_or_original_runtime_validated': False, 'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
