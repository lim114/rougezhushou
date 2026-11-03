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
    from rouge import current_reconstruction as m,expansion_reference as v,current_node_readers as n,current_exchange_reference as offers
    for provider in(m,v,n,offers):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.add(m.packet()['data']['icon_reference']['file'])
    names.update(['scripts/build_current_reconstruction_344.py','scripts/verify_current_reconstruction_window_344.py','scripts/verify_full_available.py','tests/test_current_reconstruction_344.py','tests/test_current_reconstruction_view_344.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py','tests/test_current_peace_view_343.py','tests/test_current_exchange_view_323.py'])
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
        from PySide6.QtCore import Qt,QTimer,QCoreApplication,QEvent
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_reconstruction as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge344-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第344节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_reconstruction_344 import clone
                    main_panel=panel
                    def flow_entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_version_entry_exposes_reconstruction_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    from rouge import current_exchange_reference as offers
                    from tests.test_current_exchange_reference_323 import clone as clone_offers
                    data=model.reference()['data'];count=0;explicit=0;candidates=0
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;v=data['originals'][category][key];require(panel.result['requested_original']==v,'all90_exact_originals_preserved_complete')
                            require(all(panel.result[k]is None for k in('actual_inventory','actual_consumed','actual_received','actual_choice','actual_variant','actual_reward_pool','actual_remaining_exchanges','actual_first_type','actual_eligible')),'actual_inventory_transition_reward_pool_and_variant_unknown')
                            if category=='scenes':require(panel.scene_id=='source-scene'and panel.choices.count()==0,'all46_raw_scenes_no_guessed_menu')
                            else:
                                require(panel.scene_id=='source-choice'and panel.choice_id=='source-choice','raw_choice_opens_own_exact_row');c=model.choice_reference(panel.result,panel.scene_id,panel.choice_id)
                                if v['nextSceneId']:
                                    explicit+=1;require(panel.follow_scene()and panel.choices.count()==0 and panel.result['scenes'][panel.scene_id]['description']==data['originals']['scenes'][v['nextSceneId']]['description'],'all36_explicit_next_scenes_exact_no_further_menu')
                                else:
                                    candidates+=1;require(not panel.follow_scene()and '原件没有指定下一段'in panel.player.toPlainText(),'all8_literal_sacrifice_candidates_no_invented_next')
                                    if v['title']=='继续赞助它':require(panel.catalogue_button.isHidden()and c['role']=='unknown_exchange','raw_continue_never_infers_offering_type_by_id')
                            observations.append({'category':category,'key':key,'scene':panel.scene_id,'choice':panel.choice_id,'association':panel.result['requested_choice_association']});count+=1;dialog.close();main_panel.flow_dialog=None;dialog.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);gui.processEvents()
                    require((count,explicit,candidates)==(90,36,8),'all90_entries_36_explicit_8_literal_scope_accounted');dialog=flow_entry('choices','choice_ro6_sacrifice1_1');panel=dialog.panel;shot('source-exchange')
                    panel.go_start();require(panel.choice_id is None and panel.choices.count()==4 and panel.natural_controls.isHidden()and panel.reward_card.isHidden()and panel.catalogue_button.isHidden()and panel.naturals.value()==-1,'document_overview_four_alternatives_default_conditions_unknown')
                    require(all(x in panel.player.toPlainText()for x in('“声带”','“手掌”','第Ⅰ、Ⅵ层','实际科技、首次类型和剩余次数未知')),'known_prerequisites_not_actual_unlock')
                    require(not any(hasattr(panel,n)for n in('gold','offer','difficulty','operator','action_points')),'unrelated_conditions_absent_not_disabled')
                    for path,end in [([2,4,16,18],'doc:19'),([6,8,22,24],'doc:25'),([2,4,20],'doc:21'),([6,8,26],'doc:27'),([10,12],'doc:13'),([14],'doc:15')]:
                        panel.go_start()
                        for row in path:
                            select(panel.choices,'doc-choice:'+str(row));c=model.choice_reference(panel.result,panel.scene_id,panel.choice_id)
                            if c['role'].startswith(('choose_','continue_')):require(not c['document_next_is_original_next']and '按钮只沿文献翻页'in panel.player.toPlainText(),'documentary_exchange_transition_not_original_server_next')
                            if c['role']in('claim_relic','claim_part'):require('不按候选记录份数倍增'in panel.player.toPlainText()and c['reward_quantity_reference']==1,'single_receipt_one_item_not_variant_count')
                            require(panel.follow_scene(),'every_documented_branch_step_readable')
                        require(panel.scene_id==end and panel.choices.count()==0 and not panel.follow_scene(),'all_six_paths_own_terminal_no_infinite_exchange')
                    panel.go_start();select(panel.choices,'doc-choice:2');require(panel.catalogue_button.isVisible()and panel.natural_controls.isHidden(),'offering_catalogue_only_known_relic_branch');shot('relic-offering');QTest.mouseClick(panel.catalogue_button,Qt.MouseButton.LeftButton);gui.processEvents();offer_child=panel.catalogue_dialog;op=offer_child.panel
                    require(op.item_id is None and op.items.count()==284 and '不是奖励池'in op.count.text(),'actual_current_directory_not_inventory_or_reward_pool')
                    choose(op.offer,False);op.search.setText('焚毁');gui.processEvents();op.items.setCurrentRow(0);gui.processEvents();saved=(op.item_id,op.search.text(),op.offer.currentData());require(saved[0]is not None,'actual_nondefault_catalogue_selection')
                    require(main_panel.refresh_reference()and panel.catalogue_dialog is offer_child and (op.item_id,op.search.text(),op.offer.currentData())==saved,'real_parent_refresh_keeps_owned_directory_and_filters')
                    f=dest.with_name('window-offering-directory.png');require(offer_child.grab().save(str(f),'PNG'),'owned_directory_actual_PNG');images.append({'name':'offering-directory','path':str(f),'sha256':sha256(f.read_bytes()).hexdigest(),'native':native(offer_child)})
                    offer_root=temporary/'offer-source';clone_offers(offer_root);offer_file=offer_root/offers.DATA;offer_file.write_bytes(offer_file.read_bytes()+b'x')
                    with patch.object(offers,'ROOT',offer_root):
                        text=panel.player.toPlainText();require(panel.refresh_reference()and panel.player.toPlainText()==text and panel.catalogue_button.isHidden()and not offer_child.isVisible(),'optional_catalogue_source_loss_closes_only_child_keeps_verified_event')
                    require(panel.refresh_reference()and panel.catalogue_button.isVisible()and panel.catalogue_dialog is None,'optional_catalogue_recovery_requires_manual_open');require(panel.open_catalogue(),'catalogue_reopen_after_source_recovery');offer_child=panel.catalogue_dialog;select(panel.choices,'doc-choice:6');require(not offer_child.isVisible()and panel.catalogue_button.isHidden(),'switch_to_parts_closes_and_hides_relic_directory')
                    require(panel.follow_scene(),'read_parts_conversion');select(panel.choices,'doc-choice:8');require(panel.follow_scene(),'read_parts_continuation');select(panel.choices,'doc-choice:22');require(panel.catalogue_button.isHidden()and '不能替代首次交换类型'in panel.player.toPlainText(),'part_subtypes_not_first_exchange_category');shot('parts-again')
                    panel.go_start();select(panel.choices,'doc-choice:10');require(panel.natural_controls.isVisible(),'natural_control_only_two_natural_payment')
                    for value in(0,1):panel.naturals.setValue(value);gui.processEvents();require(not panel.follow_scene(),'zero_or_one_natural_blocks_only_documented_payment')
                    shot('natural-blocked');panel.naturals.setValue(2);gui.processEvents();require(panel.follow_scene()and panel.natural_controls.isHidden(),'two_naturals_can_read_next_not_actual_consumption');select(panel.choices,'doc-choice:12');require(panel.reward_card.isVisible()and not panel.reward_icon.pixmap().isNull()and '不再次消耗2件自然物'in panel.player.toPlainText()and '没有独立给出领取件数'in panel.player.toPlainText(),'named_reward_exact_picture_no_second_payment_or_quantity_guess');shot('named-receipt')
                    panel.go_start();select(panel.choices,'doc-choice:10');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_nonzero_scroll_range');bar.setValue(min(4,bar.maximum()));prior=reading(reader);before_choice=panel.choice_id;tab=panel.tabs.currentIndex();condition=panel.naturals.value();require(main_panel.refresh_reference(),'real_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.choice_id==before_choice and panel.tabs.currentIndex()==tab and panel.naturals.value()==condition,'two_real_nonzero_readings_choice_tab_and_condition_kept');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader)})
                    panel.scene.setCurrentIndex(panel.scene.findData('doc:11'));gui.processEvents();select(panel.choices,'doc-choice:12');damaged=temporary/'damaged';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes();picture=damaged/data['icon_reference']['file'];picture_raw=picture.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        picture.write_bytes(picture_raw+b'x');text=panel.player.toPlainText();require(panel.refresh_reference()and panel.player.toPlainText()==text and '图片暂缺'in panel.reward_icon.text(),'damaged_picture_keeps_named_reward_text');picture.write_bytes(picture_raw);require(panel.refresh_reference()and not panel.reward_icon.pixmap().isNull(),'verified_reward_picture_restored');file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()==''and panel.reward_card.isHidden()and panel.natural_controls.isHidden()and panel.catalogue_button.isHidden(),'actual_source_damage_clears_old_reading_controls_and_picture');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'manual_recovery_no_old_choice_restore')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_parent_open_closes_previous_reader');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_reader')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_025'));gui.processEvents();QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel
                    require(panel.scene_id=='doc:1'and panel.choice_id is None and panel.catalogue_button.isHidden()and panel.naturals.value()==-1,'node_defaults_unknown_no_reused_original_or_condition');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'node_version_notice_visible');node.refresh();require(dialog.isVisible(),'node_same_source_refresh_keeps_reader');f=dest.with_name('window-node-banner.png');require(dialog.grab().save(str(f),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'node-banner','path':str(f),'sha256':sha256(f.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_loss_keeps_old_catalogue_text');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'node_recovery_requires_manual_open')
                    node_dialog=node.current_reference_window;panel=node_dialog.panel;select(panel.choices,'doc-choice:2');require(panel.open_catalogue(),'node_owned_directory_open');node_catalogue=panel.catalogue_dialog;idx=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();QTest.mouseClick(main_panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(main_panel.entries.count()>0,'manual_recheck_repopulates_cleared_version_entries');dialog=flow_entry('choices','choice_ro6_sacrifice1_1');panel=dialog.panel;panel.go_start();select(panel.choices,'doc-choice:2');require(panel.open_catalogue(),'version_owned_directory_open');version_catalogue=panel.catalogue_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(all(not x.isVisible()for x in(dialog,node_dialog,node_catalogue,version_catalogue)),'actual_MainWindow_closes_both_reader_and_catalogue_trees');done=True;gui.exit(0)
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
    after=bound_files();result={'section':344,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
