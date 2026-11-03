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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-box-event-322/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_box_event_reference_322.py','scripts/verify_box_event_window_322.py','scripts/verify_full_available.py','tests/test_box_event_reference_322.py','tests/test_box_event_view_322.py'])
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
        from rouge import app as app_module,box_event_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge322-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第322节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                        index=combo.findData(value);require(index>=0,'exact_native_combo_value_present');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'direct_exact_choice_without_prefix_keyboard_traversal')
                    def select_choice(cid):
                        row=next(i for i in range(panel.choices.count())if panel.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid);item=panel.choices.item(row);panel.choices.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.choices.viewport(),Qt.MouseButton.LeftButton,pos=panel.choices.visualItemRect(item).center());gui.processEvents();require(panel.choice_id==cid,'actual_mouse_selects_document_option')
                    def entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category)
                        row=next(i for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);main_panel.entries.setCurrentRow(row);gui.processEvents();require(main_panel.flow_button.isVisible(),'actual_update_catalog_exact_entry_visible');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    dialog=entry('scenes','scene_ro6_end2_enter');panel=dialog.panel;require(dialog.isVisible()and panel.scene_id=='scene_ro6_end2_enter'and panel.choice_id is None,'actual_MainWindow_opens_exact_box_scene')
                    expected={'scene_ro6_end2_enter':['protect','leave','covenant','print'],'scene_ro6_end2_2':['normal_battle'],'scene_ro6_end2_1':[],'scene_ro6_end2_3':[]}
                    for sid,choices in expected.items():
                        choose(panel.scene,sid);require([panel.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.choices.count())]==choices,'all_four_scenes_keep_exact_document_grouping')
                        for cid in choices:
                            select_choice(cid);c=panel.result['choices'][cid];observations.append({'scene':sid,'choice':cid,'text':panel.player.toPlainText(),'variants':c['variant_ids'],'next_scene':c['next_scene_id'],'stage_ids':c['stage_ids']})
                    choose(panel.scene,'scene_ro6_end2_enter');select_choice('protect');require(panel.result['choices']['protect']['variant_ids']==['choice_ro6_end2_1','choice_ro6_end2_4','choice_ro6_end2_7']and panel.result['actual_variant']is None,'all_three_same_wording_variants_preserved_not_selected');shot('protect-variants')
                    QTest.mouseClick(panel.next_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id=='scene_ro6_end2_2','common_primary_next_scene_followed');select_choice('normal_battle');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=panel.battle_dialog
                    require(battle.isVisible()and battle.panel.stage_id=='ro6_b_5'and battle.panel.map_image.pixmap()is not None and not battle.panel.map_image.pixmap().isNull(),'current_normal_boss_map_exact_primary_identity');old_panel=panel;panel=battle.panel;shot('normal-boss-map');panel=old_panel;battle.close()
                    QTest.mouseClick(panel.start_button,Qt.MouseButton.LeftButton);gui.processEvents();select_choice('covenant');require(panel.result['declared_has_covenant']is None and panel.result['actual_eligible']is None,'unknown_condition_not_asserted_actual_eligible');shot('covenant-unknown')
                    choose(panel.covenant,False);require(panel.choice_id=='covenant'and not panel.next_button.isEnabled()and not panel.battle_button.isEnabled()and not panel.follow_scene()and not panel.open_battle(),'missing_covenant_blocks_document_branch_without_resetting_choice');shot('covenant-missing')
                    choose(panel.covenant,True);require(panel.next_button.isEnabled()and panel.battle_button.isEnabled()and panel.result['actual_eligible']is None,'known_condition_only_not_full_server_eligibility');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=panel.battle_dialog
                    require(battle.isVisible()and battle.panel.stage_id=='ro6_b_5_b'and battle.panel.map_image.pixmap()is not None and not battle.panel.map_image.pixmap().isNull(),'current_conditional_boss_map_distinct_exact_identity');old_panel=panel;panel=battle.panel;shot('conditional-boss-map');panel=old_panel
                    choose(panel.covenant,False);require(not battle.isVisible(),'condition_change_closes_inapplicable_owned_map');choose(panel.covenant,True)
                    QTest.mouseClick(panel.next_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id=='scene_ro6_end2_3'and panel.choices.count()==0 and not panel.battle_button.isVisible(),'explicit_next_story_does_not_invent_print_confirmation_parent');shot('next-story-no-guessed-option')
                    QTest.mouseClick(panel.start_button,Qt.MouseButton.LeftButton);gui.processEvents();select_choice('print');require(not panel.battle_button.isVisible()and not panel.open_battle()and '不借用相邻'in panel.player.toPlainText(),'unbound_print_choice_does_not_borrow_neighbor_map');shot('unbound-print')
                    select_choice('covenant');dialog.resize(900,530);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(14,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'two_readers_naturally_scroll_nonzero');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.scene_id,panel.choice_id,panel.covenant.currentData(),panel.tabs.currentIndex());QTest.mouseClick(main_panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.scene_id,panel.choice_id,panel.covenant.currentData(),panel.tabs.currentIndex()),'parent_refresh_preserves_condition_choice_tab_and_nonzero_reading');refreshes.append({'before':prior,'after':reading(reader),'keys':keys})
                    panel.tabs.setCurrentIndex(0);dialog.resize(1050,810);gui.processEvents();panel.open_battle();battle=panel.battle_dialog
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'actual_public_clone_valid_before_damage');target.write_bytes(raw+b' ')
                        try:
                            QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.scene.count()==panel.choices.count()==0 and panel.technical.toPlainText()==''and not battle.isVisible(),'actual_public_damage_clears_readers_choices_and_owned_map');shot('source-loss-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id is None and panel.choice_id is None,'source_recovery_requires_manual_selection')
                    dialog.close();panel=main_panel
                    for key in('choice_ro6_end2_1','choice_ro6_end2_4','choice_ro6_end2_7','choice_ro6_end2_5','choice_ro6_end2_6'):
                        dialog=entry('choices',key);panel=dialog.panel;target=model.locate('choices',key);require(panel.scene_id==target['scene_id']and panel.choice_id==target['choice_id']and panel.result['actual_variant']is None,'exact_primary_choice_entry_keeps_all_variants_and_group_scene');observations.append({'catalog_primary_choice':key,'group':target['choice_id'],'actual_variant':None});dialog.close();panel=main_panel
                    dialog=entry('scenes','scene_ro6_end2_2');old=dialog;QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not old.isVisible(),'repeat_open_closes_prior_box_dialog');dialog=main_panel.flow_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_owned_box_dialog')
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
    after=bound_files();result={'section':322,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
