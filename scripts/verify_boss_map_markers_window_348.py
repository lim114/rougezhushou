"""Actual native MainWindow update-reader exercise with temporary empty state."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-expansion-313').rglob('*')if p.is_file()}
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-battle-314').rglob('*')if p.is_file())
    portraits=json.loads((ROOT/'research/p3-current-battle-314/enemy-images.json').read_bytes())['images'];names.update(v['file']for v in portraits.values())
    names.update('tests/test_current_reward_'+name+'_315.py'for name in('reference','view','integration'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-rewards-315').rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-rewards-315/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_reward_reference_315.py','scripts/verify_current_rewards_window_315.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
    images=json.loads((ROOT/'research/p3-expansion-313/map-images.json').read_bytes())['images'];names.update(v['file']for v in images.values())
    names.update(['tests/test_current_map_position_319.py','tests/test_current_map_position_view_319.py','tests/test_current_map_position_integration_319.py','scripts/build_current_map_position_319.py','scripts/verify_current_map_position_window_319.py','research/p3-current-map-position-319/runtime-manifest.json']);names.update(json.loads((ROOT/'research/p3-current-map-position-319/runtime-manifest.json').read_bytes())['files'])
    names.update(['scripts/build_current_map_markers_337.py','scripts/verify_current_map_markers_window_337.py','tests/test_current_map_markers_337.py','tests/test_current_map_markers_view_337.py','research/p3-current-map-markers-337/runtime-manifest.json']);names.update(json.loads((ROOT/'research/p3-current-map-markers-337/runtime-manifest.json').read_bytes())['files'])
    names.update(['rouge/boss_map_markers.py','scripts/build_boss_map_markers_348.py','scripts/verify_boss_map_markers_window_348.py','tests/test_boss_map_markers_348.py','tests/test_boss_map_markers_view_348.py','research/p3-boss-map-markers-348/runtime-manifest.json']);names.update(json.loads((ROOT/'research/p3-boss-map-markers-348/runtime-manifest.json').read_bytes())['files'])
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=60000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')};failure=None;window=None;gui=None;exitcode=None;done=False
    def require(value,name):
        if not value:raise AssertionError(name)
        if name not in checks:checks.append(name)
    def forbidden(name):
        def fail(*a,**kw):calls[name]+=1;raise AssertionError('Forbidden real operation: '+name)
        return fail
    try:
        if sys.platform!='win32':raise RuntimeError('Actual Windows required')
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_map_position as model,boss_map_markers as symbols
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge348-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第348节 · 当前固定地图可见标志（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.expansion_update;state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native()})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                dialog=None
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is panel,'actual_MainWindow_update_tab_opened')
                    main_panel=panel;QTest.keyClick(panel.scope,Qt.Key.Key_End);QTest.keyClick(panel.scope,Qt.Key.Key_Return);gui.processEvents();require(panel.scope.currentData()is False,'current_complete_stage_catalog_available')
                    battle_dialog=None;owned=None
                    def open_positions(sid):
                        nonlocal panel,dialog,battle_dialog
                        if battle_dialog is not None:battle_dialog.close()
                        panel=main_panel;item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle_dialog=panel.current_battle_dialog;require(battle_dialog.isVisible()and battle_dialog.panel.stage_id==sid,'actual_MainWindow_exact_current_preview')
                        QTest.mouseClick(battle_dialog.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle_dialog.panel.position_dialog;panel=dialog.panel;require(dialog.isVisible()and panel.result['stage_id']==sid,'actual_current_preview_opens_owned_position_dialog');require(panel.selected is None and panel.original.point_center()is None,'position_reader_initially_no_auto_cell_or_marker')
                    total=0;measured=symbols.packet()['data']['bindings']
                    for sid in symbols.STAGES:
                        open_positions(sid);expected=measured[sid]['points'];require(panel.result['points']==expected and not panel.result['supports_inverse']and not panel.result['supports_segments'],'all16_exact_configurations_keep_only_observed_visible_symbols');require('可见标志'in panel.player.toPlainText()and '精确误差尚未测量'in panel.player.toPlainText(),'overview_visible_symbols_not_pixel_accuracy_or_actual_feet')
                        for point in panel.result['points']:
                            center=panel.grid.center(point['row'],point['col']);QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=center.toPoint());gui.processEvents();require(panel.selected==(point['row'],point['col'])and panel.original.point_center()is not None,'all75_real_grid_clicks_show_exact_declared_symbols');require('不是敌人实际脚点'in panel.player.toPlainText()and '标志'in panel.combo.currentText(),'symbol_labels_not_claimed_enemy_foot_or_spawn');require(json.loads(panel.technical.toPlainText())['selected_cell']['point']==point,'complete_selected_symbol_record_retained');observations.append({'stage':sid,'cell':[point['row'],point['col']],'pixel':point['pixel'],'kind':point['kind'],'actual_combat_accuracy_claimed':False});total+=1
                            for width,height in((850,520),(1280,850)):
                                dialog.resize(width,height);gui.processEvents();rect=panel.original.image_rect();actual=panel.original.point_center();require(abs((actual.x()-rect.left())/rect.width()-point['pixel'][0]/512)<1e-9 and abs((actual.y()-rect.top())/rect.height()-point['pixel'][1]/286)<1e-9,'all75_symbols_preserve_exact_source_ratio_under_two_window_sizes')
                        if '_dlc1'not in sid:
                            if sid=='ro6_b_4':panel.select_cell(6,0)
                            panel.tabs.setCurrentIndex(0);shot(sid)
                        if sid=='ro6_b_4':
                            require(panel.result['points'][2]['color_pixel_count']==64 and panel.result['points'][2]['manual_symbol_estimate']==[69,173],'dim_symbol_uses_explicit_contrast_without_moving_manual_observation');dialog.resize(850,440);panel.player.setFixedHeight(52);panel.technical.setFixedHeight(52);gui.processEvents()
                            for reader in(panel.player,panel.technical):
                                panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_nonzero_marker_reading');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.selected,panel.combo.currentIndex(),panel.tabs.currentIndex());QTest.mouseClick(battle_dialog.panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.selected,panel.combo.currentIndex(),panel.tabs.currentIndex()),'real_parent_refresh_keeps_two_nonzero_readings_marker_choice_and_tab');refreshes.append({'before':prior,'after':reading(reader),'keys':keys})
                        known={(p['row'],p['col'])for p in expected};unknown=next((r,c)for r in range(panel.result['rows'])for c in range(panel.result['cols'])if(r,c)not in known);panel.select_cell(*unknown);require(panel.original.point_center()is None,'unobserved_other_cell_clears_marker');QTest.mouseClick(panel.original,Qt.MouseButton.LeftButton,pos=panel.original.image_rect().center().toPoint());gui.processEvents();require(panel.selected==unknown and panel.original.point_center()is None,'bitmap_click_does_not_infer_unmeasured_cells')
                    require(total==75 and len(observations)==75,'all75_stage_symbol_pairs_complete')
                    open_positions('ro6_b_7');require(len(panel.result['points'])==8,'old337_eight_symbols_retained');panel.select_cell(7,6);require(panel.original.point_center()is not None,'old337_target_still_draws');shot('old337-target')
                    open_positions('ro6_n_6_2');require(len(panel.result['points'])==5 and panel.result['points'][0].get('kind')is None,'old319_ground_center_scope_unchanged');point=panel.result['points'][0];panel.select_cell(point['row'],point['col']);require(panel.original.point_center()is not None,'old319_ground_center_still_draws')
                    open_positions('ro6_n_1_2');require(panel.result['points']==[]and not panel.combo.isEnabled(),'remaining_unmapped_stage_not_given_guessed_points')
                    open_positions('ro6_b_1');map_panel=panel;bpanel=battle_dialog.panel;bpanel.tabs.setCurrentIndex(2);gui.processEvents();a=next(a for a in bpanel.result['actions']if a['raw']['actionType']=='SPAWN'and a['queue']['kind']=='main');bpanel.actions.setCurrentRow(next(i for i in range(bpanel.actions.count())if bpanel.actions.item(i).data(Qt.ItemDataRole.UserRole)==a['key']));QTest.mouseClick(bpanel.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();action_dialog=bpanel.action_position_dialog;panel=action_dialog.panel;entry=next(e for e in panel.result['entries']if e['label']=='终点参考格');panel.combo.setCurrentIndex(panel.combo.findData(entry['key']));gui.processEvents();require(panel.original.point_center()is not None and '原图可见标志位置'in panel.player.toPlainText(),'real_action_target_maps_to_own_new_visible_symbol');require(panel.result['actual_path']is None and panel.result['absolute_time']is None and not panel.result['run_updated'],'action_link_does_not_invent_actual_path_clock_or_placement');shot('action-target-reference');action_dialog.close();panel=map_panel
                    from tests.test_boss_map_markers_348 import clone as clone_sources
                    cloned=temporary/'public-clone';clone_sources(cloned);target=cloned/symbols.DATA;raw=target.read_bytes()
                    with patch.object(symbols,'ROOT',cloned):
                        require(symbols.packet()is not None,'public_new_marker_source_clone_valid');target.write_bytes(raw+b' ');QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.grid.result is None and panel.original.pixmap.isNull()and panel.original.point_center()is None and panel.technical.toPlainText()=='','bad_new_source_clears_image_grid_and_marker');shot('symbol-source-cleared');require(model.stage_reference('ro6_b_7')is not None and model.stage_reference('ro6_n_6_2')is not None,'bad_new_source_leaves_old337_and319_available');target.write_bytes(raw);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.selected is None and panel.original.point_center()is None,'source_recovery_requires_manual_new_selection')
                    QTest.mouseClick(battle_dialog.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();previous=dialog;dialog=battle_dialog.panel.position_dialog;require(not previous.isVisible()and dialog.isVisible(),'reopening_closes_previous_owned_map');battle_dialog.close();gui.processEvents();require(not dialog.isVisible(),'closing_battle_closes_owned_map')
                    panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();window.close();gui.processEvents();require(not battle_dialog.isVisible()and not dialog.isVisible(),'actual_MainWindow_and_owned_map_tree_closed');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            QTimer.singleShot(250,exercise)
            QTimer.singleShot(args.visible_ms,lambda:gui.exit(2)if not done else None)
            exitcode=gui.exec()
            require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    after=bound_files();result={'section':348,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
