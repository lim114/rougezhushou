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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-lake-328'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-lake-328/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_lake_328.py','scripts/verify_current_lake_window_328.py','scripts/verify_full_available.py','tests/test_current_lake_328.py','tests/test_current_lake_view_328.py'])
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
        from rouge import app as app_module,current_lake as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge328-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第328节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_control_value_available');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'direct_exact_selection_no_long_prefix_traversal')
                    def select(widget,key):
                        index=next(i for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);item=widget.item(index);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_mouse_selects_exact_item_or_document_group')
                    def entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_current_event_battles');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    def flow_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_whole_encounter');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    from tests.test_current_lake_328 import clone,cid,sid
                    dialog=flow_entry('scenes','scene_ro6_bat5_enter');panel=dialog.panel
                    for key,scene in panel.result['scenes'].items():
                        choose(panel.scene,key);require(panel.choices.count()==len(scene['choice_ids']),'all10_scenes_keep_declared_document_actions')
                        for action in scene['choice_ids']:
                            select(panel.choices,action);c=panel.result['choices'][action];require(c['title']in panel.player.toPlainText(),'all14_phase_action_references_readable');observations.append({'scene':key,'choice':action,'next':c['next_scene_id'],'documented_outcomes':[x['scene_id']for x in c['documented_outcomes']]})
                    for n in(4,6):
                        dialog.close();dialog=flow_entry('choices',cid(n));panel=dialog.panel;require(panel.scene_id is None and panel.choice_id is None and '请先从上方选择'in panel.player.toPlainText(),'shared_action_requires_phase_without_default');require(main_panel.refresh_reference()and '请先从上方选择'in panel.player.toPlainText(),'phase_prompt_survives_parent_refresh');shot('phase-prompt-'+str(n))
                        for phase in(1,5,6):choose(panel.scene,sid(phase));require(panel.choice_id==cid(n),'shared_action_focuses_exact_selected_phase')
                    dialog.close();dialog=flow_entry('choices',cid(7));panel=dialog.panel;require(panel.scene_id==sid(5)and panel.follow_scene()and panel.scene_id==sid(6),'repeat_note_watch_phase_separate_from_magnet');select(panel.choices,cid(8));require(not panel.follow_scene()and not panel.next_button.isEnabled()and all(b.isVisible()for b in panel.outcome_buttons),'random_choice_has_no_synthetic_next');require(not panel.open_documented_outcome(sid(9)),'unlisted_random_outcome_rejected');shot('two-documented-results')
                    for phase in(7,8):
                        choose(panel.scene,sid(6));select(panel.choices,cid(8));button=next(b for b in panel.outcome_buttons if b.property('sceneId')==sid(phase));QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id==sid(phase)and panel.result['actual_outcome']is None and not any(b.isVisible()for b in panel.outcome_buttons),'each_documented_result_separate_not_actual_random_selection');shot('result-'+str(phase))
                    select(panel.choices,cid(10));require('1件珍贵收藏品'in panel.player.toPlainText()and panel.result['choices'][cid(10)]['reward_reference']['pool']is None,'one_precious_reward_no_invented_pool_or_grant');shot('reward')
                    for n,phase,count in((5,3,3),(9,7,2)):
                        dialog.close();dialog=flow_entry('choices',cid(n));panel=dialog.panel;require(panel.open_battle(),'both_exact_lake_battle_readers_open');child=panel.battle_dialog;require(child.panel.choice_id==cid(n)and child.panel.stages.count()==count and child.panel.stages.currentData()is None,'normal_unspecified_and_explicit_urgent_config_boundaries');require(child.panel.open_full_flow(),'battle_reader_back_to_lake_flow');full=child.panel.flow_dialog;require(full.panel.scene_id==sid(phase)and full.panel.choice_id==cid(n),'reverse_battle_entry_uses_documented_phase');full.close()
                    choose(child.panel.stages,'ro6_e_t_5');require(child.panel.open_battle(),'exact_urgent_lake_fixed_map_opens');battle=child.panel.battle_dialog;require(battle.panel.stage_id=='ro6_e_t_5','current_urgent_map_ID_exact');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'same_source_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.scene_id==sid(7)and panel.choice_id==cid(9)and child.isVisible()and battle.isVisible()and child.panel.stages.currentData()=='ro6_e_t_5','parent_refresh_keeps_both_readers_phase_and_nested_map');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'phase':panel.scene_id})
                    shot('urgent-with-map')
                    with patch('rouge.current_event_battles.locate',return_value=None):require(panel.refresh_reference()and panel.result is not None and not panel.battle_button.isEnabled()and not child.isVisible()and not battle.isVisible(),'optional_map_index_loss_keeps_lake_dialogue')
                    require(panel.refresh_reference()and panel.open_battle(),'optional_map_index_recovery_manual');child=panel.battle_dialog
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference(),'actual_lake_bytes_damage_detected');require(panel.result is None and not child.isVisible()and panel.technical.toPlainText()==''and not any(b.isVisible()for b in panel.outcome_buttons),'source_loss_clears_dialogue_outcomes_and_children');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'recovery_requires_manual_phase_choice')
                    dialog.close();dialog=flow_entry('choices',cid(9));panel=dialog.panel;require(panel.open_battle(),'manual_reopen_lake_battle');child=panel.battle_dialog;require(child.panel.open_full_flow(),'manual_reopen_reverse_flow');full=child.panel.flow_dialog;old=dialog;require(main_panel.open_documented_flow()and not old.isVisible()and not child.isVisible()and not full.isVisible(),'repeat_parent_open_closes_entire_lake_tree');dialog=main_panel.flow_dialog;panel=dialog.panel;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_lake_flow')
                    dialog.close();panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();done=True;window.close();gui.processEvents();gui.exit(0)
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
    after=bound_files();result={'section':328,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
