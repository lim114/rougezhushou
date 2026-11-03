"""Actual native terrain directory exercise, using isolated public state only."""
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
    from rouge import current_battle_reference as b,current_stage_directory as d,current_terrain as t,current_map_position as p,expansion_reference as v
    names={x.relative_to(ROOT).as_posix() for x in(ROOT/'rouge').glob('*.py')}
    for provider in(b,d,t,p,v):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    maps=json.loads((ROOT/'research/p3-expansion-313/map-images.json').read_bytes())['images']
    names.update(row['file'] for row in maps.values())
    names.update(('scripts/verify_current_terrain_directory_window_378.py','scripts/verify_full_available.py',
        'tests/test_current_terrain_directory_378.py','scripts/check_current_terrain_directory_378.py','research/p3-current-terrain-directory-378/source-notes.json'))
    return {name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);parser.add_argument('--visible-ms',type=int,default=120000)
    args=parser.parse_args();dest=args.receipt.resolve()
    if dest.exists():raise FileExistsError('Never overwrite actual evidence')
    dest.parent.mkdir(parents=True,exist_ok=True);before={};after={};checks=[];images=[];refreshes=[];jumps=[];full_scope={}
    calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    failure=None;window=None;gui=None;exitcode=None;done=False
    def require(value,name):
        if not value:raise AssertionError(name)
        if name not in checks:checks.append(name)
    def forbidden(name):
        def fail(*args,**kwargs):calls[name]+=1;raise AssertionError('Forbidden real operation '+name)
        return fail
    try:
        before=bound_files()
        if sys.platform!='win32':raise RuntimeError('Actual Windows required')
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        from rouge import app as a,current_terrain_directory as model,current_battle_reference as battle
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge378-public-') as folder,ExitStack() as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(a,name,value))
            backend=a.DesktopBackend;stack.enter_context(patch.object(a,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(a.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(a,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(a,'read_key',side_effect=forbidden('credential_read')))
            window=a.MainWindow();window.resize(1280,900);window.setWindowTitle('第378节 · 地形与效果反查（公开隔离验收）');window.show();gui.processEvents()
            state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def click(button):
                require(button.isVisible() and button.isEnabled(),'actual_visible_usable_button');QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents()
            def native(widget):
                owner=widget.window();h=int(owner.winId());pid=win32process.GetWindowThreadProcessId(h)[1]
                require(win32gui.IsWindowVisible(h) and not win32gui.IsIconic(h) and pid==os.getpid(),'visible_owned_native_HWND_PID')
                return {'hwnd':h,'pid':pid,'size':[owner.width(),owner.height()]}
            def shot(name,widget):
                gui.processEvents();path=dest.with_name('window-'+name+'.png');require(not path.exists() and widget.grab().save(str(path),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':name,'path':str(path),'sha256':sha256(path.read_bytes()).hexdigest(),'native':native(widget)})
            def reading(widget):
                c=widget.textCursor();return {'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def ordinary():
                common=window.reference_panel('stages');gui.processEvents();click(common.terrain_directory_button);dialog=common.terrain_directory_dialog
                require(dialog is not None and dialog.isVisible() and dialog.panel.reference is not None,'actual_common_page_terrain_directory_entry')
                return common,dialog,dialog.panel
            def exercise():
                nonlocal done,failure,full_scope
                dialog=None
                try:
                    common,dialog,p=ordinary();ref=p.reference;require(p.result is None and not p.open_button.isEnabled(),'no_implicit_terrain_or_cell_selection')
                    shot('ordinary-entry',common)
                    current=battle.packet();expected={}
                    for sid,stage in current['version']['current']['details']['stages'].items():
                        level=current['inputs']['levels']['levels/'+stage['levelId'].lower()+'.json']
                        for r,line in enumerate(level['mapData']['map']):
                            for c,index in enumerate(line):expected[(sid,r,c)]=(index,level['mapData']['tiles'][index])
                    actual={}
                    for row in ref['rows']:
                        for r,c in row['cells']:
                            key=(row['stage_id'],r,c);require(key not in actual,'no_original_cell_duplicated');actual[key]=(row['tile_index'],row['tile'])
                    require(actual==expected and ref['stage_count']==len(current['version']['current']['details']['stages']),'all_original_stage_cells_and_exact_parameter_records_complete')
                    full_scope={'stage_configurations':ref['stage_count'],'terrain_declarations_in_use':len(ref['rows']),'exact_grid_cells':len(actual),'all_original_cell_mapping_sha256':model.digest([[list(k),v] for k,v in sorted(actual.items())]),'actual_effect_applied':None}
                    for kind,_ in model.KINDS:
                        p.kind.setCurrentIndex(p.kind.findData(kind));gui.processEvents();wanted=[r for r in ref['rows'] if kind is None or r['terrain_kind']==kind]
                        require(p.entries.count()==len(wanted),'all_terrain_purpose_branches_match_original_records')
                    p.kind.setCurrentIndex(p.kind.findData(None));p.search.setText('生命');gui.processEvents()
                    require(p.entries.count()==len(model.rows('生命',reference=ref)) and p.entries.count()>0,'player_effect_text_search_not_only_raw_tile_code');shot('effect-search',p)
                    exemplar=next(r for r in ref['rows']if r['tile_key']=='tile_healing')
                    p.search.setText(exemplar['terrain_name']);p.kind.setCurrentIndex(p.kind.findData(exemplar['terrain_kind']))
                    p.floor.setCurrentIndex(p.floor.findData(exemplar['floor']));p.play_kind.setCurrentIndex(p.play_kind.findData(exemplar['play_kind']));gui.processEvents()
                    intersect=model.rows(exemplar['terrain_name'],exemplar['terrain_kind'],exemplar['floor'],exemplar['play_kind'],reference=ref)
                    displayed=[tuple(p.entries.item(i).data(Qt.ItemDataRole.UserRole))for i in range(p.entries.count())]
                    require(bool(intersect)and displayed==[tuple(r['key'])for r in intersect]
                        and (p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData())==(exemplar['terrain_kind'],exemplar['floor'],exemplar['play_kind']),
                        'actual_nonempty_search_kind_floor_source_intersection_has_exact_ordered_original_keys')
                    require(p.result is None and not p.open_button.isEnabled(),'combined_filter_does_not_implicitly_select_entry_or_cell')
                    healing=exemplar
                    active_filters=(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData())
                    require(active_filters==(exemplar['terrain_name'],exemplar['terrain_kind'],exemplar['floor'],exemplar['play_kind'])
                        and all(value not in (None,'') for value in active_filters),'all_four_nonempty_filters_retained_before_actual_selection')
                    selected_item=next(p.entries.item(i) for i in range(p.entries.count())if tuple(p.entries.item(i).data(Qt.ItemDataRole.UserRole))==tuple(healing['key']))
                    p.entries.scrollToItem(selected_item);gui.processEvents()
                    QTest.mouseClick(p.entries.viewport(),Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,p.entries.visualItemRect(selected_item).center());gui.processEvents()
                    require(p.selected_key==tuple(healing['key']) and p.cells.currentIndex()==-1 and not p.open_button.isEnabled(),'exact_healing_record_requires_manual_cell')
                    require(active_filters==(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData()),'actual_entry_click_keeps_all_four_nonempty_filters')
                    require(len({model.label(row)for row in ref['rows']})==len(ref['rows'])
                        and all(dict(model.directory.KINDS)[row['play_kind']]in model.label(row)
                            and row['stage_id']not in model.label(row)and row['tile_key']not in model.label(row)for row in ref['rows']),
                        'all_exact_records_have_distinct_chinese_source_variant_and_effect_labels')
                    p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog;require(child.panel.selected==tuple(healing['cells'][0]) and child.panel.stage_id==healing['stage_id'],'actual_map_opens_exact_stage_and_cell')
                    require(child.panel.result['tiles'][child.panel.result['map'][healing['cells'][0][0]][healing['cells'][0][1]]]==healing['tile'],'opened_map_has_exact_original_tile_parameters');jumps.append({'stage_id':healing['stage_id'],'cell':healing['cells'][0],'tile_index':healing['tile_index']});shot('healing-map',child.panel)
                    child.close();gui.processEvents()
                    require(p.map_dialog is None and not child.isVisible()and child.panel.result is None and child.panel.image_raw is None,
                        'actual_owned_map_X_clears_exact_result_and_image_bytes')
                    click(p.open_button);child=p.map_dialog;QTest.keyClick(child,Qt.Key.Key_Escape);gui.processEvents()
                    require(p.map_dialog is None and not child.isVisible()and child.panel.result is None and child.panel.image_raw is None,
                        'actual_owned_map_Escape_clears_exact_result_and_image_bytes')
                    click(p.open_button);child=p.map_dialog
                    require(child.isVisible()and child.panel.selected==tuple(healing['cells'][0]),'manual_exact_cell_map_reopen_after_X_and_Escape')
                    dialog.resize(900,450);gui.processEvents()
                    for reader in(p.player,p.technical):
                        p.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(4);c.setPosition(20,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c)
                        require(reader.verticalScrollBar().maximum()>0,'two_real_readers_have_nonzero_scroll_range');reader.verticalScrollBar().setValue(2);prior=reading(reader)
                        saved=(p.selected_key,p.cells.currentData(),p.tabs.currentIndex(),p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData())
                        require(active_filters==(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData())
                            and all(value not in (None,'') for value in active_filters),'real_parent_refresh_starts_with_all_four_nonempty_filters')
                        require(common.refresh_reference(),'actual_common_parent_refresh');gui.processEvents()
                        require(common.terrain_directory_dialog is dialog and p.map_dialog is child and child.isVisible() and reading(reader)==prior and saved==(p.selected_key,p.cells.currentData(),p.tabs.currentIndex(),p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData()),'real_parent_refresh_preserves_selected_cell_both_readings_filters_and_owned_map')
                        require(active_filters==(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData()),
                            'real_parent_refresh_preserves_original_nonempty_query_kind_floor_source')
                        refreshes.append({'reader':'player' if reader is p.player else'technical','before':prior,'after':reading(reader),'selected':saved,'nonempty_filters':active_filters})
                    unknown=next(r for r in ref['rows'] if r['tile_key']=='tile_pollution_roadf');p.select_target(unknown['key']);p.tabs.setCurrentIndex(0);gui.processEvents()
                    require(not child.isVisible() and unknown['terrain']['effects']==[] and p.result['actual_effect_applied']is None,'unknown_terrain_never_borrows_similar_key_effect_or_live_result');shot('unconfirmed-terrain',p)
                    p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog
                    with patch.object(model.terrain,'evidence_identity',return_value=None):
                        require(common.refresh_reference(),'common_source_survives_independent_terrain_evidence_loss');gui.processEvents()
                        require(p.reference is None and p.result is None and p.entries.count()==0 and p.technical.toPlainText()=='' and not p.open_button.isEnabled() and not child.isVisible() and child.panel.result is None and child.panel.image_raw is None,'bad_terrain_evidence_clears_all_old_details_and_owned_map')
                        shot('source-loss',p)
                    require(p.refresh_reference() and p.result is None and p.cells.count()==0,'recovered_source_does_not_restore_old_selection')
                    p.select_target(healing['key']);p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog
                    p.result['row']['tile']['tileKey']='tile_start';require(not p.open_map() and p.result is None and not child.isVisible(),'forged_original_tile_cannot_open_or_keep_old_map')
                    require(p.refresh_reference() and p.select_target(healing['key']),'manual_reselection_after_forgery');p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog
                    QTest.keyClick(dialog,Qt.Key.Key_Escape);gui.processEvents()
                    require(not dialog.isVisible()and p.reference is None and p.result is None and p.selected_key is None
                        and p.entries.count()==0 and p.map_dialog is None and not child.isVisible()
                        and child.panel.result is None and child.panel.image_raw is None,
                        'actual_directory_Escape_clears_directory_and_owned_map_result_and_image_bytes')
                    common,dialog,p=ordinary();require(p.result is None,'manual_directory_reopen_after_Escape_stays_unselected')
                    p.select_target(healing['key']);p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog
                    window.reference_panel('squads');gui.processEvents();require(not dialog.isVisible() and not child.isVisible() and p.reference is None and child.panel.result is None,'actual_page_switch_closes_and_clears_directory_map_tree')
                    common,dialog,p=ordinary();p.select_target(healing['key']);p.cells.setCurrentIndex(0);click(p.open_button);child=p.map_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_unchanged');require(all(v==0 for v in calls.values()) and not window.auto.isChecked(),'all_seven_real_external_operations_zero')
                    window.close();gui.processEvents();require(not dialog.isVisible() and not child.isVisible() and p.reference is None and child.panel.result is None,'actual_MainWindow_close_clears_owned_tree');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            def timeout():
                nonlocal failure
                if not done:failure=failure or {'type':'TimeoutError','message':f'Native exercise exceeded {args.visible_ms} ms'};window.close();gui.exit(2)
            QTimer.singleShot(250,exercise);QTimer.singleShot(args.visible_ms,timeout);exitcode=gui.exec();require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    try:after=bound_files()
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    result={'section':378,'passed':done and failure is None and exitcode==0 and bool(before) and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName() if gui else None,'qt_exit_code':exitcode,'configured_visible_ms':args.visible_ms,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'full_original_terrain_scope':full_scope,'actual_readings':jumps,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
