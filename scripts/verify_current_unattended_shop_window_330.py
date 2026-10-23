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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-unattended-shop-330'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-unattended-shop-330/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_unattended_shop_330.py','scripts/verify_current_unattended_shop_window_330.py','scripts/verify_full_available.py','tests/test_current_unattended_shop_330.py','tests/test_current_unattended_shop_view_330.py'])
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
        from rouge import app as app_module,current_unattended_shop as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge330-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第330节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    def flow_entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_whole_encounter');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    from tests.test_current_unattended_shop_330 import clone,by_original
                    d=model.reference()
                    for category,keys in(('scenes',d['scenes']),('choices',d['data']['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;target=model.locate(category,key);require((panel.scene_id,panel.choice_id,panel.result['requested_original_id'])==(target['scene_id'],target['choice_id'],target['original_choice_id']),'all15_exact_version_entries_keep_requested_original_not_live_variant');require(panel.result['actual_variant']is None,'requested_original_not_actual_variant');dialog.close()
                    dialog=flow_entry('scenes','scene_ro6_wish_enter');panel=dialog.panel
                    for sid,scene in panel.result['scenes'].items():
                        choose(panel.scene,sid);require(panel.choices.count()==len(scene['choice_ids']),'all4_scenes_only_entry_has_choices')
                        for key in scene['choice_ids']:
                            select(panel.choices,key);c=panel.result['choices'][key];require(c['title']in panel.player.toPlainText()and not panel.battle_button.isVisible(),'all4_groups_readable_without_false_battle');observations.append({'scene':sid,'group':key,'variants':c['variant_ids'],'next_scene_ids':c['next_scene_ids'],'reward_quantity':c['reward_quantity_reference'],'gold_cost':c['gold_cost_reference']})
                    dialog.close();dialog=flow_entry('choices','choice_ro6_wish_6');panel=dialog.panel;selected=panel.choice_id;panel.gold.setValue(0)
                    for held in(None,False,True):
                        choose(panel.fossil,held);require(panel.choice_id==selected and panel.next_button.isEnabled()==(held is not False),'fossil_three_states_gate_only_held_choice')
                        if held is False:require(not panel.follow_scene(),'missing_fossil_stops_only_held_followup');shot('fossil-unmet')
                    require('增加可选项不等于增加领取件数'in panel.player.toPlainText()and '未写交出或消耗'in panel.player.toPlainText(),'held_not_consumed_and_option_count_not_reward_count');shot('fossil-held');choose(panel.fossil,False);select(panel.choices,by_original(panel.result,2)['id']);require(panel.next_button.isEnabled()and panel.follow_scene()and panel.scene_id=='scene_ro6_wish_1','two_small_barrels_one_reward_independent_of_fossil_or_gold')
                    dialog.close();dialog=flow_entry('choices','choice_ro6_wish_8');panel=dialog.panel;require(panel.result['requested_original_id']=='choice_ro6_wish_8'and panel.result['actual_variant']is None,'exact_second_original_record_kept_for_reference_only');require(not panel.follow_scene()and all(b.isVisible()for b in panel.followup_buttons),'two_same_text_followups_no_default_next');require(not panel.open_documented_followup('scene_ro6_wish_1'),'unlisted_followup_rejected');panel.gold.setValue(3);require(not any(b.isEnabled()for b in panel.followup_buttons)and not panel.open_documented_followup('scene_ro6_wish_3'),'three_gold_blocks_both_four_gold_followups');shot('upgrade-unmet');panel.gold.setValue(4);choose(panel.fossil,False);require(all(b.isEnabled()for b in panel.followup_buttons),'four_gold_unlocks_reading_without_requiring_fossil');require('不是当场又获得1件'in panel.player.toPlainText()and '累计成8'in panel.player.toPlainText(),'upgrade_not_reward_or_duplicate_payment');shot('upgrade-two-records');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'same_source_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.gold.value()==4 and panel.fossil.currentData()is False and panel.result['requested_original_id']=='choice_ro6_wish_8','parent_refresh_keeps_two_readers_conditions_and_original_record');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'gold':panel.gold.value(),'has_fossil':panel.fossil.currentData()})
                    panel.tabs.setCurrentWidget(panel.player)
                    for sid in('scene_ro6_wish_2','scene_ro6_wish_3'):
                        panel.go_start();select(panel.choices,by_original(panel.result,3)['id']);button=next(b for b in panel.followup_buttons if b.property('sceneId')==sid);QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id==sid and panel.choices.count()==0 and panel.result['actual_upgrade']is None,'each_same_text_record_separate_no_loop_or_tier');shot('followup-'+sid.rsplit('_',1)[1])
                    panel.go_start();select(panel.choices,by_original(panel.result,3)['id']);damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference(),'actual_shop_bytes_damage_detected');require(panel.result is None and panel.technical.toPlainText()==''and not any(b.isVisible()for b in panel.followup_buttons),'source_loss_clears_choices_and_followup_buttons');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None and panel.result['requested_original_id']is None,'manual_recovery_drops_old_scene_choice_and_original_source')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_parent_open_closes_previous_shop');dialog=main_panel.flow_dialog;panel=dialog.panel;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_shop_flow')
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
    after=bound_files();result={'section':330,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
