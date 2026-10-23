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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-cave-334'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-cave-334/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_cave_334.py','scripts/verify_current_cave_window_334.py','scripts/verify_full_available.py','tests/test_current_cave_334.py','tests/test_current_cave_view_334.py'])
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
        from rouge import app as app_module,current_cave as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge334-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第334节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_cave_334 import clone
                    data=model.packet()['data'];sources=[]
                    for category,keys in(('scenes',data['originals']['scenes']),('choices',data['originals']['choices'])):
                        for key in keys:
                            dialog=flow_entry(category,key);panel=dialog.panel;t=model.locate(category,key);require(panel.source_request==t['source_request']and panel.result['source_request']==t['source_request'],'all90_version_entries_preserve_exact_original_source');require(panel.scene_id==t['scene_id']and panel.choice_id==(None if t['phase_needed']else t['choice_id']),'original_entry_never_defaults_ambiguous_phase');require(panel.result['actual_outcome']is None and panel.result['actual_variant']is None,'original_entry_not_actual_outcome_or_variant');sources.append({'category':category,'key':key,'phase_needed':t['phase_needed']});dialog.close()
                    require(len(sources)==90,'all90_original_entries_exercised')
                    dialog=flow_entry('scenes','scene_ro6_bat6_enter');panel=dialog.panel
                    require(not any(hasattr(panel,n)for n in('gold','controller','seeds','fossil')),'no_irrelevant_resource_controls')
                    for sid,scene in panel.result['scenes'].items():
                        choose(panel.scene,sid);require(panel.choices.count()==len(scene['choice_ids']),'all10_document_stages_keep_exact_choice_groups')
                        for cid in scene['choice_ids']:
                            select(panel.choices,cid);c=model.choice_reference(panel.result,sid,cid);require(c['title']in panel.player.toPlainText(),'all10_stage_choice_references_readable');observations.append({'scene':sid,'choice':cid,'original_count':len(c['variant_ids']),'next':c['next_scene_id'],'alternatives':c['record_next_scene_ids']})
                    def pick(role,sid=None):
                        key='cave-choice:'+role;sid=sid or panel.result['choices'][key]['scene_ids'][0];choose(panel.scene,sid);select(panel.choices,key);return model.choice_reference(panel.result,panel.scene_id,panel.choice_id)
                    pick('dig');require(not panel.follow_scene()and sum(b.isVisible()for b in panel.outcome_buttons)==4,'random_dig_has_four_separate_references_no_default_next');require(not panel.open_documented_outcome('cave-scene:end'),'unlisted_outcome_rejected');shot('four-results')
                    for outcome in('crow','squirrel','empty','danger'):
                        pick('dig');button=next(b for b in panel.outcome_buttons if b.property('sceneId')=='cave-scene:'+outcome);QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id=='cave-scene:'+outcome and panel.result['actual_outcome']is None,'actual_buttons_show_each_documented_result_without_selecting_real_outcome')
                    for role,low in(('gold','low_gold'),('empty','low_empty')):
                        c=pick(role);require(c['next_scene_id']is None and len(c['reference_followups'])==2 and not panel.follow_scene(),'same_caption_divergent_record_followups_have_no_default');require('原记录有不同后续'in panel.player.toPlainText(),'divergent_record_plain_language_notice');shot(role+'-different-followups');button=next(b for b in panel.followup_buttons if b.property('sceneId')=='cave-scene:'+low);QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id=='cave-scene:'+low,'documented_gold_and_empty_low_contexts_remain_separate');pick('again','cave-scene:'+low);require(sum(b.isVisible()for b in panel.outcome_buttons)==4 and not panel.follow_scene(),'repeat_four_document_cases_no_infinite_auto_loop');pick(role);require(panel.open_reference_followup('cave-scene:end')and panel.choices.count()==0,'current_record_end_alternative_has_no_synthetic_next')
                    c=pick('relic');require(c['reward_reference']=={'quantity':1,'kind':'收藏品','pool':None}and '不与其它结果相加'in panel.player.toPlainText(),'one_relic_quantity_unknown_pool_not_combined_with_gold');shot('one-relic');require(panel.follow_scene()and panel.scene_id=='cave-scene:end','all_relic_record_variants_explicit_end');pick('battle');require(panel.battle_button.isVisible()and not panel.battle_button.isEnabled()and not panel.open_battle()and panel.battle_dialog is None,'generic_difficult_battle_never_mapped_to_unverified_stage_or_urgent');shot('battle-unknown')
                    dialog.close()
                    for key,target in(('choice_ro6_bat6_3','cave-scene:low_gold'),('choice_ro6_bat6_19','cave-scene:end')):
                        dialog=flow_entry('choices',key);panel=dialog.panel;c=model.choice_reference(panel.result,panel.scene_id,panel.choice_id);require(c['source_variant_id']==key and c['next_scene_id']==target and not any(b.isVisible()for b in panel.followup_buttons),'exact_requested_record_uses_its_own_destination_not_caption_default');shot('exact-'+('ends'if target.endswith('end')else'continues'));require(panel.follow_scene()and panel.scene_id==target,'exact_requested_original_followup_retained');dialog.close()
                    dialog=flow_entry('choices','choice_ro6_bat6_7');panel=dialog.panel;require(panel.scene_id is None and '请先选择'in panel.player.toPlainText(),'same_caption_original_repeat_requires_phase');choose(panel.scene,'cave-scene:low_empty');require(panel.choice_id=='cave-choice:again'and panel.source_request['key']=='choice_ro6_bat6_7','manual_phase_keeps_exact_original_source');shot('phase-choice');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();source=deepcopy(panel.source_request);require(main_panel.refresh_reference(),'same_source_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.source_request==source and panel.scene_id=='cave-scene:low_empty'and panel.choice_id=='cave-choice:again','parent_refresh_preserves_two_real_readers_phase_choice_and_source');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'source_request':source})
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference()and panel.result is None and panel.source_request is None and panel.technical.toPlainText()=='','actual_cave_source_damage_clears_old_source_and_readers');require(not any(b.isVisible()for b in panel.outcome_buttons+panel.followup_buttons),'bad_source_clears_all_outcome_and_alternative_buttons');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None and panel.source_request is None,'manual_source_recovery_requires_reselection')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeated_version_open_closes_previous_cave');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_cave')
                    node=window.node_catalog;idx=tabs.indexOf(node);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(idx).center());gui.processEvents();node.list.setCurrentRow(next(i for i,e in enumerate(node.entries)if e['key']=='event:community_group_017'));gui.processEvents();require(node.current_reference_button.isVisible(),'real_node_catalogue_entry_available');QTest.mouseClick(node.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.current_reference_window;panel=dialog.panel;require(panel.source_request is None and panel.choice_id is None and panel.result['actual_eligible']is None,'catalogue_overview_not_actual_source_phase_or_eligibility');require('请核对实际游戏版本'in dialog.node_reference_banner.text(),'catalogue_version_reference_notice');node.refresh();require(dialog.isVisible(),'catalogue_same_source_refresh_preserves_cave');imagefile=dest.with_name('window-node-notice.png');require(dialog.grab().save(str(imagefile),'PNG'),'actual_outer_dialog_screenshot_saved');images.append({'name':'node-notice','path':str(imagefile),'sha256':sha256(imagefile.read_bytes()).hexdigest(),'native':native(dialog)})
                    with patch.object(model,'ROOT',damaged):
                        prior=node.player_detail.toPlainText();file.write_bytes(raw+b' ');node.show_selected();require(not dialog.isVisible()and node.player_detail.toPlainText()==prior,'new_source_failure_preserves_old_catalogue_information');file.write_bytes(raw);node.show_selected();require(node.current_reference_window is None and node.open_current_event_reference(),'catalogue_source_recovery_requires_manual_open')
                    dialog=node.current_reference_window;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_close_closes_cave_reader');done=True;gui.exit(0)
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
    after=bound_files();result={'section':334,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
