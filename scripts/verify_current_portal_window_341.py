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
    from rouge import current_portal as m,expansion_reference as v,current_node_readers as n,current_agency as agency
    for provider in(m,v,n,agency):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update('rouge/data/'+v['file']for v in agency.packet()['data']['profession_icons'].values())
    names.update(['scripts/build_current_portal_341.py','scripts/verify_current_portal_window_341.py','scripts/verify_full_available.py','tests/test_current_portal_341.py','tests/test_current_portal_view_341.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py','tests/test_current_agency_view_340.py'])
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
        from rouge import app as app_module,current_portal as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge341-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第341节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_portal_341 import clone
                    from PySide6.QtCore import QEvent
                    main_panel=panel
                    def flow_entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_version_entry_exposes_portal_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    data=model.reference()['data'];count=0
                    for category,records in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key,original in records.items():
                            dialog=flow_entry(category,key);panel=dialog.panel;require(panel.source_request=={'category':category,'key':key}and panel.result['requested_original']==original,'all190_original_entries_keep_exact_complete_source');require(panel.parts.value()==-1 and all(panel.result[k]is None for k in('actual_inventory','actual_consumed','actual_teleported','actual_destination','actual_variant','actual_eligible')),'no_actual_inventory_payment_destination_or_variant_claim')
                            if category=='scenes':require(panel.scene_id=='source-scene'and panel.choices.count()==0,'raw_scene_not_assigned_guessed_outgoing_choices')
                            else:
                                require(panel.scene_id=='source-choice'and panel.choice_id=='source-choice','raw_choice_separate_unproven_parent_reference')
                                if original['nextSceneId']:
                                    require(panel.follow_scene()and panel.scene_id=='source-next'and panel.choices.count()==0 and panel.result['scenes']['source-next']['source_scene_ids']==[original['nextSceneId']],'every_explicit_raw_pointer_exact_no_outgoing_stitch')
                                else:require(not panel.follow_scene()and not panel.next_button.isVisible()and not panel.open_battle(),'teleport_no_invented_scene_map_or_second_payment')
                            if category=='choices'and original['nextSceneId']is None:require(panel.result['requested_choice_association']=='full_literal_teleport_candidate'and '尚未证明其属于溯源'in panel.player.toPlainText(),'19_literal_teleport_candidates_not_proven_server_parent')
                            observations.append({'category':category,'key':key,'requested_source':panel.source_request,'actual_context':panel.scene_id,'raw_next':original.get('nextSceneId'),'actual_destination':panel.result['actual_destination']});count+=1
                            dialog.close();main_panel.flow_dialog=None;dialog.deleteLater();gui.sendPostedEvents(None,QEvent.Type.DeferredDelete);dialog=None
                    require(count==190,'all190_exact_original_entries_exercised_with_owned_fixture_cleanup')
                    dialog=flow_entry('scenes','scene_ro6_portal1a_enter');panel=dialog.panel;require(panel.scene_id=='source-scene'and panel.choices.count()==0,'opening_raw_red_narrative_does_not_select_document_menu');panel.go_start();require(panel.scene_id=='overview'and panel.parts.value()==-1,'document_overview_not_assumed_fog_or_inventory');require(not any(hasattr(panel,n)for n in('gold','difficulty','offer','controller','source_key')),'no_unrelated_controls')
                    for fog in('红雾','蓝雾','绿雾','金雾','橙雾','紫雾'):
                        choose(panel.scene,'fog:'+fog);require(fog in panel.player.toPlainText(),'all_six_plain_fog_names_and_own_narrative');ids={panel.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.choices.count())};require(('no-engine:alt'in ids)==(fog=='红雾'),'red_alternate_caption_not_universal')
                        if fog=='绿雾':require({'leave:0','leave:1'}<=ids and '实际选择依据未知'in panel.player.toPlainText(),'green_conflict_both_candidates_no_default_resolution')
                        shot('fog-'+fog)
                    choose(panel.scene,'fog:红雾');select(panel.choices,'pay:1');panel.parts.setValue(0);require(not panel.follow_scene(),'zero_processed_parts_blocks_payment');select(panel.choices,'leave:0');require(not panel.follow_scene(),'document_leave_has_processed_part_rowspan_condition');select(panel.choices,'no-engine:normal');require(panel.follow_scene()and panel.choices.count()==0,'zero_processed_parts_reads_no_engine_narrative')
                    choose(panel.scene,'fog:红雾');select(panel.choices,'pay:1');panel.parts.setValue(1);require(panel.follow_scene()and panel.scene_id=='after:1','one_processed_part_reads_only_selected_payment_followup');select(panel.choices,'confirm:1');require(panel.part_controls.isHidden()and not panel.next_button.isVisible()and not panel.open_battle()and '不把确认当作再次支付1件'in panel.player.toPlainText(),'confirmation_no_second_cost_or_map_guess');shot('confirmation')
                    for i in(2,3):
                        choose(panel.scene,'fog:红雾');select(panel.choices,'pay:'+str(i));require(panel.follow_scene()and panel.scene_id=='after:'+str(i),'three_payment_alternatives_keep_separate_document_occurrences')
                    choose(panel.scene,'fog:红雾');select(panel.choices,'no-engine:alt');require(not panel.follow_scene(),'positive_inventory_does_not_match_no_engine_branch');choose(panel.scene,'fog:绿雾');select(panel.choices,'leave:1');require(panel.follow_scene()and panel.scene_id=='leave:1','green_second_leave_remains_independently_readable')
                    choose(panel.scene,'fog:红雾');select(panel.choices,'pay:2');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);before_choice=panel.choice_id;tab=panel.tabs.currentIndex();parts=panel.parts.value();source=dict(panel.source_request);require(main_panel.refresh_reference(),'actual_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.choice_id==before_choice and panel.tabs.currentIndex()==tab and panel.parts.value()==parts and panel.source_request==source,'two_nonzero_readings_selection_tab_condition_and_source_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()==''and panel.part_controls.isHidden(),'real_source_loss_clears_old_reading_and_controls');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_does_not_restore_old_context')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_parent_open_closes_previous_reader');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_reader');node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_027'));gui.processEvents();QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel;require(panel.scene_id=='overview'and panel.source_request is None and panel.parts.value()==-1,'node_opens_unknown_fog_and_parts_overview');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'node_version_notice_visible');node.refresh();require(dialog.isVisible(),'node_refresh_keeps_reader');imagefile=dest.with_name('window-node-banner.png');require(dialog.grab().save(str(imagefile),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'node-banner','path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_loss_keeps_old_catalogue_text');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'node_recovery_requires_manual_open')
                    node_dialog=node.current_reference_window;idx=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();dialog=flow_entry('choices','choice_ro6_portal1a_4');panel=dialog.panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not node_dialog.isVisible(),'actual_MainWindow_close_cleans_both_entry_readers');done=True;gui.exit(0)
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
    after=bound_files();result={'section':341,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
