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
        from rouge import app as app_module,current_map_position as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge319-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第319节 · 当前固定地图格子对照（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('stages');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
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
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is panel,'actual_MainWindow_common_reference_tab_opened')
                    main_panel=panel;require(panel.scope.isHidden(),'common_page_has_no_update_scope_control');require(panel.scope.currentData()is False,'current_complete_stage_catalog_available')
                    battle_dialog=None;owned=None
                    def open_positions(sid):
                        nonlocal panel,dialog,battle_dialog
                        if battle_dialog is not None:battle_dialog.close()
                        panel=main_panel;item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle_dialog=panel.current_battle_dialog;require(battle_dialog.isVisible()and battle_dialog.panel.stage_id==sid,'actual_MainWindow_exact_current_preview')
                        QTest.mouseClick(battle_dialog.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle_dialog.panel.position_dialog;panel=dialog.panel;require(dialog.isVisible()and panel.result['stage_id']==sid,'actual_current_preview_opens_owned_position_dialog');require(panel.selected is None and panel.original.point_center()is None,'position_reader_initially_no_auto_cell_or_marker')
                    for sid in ('ro6_n_6_2','ro6_n_3_2_dlc1','ro6_b_6'):
                        open_positions(sid);require(bool(panel.result['points'])and not panel.result['supports_inverse']and not panel.result['supports_segments'],'current_full_geometry_admission_is_points_only');point=panel.result['points'][0];center=panel.grid.center(point['row'],point['col']);QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=center.toPoint());gui.processEvents();require(panel.selected==(point['row'],point['col'])and panel.original.point_center()is not None,'actual_grid_click_maps_only_independently_observed_center');require('近似中心'in panel.player.toPlainText()and json.loads(panel.technical.toPlainText())['selected_cell']['point']==point,'actual_readable_cell_and_complete_point_source');require(panel.combo.currentIndex()>0 and panel.combo.currentData()==str(point['row'])+':'+str(point['col']),'actual_grid_click_keeps_known_cell_dropdown_synchronized');observations.append({'stage':sid,'selected_cell':panel.selected,'pixel_reference':point['pixel'],'original_bitmap_sha256':panel.result['image']['sha256'],'absolute_actual_battle_accuracy_claimed':False});shot(sid+'-verified-center')
                        for width,height in ((850,520),(1280,850)):
                            dialog.resize(width,height);gui.processEvents();rect=panel.original.image_rect();actual=panel.original.point_center();require(abs((actual.x()-rect.left())/rect.width()-point['pixel'][0]/panel.original.pixmap.width())<1e-9 and abs((actual.y()-rect.top())/rect.height()-point['pixel'][1]/panel.original.pixmap.height())<1e-9,'actual_marker_keeps_source_pixel_at_two_sizes')
                        if sid=='ro6_n_3_2_dlc1':require(point['tile_key']=='tile_road'and all(d['baseline_stage_id']!=sid for d in panel.result['mapping_evidence']['donors']),'new_DLC_identity_road_point_uses_full_geometry_not_same_id')
                        if sid=='ro6_n_6_2':
                            dialog.resize(900,410);gui.processEvents()
                            for reader in(panel.player,panel.technical):
                                panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_selected_cell_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.selected,panel.combo.currentIndex(),panel.tabs.currentIndex());QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.selected,panel.combo.currentIndex(),panel.tabs.currentIndex()),'actual_refresh_preserves_cell_choice_tab_and_nonzero_reading');refreshes.append({'before':prior,'after':reading(reader),'keys':keys,'actual_position_dialog_size':[dialog.width(),dialog.height()]})
                        known={(p['row'],p['col'])for p in panel.result['points']};other=next((r,c)for r in range(panel.result['rows'])for c in range(panel.result['cols'])if(r,c)not in known);QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.center(*other).toPoint());gui.processEvents();require(panel.selected==other and panel.original.point_center()is None and'不在原图上猜位置'in panel.player.toPlainText(),'unmeasured_cell_clears_previous_original_marker');QTest.mouseClick(panel.original,Qt.MouseButton.LeftButton,pos=panel.original.image_rect().center().toPoint());gui.processEvents();require(panel.selected==other and panel.original.point_center()is None,'clicking_bitmap_does_not_infer_logical_cell');observations.append({'stage':sid,'unmapped_cell':other,'marker':None})
                    open_positions('ro6_n_1_2');require(panel.result['points']==[]and not panel.combo.isEnabled()and not panel.original.pixmap.isNull(),'unmapped_stage_keeps_complete_grid_and_exact_bitmap');QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.center(0,0).toPoint());gui.processEvents();require(panel.selected==(0,0)and panel.original.point_center()is None,'unmapped_stage_grid_selection_never_creates_image_mapping');observations.append({'stage':'ro6_n_1_2','unmapped_cell':[0,0],'marker':None});shot('unmapped-stage-grid')
                    open_positions('ro6_n_6_2');combo=panel.combo;QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(panel.selected is not None and panel.original.point_center()is not None,'actual_known_center_dropdown_selects_marker')
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'actual_public_map_clone_valid_before_corruption');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.grid.result is None and panel.original.pixmap.isNull()and panel.original.point_center()is None and not panel.technical.toPlainText(),'actual_source_corruption_clears_grid_bitmap_markers_and_reader');shot('map-source-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.selected is None and panel.original.point_center()is None,'actual_source_recovery_requires_new_manual_cell_choice')
                    QTest.mouseClick(battle_dialog.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();previous=dialog;dialog=battle_dialog.panel.position_dialog;require(not previous.isVisible()and dialog.isVisible(),'repeated_position_open_closes_previous_owned_dialog');battle_dialog.close();gui.processEvents();require(not dialog.isVisible(),'closing_current_battle_also_closes_position_dialog')
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
    after=bound_files();result={'section':319,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
