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
    names.update(['rouge/current_action_positions.py','rouge/current_action_positions_view.py','tests/test_current_action_positions_320.py','tests/test_current_action_positions_view_320.py','scripts/verify_current_action_positions_window_320.py'])
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
        from rouge import app as app_module,current_action_positions as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge320-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第320节 · 当前出怪与装置位置（公开隔离验收）');window.show();gui.processEvents()
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
                    def open_action(sid,key):
                        nonlocal panel,dialog,battle_dialog
                        if battle_dialog is not None:battle_dialog.close()
                        panel=main_panel;item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle_dialog=panel.current_battle_dialog;require(battle_dialog.isVisible()and battle_dialog.panel.stage_id==sid,'actual_MainWindow_exact_current_preview')
                        battle=battle_dialog.panel;battle.tabs.setCurrentIndex(2);item=next(battle.actions.item(i)for i in range(battle.actions.count())if battle.actions.item(i).data(Qt.ItemDataRole.UserRole)==key);battle.actions.scrollToItem(item);gui.processEvents();QTest.mouseClick(battle.actions.viewport(),Qt.MouseButton.LeftButton,pos=battle.actions.visualItemRect(item).center());require(battle.action_key==key and battle.action_position_button.isEnabled(),'actual_current_action_row_and_position_button')
                        QTest.mouseClick(battle.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle.action_position_dialog;panel=dialog.panel;require(dialog.isVisible()and panel.result['action_key']==key,'actual_current_preview_opens_exact_owned_action_map');require(panel.entry_key is None and panel.original.point_center()is None and panel.grid.selected is None,'action_position_initially_no_auto_reference_or_marker')
                    for sid,key in (('ro6_n_2_3','1'),('ro6_n_1_1','10'),('ro6_n_1_1','38'),('ro6_n_1_1','0'),('ro6_n_1_3','10')):
                        open_action(sid,key)
                        if panel.combo.count()>1:
                            QTest.keyClick(panel.combo,Qt.Key.Key_Home);QTest.keyClick(panel.combo,Qt.Key.Key_Down);QTest.keyClick(panel.combo,Qt.Key.Key_Return);gui.processEvents();entry=panel.result['entries'][0];cell=entry['cell'];require(panel.entry_key=='0'and panel.grid.selected==(cell['row'],cell['col']),'actual_action_point_choice_marks_exact_source_grid');require(panel.original.point_center()is not None if entry['center']else panel.original.point_center()is None,'only_approved_action_cell_center_gets_original_marker')
                            selected=panel.grid.selected;QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.center(0,0).toPoint());QTest.mouseClick(panel.original,Qt.MouseButton.LeftButton,pos=panel.original.image_rect().center().toPoint());require(panel.grid.selected==selected,'action_view_never_changes_reference_by_grid_or_inverse_image_click')
                        else:require(not panel.combo.isEnabled()and panel.grid.selected is None and panel.original.point_center()is None,'branch_or_empty_alias_no_borrowed_route_or_marker')
                        observations.append({'stage':sid,'action_key':key,'selected':panel.entry_key,'cell':panel.grid.selected,'original_center_present':panel.original.point_center()is not None,'binding_reference_count':len(panel.result['entries']),'actual_occurrence_known':False});shot(sid+'-action'+key)
                    open_action('ro6_n_2_3','1');panel.combo.setCurrentIndex(1);dialog.resize(900,410);gui.processEvents()
                    require(panel.original.point_center()is not None,'actual_unique_predefined_alias_maps_to_verified_center')
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_action_reader_has_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.entry_key,panel.combo.currentIndex(),panel.tabs.currentIndex(),panel.grid.selected);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.entry_key,panel.combo.currentIndex(),panel.tabs.currentIndex(),panel.grid.selected),'actual_action_refresh_preserves_exact_choice_tab_and_nonzero_reading');refreshes.append({'before':prior,'after':reading(reader),'keys':keys})
                    clone=temporary/'public-clone';position=model.positions;manifest=json.loads((ROOT/position.MANIFEST).read_bytes())
                    for name in(position.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/position.DATA;raw=target.read_bytes()
                    with patch.object(position,'ROOT',clone):
                        require(position.packet()is not None,'actual_public_map_clone_valid_before_corruption');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.grid.result is None and panel.original.pixmap.isNull()and panel.original.point_center()is None and not panel.technical.toPlainText(),'actual_source_corruption_clears_action_grid_bitmap_marker_and_reader');shot('action-map-source-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.entry_key is None and panel.grid.selected is None and panel.original.point_center()is None,'actual_recovery_requires_new_manual_action_choice')
                    QTest.mouseClick(battle_dialog.panel.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();previous=dialog;dialog=battle_dialog.panel.action_position_dialog;require(not previous.isVisible()and dialog.isVisible(),'repeated_action_map_open_closes_previous_owned_dialog');battle_dialog.close();gui.processEvents();require(not dialog.isVisible(),'closing_current_battle_also_closes_action_map_dialog')
                    panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();done=True;window.close();gui.processEvents();gui.exit(0)
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
    after=bound_files();result={'section':320,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
