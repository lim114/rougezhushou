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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-vine-events-333'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-vine-events-333/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_vine_events_333.py','scripts/verify_current_vine_events_window_333.py','scripts/verify_full_available.py','tests/test_current_vine_events_333.py','tests/test_current_vine_events_view_333.py'])
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
        from rouge import app as app_module,current_vine_events as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge333-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第333节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_vine_events_333 import clone,by_original
                    data=model.packet()['data'];entry_count=0
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;t=model.locate(category,key);require((panel.event_id,panel.scene_id,panel.choice_id)==(t['event_id'],t['scene_id'],t['choice_id']),'all14_original_entries_keep_exact_event_scene_choice');require(panel.result['actual_eligible']is None and panel.result['actual_future_region']is None,'source_entry_not_actual_eligibility_or_weather');entry_count+=1;dialog.close()
                    for title,event in data['events'].items():
                        dialog=flow_entry('scenes',event['entry_scene_id']);panel=dialog.panel
                        require(hasattr(panel,'gold')==(title=='沉寂之屋')and hasattr(panel,'controller')==(title=='呼吸的红苔')and hasattr(panel,'seeds')==(title=='呼吸的红苔'),'only_relevant_event_condition_controls')
                        for sid,scene in panel.result['scenes'].items():
                            choose(panel.scene,sid);require(panel.choices.count()==len(scene['choice_ids']),'all8_scenes_preserve_their_complete_choices')
                            for key in scene['choice_ids']:
                                select(panel.choices,key);c=panel.result['choices'][key];require(c['title']in panel.player.toPlainText()and not panel.battle_button.isVisible(),'all6_choices_readable_no_false_battle');observations.append({'event':title,'scene':sid,'choice':key,'original_ids':c['variant_ids'],'next':c['next_scene_id']})
                        dialog.close()
                    require(entry_count==14,'fourteen_version_entries_exercised')
                    dialog=flow_entry('choices','choice_ro6_normal1_2');panel=dialog.panel;panel.gold.setValue(7);require(not panel.follow_scene()and not panel.next_button.isEnabled(),'7gold_blocks_only8gold_choice');shot('house-seven-gold');panel.gold.setValue(8);require(panel.follow_scene(),'8gold_allows_documented_followup_not_actual_payment');panel.go_start();select(panel.choices,by_original(panel.result,'choice_ro6_normal1_1')['id']);panel.gold.setValue(0);require('2目标生命值'in panel.player.toPlainText()and '不套用黑诞的保底规则'in panel.player.toPlainText(),'target_life_cost_not_operator_hp_or_copied_life_floor');require('不是收藏品'in panel.player.toPlainText()and '不自动补成1件'in panel.player.toPlainText(),'named_scrap_not_relic_or_guessed_quantity');shot('house-target-life');require(panel.follow_scene(),'gold_does_not_block_independent_target_life_branch');dialog.close()
                    dialog=flow_entry('choices','choice_ro6_normal3_1');panel=dialog.panel;choose(panel.controller,False);panel.seeds.setValue(3);require(not panel.follow_scene(),'seeds_do_not_satisfy_controller_branch');choose(panel.controller,True);require('30源石锭'in panel.player.toPlainText()and '持有不等于已经消耗'in panel.player.toPlainText(),'30gold_only_controller_branch_no_assumed_controller_spend');require('不是现在全队获得属性加成'in panel.player.toPlainText(),'future_region_not_current_map_or_team_modifier');shot('red-controller');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'same_source_version_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.controller.currentData()is True and panel.seeds.value()==3,'parent_refresh_keeps_both_real_readers_choice_and_local_conditions');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'controller':True,'seeds':3})
                    panel.tabs.setCurrentIndex(0);panel.go_start();select(panel.choices,by_original(panel.result,'choice_ro6_normal3_2')['id']);panel.seeds.setValue(0);require(not panel.follow_scene(),'zero_seeds_blocks_sowing');panel.seeds.setValue(1);choose(panel.controller,False);require('不是获得1枚种子'in panel.player.toPlainText()and '选择时的直接变化'not in panel.player.toPlainText(),'seed_is_consumed_not_reward_or30gold');shot('red-seed');require(panel.follow_scene(),'one_seed_branch_independent_of_controller');panel.go_start();select(panel.choices,by_original(panel.result,'choice_ro6_normal3_3')['id']);panel.seeds.setValue(0);require(panel.follow_scene(),'leave_independent_of_all_special_conditions');shot('red-leave')
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()=='','actual_vine_bytes_damage_clears_old_reading');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_requires_scene_and_choice_reselection')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_version_open_closes_previous_reader');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_reader')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is node,'actual_MainWindow_node_tab_opened')
                    node.runtime_context={'gold':100,'has_controller':True,'seeds':3}
                    for event_id in model.CATALOGUE_IDS:
                        node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:'+event_id));gui.processEvents();require(node.current_reference_button.isVisible(),'both_new_node_catalogue_entries_available');QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel;require(panel.choice_id is None and panel.result['actual_eligible']is None,'catalogue_entry_not_actual_choice');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'real_dialog_current_version_notice')
                        if hasattr(panel,'gold'):require(panel.gold.value()==-1,'run_gold_not_auto_applied')
                        else:require(panel.controller.currentData()is None and panel.seeds.value()==-1,'run_controller_and_seed_not_auto_applied')
                        node.refresh();require(dialog.isVisible(),'catalogue_same_source_refresh_preserves_reader')
                    file=damaged/model.DATA
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'bridge_source_loss_closes_new_reader_but_legacy_text_remains');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'catalogue_recovery_requires_manual_open')
                    dialog=node.current_reference_window;panel=dialog.panel;gui.processEvents();imagefile=dest.with_name('window-node-version-notice.png');require(dialog.grab().save(str(imagefile),'PNG'),'actual_dialog_banner_screenshot_saved');images.append({'name':'node-version-notice','path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(dialog)})
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_close_closes_new_node_reader');done=True;gui.exit(0)
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
    after=bound_files();result={'section':333,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
