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
    from rouge import current_enemy_spawns as model,expansion_reference as version,current_battle_reference as battle,current_stage_directory as directory,current_enemy_stage_index as index,current_map_position as positions
    for provider in(model,version,battle,directory,index,positions):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data/battle-maps').glob('*.png'))
    for folder in('current-enemies','portraits'):names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data'/folder).glob('*.png'))
    names.update(('scripts/verify_current_enemy_spawns_window_371.py','scripts/build_current_enemy_spawns_371.py','scripts/verify_full_available.py','tests/test_current_enemy_spawns_371.py','tests/test_current_enemy_spawns_view_371.py'))
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
        from rouge import app as app_module, current_enemy_spawns as model
        from rouge import current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge371-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第371节 · 敌人出怪与条件反查（公开隔离验收）')
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
                dialog=None;child=None
                try:
                    from rouge import current_enemy_stage_index as index
                    common=window.reference_panel('stages');gui.processEvents()
                    click(common.enemy_directory_button);directory=common.enemy_directory_dialog;ip=directory.panel
                    ip.search.setText('鸭爵');gui.processEvents()
                    item=next(ip.entries.item(i)for i in range(ip.entries.count())if tuple(ip.entries.item(i).data(Qt.ItemDataRole.UserRole))==('ro6_n_1_1','0'))
                    ip.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(ip.entries.viewport(),Qt.MouseButton.LeftButton,pos=ip.entries.visualItemRect(item).center());gui.processEvents();click(ip.open_button);child=ip.battle_dialog;parent=child.panel
                    require(parent.stage_id=='ro6_n_1_1'and parent.enemy_key=='0','ordinary_common_enemy_directory_opens_exact_battle_enemy')
                    require(parent.enemy_spawns_button.isVisible()and parent.enemy_spawns_button.isEnabled(),'ordinary_exact_enemy_has_spawn_reverse_entry')
                    shot('ordinary-enemy-entry',parent)
                    def open_enemy(key):
                        parent.tabs.setCurrentIndex(1);require(parent.enemy_choices.select_value(key),'exact_enemy_choice_exists');gui.processEvents();click(parent.enemy_spawns_button);d=parent.enemy_spawns_dialog
                        require(d is not None and d.isVisible()and d.panel.result is not None,'actual_owned_enemy_spawn_dialog_visible')
                        require(d.panel.result['enemy_key']==key and d.panel.result['stage_id']==parent.stage_id,'exact_enemy_and_stage_identity_kept')
                        return d,d.panel
                    def select(p,kind):
                        choose(p.kind,kind);require(p.entries.count()>1,'selected_kind_has_direct_records');p.entries.setCurrentIndex(1);gui.processEvents();require(p.selected()is not None,'actual_direct_action_selected');return p.entries.currentData()
                    dialog,panel=open_enemy('5');key=select(panel,'main');require(panel.result['enemy']['name']=='空值体','correct_exact_enemy_chinese_name')
                    require('不是实际出场数量'in panel.player.toPlainText()and'准确时刻：未知'in panel.player.toPlainText(),'player_distinguishes_record_count_and_unknown_absolute_time')
                    shot('main-spawn-conditions',panel)
                    previous=dialog;parent.tabs.setCurrentIndex(1);click(parent.enemy_spawns_button);dialog=parent.enemy_spawns_dialog;panel=dialog.panel
                    require(not previous.isVisible()and previous.panel.result is None,'repeat_entry_closes_and_clears_previous_snapshot')
                    key=select(panel,'main');click(panel.action_button)
                    require(parent.action_key==key and parent.tabs.currentIndex()==2,'exact_reverse_action_jump_reaches_original_queue_ordinal')
                    jumps.append({'stage_id':parent.stage_id,'enemy_key':panel.enemy_key,'action_key':key,'queue_kind':'main'})
                    dialog.resize(900,450);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(16);cursor.setPosition(35,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);gui.processEvents();require(reader.verticalScrollBar().maximum()>0,'actual_reader_has_nonzero_scroll_range');reader.verticalScrollBar().setValue(min(5,reader.verticalScrollBar().maximum()));gui.processEvents();prior=reading(reader);tab=panel.tabs.currentIndex()
                        require(prior['scroll']>0 and prior['anchor']!=prior['position'],'actual_nonzero_reading_and_selection_recorded')
                        require(parent.refresh_reference(),'true_battle_parent_refresh_success');gui.processEvents()
                        require(dialog.isVisible()and panel.entries.currentData()==key and panel.kind.currentData()=='main'and panel.tabs.currentIndex()==tab and reading(reader)==prior,'true_parent_keeps_exact_selected_action_filter_tab_and_two_readings')
                        refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'enemy_key':panel.enemy_key,'action_key':key})
                    panel.tabs.setCurrentIndex(0);click(panel.position_button);map_dialog=parent.action_position_dialog;require(map_dialog.isVisible()and map_dialog.panel.result['action_key']==key,'map_request_uses_exact_original_action')
                    require(map_dialog.panel.result['actual_path']is None and map_dialog.panel.result['absolute_time']is None,'map_reference_does_not_invent_live_route_or_clock')
                    shot('exact-existing-map-reference',map_dialog.panel)
                    dialog.close();gui.processEvents();require(panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'direct_X_clears_actual_spawn_and_owned_map_data')
                    dialog,panel=open_enemy('4');key=select(panel,'branch');require(all(r['action']['queue']['kind']=='branch'for r in model.rows(panel.result,'branch')),'actual_branch_filter_does_not_include_main_wave')
                    shot('conditional-branch',panel);click(panel.action_button);require(parent.action_key==key and parent.queue_kind.currentData()=='branch','branch_jump_preserves_exact_original_branch_ordinal')
                    jumps.append({'stage_id':parent.stage_id,'enemy_key':panel.enemy_key,'action_key':key,'queue_kind':'branch'})
                    old_dialog=dialog;old_panel=panel;dialog,panel=open_enemy('8');require(not old_dialog.isVisible()and old_panel.result is None,'changing_exact_enemy_clears_old_relation')
                    require(panel.result['entries']==[]and not panel.action_button.isEnabled()and'不能据此排除'in panel.player.toPlainText(),'no_direct_spawn_keeps_dynamic_generation_unknown')
                    shot('no-direct-record',panel)
                    dialog,panel=open_enemy('5');key=select(panel,'main');click(panel.position_button);map_dialog=parent.action_position_dialog
                    damaged=temporary/'manifest-damaged.json';manifest_path=battle_model.version._file(model.MANIFEST);raw=manifest_path.read_bytes();damaged.write_bytes(raw+b'x');original=battle_model.version._file
                    with patch.object(battle_model.version,'_file',side_effect=lambda name:damaged if name==model.MANIFEST else original(name)):
                        require(parent.refresh_reference(),'ordinary_parent_survives_relation_source_failure');gui.processEvents()
                        require(panel.result is None and panel.entries.currentData()is None and panel.technical.toPlainText()==''and panel.player.toPlainText()==model.UNAVAILABLE and not panel.action_button.isEnabled(),'actual_bad_source_clears_both_readers_and_jump')
                        require(not map_dialog.isVisible()and map_dialog.panel.result is None,'source_loss_clears_exact_owned_map_data')
                        shot('source-loss',panel)
                        damaged.write_bytes(raw);require(panel.refresh_reference(),'repaired_source_refetch_success');gui.processEvents()
                        require(panel.result is not None and panel.selected()is None and not panel.action_button.isEnabled(),'repair_does_not_restore_old_selected_action')
                    key=select(panel,'main');shot('manual-reselection-after-recovery',panel)
                    panel.result['enemy']['name']='forged';require(not panel.follow_action()and panel.result is None,'mutated_same_stage_snapshot_cannot_jump')
                    require(panel.refresh_reference(),'refetch_after_forgery');select(panel,'main');click(panel.position_button);map_dialog=parent.action_position_dialog
                    QTest.keyClick(dialog,Qt.Key.Key_Escape);gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'Escape_clears_spawn_and_owned_map_actual_data')
                    current=battle_model.packet();inventory=model.evidence();checked=0
                    for sid,stage in current['version']['current']['details']['stages'].items():
                        level_key='levels/'+stage['levelId'].lower()+'.json';level=current['inputs']['levels'][level_key];declared=inventory['stages'][sid]
                        require(declared['level_key']==level_key and len(declared['references'])==len(level['enemyDbRefs']),'all_original_stage_binding_counts_kept')
                        all_actions=[a for q in battle_model.queues(level)for a in q['actions']]
                        for i,e in enumerate(level['enemyDbRefs']):
                            expected=[str(j)for j,a in enumerate(all_actions)if a['actionType']=='SPAWN'and a['key']==e['id']]
                            require(declared['references'][i]['action_keys']==expected,'all2060_original_direct_action_relations_match_exact_ordinal')
                            checked+=1
                    require(checked==2060 and inventory['counts']['spawn_records']==7696 and inventory['counts']['no_direct_spawn_references']==110,'complete_inventory_scope_counts_match_fixed_sources')
                    full_scope={'stage_configurations':len(inventory['stages']),'exact_enemy_references':checked,'spawn_records':7696,'no_direct_spawn_references':110,'all2060_windows_opened':False,'actual_execution_verified':False}
                    dialog,panel=open_enemy('5');select(panel,'main');click(panel.position_button);map_dialog=parent.action_position_dialog;window.reference_panel('squads');gui.processEvents()
                    require(not directory.isVisible()and not child.isVisible()and not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'ordinary_page_switch_clears_owned_reverse_and_map_tree')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');require(len(images)==7,'seven_actual_native_screenshots_recorded');native(window);window.close();gui.processEvents();done=True;gui.exit(0)
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
    result = {'section': 371, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'full_original_reference_scope': full_scope,
              'all184_original_stage_counts': original_counts, 'actual_filter_observations': filters,
              'representative_exact_window_jumps': jumps, 'all2060_windows_claimed_open': False,
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
