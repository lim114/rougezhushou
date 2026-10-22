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
    from rouge import current_peace as m,expansion_reference as v,current_node_readers as n
    for provider in(m,v,n):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.add(m.packet()['data']['icon_reference']['file'])
    names.update(['scripts/build_current_peace_343.py','scripts/verify_current_peace_window_343.py','scripts/verify_full_available.py','tests/test_current_peace_343.py','tests/test_current_peace_view_343.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py','tests/test_current_scout_view_342.py'])
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
        from rouge import app as app_module,current_peace as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge343-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第343节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_peace_343 import clone
                    main_panel=panel
                    def flow_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_version_entry_exposes_peace_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    data=model.reference()['data'];count=0
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;t=model.locate(category,key)
                            require((panel.scene_id,panel.choice_id)==(t['scene_id'],t['choice_id']),'all7_exact_original_entries_open_correct_scene_and_choice')
                            require(all(panel.result[k]is None for k in('actual_current_floor_completion','actual_target_node','actual_moved','actual_marked','actual_battle_won','actual_received','actual_attack_speed_stacks','actual_eligible')),'actual_conditions_movement_rewards_and_win_stacks_unknown')
                            count+=1;observations.append({'category':category,'key':key,'scene':panel.scene_id,'choice':panel.choice_id});dialog.close()
                    require(count==7,'all_seven_original_entries_exercised');dialog=flow_entry('scenes','scene_ro6_task1_enter');panel=dialog.panel
                    require(panel.choice_id is None and panel.choices.count()==2 and panel.reward_card.isHidden()and panel.completion_controls.isHidden()and panel.completed.currentData()is None,'overview_two_alternatives_no_default_reward_or_condition')
                    require(not any(hasattr(panel,n)for n in('offer','gold','difficulty','parts','operator','action_points')),'unrelated_resource_conditions_absent_not_disabled')
                    select(panel.choices,'choice_ro6_task1_1');require(panel.reward_card.isVisible()and not panel.reward_icon.pixmap().isNull()and panel.completion_controls.isHidden(),'join_exact_verified_item_image_no_move_control');text=panel.player.toPlainText()
                    require(all(x in text for x in('不等于已经前往或获胜','永久攻速奖励还要求作战胜利','+10也不是+10%','累计胜利次数')),'join_item_and_win_timing_separate_no_percent_or_stack_guess');shot('join')
                    require(panel.follow_scene()and panel.choices.count()==2 and panel.choice_id is None,'join_followup_has_only_move_and_mark');select(panel.choices,'choice_ro6_task1_3')
                    require(panel.completion_controls.isVisible()and not panel.battle_button.isVisible()and not panel.follow_scene(),'only_move_condition_visible_no_fabricated_map_or_next')
                    for value in(None,True,False):
                        choose(panel.completed,value);c=model.choice_reference(panel.result,panel.scene_id,panel.choice_id);require(c['documented_no_move_reference']is(True if value is True else None),'all_three_completion_values_keep_one_way_exception');require(panel.result['actual_moved']is None and panel.result['actual_target_node']is None,'comparison_never_actual_move_or_target')
                        text=panel.player.toPlainText();require('未完成并不保证一定移动'in text,'one_way_not_inverted')
                        if value is False:require('仍不能据此保证移动或指定目的地'in text,'false_condition_not_success_proof')
                        if value is True:require('这不是本局实际状态'in text,'true_condition_only_declared_reference')
                    shot('move-unknown-result');choose(panel.completed,True);shot('move-completed');select(panel.choices,'choice_ro6_task1_4')
                    require(panel.completion_controls.isHidden()and panel.reward_card.isVisible(),'mark_hides_move_only_control_keeps_item_reference')
                    require('标记不表示已移动、进入作战或取得胜利'in panel.player.toPlainText()and not panel.battle_button.isVisible()and not panel.follow_scene(),'mark_not_move_battle_or_win');shot('mark')
                    panel.go_start();select(panel.choices,'choice_ro6_task1_2');require(panel.reward_card.isHidden()and panel.reward_icon.pixmap().isNull()and panel.completion_controls.isHidden(),'leave_clears_reward_image_and_move_controls');shot('leave');require(panel.follow_scene()and panel.choices.count()==0,'leave_terminal_no_reward_or_rejoin')
                    panel.scene.setCurrentIndex(panel.scene.findData('scene_ro6_task1_1'));gui.processEvents();select(panel.choices,'choice_ro6_task1_3');choose(panel.completed,False);dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);before_choice=panel.choice_id;tab=panel.tabs.currentIndex();condition=panel.completed.currentData();require(main_panel.refresh_reference(),'real_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.choice_id==before_choice and panel.tabs.currentIndex()==tab and panel.completed.currentData()is condition,'two_real_nonzero_readings_choice_tab_and_condition_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes();picture=damaged/data['icon_reference']['file'];picture_raw=picture.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        picture.write_bytes(picture_raw+b'x');before_text=panel.player.toPlainText();require(panel.refresh_reference()and panel.player.toPlainText()==before_text and '图片暂缺'in panel.reward_icon.text(),'damaged_ornament_keeps_verified_item_text');picture.write_bytes(picture_raw);require(panel.refresh_reference()and not panel.reward_icon.pixmap().isNull(),'verified_item_image_restored')
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()==''and panel.reward_card.isHidden()and panel.reward_icon.pixmap().isNull()and panel.completion_controls.isHidden(),'actual_source_damage_clears_reading_image_and_conditions');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_no_old_choice_restore')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_parent_open_closes_previous_reader');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_reader')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_019'));gui.processEvents();QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel
                    require(panel.choice_id is None and panel.reward_card.isHidden()and panel.completed.currentData()is None,'node_overview_defaults_unknown_no_reward_or_condition');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'node_version_notice_visible');node.refresh();require(dialog.isVisible(),'node_same_source_refresh_keeps_reader');imagefile=dest.with_name('window-node-banner.png');require(dialog.grab().save(str(imagefile),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'node-banner','path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_loss_keeps_old_catalogue_text');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'node_recovery_requires_manual_open')
                    node_dialog=node.current_reference_window;idx=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();dialog=flow_entry('choices','choice_ro6_task1_3');panel=dialog.panel
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not node_dialog.isVisible(),'actual_MainWindow_close_cleans_both_current_reader_entries');done=True;gui.exit(0)
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
    after=bound_files();result={'section':343,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
