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
    from rouge import current_event_item_uses as model, expansion_reference as version
    from rouge import current_reward_origins as origins, current_named_reward_origins as named
    for provider in [model, model.directory, version, origins, named, *model.directory.providers().values()]:
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/build_current_event_item_uses_376.py', 'scripts/verify_current_event_item_uses_window_376.py',
                  'tests/test_current_event_item_uses_376.py', 'tests/test_current_event_item_uses_view_376.py', 'scripts/verify_full_available.py'))
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
        from rouge import app as app_module, current_event_item_uses as model
        from tests.test_current_event_item_uses_376 import clone
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge376-public-') as folder, ExitStack() as stack:
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
            window = app_module.MainWindow(); window.resize(1260, 900); window.setWindowTitle('第376节 · 物品用途、条件与取得来源（公开隔离验收）')
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

            def ordinary(category='scenes'):
                nonlocal common, dialog, panel
                common = window.reference_panel(category); gui.processEvents()
                require(window.centralWidget().currentWidget() is common and common.full_catalog and common.scope.isHidden(), 'ordinary_events_page_not_separate_version_tab')
                if not common.event_item_uses_button.isEnabled():
                    click(common.refresh_button)
                    require(common.event_item_uses_button.isEnabled(), 'real_parent_recheck_restores_resource_entry_after_source_repair')
                require(common.event_item_uses_button.isVisible(), 'ordinary_events_page_exposes_current_catalogue')
                click(common.event_item_uses_button); dialog = common.event_item_uses_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.result is not None, 'actual_owned_event_item_uses_visible')
                return panel

            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(), 'scroll': widget.verticalScrollBar().value()}

            def exercise():
                nonlocal done, failure, dialog, panel
                try:
                    ordinary(); rows=panel.result['data']['rows']
                    require(len(rows)==12 and len({r['item_id'] for r in rows})==7 and len({r['event_id'] for r in rows})==6,'12_literal_named_uses7_items6_events')
                    require(panel.entries.currentItem() is None and panel.item.count()==8 and not panel.open_button.isEnabled() and panel.origins_button.isHidden(),'initial_named_use_overview_has_no_possession_or_source_claim')
                    require(all(r['literal'] in r['entry']['description'] and r['literal'].endswith(r['item']['name']) for r in rows),'all12_roles_require_explicit_verb_and_exact_full_item_name')
                    require(all(r['actual_held'] is None and r['quantity_reference'] is None and r['actual_consumed'] is None for r in rows),'all_named_quantities_and_actual_inventory_remain_unknown')
                    shot('overview',panel)
                    for item_id in dict.fromkeys(r['item_id'] for r in rows):
                        choose(panel.item,item_id)
                        require(panel.entries.count()>0 and all(r['item_id']==item_id for r in panel.result['rows']),'all7_named_item_filter_branches_preserve_identity')
                        filters.append({'item_id':item_id,'ids':[r['id']for r in panel.result['rows']]})
                    choose(panel.item,None)
                    for role,_label in model.ROLES:
                        choose(panel.role,role); require(panel.entries.count()>0 and all(r['role']==role for r in panel.result['rows']),'all_three_role_filters_keep_possession_offering_consumption_separate')
                    choose(panel.role,None)
                    for row in rows:
                        select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                        require((child.panel.event_id,child.panel.scene_id,child.panel.choice_id)==(row['event_id'].split(':',1)[1],row['entry']['scene_id'],row['entry']['choice_id']),'all12_exact_reader_event_phase_choice_targets')
                        require(child.panel.result.get('actual_eligible') is None and not child.panel.result.get('run_updated',True),'opening_item_use_does_not_update_actual_eligibility_or_run')
                        observations.append({'item_id':row['item_id'],'role':row['role'],'event':row['event_title'],'scene':child.panel.scene_id,'choice':child.panel.choice_id,'native':native(child)})
                    controller=[r for r in rows if r['item_id']=='rogue_6_scrap_G_12']; require(len(controller)==3 and all(r['role']=='held'for r in controller),'three_controller_uses_are_held_conditions_not_consumption_or_reward')
                    row=controller[0]; select(panel.entries,row['id']); click(panel.open_button)
                    require(panel.event_dialog.panel.result['declared_has_controller'] is None and '没有据此扣除物品' in panel.player.toPlainText(),'controller_current_possession_kept_unknown_and_not_spent')
                    shot('controller-held',panel)
                    choose(panel.item,'rogue_6_relic_cargo_13'); require(panel.entries.count()==4,'key_four_distinct_uses_kept')
                    choose(panel.role,'offered'); require(panel.entries.count()==3 and len({r['entry']['scene_id'] for r in panel.result['rows']})==3,'key_three_offerings_retain_three_different_ritual_steps')
                    row=panel.result['rows'][0]; select(panel.entries,row['id'])
                    require('不能据此说一把钥匙可完成三步' in panel.player.toPlainText() and '不默认每次1件' in panel.player.toPlainText(),'key_not_single_all_steps_or_assumed_three_consumed')
                    shot('key-three-steps',panel); choose(panel.role,None); choose(panel.item,None)
                    for iid in ('rogue_6_relic_final_4','rogue_6_relic_final_6','rogue_6_relic_final_5'):
                        row=next(r for r in rows if r['item_id']==iid); select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                        require(child.panel.choice_id==row['entry']['choice_id'] and '调谐仪式' in panel.player.toPlainText(),'three_ending_materials_keep_own_exact_ritual_effect')
                    shot('ritual-material',panel)
                    source_items=set()
                    for iid in dict.fromkeys(r['item_id'] for r in rows):
                        row=next(r for r in rows if r['item_id']==iid); select(panel.entries,row['id'])
                        target=model.acquisition_target(panel.result)
                        if target is None:
                            require(panel.origins_button.isHidden(),'unsupported_acquisition_source_option_hidden_not_disabled_placeholder')
                            continue
                        source_items.add(iid); click(panel.origins_button); origins=panel.origins_dialog
                        require(origins.isVisible() and origins.panel.item_id==iid and origins.panel.category==row['category'],'known_acquisition_source_opens_exact_item_and_category')
                    require(source_items=={'rogue_6_scrap_G_12','rogue_6_relic_cargo_13','rogue_6_relic_final_4','rogue_6_relic_final_6'},'only_four_existing_acquisition_items_are_linked_not_a_new_complete_pool')
                    row=controller[0]; select(panel.entries,row['id']); click(panel.origins_button); origins=panel.origins_dialog
                    require(origins.panel.entries.count()==2,'controller_two_existing_338_acquisition_choices_preserved')
                    source_row=origins.panel.result['rows'][0]; select(origins.panel.entries,source_row['key']); click(origins.panel.open_button); source_child=origins.panel.event_dialog
                    require(source_child.isVisible() and source_child.panel.scene_id==source_row['scene_id'] and source_child.panel.choice_id==source_row['choice_id'],'named_use_to_acquisition_to_exact_original_dialogue_tree')
                    shot('known-source',origins.panel)
                    row=next(r for r in rows if r['item_id']=='rogue_6_relic_legacy_113'); select(panel.entries,row['id'])
                    require(origins.panel.result is None and source_child.panel.result is None and not origins.isVisible() and not source_child.isVisible(),'changing_item_clears_entire_old_acquisition_event_tree')
                    require(panel.origins_button.isHidden() and '不表示无法获得' in panel.player.toPlainText(),'missing_acquisition_link_not_impossible_drop_claim')
                    shot('source-not-covered',panel)
                    row=controller[0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog; click(panel.origins_button); origins=panel.origins_dialog
                    dialog.resize(720,420); gui.processEvents()
                    for reader in (panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor=reader.textCursor(); cursor.setPosition(3); cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        require(reader.verticalScrollBar().maximum()>0,'both_item_use_readers_have_real_nonzero_scroll')
                        reader.verticalScrollBar().setValue(min(3,reader.verticalScrollBar().maximum())); prior=reading(reader); tab=panel.tabs.currentIndex()
                        require(common.refresh_reference(),'real_common_parent_refresh_for_use_and_source'); gui.processEvents()
                        require(reading(reader)==prior and panel.selected_key==row['id'] and panel.tabs.currentIndex()==tab and panel.event_dialog is child and child.isVisible() and panel.origins_dialog is origins and origins.isVisible(),'both_readings_choice_tab_and_two_owned_reader_types_kept')
                        refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    damaged=clone(temporary/'damaged'); path=damaged/model.DATA; raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x'); require(common.refresh_reference(),'ordinary_parent_survives_named_use_source_loss'); gui.processEvents()
                        require(panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()=='' and panel.player.toPlainText()==model.UNAVAILABLE and child.panel.result is None and origins.panel.result is None and not dialog.isVisible(),'bad_source_clears_actual_use_source_and_owned_event_data')
                        shot('source-loss',common); path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.selected_key is None and not panel.open_button.isEnabled() and panel.origins_button.isHidden(),'named_use_source_repair_requires_manual_reselection')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    win32gui.PostMessage(int(dialog.winId()),0x0010,0,0)
                    for _native_close_tick in range(300):
                        QTest.qWait(10)
                        if not dialog.isVisible(): break
                    require(not dialog.isVisible() and panel.result is None and child.panel.result is None,'native_WM_CLOSE_clears_named_use_actual_tree')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    QTest.keyClick(child,Qt.Key.Key_Escape); gui.processEvents(); require(child.panel.result is None and panel.result is not None,'nested_reader_Escape_clears_actual_data_only')
                    click(panel.open_button); child=panel.event_dialog; QTest.keyClick(dialog,Qt.Key.Key_Escape); gui.processEvents()
                    require(not dialog.isVisible() and panel.result is None and child.panel.result is None,'native_Escape_clears_named_use_actual_tree')
                    ordinary('relics'); require(common.event_item_uses_button.isVisible(),'ordinary_item_page_also_exposes_named_use_lookup')
                    row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog
                    window.reference_panel('squads'); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and panel.result is None and child.panel.result is None,'page_switch_clears_named_use_and_exact_reader')
                    ordinary(); row=panel.result['rows'][0]; select(panel.entries,row['id']); click(panel.open_button); child=panel.event_dialog; click(panel.origins_button); origins=panel.origins_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_unchanged')
                    require(all(v==0 for v in calls.values()) and not window.auto.isChecked(),'all_seven_real_external_operations_zero')
                    require(len(images)==7,'seven_actual_native_screenshots_recorded'); native(window); window.close(); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible() and not origins.isVisible() and panel.result is None and child.panel.result is None and origins.panel.result is None,'actual_MainWindow_close_clears_named_use_and_source_trees')
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
    result = {'section': 376, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
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
