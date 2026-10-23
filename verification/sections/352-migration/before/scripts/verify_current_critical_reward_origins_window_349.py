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
    from rouge import current_critical_reward_origins as m,expansion_reference as v,current_reward_origins as n
    from rouge import current_named_reward_origins as named
    providers=[m,v,n,named,*m.PROVIDERS,*named.providers().values(),*n.PROVIDERS.values()]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/build_current_critical_reward_origins_349.py','scripts/verify_current_critical_reward_origins_window_349.py','scripts/verify_full_available.py','tests/test_current_critical_reward_origins_349.py','tests/test_current_critical_reward_origins_view_349.py','tests/test_current_named_reward_origins_347.py','tests/test_current_named_reward_origins_view_347.py','tests/test_current_reward_origins_338.py','tests/test_current_reward_origins_view_338.py'])
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
        from rouge import app as app_module,current_critical_reward_origins as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge349-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第349节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_critical_reward_origins_349 import clone
                    from rouge import current_reward_origins as unified
                    main_panel=panel
                    def origins_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.origins_button.isVisible(),'real_version_item_exposes_named_acquisition_entry');QTest.mouseClick(main_panel.origins_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.origins_dialog
                    rows=model.packet()['data']['rows'];require(len(rows)==3,'three_new_explicit_grants')
                    for row in rows:
                        dialog=origins_entry('relics',row['item_id']);panel=dialog.panel
                        require(panel.entries.currentItem()is None and not panel.open_button.isEnabled(),'default_no_selection_or_claim')
                        select(panel.entries,row['key']);QTest.mouseClick(panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        child=panel.event_dialog;require(child is not None and child.isVisible(),'three_actual_item_condition_windows')
                        c=child.panel;expected={'entry':{'floor','node_type','post_update_clear'},'revive':{'node_type','next_unmarked_after_first_down','rescue_used'},'blueprint':set()}[row['event_id']]
                        require(set(c.controls)==expected and hasattr(c,'gold')==(row['event_id']=='entry'),'only_item_relevant_controls_present')
                        require(c.flow_button.text()in c.player.toPlainText(),'instruction_names_actual_current_condition_panel_button')
                        require(c.result['actual_received']is None and c.result['actual_quantity']is None and not c.result['complete_acquisition_pool']and not c.result['run_updated'],'unknown_quantity_qualification_and_inventory_preserved')
                        require(c.open_flow(),'exact_flow_opened');flow=c.flow_dialog;require(flow.isVisible()and (flow.panel.scene_id,flow.panel.choice_id)==(row['reader_target']['scene_id'],row['reader_target']['choice_id']),'all_three_exact_original_choices_visible')
                        if row['event_id']=='entry':require(flow.panel.result['source_request']==row['target']['source_request']and flow.panel.result['choices'][flow.panel.choice_id]['variant_ids']==[row['choice_id']],'exit_original_and_document_identifiers_separately_exact')
                        if row['event_id']=='entry':
                            choose(c.controls['floor'],1);choose(c.controls['node_type'],'险路尽头');choose(c.controls['post_update_clear'],True)
                            for gold,match in [(9,False),(10,True)]:
                                c.gold.setValue(gold);gui.processEvents();v=c.result['condition_reference'];require(v['listed_conditions_status']=='listed_matched'and v['choice_checks'][row['choice_id']][-1]['matches']is match,'nine_ten_gold_boundary_does_not_remove_event')
                            panel=c;shot('prayer-condition');panel=dialog.panel
                        elif row['event_id']=='revive':
                            choose(c.controls['node_type'],'不期而遇');choose(c.controls['next_unmarked_after_first_down'],True);choose(c.controls['rescue_used'],True)
                            require(c.result['condition_reference']['listed_conditions_status']=='not_matched','used_rescue_not_matched')
                            choose(c.controls['rescue_used'],False);require(c.result['condition_reference']['listed_conditions_status']=='listed_matched','unused_rescue_listed_conditions_match_only')
                            require('不是当前生命值'in c.player.toPlainText()and '整数如何处理尚未核验'in c.player.toPlainText(),'rescue_cost_maximum_not_current_or_guessed_rounding')
                            panel=c;shot('rescue-condition');panel=dialog.panel
                        else:
                            require(c.result['condition_reference']['listed_conditions_status']=='unknown'and not c.controls,'blueprint_full_prerequisites_unknown')
                            panel=c;shot('blueprint-condition');panel=dialog.panel
                        observations.append({'item_id':row['item_id'],'event_id':row['event_id'],'exact_choice':flow.panel.choice_id,'controls':sorted(c.controls)})
                        dialog.close();require(not child.isVisible()and not flow.isVisible(),'all_three_parent_close_entire_tree')
                    dialog=origins_entry('relics','rogue_6_relic_final_7');panel=dialog.panel;select(panel.entries,'critical349:choice_ro6_final1_8');require(panel.open_event(),'reopen_for_refresh');child=panel.event_dialog;c=child.panel;c.gold.setValue(9);require(c.open_flow(),'flow_before_refresh');flow=c.flow_dialog
                    # Original reader's own manual values are independent; advance it to a different exact source option.
                    flow.panel.choices.setCurrentRow(0);flow_choice=flow.panel.choice_id;child.resize(700,390);gui.processEvents()
                    for reader in(c.player,c.technical):
                        c.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(3,bar.maximum()));prior=reading(reader);tab=c.tabs.currentIndex()
                        require(main_panel.refresh_reference(),'real_version_parent_refresh');gui.processEvents();require(reading(reader)==prior and c.tabs.currentIndex()==tab and c.gold.value()==9,'two_nonzero_readings_tabs_and_declared_cost_kept')
                        refreshes.append({'reader':'player'if reader is c.player else'technical','before':prior,'after':reading(reader)})
                    require(c.flow_dialog is flow and flow.isVisible()and flow.panel.choice_id==flow_choice,'advanced_flow_original_selection_kept')
                    require(c.open_flow()and not flow.isVisible(),'repeat_open_closes_old_flow');flow=c.flow_dialog
                    panel.entries.setCurrentRow(-1);require(not child.isVisible()and not flow.isVisible(),'deselect_closes_conditions_and_flow')
                    select(panel.entries,'critical349:choice_ro6_final1_8');require(panel.open_event(),'open_before_source_loss');child=panel.event_dialog;require(child.panel.open_flow(),'flow_before_source_loss');flow=child.panel.flow_dialog
                    damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b'x');require(not panel.refresh_reference()and panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()==''and not child.isVisible()and not flow.isVisible(),'bad_source_clears_entire_tree');shot('source-loss')
                        require(unified.reference('relics','rogue_6_relic_artifact_5')is not None and unified.reference('relics','rogue_6_relic_cargo_13')is not None,'old338_and347_remain_available')
                        file.write_bytes(raw);require(panel.refresh_reference()and panel.entries.currentItem()is None and not panel.open_event(),'recovery_requires_manual_item_reselection')
                    select(panel.entries,'critical349:choice_ro6_final1_8');panel.result['rows'][0]['target']={};require(not panel.open_event()and panel.result is None,'forged_target_rejected')
                    require(panel.refresh_reference(),'fresh_after_forged_target');select(panel.entries,'critical349:choice_ro6_final1_8');require(panel.open_event(),'reopen_for_main_close');child=panel.event_dialog;require(child.panel.open_flow(),'nested_flow_for_main_close');flow=child.panel.flow_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible()and not flow.isVisible(),'actual_MainWindow_closes_whole_acquisition_tree')
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
    after=bound_files();result={'section':349,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
