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
    from rouge import current_resting as m,expansion_reference as v,current_node_readers as n
    for provider in(m,v,n):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.add(m.packet()['data']['icon_reference']['file'])
    names.update(['scripts/build_current_resting_345.py','scripts/verify_current_resting_window_345.py','scripts/verify_full_available.py','tests/test_current_resting_345.py','tests/test_current_resting_view_345.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py','tests/test_current_reconstruction_view_344.py'])
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
        from rouge import app as app_module,current_resting as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge345-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第345节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_resting_345 import clone
                    main_panel=panel
                    def flow_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_version_entry_exposes_resting_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    data=model.reference()['data'];count=0;explicit=0;candidate=0
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;v=data['originals'][category][key];require(panel.result['requested_original']==v,'all24_exact_original_records_preserved_complete')
                            require(all(panel.result[k]is None for k in('actual_inventory','actual_received','actual_result','actual_choice','actual_transition','actual_eligible','actual_pool','actual_left','actual_gold_total')),'actual_results_inventory_transition_pool_and_gold_total_unknown')
                            if category=='scenes':require(panel.scene_id=='source-scene'and panel.choices.count()==0,'all12_raw_scenes_no_guessed_menu')
                            else:
                                require(panel.scene_id=='source-choice'and panel.choice_id=='source-choice','raw_choices_open_exact_own_row')
                                if v['nextSceneId']:explicit+=1;require(panel.follow_scene()and panel.choices.count()==0 and panel.result['scenes'][panel.scene_id]['description']==data['originals']['scenes'][v['nextSceneId']]['description'],'all8_explicit_next_exact_no_more_menu')
                                else:candidate+=1;require(not panel.follow_scene()and '随机候选没有指定下一段'in panel.player.toPlainText(),'all4_no_next_candidates_no_assumed_case_or_result')
                            observations.append({'category':category,'key':key,'scene':panel.scene_id,'choice':panel.choice_id});count+=1;dialog.close()
                    require((count,explicit,candidate)==(24,8,4),'all24_original_scope_accounted');dialog=flow_entry('scenes','scene_ro6_surprise_enter');panel=dialog.panel;panel.go_start()
                    require(panel.choice_id is None and panel.choices.count()==1 and panel.reward_card.isHidden()and panel.original_button.isHidden(),'default_no_item_result_or_conflict_popup_guess');require(not any(hasattr(panel,k)for k in('naturals','gold','offer','difficulty','operator','action_points')),'unrelated_conditions_absent_not_disabled')
                    select(panel.choices,'option:enter');require(panel.reward_card.isVisible()and not panel.reward_icon.pixmap().isNull(),'unique_named_key_reference_and_exact_icon');require(data['named_item_binding']['original_item_pointer']is None and '没有给出物品编号'in panel.player.toPlainText()and '不能相加成198'in panel.player.toPlainText(),'missing_original_item_pointer_and_double99_not_fabricated');shot('named-key')
                    paths=[(['dog','dog-orchard'],'doc:20'),(['dog','dog-race'],'doc:24'),(['net','observe'],'doc:26'),(['net','net-mud'],'doc:30'),(['squirrel','squirrel-orchard'],'doc:34'),(['squirrel','squirrel-race'],'doc:38'),(['squirrel','legacy-squirrel-mud'],'legacy:end')]
                    for (first,last),end in paths:
                        panel.go_start();steps=['option:enter','option:look','result:first-'+first,'reward:'+first]
                        if last=='observe':steps+=['reward:observe']
                        else:steps+=['option:touch-'+first,'result:'+last,'reward:legacy-gold99'if last.startswith('legacy')else'reward:gold99'if last=='net-mud'else'reward:'+last]
                        for key in steps:
                            select(panel.choices,key);c=model.choice_reference(panel.result,panel.scene_id,panel.choice_id)
                            if c['presentation']=='outcome_reference':require(c['actual_game_button']is False and '不是新增游戏按钮'in panel.player.toPlainText(),'outcome_cards_are_not_actual_buttons')
                            if c['scope']=='legacy_unresolved':require('当前归属未证'in panel.player.toPlainText(),'legacy_mud_candidate_never_current_proven_result')
                            if c['role']=='resource':require('只解释这一按钮'in panel.player.toPlainText(),'rewards_single_step_not_other_cases_summed')
                            require(panel.follow_scene(),'each_documentary_case_step_readable')
                        require(panel.scene_id==end and panel.choices.count()==0 and not panel.follow_scene(),'all7_paths_own_terminal_no_invented_loop')
                    choose(panel.scene,'outcomes:first');require(panel.choices.count()==3 and '结果参考，非游戏菜单'in panel.player.toPlainText(),'three_initial_outcomes_are_documented_not_actual_menu');shot('first-results')
                    choose(panel.scene,'outcomes:net');require(panel.choices.count()==1 and '不能据此认定只有1项或补出第2项'in panel.player.toPlainText(),'net_old2_list1_conflict_remains_unresolved');shot('net-count-conflict')
                    choose(panel.scene,'outcomes:squirrel');require(panel.choices.count()==3 and '旧PRTS'in panel.player.toPlainText(),'squirrel_two_bwiki_plus_unproven_legacy_extra');select(panel.choices,'result:legacy-squirrel-mud');require('归属未证'in panel.player.toPlainText()and '不是新增游戏按钮'in panel.player.toPlainText(),'legacy_extra_separate_not_merged_current_pool');shot('squirrel-extra')
                    choose(panel.scene,'doc:28');select(panel.choices,'reward:gold99');require(panel.original_button.isVisible()and '与原项不同'in panel.next_button.text()and '不能相加成198'in panel.player.toPlainText(),'document99_conflict_both_directions_visible_no198_total');shot('gold99-conflict')
                    QTest.mouseClick(panel.original_button,Qt.MouseButton.LeftButton);gui.processEvents();leaf=panel.original_dialog;require(leaf.panel.result['requested_original']['id']=='choice_ro6_surprise_12'and leaf.panel.original_button.isHidden()and not leaf.panel.open_original(),'exact_original99_owned_leaf_no_recursive_popup');require(leaf.panel.follow_scene()and leaf.panel.result['scenes'][leaf.panel.scene_id]['source_scene_ids']==['scene_ro6_surprise_1']and leaf.panel.choices.count()==0,'original99_exact_bed_not_document_leave_or_reward_loop');require(main_panel.refresh_reference()and panel.original_dialog is leaf and leaf.panel.scene_id=='source-next','real_parent_refresh_keeps_exact_comparison_leaf_position')
                    f=dest.with_name('window-original99-bed.png');require(leaf.grab().save(str(f),'PNG'),'owned_original_comparison_PNG');images.append({'name':'original99-bed','path':str(f),'sha256':sha256(f.read_bytes()).hexdigest(),'native':native(leaf)})
                    require(panel.open_original()and not leaf.isVisible(),'reopen_comparison_closes_old_leaf');leaf=panel.original_dialog;select(panel.choices,'reward:gold99');choose(panel.scene,'doc:12');select(panel.choices,'reward:observe');require(not leaf.isVisible()and panel.original_button.isHidden(),'switch_to_normal_reward_closes_and_hides_comparison')
                    choose(panel.scene,'doc:28');select(panel.choices,'reward:gold99');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);before_choice=panel.choice_id;tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'real_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.choice_id==before_choice and panel.tabs.currentIndex()==tab,'two_real_nonzero_readings_choice_and_tab_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    panel.go_start();select(panel.choices,'option:enter');damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes();picture=damaged/data['icon_reference']['file'];picture_raw=picture.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        picture.write_bytes(picture_raw+b'x');text=panel.player.toPlainText();require(panel.refresh_reference()and panel.player.toPlainText()==text and '图片暂缺'in panel.reward_icon.text(),'bad_named_reference_picture_keeps_text');picture.write_bytes(picture_raw);require(panel.refresh_reference()and not panel.reward_icon.pixmap().isNull(),'verified_reference_picture_restored');choose(panel.scene,'doc:28');select(panel.choices,'reward:gold99');require(panel.open_original(),'comparison_open_before_whole_source_loss');leaf=panel.original_dialog;file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()==''and panel.reward_card.isHidden()and panel.original_button.isHidden()and not leaf.isVisible(),'whole_source_loss_clears_text_controls_image_and_leaf');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_no_prior_choice_restore')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeat_parent_open_closes_previous_event');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_event')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_023'));gui.processEvents();QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel
                    require(panel.choice_id is None and panel.reward_card.isHidden()and panel.original_button.isHidden(),'node_defaults_no_actual_result_or_item');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'node_version_notice_visible');node.refresh();require(dialog.isVisible(),'node_same_source_refresh_keeps_event');f=dest.with_name('window-node-banner.png');require(dialog.grab().save(str(f),'PNG'),'actual_outer_dialog_PNG');images.append({'name':'node-banner','path':str(f),'sha256':sha256(f.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_loss_keeps_legacy_catalogue_text');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'node_recovery_requires_manual_open')
                    node_dialog=node.current_reference_window;panel=node_dialog.panel;choose(panel.scene,'doc:28');select(panel.choices,'reward:gold99');require(panel.open_original(),'node_owned_comparison_open');node_leaf=panel.original_dialog;idx=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();QTest.mouseClick(main_panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(main_panel.entries.count()>0,'manual_recheck_repopulates_cleared_version_entries');dialog=flow_entry('choices','choice_ro6_surprise_12');panel=dialog.panel;panel.go_start();choose(panel.scene,'doc:28');select(panel.choices,'reward:gold99');require(panel.open_original(),'version_owned_comparison_open');version_leaf=panel.original_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(all(not x.isVisible()for x in(dialog,node_dialog,node_leaf,version_leaf)),'actual_MainWindow_closes_both_event_and_comparison_trees');done=True;gui.exit(0)
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
    after=bound_files();result={'section':345,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
