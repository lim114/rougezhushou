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
    from rouge import current_exit as m,expansion_reference as v,current_node_readers as n
    for provider in(m,v,n):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/build_current_exit_339.py','scripts/verify_current_exit_window_339.py','scripts/verify_full_available.py','tests/test_current_exit_339.py','tests/test_current_exit_view_339.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py','tests/test_current_reward_origins_view_338.py'])
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
        from rouge import app as app_module,current_exit as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge339-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第339节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_exit_339 import clone
                    main_panel=panel
                    def flow_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_version_entry_exposes_exit_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    data=model.reference()['data'];count=0
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices']),('relics',['rogue_6_relic_final_7'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;require(panel.source_request=={'category':category,'key':key},'all14_original_entries_keep_exact_source_request');require(all(v is None for v in panel.result['declared'].values()),'every_entry_defaults_to_unknown_conditions');require(panel.result['actual_eligible']is None and panel.result['actual_received']is None,'no_eligibility_or_reward_claim')
                            target=panel.result['source_targets']
                            if len(target)>1:require(panel.scene_id is None and panel.choice_id is None and '不止一处'in panel.player.toPlainText(),'ambiguous_source_does_not_pick_document_occurrence')
                            else:require((panel.scene_id,panel.choice_id)==target[0],'unique_source_opens_exact_context_and_choice')
                            observations.append({'category':category,'key':key,'source_request':panel.source_request,'scene':panel.scene_id,'choice':panel.choice_id,'source_targets':target,'actual_received':panel.result['actual_received']});count+=1;dialog.close()
                    require(count==14,'all_fourteen_original_entries_exercised')
                    dialog=flow_entry('scenes','scene_ro6_final1_enter');panel=dialog.panel
                    def role(name,occurrence=0):
                        c=[v for v in panel.result['choices'].values()if v['role']==name][occurrence];choose(panel.scene,c['scene_id']);select(panel.choices,c['id']);return c
                    require(not any(hasattr(panel,n)for n in('controller','source_key','processed_parts','seeds')),'no_unrelated_event_controls');require(panel.choices.count()==4,'root_has_only_four_documented_options_no_invented_three')
                    role('persuade_part');panel.action_points.setValue(7);panel.difficulty.setValue(15);require('等量希望为7'in panel.player.toPlainText()and '基础奖励为1件加工品'in panel.player.toPlainText(),'grade15_base_part_and_separate_equal_conversion');shot('grade15-base')
                    panel.difficulty.setValue(16);require('本节点不再获得加工品'in panel.player.toPlainText()and not panel.follow_scene(),'grade16_override_keeps_old_prose_but_blocks_part_variant');require(all(c['actual_variant_id']is None for c in panel.result['choices'].values()),'difficulty_never_chooses_hidden_original');shot('grade16-no-part')
                    panel.difficulty.setValue(15);require(panel.follow_scene()and panel.choices.count()==2,'documented_first_persuade_reaches_two_branch_options');role('confirm');require('不把取得加工品与后续确认当成两次希望奖励相加'in panel.player.toPlainText()and not panel.next_button.isVisible(),'confirmation_no_extra_reward_or_invented_next_map');shot('confirmation')
                    role('persuade_part',1);require(panel.follow_scene()and panel.scene_id=='document:exit-repeat-result'and panel.choices.count()==0,'repeat_narrative_occurrence_is_terminal_not_farming_loop');shot('repeat-terminal')
                    for i in range(2):
                        role('persuade_no_part',i);require('前置情景没有文献证据'in panel.player.toPlainText(),'source_only_variant_not_attached_to_initial_menu');require(panel.follow_scene()and panel.scene_id=='document:exit-repeat-result','source_only_variant_only_reads_exact_known_followup')
                    role('persuade_no_part');shot('source-only')
                    role('recruit');require('不能显示免费招募'in panel.player.toPlainText()and '重新判定随机效果'in panel.player.toPlainText(),'stashed_ticket_no_free_recruit_or_fixed_random_result');require(panel.follow_scene()and panel.choices.count()==0,'recruit_narrative_no_invented_loop_or_region_move');shot('recruit')
                    role('leave');require(panel.follow_scene()and panel.choices.count()==0,'leave_has_own_terminal_narrative_no_transition')
                    role('help');panel.gold.setValue(9);require(not panel.follow_scene(),'gold9_blocks_only_help_followup');panel.gold.setValue(10);require('谒日之祈'in panel.player.toPlainText()and '没有独立件数'in panel.player.toPlainText(),'gold10_named_reward_without_quantity_or_map_guess');shot('help-reward');require(panel.follow_scene()and panel.choices.count()==0,'gold10_can_read_help_narrative_not_grant')
                    role('help');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);before_choice=panel.choice_id;tab=panel.tabs.currentIndex();declared=dict(panel.result['declared']);request=dict(panel.source_request)
                        require(main_panel.refresh_reference(),'real_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.choice_id==before_choice and panel.tabs.currentIndex()==tab and panel.result['declared']==declared and panel.source_request==request,'two_real_nonzero_readings_choice_tab_conditions_and_source_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()=='','actual_source_damage_clears_old_exit_reading');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_does_not_restore_old_choice')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_parent_open_closes_previous_reader');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_reader')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_033'));gui.processEvents();QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel;require(panel.choice_id is None and all(v is None for v in panel.result['declared'].values()),'node_overview_does_not_reuse_page_conditions');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'node_version_notice_visible');node.refresh();require(dialog.isVisible(),'node_same_source_refresh_keeps_reader');imagefile=dest.with_name('window-node-banner.png');require(dialog.grab().save(str(imagefile),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'node-banner','path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_loss_keeps_old_catalogue_text');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'node_recovery_requires_manual_open')
                    node_dialog=node.current_reference_window;idx=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();dialog=flow_entry('relics','rogue_6_relic_final_7');panel=dialog.panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not node_dialog.isVisible(),'actual_MainWindow_close_cleans_both_current_reader_entries');done=True;gui.exit(0)
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
    after=bound_files();result={'section':339,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
