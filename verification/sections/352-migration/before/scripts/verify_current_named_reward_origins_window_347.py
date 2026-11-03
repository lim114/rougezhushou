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
    from rouge import current_named_reward_origins as m,expansion_reference as v,current_reward_origins as n
    providers=[m,v,n,*m.providers().values(),*n.PROVIDERS.values()]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/build_current_named_reward_origins_347.py','scripts/verify_current_named_reward_origins_window_347.py','scripts/verify_full_available.py','tests/test_current_named_reward_origins_347.py','tests/test_current_named_reward_origins_view_347.py','tests/test_current_reward_origins_338.py','tests/test_current_reward_origins_view_338.py'])
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
        from rouge import app as app_module,current_named_reward_origins as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge347-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第347节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_named_reward_origins_347 import clone
                    from rouge import current_reward_origins as unified
                    main_panel=panel
                    def origins_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.origins_button.isVisible(),'real_version_item_exposes_named_acquisition_entry');QTest.mouseClick(main_panel.origins_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.origins_dialog
                    rows=model.packet()['data']['rows'];require(len(rows)==11 and len({r['item_id']for r in rows})==11 and len({r['reader_key']for r in rows})==7,'eleven_new_items_seven_existing_readers')
                    for row in rows:
                        dialog=origins_entry('relics',row['item_id']);panel=dialog.panel;require(panel.entries.count()==1 and panel.entries.currentItem()is None and not panel.open_button.isEnabled()and panel.event_dialog is None,'new_items_no_default_selection_or_claim')
                        select(panel.entries,row['key']);require('不补成1件'in panel.player.toPlainText()and '完整获取池'in panel.player.toPlainText(),'quantity_and_complete_pool_not_claimed');QTest.mouseClick(panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.event_dialog;target=row['target'];require(child is not None and child.isVisible(),'all11_actual_mouse_open_owned_reader')
                        if 'source_request'in target:require(child.panel.result['source_request']==target['source_request']and child.panel.result['requested_original']==row['choice']and child.panel.choice_id=='source-choice','raw_source_targets_keep_exact_original_choice_and_scope')
                        else:require((child.panel.scene_id,child.panel.choice_id)==(target['scene_id'],target['choice_id']),'document_targets_keep_exact_scene_and_choice')
                        require(child.panel.result['actual_eligible']is None and not child.panel.result['run_updated'],'all11_actual_qualification_and_inventory_remain_unknown')
                        require(panel.result['actual_quantity']is None and panel.result['actual_received']is None and not panel.result['complete_acquisition_pool'],'new_rows_not_auto_received_or_complete_pool')
                        observations.append({'category':'relics','key':row['item_id'],'original_choice':row['choice_id'],'reader':row['reader_key'],'scene':child.panel.scene_id,'choice':child.panel.choice_id});dialog.close();require(not child.isVisible(),'each_parent_close_cleans_own_event')
                    dialog=origins_entry('relics','rogue_6_relic_cargo_13');panel=dialog.panel;require(panel.entries.maximumHeight()==120 and panel.player.height()>panel.entries.height(),'short_acquisition_list_leaves_more_space_for_reading');shot('key-list');select(panel.entries,'named347:choice_ro6_surprise_1');require('没有给出物品编号'in panel.player.toPlainText()and '不能合计198'in panel.player.toPlainText(),'missing_key_pointer_and_double99_limit_visible');require(panel.open_event(),'key_exact_source_event_open');child=panel.event_dialog;require(child.panel.follow_scene(),'key_child_reading_advanced_to_explicit_next');dialog.resize(720,390);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(3,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'real_version_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)=='named347:choice_ro6_surprise_1'and panel.tabs.currentIndex()==tab,'two_real_nonzero_readings_selection_and_tab_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    require(panel.event_dialog is child and child.isVisible()and child.panel.scene_id=='source-next','nested_original_reading_keeps_explicit_next_after_real_parent_refresh');panel.tabs.setCurrentIndex(0);shot('key-selected');old=child;require(panel.open_event()and not old.isVisible(),'repeat_open_closes_previous_child');old=panel.event_dialog;panel.entries.setCurrentRow(-1);require(not old.isVisible()and panel.event_dialog is None,'choice_deselect_closes_child')
                    dialog=origins_entry('relics','rogue_6_relic_cargo_12');panel=dialog.panel;select(panel.entries,'named347:choice_ro6_normal2_1');require('持有笼控器是条件'in panel.player.toPlainText()and panel.result['item']['name']=='猎印','held_controller_not_mislisted_as_reward_or_consumed');require(panel.open_event()and panel.event_dialog.panel.controller.currentData()is None,'hunter_only_required_control_default_unknown');shot('hunter-condition')
                    dialog=origins_entry('relics','rogue_6_relic_final_6');panel=dialog.panel;select(panel.entries,'named347:choice_ro6_sacrifice2_21');require('不能在本项再扣一次'in panel.player.toPlainText(),'civilization_receipt_not_second_natural_payment');require(panel.open_event()and panel.event_dialog.panel.natural_controls.isHidden(),'civilization_receipt_hides_unrelated_natural_count_control');shot('civilization-receipt')
                    dialog=origins_entry('relics','rogue_6_relic_artifact_4');panel=dialog.panel;select(panel.entries,'named347:choice_ro6_normal4_26');require(panel.open_event(),'dog_reward_exact_event_open');child=panel.event_dialog;require(child.panel.reward_card.isVisible()and not child.panel.reward_icon.pixmap().isNull()and '攻击力+10%'in child.panel.player.toPlainText(),'dog_named_picture_and_effect_remain_exact');shot('dog-source')
                    for category,iid in[('relics','rogue_6_relic_artifact_5'),('relics','rogue_6_relic_cargo_10'),('scrap','rogue_6_scrap_G_12')]:
                        dialog=origins_entry(category,iid);panel=dialog.panel
                        for i,row in enumerate(panel.result['rows']):
                            select(panel.entries,row['key']);require(panel.open_event(),'six_old338_exact_targets_retained');child=panel.event_dialog;require((child.panel.event_id,child.panel.scene_id,child.panel.choice_id)==(row['event_id'],row['scene_id'],row['choice_id']),'old_six_exact_reader_scene_choice_unchanged');observations.append({'category':category,'key':iid,'reader':row['reader'],'scene':child.panel.scene_id,'choice':child.panel.choice_id})
                        if category=='scrap':require(panel.entries.count()==2,'old_controller_two_acquisitions_not_recounted_new');shot('old-controller')
                    require(len(observations)==17,'all17_old_and_new_choice_links_actual_window_exercised')
                    dialog=origins_entry('relics','rogue_6_relic_cargo_13');panel=dialog.panel;select(panel.entries,'named347:choice_ro6_surprise_1');require(panel.open_event(),'event_open_before_source_loss');child=panel.event_dialog;damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b'x');require(not panel.refresh_reference()and panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()==''and not child.isVisible(),'source_loss_clears_list_text_and_owned_event');shot('source-loss');require(unified.reference('relics','rogue_6_relic_artifact_5')is not None,'new_source_damage_does_not_remove_old338');file.write_bytes(raw);require(panel.refresh_reference()and panel.entries.currentItem()is None and not panel.open_button.isEnabled()and not panel.open_event(),'source_recovery_requires_manual_reselection')
                    select(panel.entries,'named347:choice_ro6_surprise_1');panel.result['rows'][0]['target']={};require(not panel.open_event()and panel.result is None,'forged_target_rejected_before_child_open');require(panel.refresh_reference(),'manual_restore_after_forged_local_reading');select(panel.entries,'named347:choice_ro6_surprise_1');require(panel.open_event(),'child_reopened_for_root_close');child=panel.event_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_acquisition_and_event_tree')
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
    after=bound_files();result={'section':347,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
