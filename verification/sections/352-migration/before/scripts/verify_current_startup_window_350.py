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
    from rouge import current_startup as m,expansion_reference as v,current_reward_origins as n
    from rouge import current_named_reward_origins as named
    providers=[m,v]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/build_current_startup_350.py','scripts/verify_current_startup_window_350.py','scripts/verify_full_available.py','tests/test_current_startup_350.py','tests/test_current_startup_view_350.py','tests/test_original_entry_planning.py'])
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
        from rouge import app as app_module,current_startup as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge350-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第350节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    from tests.test_current_startup_350 import clone
                    from rouge import current_reward_origins as unified
                    main_panel=panel
                    def origins_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.origins_button.isVisible(),'real_version_item_exposes_named_acquisition_entry');QTest.mouseClick(main_panel.origins_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.origins_dialog
                    main_panel=panel
                    def entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'actual_version_source_exposes_startup_flow');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    rows=model.reference()['choices'];require(len(rows)==12,'twelve_current_exact_choices')
                    for cid,row in rows.items():
                        dialog=entry('choices',cid);panel=dialog.panel;require(panel.choice_id==cid,'all12_actual_source_choice_entries_selected')
                        inherited=row['kind']=='inherited';require(panel.gold.isVisible()==(cid=='choice_ro6_startbuff_3')and panel.inherited.isVisible()==inherited,'only_selected_support_relevant_inputs_visible')
                        require(panel.result['actual_received']is None and panel.result['actual_displayed_choice_ids']is None and not panel.result['run_updated'],'directory_never_claims_menu_or_actual_rewards')
                        require(not panel.next_button.isVisible()and not panel.battle_button.isVisible(),'no_fabricated_followup_or_battle')
                        if inherited:require(not panel.reward_icon.pixmap().isNull(),'all_six_current_support_icons_present')
                        observations.append({'category':'choices','key':cid,'scene':panel.scene_id,'choice':panel.choice_id,'source_pointer_verified':row['source_scene_pointer_verified']})
                        if cid in('choice_ro6_startbuff_1','choice_ro6_startbuff_10','choice_ro6_startbuff_12'):shot(cid)
                        dialog.close()
                    for cid in model.reference()['data']['inherited_ids']:
                        iid=rows[cid]['item_id'];dialog=entry('relics',iid);panel=dialog.panel;require(panel.choice_id==cid,'all_six_item_effects_open_exact_inherited_option_not_inferred_inventory');observations.append({'category':'relics','key':iid,'choice':cid});dialog.close()
                    dialog=entry('scenes',model.SCENE);panel=dialog.panel;require(panel.choices.count()==12 and panel.choice_id is None,'scene_overview_no_default_choice');observations.append({'category':'scenes','key':model.SCENE,'choice':None})
                    choose(panel.group,'regular');require(panel.choices.count()==6 and panel.choice_id is None,'separate_regular_six_candidates');choose(panel.group,'inherited');require(panel.choices.count()==6,'separate_inherited_six_sources');choose(panel.group,'all')
                    select(panel.choices,'choice_ro6_startbuff_3');choose(panel.mode,'NORMAL');panel.previous.setValue(1);panel.gold.setValue(6);require(model.choice_reference(panel.result,model.SCENE,panel.choice_id)['listed_condition_match']is False,'one_previous_region_not_enough');panel.previous.setValue(2)
                    for gold,want in[(5,False),(6,True)]:panel.gold.setValue(gold);gui.processEvents();require(model.choice_reference(panel.result,model.SCENE,panel.choice_id)['listed_condition_match']is want,'five_six_gold_boundary_exact')
                    shot('regular-cost');dialog.resize(700,390);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_nonzero_reading_range');bar.setValue(min(3,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(main_panel.refresh_reference(),'real_version_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.choice_id=='choice_ro6_startbuff_3'and panel.previous.value()==2 and panel.gold.value()==6,'two_readings_manual_values_and_choice_survive_parent_refresh');refreshes.append({'before':prior,'after':reading(reader)})
                    select(panel.choices,'choice_ro6_startbuff_7');choose(panel.inherited,'choice_ro6_startbuff_8');require(model.choice_reference(panel.result,model.SCENE,panel.choice_id)['listed_condition_match']is False,'six_same_name_legacy_records_not_interchanged');choose(panel.inherited,'choice_ro6_startbuff_7');require(model.choice_reference(panel.result,model.SCENE,panel.choice_id)['listed_condition_match']is True,'exact_inherited_choice_matches_listed_only');choose(panel.mode,'OTHER');require(model.choice_reference(panel.result,model.SCENE,panel.choice_id)['listed_condition_match']is False,'inherited_normal_mode_only');choose(panel.mode,'NORMAL')
                    damaged=temporary/'damaged';clone(damaged);path=damaged/model.DATA;raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(not panel.refresh_reference()and panel.result is None and panel.technical.toPlainText()==''and panel.reward_icon.pixmap().isNull(),'damaged_source_clears_choices_text_and_picture');shot('source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.scene_id is None and panel.choice_id is None,'source_recovery_requires_manual_reselection')
                    old=dialog;dialog=entry('choices','choice_ro6_startbuff_12');panel=dialog.panel;require(not old.isVisible(),'repeat_parent_open_closes_old_startup_window')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_closes_current_startup_tree')
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
    after=bound_files();result={'section':350,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
