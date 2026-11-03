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
    from rouge import current_reward_origins as m,expansion_reference as v
    for provider in(m,v,*m.PROVIDERS.values()):
        names.add(provider.MANIFEST)
        manifest=json.loads((ROOT/provider.MANIFEST).read_bytes())
        names.update(manifest['files'])
    names.update(['scripts/build_current_reward_origins_338.py','scripts/verify_current_reward_origins_window_338.py','scripts/verify_full_available.py','tests/test_current_reward_origins_338.py','tests/test_current_reward_origins_view_338.py','tests/test_current_memory_tree_view_336.py','tests/test_current_lone_dog_view_335.py','tests/test_current_vine_events_view_333.py'])
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
        from rouge import app as app_module,current_reward_origins as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge338-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第338节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_reward_origins_338 import ITEMS,clone
                    main_panel=panel
                    count=0
                    for category,key,expected_count in ITEMS:
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key)
                        require(main_panel.origins_button.isVisible(),'real_item_entry_exposes_acquisition_button')
                        QTest.mouseClick(main_panel.origins_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.origins_dialog;panel=dialog.panel
                        require(panel.entries.count()==expected_count and panel.entries.currentItem()is None and not panel.open_button.isEnabled(),'item_overview_has_exact_count_no_default_choice')
                        native(dialog)
                        for i,row in enumerate(panel.result['rows']):
                            select(panel.entries,row['key']);require(row['event_title']in panel.player.toPlainText()and row['choice']['title']in panel.player.toPlainText(),'plain_event_option_costs_and_scope')
                            require('不是完整获取池'in panel.player.toPlainText()and '原文未独立写明'in panel.player.toPlainText(),'no_complete_pool_or_invented_quantity')
                            QTest.mouseClick(panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.event_dialog;cp=child.panel
                            require((cp.event_id,cp.scene_id,cp.choice_id)==(row['event_id'],row['scene_id'],row['choice_id']),'each_of_six_routes_exact_event_scene_and_choice')
                            require(cp.result['actual_eligible']is None,'no_actual_eligibility_or_claim')
                            if key==ITEMS[0][1]:require(all(v is None for v in cp.result['declared'].values()),'memory_conditions_unknown_not_inventory_autofill')
                            elif key==ITEMS[1][1]:require(not hasattr(cp,'gold')and not hasattr(cp,'action_points'),'dog_has_no_unrelated_resource_controls')
                            else:require(cp.gold.value()==-1 and not hasattr(cp,'controller'),'controller_reward_cost_comparison_is_event_specific')
                            observations.append({'item_id':key,'origin_key':row['key'],'scene':cp.scene_id,'choice':cp.choice_id,'actual_received':cp.result.get('actual_received'),'actual_eligible':cp.result['actual_eligible']});count+=1
                            if i==0:
                                cp.player.setFocus();gui.processEvents();imagefile=dest.with_name('window-event-'+key+'.png');require(child.grab().save(str(imagefile),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'event-'+key,'path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(child)})
                            child.close()
                        shot(key)
                        dialog.close()
                    require(count==6,'all_six_acquisition_routes_exercised')
                    choose(main_panel.category,'relics');select(main_panel.entries,ITEMS[0][1]);require(main_panel.open_reward_origins(),'manual_memory_origins_open');dialog=main_panel.origins_dialog;panel=dialog.panel;select(panel.entries,panel.result['rows'][1]['key']);require(panel.open_event(),'origin_opens_memory_reader');child=panel.event_dialog;child.panel.processed_parts.setValue(2);dialog.resize(720,390);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);key=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole);tab=panel.tabs.currentIndex()
                        require(main_panel.refresh_reference(),'real_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)==key and panel.tabs.currentIndex()==tab,'two_real_nonzero_readings_selection_tab_origin_kept');require(child.isVisible()and child.panel.processed_parts.value()==2,'same_source_refresh_keeps_child_and_declared_condition');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    old=child;require(panel.open_event()and not old.isVisible(),'repeated_event_open_closes_previous');child=panel.event_dialog;select(panel.entries,panel.result['rows'][0]['key']);require(not child.isVisible()and panel.event_dialog is None,'changing_origin_closes_previous_event')
                    require(panel.open_event(),'event_reopened_for_real_source_loss');child=panel.event_dialog
                    damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()==''and not child.isVisible(),'real_source_damage_clears_old_list_text_and_event');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.entries.currentItem()is None and not panel.open_button.isEnabled(),'manual_source_recovery_requires_reselection')
                    select(panel.entries,panel.result['rows'][0]['key']);require(panel.open_event(),'manual_recovery_exact_origin_reopens');child=panel.event_dialog;main_panel.entries.setCurrentRow(-1);gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'parent_item_change_closes_entire_tree')
                    select(main_panel.entries,ITEMS[0][1]);require(main_panel.open_reward_origins(),'real_parent_can_reopen');dialog=main_panel.origins_dialog;panel=dialog.panel;select(panel.entries,panel.result['rows'][2]['key']);require(panel.open_event(),'third_cost_branch_opened');child=panel.event_dialog
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');main_panel.refresh_reference();require(not dialog.isVisible()and not child.isVisible()and main_panel.origins_button.isHidden(),'bad_supplement_parent_refresh_closes_tree_keeps_item_detail');require(main_panel.result['row']['id']==ITEMS[0][1],'old_item_description_preserved_when_new_supplement_fails');file.write_bytes(raw)
                    main_panel.refresh_reference();require(main_panel.origins_dialog is None,'parent_recovery_does_not_auto_reopen')
                    select(main_panel.entries,'rogue_6_relic_cargo_13');require(main_panel.origins_button.isHidden()and not main_panel.open_reward_origins(),'consumed_key_not_mislabelled_as_reward_origin')
                    select(main_panel.entries,ITEMS[1][1]);require(main_panel.open_reward_origins(),'dog_origins_reopen_for_MainWindow_close');dialog=main_panel.origins_dialog;panel=dialog.panel;select(panel.entries,panel.result['rows'][0]['key']);require(panel.open_event(),'dog_exact_origin_open_for_close');child=panel.event_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_close_closes_entire_new_reader_tree');done=True;gui.exit(0)
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
    after=bound_files();result={'section':338,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
