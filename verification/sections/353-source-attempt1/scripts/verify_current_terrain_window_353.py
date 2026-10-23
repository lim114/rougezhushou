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
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_map_position as m,expansion_reference as v,current_terrain as t
    from rouge import current_named_reward_origins as named
    providers=[m,v,t,m.battle]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_terrain_window_353.py','scripts/verify_full_available.py','tests/test_current_terrain_353.py','tests/test_current_terrain_view_353.py','verification/sections/353-preparation/scope.json'])
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=120000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
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
        with TemporaryDirectory(prefix='rouge353-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第353节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_terrain_control_value_available');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'real_terrain_control_selection')
                    def select(widget,key):
                        item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'real_common_stage_selection')
                    main_panel=panel
                    def entry(stage):
                        select(main_panel.entries,stage);QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=main_panel.current_battle_dialog;QTest.mouseClick(battle.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();return battle.panel.position_dialog
                    reference=model.packet();require(reference is not None,'actual_current_map_and_terrain_evidence_ready')
                    def stage_for(key):
                        for sid,stage in reference['current']['version']['current']['details']['stages'].items():
                            level=reference['current']['inputs']['levels']['levels/'+stage['levelId'].lower()+'.json']
                            if any(level['mapData']['tiles'][index]['tileKey']==key for row in level['mapData']['map']for index in row):return sid
                        raise AssertionError('No original cell for '+key)
                    subjects=[('ro6_n_5_8',key)for key in('tile_healing','tile_bigforce','tile_infection')]+[(stage_for(key),key)for key in('tile_volcano','tile_telin','tile_ftstart','tile_hole','tile_grass','tile_pollution_roadf')]
                    for sid,key in subjects:
                        dialog=entry(sid);panel=dialog.panel;choose(panel.terrain_kind,key);locations=model.terrain_locations(panel.result,key);require(panel.terrain_cells.count()==len(locations)+1 and panel.grid.highlight_cells=={(r['row'],r['col'])for r in locations},'exact_type_filter_and_all_matching_grid_cells_highlighted')
                        choose(panel.terrain_cells,(locations[0]['row'],locations[0]['col']));cell=model.cell_reference(panel.result,*panel.selected);text=panel.player.toPlainText()
                        require(cell['tile']['tileKey']==key and cell['terrain']['name']in text,'selected_exact_tile_and_own_terrain_description');require((panel.original.point is not None)==cell['mapped_to_original'],'uncalibrated_special_tiles_never_projected_to_original')
                        if key=='tile_healing':require('3%'in text,'actual_healing_three_percent')
                        if key=='tile_bigforce':require('1个等级'in text,'actual_push_pull_one_level')
                        if key=='tile_infection':require('100点真实伤害'in text and '50%'in text and '300秒'in text,'actual_infection_own_three_effect_parameters')
                        if key=='tile_pollution_roadf':require('名称未核实'in text and '尚未取得准确中文名称'in text,'unverified_suffix_stays_unknown_not_assigned_pollution_mechanic')
                        observations.append({'stage':sid,'tile_key':key,'cell':list(panel.selected),'matched_cells':len(locations),'original_projected':cell['mapped_to_original']})
                        if key in('tile_healing','tile_infection','tile_telin','tile_pollution_roadf'):shot(key)
                        dialog.close()
                    dialog=entry('ro6_n_5_8');panel=dialog.panel;choose(panel.terrain_kind,'tile_infection');choose(panel.terrain_cells,panel.terrain_cells.itemData(1));dialog.resize(950,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'real_nonzero_terrain_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();selected=panel.selected
                        require(main_panel.refresh_reference(),'actual_common_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.selected==selected and panel.terrain_kind.currentData()=='tile_infection','two_readers_cell_type_scroll_selection_and_tab_survive_parent_refresh');refreshes.append({'before':prior,'after':reading(reader)})
                    from rouge import current_terrain as terrain
                    damaged=temporary/'damaged';manifest=json.loads((terrain.ROOT/terrain.MANIFEST).read_bytes())
                    for name in(terrain.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((terrain.ROOT/name).read_bytes())
                    path=damaged/terrain.NOTES;raw=path.read_bytes()
                    with patch.object(terrain,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(not panel.refresh_reference()and panel.result is None and panel.terrain_kind.count()==0 and panel.terrain_cells.count()==0 and not panel.grid.highlight_cells and panel.original.point is None,'actual_evidence_byte_damage_clears_types_cells_grid_image_and_marker');shot('terrain-source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.selected is None and panel.terrain_kind.currentData()is None,'evidence_recovery_requires_manual_cell_and_type')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_closes_terrain_map_tree')
                    done=True;gui.exit(0)
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
    after=bound_files();result={'section':353,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
