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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-event-battles-326'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-event-battles-326/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_event_battles_326.py','scripts/verify_current_event_battles_window_326.py','scripts/verify_full_available.py','tests/test_current_event_battles_326.py','tests/test_current_event_battles_view_326.py'])
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
        from rouge import app as app_module,current_event_battles as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge326-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第326节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_control_value_available');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'direct_exact_selection_no_long_prefix_traversal')
                    def select(widget,key):
                        index=next(i for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);item=widget.item(index);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_mouse_selects_exact_item_or_document_group')
                    def entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_current_event_battles');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    def event_entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.event_battles_button.isVisible(),'real_update_entry_exposes_named_event_battles');QTest.mouseClick(main_panel.event_battles_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.event_battles_dialog
                    dialog=event_entry('choices','choice_ro6_bat3_5');panel=dialog.panel
                    require(panel.choice_id=='choice_ro6_bat3_5'and panel.stages.count()==2 and panel.stages.itemData(1)=='ro6_e_t_3','explicit_emergency_excludes_normal_configuration');require(panel.stages.currentData()is None and not panel.open_battle(),'no_default_actual_stage');shot('emergency-only')
                    choose(panel.stages,'ro6_e_t_3');QTest.mouseClick(panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.battle_dialog;require(child.isVisible()and child.panel.stage_id=='ro6_e_t_3','emergency_exact_fixed_preview');saved=panel;panel=child.panel;shot('emergency-map');panel=saved
                    require(child.panel.open_event_origins(),'current_battle_reverse_entry_opens');reverse=child.panel.event_origins_dialog;require(reverse.isVisible()and reverse.panel.stage_id=='ro6_e_t_3'and reverse.panel.choices.count()==2,'emergency_reverse_keeps_both_unrestricted_and_explicit_options');saved=panel;panel=reverse.panel;shot('reverse-options');panel=saved
                    dialog.close();require(not child.isVisible()and not reverse.isVisible(),'parent_closes_entire_forward_reverse_tree')
                    dialog=event_entry('scenes','scene_ro6_normal2_enter');panel=dialog.panel;require(panel.event_id=='黑诞'and panel.choice_id is None,'scene_entry_overview_not_inferred_parent_choice');select(panel.choices,'choice_ro6_normal2_2');require(panel.stages.count()==7 and '多个作战名称'in panel.player.toPlainText(),'black_three_names_six_configs_no_auto_choice');shot('black-six-configurations')
                    # Exercise all twelve caption bindings and twenty admitted references without traversal.
                    dialog.close()
                    from rouge.current_event_battles_view import CurrentEventBattlesDialog
                    dialog=CurrentEventBattlesDialog(parent=main_panel);dialog.show();panel=dialog.panel;gui.processEvents();require(panel.choices.count()==12,'complete_twelve_documented_battle_options')
                    for row in panel.result['rows']:
                        select(panel.choices,row['id']);require(panel.stages.count()==len(row['stage_ids'])+1 and panel.stages.currentData()is None,'each_choice_preserves_all_configs_without_default')
                        for sid in row['stage_ids']:
                            choose(panel.stages,sid);require(panel.open_battle(),'every_admitted_config_opens');child=panel.battle_dialog;require(child.isVisible()and child.panel.stage_id==sid,'all_twenty_exact_current_map_refs');observations.append({'choice':row['id'],'event':row['event_id'],'stage':sid,'actual_stage_id':panel.result['actual_stage_id']});choose(panel.stages,None);require(not child.isVisible(),'changing_version_closes_prior_map')
                    select(panel.choices,'choice_ro6_bat5_5');require('不当作两次战斗'in panel.player.toPlainText(),'two_lake_cells_not_two_rewards');shot('lake-repeated-source')
                    select(panel.choices,'choice_ro6_bat3_3');choose(panel.stages,'ro6_t_3');panel.open_battle();child=panel.battle_dialog;child.panel.open_event_origins();reverse=child.panel.event_origins_dialog;require(reverse.panel.choices.count()==1,'normal_reverse_does_not_admit_emergency_option')
                    dialog.resize(850,450);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(panel.refresh_reference(),'same_source_panel_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.choice_id=='choice_ro6_bat3_3'and panel.stages.currentData()=='ro6_t_3'and child.isVisible()and reverse.isVisible(),'same_source_keeps_both_readers_version_and_nested_tree');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'stage':panel.stages.currentData()})
                    from tests.test_current_event_battles_326 import clone
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(child.panel.refresh_reference()and child.panel.result is not None,'optional_event_source_loss_keeps_core_battle');require(not child.panel.event_origins_button.isVisible()and reverse.panel.result is None,'optional_reverse_content_cleared');require(not panel.refresh_reference(),'actual_core_event_bytes_loss_detected');require(panel.result is None and not child.isVisible()and not reverse.isVisible()and panel.technical.toPlainText()=='','core_event_loss_closes_whole_tree_and_readers');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.choice_id is None and panel.stages.currentData()is None,'event_recovery_requires_manual_selection')
                    dialog.close();dialog=event_entry('choices','choice_ro6_sala1_3');panel=dialog.panel;require(panel.stages.count()==2 and panel.stages.itemData(1)=='ro6_duel_1','duel_source_opens_exact_current_fight');shot('duel-entry')
                    old=dialog;require(main_panel.open_event_battles()and not old.isVisible(),'repeat_open_closes_old_event_reader');dialog=main_panel.event_battles_dialog;panel=dialog.panel;choose(panel.stages,'ro6_duel_1');panel.open_battle();child=panel.battle_dialog;main_panel._unavailable();require(not dialog.isVisible()and not child.isVisible(),'update_source_loss_closes_owned_event_tree')
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
    after=bound_files();result={'section':326,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
