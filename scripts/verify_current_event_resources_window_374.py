"""Actual common-event current catalogue, with temporary public state only."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback, time
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_event_resources as model, expansion_reference as version
    for provider in [model, model.directory, version, *model.directory.providers().values()]:
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/build_current_event_resources_374.py', 'scripts/verify_current_event_resources_window_374.py',
                  'tests/test_current_event_resources_374.py', 'tests/test_current_event_resources_view_374.py', 'scripts/verify_full_available.py'))
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
        from rouge import app as app_module, current_event_resources as model
        from tests.test_current_event_resources_374 import clone
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge374-public-') as folder, ExitStack() as stack:
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
            window = app_module.MainWindow(); window.resize(1260, 900); window.setWindowTitle('第374节 · 事件资源收益与代价（公开隔离验收）')
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
                if not common.event_resources_button.isEnabled():
                    click(common.refresh_button)
                    require(common.event_resources_button.isEnabled(), 'real_parent_recheck_restores_resource_entry_after_source_repair')
                require(common.event_resources_button.isVisible(), 'ordinary_events_page_exposes_current_catalogue')
                click(common.event_resources_button); dialog = common.event_resources_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.result is not None, 'actual_owned_event_resources_visible')
                return panel

            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(), 'scroll': widget.verticalScrollBar().value()}

            def exercise():
                nonlocal done, failure, dialog, panel
                try:
                    ordinary(); rows = panel.result['data']['rows']
                    require(len(rows) == 88 and sum(len(r['effects']) for r in rows) == 100, '88_exact_occurrences100_explicit_resource_parts')
                    require(panel.entries.currentItem() is None and not panel.open_button.isEnabled(), 'initial_resource_lookup_has_no_choice_or_claim')
                    originals = {r['id']: r for r in model.directory.packet()['data']['rows']}
                    require(all(any(e == r['entry'] for e in originals[r['event_id']]['entries']) for r in rows), 'all88_choices_bound_to_exact_document_phase')
                    require(all(e['literal'] in r['entry']['description'] for r in rows for e in r['effects']), 'all100_reference_parts_have_original_literal_evidence')
                    require(panel.result['actual_net_change'] is None and not panel.result['run_updated'], 'no_guessed_net_result_or_run_write')
                    shot('overview', panel)
                    for resource, _label in model.RESOURCES:
                        choose(panel.resource, resource)
                        require(panel.entries.count() > 0 and all(any(e['resource'] == resource for e in r['matching_effects']) for r in panel.result['rows']), 'all13_resource_filter_branches_keep_exact_parts')
                        filters.append({'resource':resource,'ids':[r['id'] for r in panel.result['rows']]})
                    choose(panel.resource, None)
                    for kind, _label in model.KINDS:
                        choose(panel.kind, kind)
                        require(panel.entries.count() > 0 and all(any(e['kind'] == kind for e in r['matching_effects']) for r in panel.result['rows']), 'all_three_direction_filters_use_actual_effects')
                    choose(panel.kind, 'item'); choose(panel.resource, 'processed')
                    row = next(r for r in panel.result['rows'] if r['event_title'] == '货从口出'); select(panel.entries, row['id'])
                    require('源石锭：4' in panel.player.toPlainText() and '加工品：1件' in panel.player.toPlainText() and len(panel.result['selected']['effects']) == 2, 'gain_only_filter_keeps_the_selected_choice_gold_cost')
                    shot('cost-and-gain', panel); click(panel.open_button); child = panel.event_dialog
                    require(child.panel.scene_id == row['entry']['scene_id'] and child.panel.choice_id == row['entry']['choice_id'] and child.panel.result['declared_gold'] is None, 'exact_resource_choice_full_dialogue_keeps_gold_unknown')
                    observations.append({'event':row['event_title'],'scene':child.panel.scene_id,'choice':child.panel.choice_id,'native':native(child)})
                    choose(panel.kind, None); choose(panel.resource, None)
                    require(child.panel.result is None and not child.isVisible(), 'filter_change_clears_and_closes_old_exact_dialogue')
                    for title, choice in [('色味不同源','拿走看上去像是苹果的食物'),('色味不同源','拿走看上去像是鱼的食物'),('黑诞','落荒而逃'),('手术祭坛','小心地移除电极')]:
                        row = next(r for r in rows if r['event_title'] == title and r['entry']['title'] == choice); select(panel.entries, row['id']); click(panel.open_button); child = panel.event_dialog
                        require((child.panel.scene_id,child.panel.choice_id) == (row['entry']['scene_id'],row['entry']['choice_id']), 'life_shield_and_max_life_cases_open_exact_original_context')
                        observations.append({'event':title,'scene':child.panel.scene_id,'choice':child.panel.choice_id,'resources':[e['resource'] for e in row['effects']],'native':native(child)})
                        if title == '黑诞': require('不当作生命不足时仍无条件扣满' in panel.player.toPlainText(), 'fixed_nominal_life_cost_keeps_minimum_life_boundary')
                    require(any(e['amount_rule']=='half' and e['resource']=='max_life' and e['quantity'] is None for e in row['effects']), 'altar_half_max_life_not_filled_as_current_life_or_rounded_value')
                    shot('life-and-limits', panel)
                    row = next(r for r in rows if r['event_title'] == '沉重的契约' and r['entry']['title'] == '推翻石磨'); select(panel.entries,row['id'])
                    require(any(e['amount_rule']=='half' and e['quantity'] is None for e in row['effects']) and '取整' in panel.player.toPlainText(), 'contract_half_life_stays_unknown_with_known_ap_gain')
                    row = next(r for r in rows if r['event_title']=='险路尽头' and any(e['amount_rule']=='equal_spent_ap' for e in r['effects'])); select(panel.entries,row['id'])
                    require(any(e['resource']=='ap' and e['amount_rule']=='all' and e['quantity'] is None for e in row['effects']) and any(e['resource']=='hope' and e['amount_rule']=='equal_spent_ap' and e['quantity'] is None for e in row['effects']), 'all_ap_to_equal_hope_preserves_both_unknown_quantity_parts')
                    shot('ap-conversion',panel)
                    raw_only = [r for r in rows if r['entry']['choice_id'] in ('choice_ro6_final1_6','choice_ro6_final1_7')]
                    require(len(raw_only)==2 and all(not any(e['resource']=='processed' for e in r['effects']) for r in raw_only), 'two_original_only_exit_choices_do_not_inherit_processed_reward')
                    row = raw_only[0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    require(child.panel.scene_id==row['entry']['scene_id'] and child.panel.choice_id==row['entry']['choice_id'], 'unbound_original_exit_record_opens_own_original_only_phase')
                    observations.append({'event':row['event_title'],'scene':child.panel.scene_id,'choice':child.panel.choice_id,'native':native(child)})
                    shot('phase-only-reference',panel)
                    row = next(r for r in rows if r['event_title']=='货从口出'); select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    dialog.resize(720,420); gui.processEvents()
                    for reader in (panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor=reader.textCursor(); cursor.setPosition(3); cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        require(reader.verticalScrollBar().maximum()>0,'both_resource_readers_have_real_nonzero_scroll')
                        reader.verticalScrollBar().setValue(min(3,reader.verticalScrollBar().maximum())); prior=reading(reader); tab=panel.tabs.currentIndex()
                        require(common.refresh_reference(),'real_common_events_parent_refresh'); gui.processEvents()
                        require(reading(reader)==prior and panel.selected_key==row['id'] and panel.tabs.currentIndex()==tab and panel.event_dialog is child and child.isVisible(),'both_readings_choice_tab_and_exact_child_kept_after_actual_parent_refresh')
                        refreshes.append({'reader':'player' if reader is panel.player else 'technical','before':prior,'after':reading(reader)})
                    panel.tabs.setCurrentIndex(0); shot('reading-kept',panel)
                    damaged=clone(temporary/'damaged'); path=damaged/model.DATA; raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x'); require(common.refresh_reference(),'ordinary_events_parent_survives_resources_source_loss'); gui.processEvents()
                        require(panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()=='' and panel.player.toPlainText()==model.UNAVAILABLE and child.panel.result is None and not child.isVisible() and not dialog.isVisible(),'bad_resource_source_clears_actual_list_readers_and_owned_tree')
                        shot('source-loss',common); path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.selected_key is None and panel.entries.currentItem() is None and not panel.open_button.isEnabled(),'resource_source_repair_requires_manual_reselection')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    hwnd=int(dialog.winId()); win32gui.PostMessage(hwnd,0x0010,0,0); gui.processEvents()
                    close_deadline=time.monotonic()+3
                    while dialog.isVisible() and time.monotonic()<close_deadline: QTest.qWait(10)
                    require(not dialog.isVisible() and panel.result is None and child.panel.result is None,'native_WM_CLOSE_clears_resources_and_owned_actual_data')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    QTest.keyClick(child,Qt.Key.Key_Escape); gui.processEvents()
                    require(not child.isVisible() and child.panel.result is None and panel.result is not None and dialog.isVisible(),'nested_reader_Escape_clears_actual_data_without_closing_resource_directory')
                    click(panel.open_button); child=panel.event_dialog
                    QTest.keyClick(dialog,Qt.Key.Key_Escape); gui.processEvents()
                    require(not dialog.isVisible() and panel.result is None and child.panel.result is None,'native_Escape_clears_resources_and_owned_actual_data')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    window.reference_panel('squads'); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and panel.result is None and child.panel.result is None,'page_switch_clears_resources_and_nested_exact_reader')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_unchanged')
                    require(all(v==0 for v in calls.values()) and not window.auto.isChecked(),'all_seven_real_external_operations_zero')
                    require(len(images)==7,'seven_actual_native_screenshots_recorded'); native(window); window.close(); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and panel.result is None and child.panel.result is None,'actual_MainWindow_close_clears_whole_resource_tree')
                    done=True; gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
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
    result = {'section': 374, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
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
