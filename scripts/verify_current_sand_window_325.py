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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-sand-325'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-sand-325/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_sand_reference_325.py','scripts/verify_current_sand_window_325.py','scripts/verify_full_available.py','tests/test_current_sand_reference_325.py','tests/test_current_sand_view_325.py'])
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
        from rouge import app as app_module,current_sand_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge325-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第325节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_current_sand');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    def sand_entry(category,key):
                        nonlocal main_panel
                        main_panel=window.reference_panel(category);gui.processEvents()
                        require(tabs.currentWidget()is main_panel and main_panel.isVisible()and main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'actual_common_page_for_requested_category')
                        choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_current_sand_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    def values(panel,context):
                        for key,value in context.items():
                            if key=='gold':panel.gold.setValue(-1 if value is None else value)
                            else:choose(panel.controls[key],value)
                        gui.processEvents()
                    dialog=sand_entry('relics','rogue_6_relic_final_1');panel=dialog.panel
                    require(panel.choice_id=='choice_ro6_bomb1_1'and panel.result['context']['has_alpha']is None,'alpha_catalogue_entry_not_assumed_owned');require('不自动补成1件'in panel.player.toPlainText(),'named_alpha_quantity_not_invented');shot('informer-alpha')
                    for event in('informer','curiosity'):
                        if event=='curiosity':dialog.close();dialog=sand_entry('scenes','scene_ro6_end1_enter');panel=dialog.panel
                        for sid,scene in panel.result['scenes'].items():
                            choose(panel.scene,sid);require(panel.choices.count()==len(scene['choice_ids']),'all_seven_document_scenes_keep_exact_choices')
                            for cid in scene['choice_ids']:
                                select(panel.choices,cid);require(not panel.battle_button.isVisible()and not panel.open_battle(),'none_of_five_choices_invents_immediate_battle');observations.append({'event':event,'scene':sid,'choice':cid,'next':panel.result['choices'][cid]['next_scene_id']})
                    choose(panel.scene,'scene_ro6_end1_enter');select(panel.choices,'choice_ro6_end1_1')
                    good={'floor':5,'node_type':'命运所指','cleared_reboot':True,'has_alpha':True,'has_beta':False,'target_marked':False,'gold':49};values(panel,good)
                    require(not panel.next_button.isEnabled()and not panel.follow_scene()and '已知不符'in panel.player.toPlainText(),'49_gold_keeps_reading_but_blocks_unmet_next');shot('49-gold-unmet')
                    values(panel,{'gold':50});require(panel.next_button.isEnabled()and panel.result['actual_eligible']is None,'50_gold_only_matches_listed_conditions_not_live_eligibility');values(panel,{'target_marked':True});require(not panel.next_button.isEnabled(),'already_marked_blocks_paid_marking_option');select(panel.choices,'choice_ro6_end1_2');require(panel.next_button.isEnabled()and '随机获得'in panel.player.toPlainText(),'random_relic_option_not_blocked_by_marking_cost');shot('random-relic')
                    select(panel.choices,'choice_ro6_end1_1');values(panel,{'scope':'history','gold':0,'floor':1});require(panel.next_button.isEnabled()and '不用于否定过去'in panel.player.toPlainText(),'history_not_erased_by_current_resources_or_floor');shot('history-reference')
                    values(panel,{**good,'gold':50,'has_beta':True});require('不一致'in panel.player.toPlainText()and panel.result['context']['target_marked']is False,'two_sands_unmarked_conflict_not_silently_rewritten');shot('marker-conflict')
                    values(panel,{'has_beta':False});QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.related_dialog
                    require(child.isVisible()and child.panel.scene_id=='scene_ro6_end2_enter'and child.panel.covenant.currentData()is None,'related_box_starts_own_unknown_context_not_actual_jump')
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();declared_context=deepcopy(panel.result['context'])
                        require(main_panel.refresh_reference(),'same_source_parent_refresh_succeeds');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.result['context']==declared_context and child.isVisible(),'parent_refresh_keeps_both_readers_context_and_related_window');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'context':declared_context})
                    choose(child.panel.scene,'scene_ro6_end2_2');select(child.panel.choices,'normal_battle');require(child.panel.open_battle(),'related_box_has_its_own_documented_battle');battle=child.panel.battle_dialog;require(battle.isVisible()and battle.panel.stage_id=='ro6_b_5','box_related_map_exact_current_configuration');saved=panel;panel=battle.panel;shot('related-box-map');panel=saved
                    values(panel,{'gold':51});require(not child.isVisible()and not battle.isVisible(),'condition_change_closes_entire_related_tree');require(panel.open_related(),'related_reader_reopens');child=panel.related_dialog
                    with patch('rouge.box_event_reference.locate',return_value=None):require(not panel.open_related()and not child.isVisible()and panel.result is not None,'optional_related_source_failure_does_not_clear_core')
                    require(panel.refresh_reference()and panel.open_related(),'optional_source_can_recover_manually');child=panel.related_dialog
                    from tests.test_current_sand_reference_325 import clone
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');require(not panel.refresh_reference(),'actual_public_bytes_corruption_detected');require(panel.result is None and not child.isVisible()and panel.technical.toPlainText()==''and not panel.related_button.isVisible(),'core_loss_clears_readers_and_owned_tree');shot('source-loss');file.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'recovery_manual_no_prior_scene_restored')
                    dialog.close();dialog=sand_entry('relics','rogue_6_relic_final_2');panel=dialog.panel;require(panel.choice_id is None and panel.event_id=='curiosity'and panel.result['context']['has_beta']is None,'beta_entry_is_overview_not_possession');shot('beta-overview')
                    old=dialog;require(main_panel.open_documented_flow()and not old.isVisible(),'repeat_open_closes_old_reader');dialog=main_panel.flow_dialog;panel=dialog.panel;panel.open_related();child=panel.related_dialog;main_panel._unavailable();require(not dialog.isVisible()and not child.isVisible(),'parent_loss_closes_related_readers')
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
    after=bound_files();result={'section':325,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
