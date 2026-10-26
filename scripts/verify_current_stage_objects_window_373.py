"""Native ordinary-page enemy reverse index exercise; preparation is not execution."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
from collections import Counter
import argparse, json, os, sys, traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')).hexdigest()


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_stage_objects as model,expansion_reference as version,current_battle_reference as battle,current_stage_directory as directory,current_enemy_stage_index as index,current_map_position as positions
    for provider in(model,version,battle,directory,index,positions):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data/battle-maps').glob('*.png'))
    for folder in('current-enemies','portraits'):names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data'/folder).glob('*.png'))
    names.update(('scripts/verify_current_stage_objects_window_373.py','scripts/build_current_stage_objects_373.py','scripts/verify_full_available.py','tests/test_current_stage_objects_373.py','tests/test_current_stage_objects_view_373.py'))
    return {n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite actual native evidence')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks, images, filters, jumps, refreshes, original_counts = [], [], [], [], [], []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False
    full_scope = {}

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
        from rouge import app as app_module, current_stage_objects as model
        from rouge import current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge373-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第373节 · 关卡物件与机关（公开隔离验收）')
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

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'actual_usable_reference_button')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()


            def exercise():
                nonlocal done,failure,full_scope
                dialog=None
                try:
                    common=window.reference_panel('stages');gui.processEvents();click(common.enemy_directory_button);directory=common.enemy_directory_dialog;ip=directory.panel
                    def open_stage(sid):
                        row=next(r for r in ip.reference['data']['rows']if r['stage_id']==sid and r['enemy_key']=='0');ip.search.setText(row['name']);gui.processEvents();item=next(ip.entries.item(i)for i in range(ip.entries.count())if tuple(ip.entries.item(i).data(Qt.ItemDataRole.UserRole))==(sid,'0'));ip.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(ip.entries.viewport(),Qt.MouseButton.LeftButton,pos=ip.entries.visualItemRect(item).center());gui.processEvents();click(ip.open_button);child=ip.battle_dialog;parent=child.panel;parent.tabs.setCurrentIndex(0);gui.processEvents();require(parent.stage_id==sid,'ordinary_directory_opens_exact_stage_configuration');click(parent.stage_objects_button);dialog=parent.stage_objects_dialog;require(dialog.isVisible()and dialog.panel.result is not None,'ordinary_stage_opens_owned_object_directory');return child,parent,dialog,dialog.panel
                    def select(panel,key):
                        index=panel.entries.findData(key);require(index>0,'exact_original_object_selector_exists');panel.entries.setCurrentIndex(index);gui.processEvents();require(panel.selected()['key']==key,'actual_selection_keeps_exact_original_object_selector')
                    child,parent,dialog,panel=open_stage('ro6_n_1_1');require(panel.selected()is None and not panel.action_button.isEnabled()and not panel.position_button.isEnabled(),'initial_object_scope_requires_manual_selection');shot('ordinary-stage-object-entry',parent)
                    select(panel,'$.predefines.tokenInsts[3]');require(panel.selected()['name']=='源石祭坛'and not panel.selected()['activation_actions'],'exact_nonreward_altar_without_direct_activation_kept');require('真实伤害'in panel.player.toPlainText()and'{value}'not in panel.player.toPlainText()and'具体数值待核对'in panel.player.toPlainText(),'original_mechanism_readable_without_unresolved_computer_placeholder');shot('altar-original-mechanism',panel)
                    select(panel,'$.predefines.tokenInsts[0]');panel.activations.setCurrentIndex(1);gui.processEvents();key=panel.entries.currentData();action=panel.activations.currentData();require(panel.selected()['name']=='箱型恶笼草'and action=='4','exact_box_alias_maps_to_original_activation4');shot('box-activation-conditions',panel)
                    click(panel.action_button);require(parent.action_key=='4'and parent.tabs.currentIndex()==2,'actual_activation_jump_reaches_original_action_ordinal');jumps.append({'stage_id':parent.stage_id,'object_key':key,'action_key':action,'entity_id':panel.selected()['entity_id']})
                    dialog.resize(1060,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(14);cursor.setPosition(34,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);gui.processEvents();require(reader.verticalScrollBar().maximum()>0,'reader_has_real_nonzero_scroll_range');reader.verticalScrollBar().setValue(min(5,reader.verticalScrollBar().maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(prior['scroll']>0 and prior['anchor']!=prior['position'],'nonzero_reading_and_text_selection_are_real');require(parent.refresh_reference(),'true_parent_refresh_success');gui.processEvents();require(dialog.isVisible()and panel.entries.currentData()==key and panel.activations.currentData()==action and panel.tabs.currentIndex()==tab and reading(reader)==prior,'true_parent_keeps_filters_exact_object_activation_tab_and_two_readings');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'object_key':key,'action_key':action})
                    panel.tabs.setCurrentIndex(0);click(panel.position_button);map_dialog=panel.position_dialog;require(map_dialog.isVisible()and map_dialog.panel.result['key']==key and map_dialog.panel.result['row']['raw']['position']==panel.selected()['raw']['position'],'exact_map_uses_object_declaration_not_activation_route');require(map_dialog.panel.result['actual_position']is None and map_dialog.panel.result['actual_active']is None,'map_keeps_real_position_and_activation_unknown');shot('exact-object-declaration-map',map_dialog.panel)
                    panel.search.setText('祭坛');gui.processEvents();require(panel.selected()is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'changed_filter_clears_old_object_and_map_data');choose(panel.link,'linked');require(panel.entries.count()==1 and panel.selected()is None,'independent_link_filter_excludes_unlinked_altar_without_claiming_absence');choose(panel.link,'unlinked');require(panel.entries.count()==2,'independent_unlinked_branch_retains_altar');panel.search.clear();choose(panel.link,None)
                    old=dialog;oldpanel=panel;child,parent,dialog,panel=open_stage('ro6_n_2_2');require(not old.isVisible()and oldpanel.result is None,'new_exact_stage_closes_and_clears_previous_object_page');choose(panel.kind,'card');select(panel,'$.predefines.tokenCards[0]');require(panel.selected()['name']=='罗德岛临时雇员'and not panel.position_button.isEnabled()and not panel.action_button.isEnabled(),'predefined_card_is_not_deployed_map_object');require('5；不作为当前库存'in panel.player.toPlainText(),'card_initial_count_is_not_current_inventory');shot('predefined-card-not-map-object',panel)
                    child,parent,dialog,panel=open_stage('ro6_b_6');select(panel,'$.predefines.tokenInsts[0]');require(panel.selected()['name']=='“危朽”'and'灾厄之口'in panel.player.toPlainText(),'current_boss_object_keeps_its_exact_original_mechanism');shot('boss-associated-object',panel);click(panel.position_button);map_dialog=panel.position_dialog
                    original=battle_model.version._file;damaged=temporary/'damaged-object-manifest.json';raw=original(model.MANIFEST).read_bytes();damaged.write_bytes(raw+b'x')
                    with patch.object(battle_model.version,'_file',side_effect=lambda n:damaged if n==model.MANIFEST else original(n)):
                        require(parent.refresh_reference(),'ordinary_battle_survives_object_source_loss');gui.processEvents();require(panel.result is None and panel.technical.toPlainText()==''and panel.player.toPlainText()==model.UNAVAILABLE and not panel.action_button.isEnabled()and not panel.position_button.isEnabled(),'actual_bad_source_clears_both_readers_and_jumps');require(not map_dialog.isVisible()and map_dialog.panel.result is None and map_dialog.panel.image_raw is None,'bad_source_clears_actual_owned_map_grid_and_original_image');shot('source-loss',panel);damaged.write_bytes(raw);require(panel.refresh_reference(),'repaired_public_source_refetches');require(panel.selected()is None and panel.selected_action()is None and panel.position_dialog is None,'repaired_source_requires_manual_reselection')
                    select(panel,'$.predefines.tokenInsts[0]');panel.result['entries'][0]['name']='forged';require(not panel.open_position()and panel.result is None,'forged_object_cannot_open_map');require(panel.refresh_reference(),'refetch_after_forgery');select(panel,'$.predefines.tokenInsts[0]');click(panel.position_button);map_dialog=panel.position_dialog;QTest.keyClick(dialog,Qt.Key.Key_Escape);gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'Escape_clears_actual_object_and_owned_map_data')
                    parent.tabs.setCurrentIndex(0);click(parent.stage_objects_button);dialog=parent.stage_objects_dialog;panel=dialog.panel;select(panel,'$.predefines.tokenInsts[0]');click(panel.position_button);map_dialog=panel.position_dialog;dialog.close();gui.processEvents();require(panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'direct_X_clears_actual_object_and_owned_map_data')
                    reference=model.packet();counts=reference['inventory']['counts'];require(counts=={'instance':1652,'without_direct_activations':540,'with_direct_activations':1126,'card':14,'stages':184,'entity_types':37,'skill_records':34},'complete_original_declaration_inventory_counts');current=battle_model.packet();checked=0
                    for sid,entry in reference['inventory']['stages'].items():
                        level=current['inputs']['levels'][entry['level_key']];expected=[]
                        for container in('predefines','hardPredefines'):
                            for field in('characterInsts','tokenInsts','characterCards','tokenCards'):
                                for i,value in enumerate((level.get(container)or{}).get(field)or[]):expected.append((f'$.{container}.{field}[{i}]',(value.get('inst')or{}).get('characterKey')or value.get('characterKey'),'instance'if field.endswith('Insts')else'card'))
                        require([(r['key'],r['entity_id'],r['kind'])for r in entry['entries']]==expected,'every_original_object_or_card_identity_preserved');checked+=len(expected)
                    require(checked==1666,'all1666_original_declarations_checked_without_claiming_windows');full_scope={**counts,'all1666_windows_opened':False,'full_original_assets_source_audit':'research/p3-current-stage-objects-373/source-extraction-audit.json','current_server_verified':False}
                    parent.tabs.setCurrentIndex(0);click(parent.stage_objects_button);dialog=parent.stage_objects_dialog;panel=dialog.panel;select(panel,'$.predefines.tokenInsts[0]');click(panel.position_button);map_dialog=panel.position_dialog;window.reference_panel('squads');gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'ordinary_page_switch_clears_actual_owned_object_tree');require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');require(len(images)==7,'seven_actual_native_screenshots_recorded');native(window);window.close();gui.processEvents();done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)

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
    result = {'section': 373, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'full_original_reference_scope': full_scope,
              'all184_original_stage_counts': original_counts, 'actual_filter_observations': filters,
              'representative_exact_window_jumps': jumps, 'all1666_windows_claimed_open': False,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True,
              'private_contents_read_copied_or_restored': False, 'game_operated': False, 'chat_sent': False,
              'current_server_or_original_runtime_validated': False,
              'feature_section_published_or_completed_by_this_script': False,
              'batch_pause_state_changed_by_this_script': False,
              'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
