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
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-document-flows-321/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_documented_event_flows_321.py','scripts/verify_documented_event_flows_window_321.py','scripts/verify_full_available.py','tests/test_documented_event_flows_321.py','tests/test_documented_event_flow_view_321.py'])
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
        from rouge import app as app_module,documented_event_flows as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge321-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第321节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel;QTest.mouseClick(main_panel.ending_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.ending_dialog;panel=dialog.panel
                    require(dialog.isVisible()and panel.combo.currentData()is None,'actual_MainWindow_ending_entry_manual_no_auto_selection')
                    ending=panel
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_declared_combo_value_present')
                        combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                        require(combo.currentData()==value,'direct_exact_selection_no_keyboard_prefix_traversal')
                    def select_choice(cid):
                        row=next(i for i in range(panel.choices.count())if panel.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid)
                        item=panel.choices.item(row);panel.choices.scrollToItem(item);gui.processEvents()
                        QTest.mouseClick(panel.choices.viewport(),Qt.MouseButton.LeftButton,pos=panel.choices.visualItemRect(item).center());gui.processEvents()
                        require(panel.choice_id==cid,'actual_mouse_selects_exact_document_choice')
                    expected={
                        'scene_ro6_end4_enter':['choice_ro6_end4_1','choice_ro6_end4_2'],
                        'scene_ro6_end4_1':['choice_ro6_end4_3'],'scene_ro6_end4_2':[],
                        'scene_ro6_end5_enter':['choice_ro6_end5_1','choice_ro6_end5_3','choice_ro6_end5_5'],
                        'scene_ro6_end5_1':['choice_ro6_end5_2'],'scene_ro6_end5_2':['choice_ro6_end5_4'],'scene_ro6_end5_3':[],
                        'scene_ro6_revive_enter':['choice_ro6_revive_1','choice_ro6_revive_3'],
                        'scene_ro6_revive_1':['choice_ro6_revive_2'],'scene_ro6_revive_2':[]}
                    for group,event in [('命运所指','button'),('出现类型未确认','blueprint'),('不期而遇','revive')]:
                        choose(ending.choices.branch,group);choose(ending.combo,event)
                        require(ending.flow_button.isVisible(),'three_ending_events_have_real_flow_entry')
                        QTest.mouseClick(ending.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();flow=ending.flow_dialog;panel=flow.panel
                        require(flow.isVisible()and panel.event_id==event,'actual_ending_entry_opens_exact_event_flow')
                        for sid in panel.result['event']['scene_ids']:
                            choose(panel.scene,sid)
                            actual=[panel.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.choices.count())]
                            require(actual==expected[sid],'all_ten_scenes_show_only_documented_choices')
                            require(panel.choice_id is None,'new_scene_has_no_automatic_choice')
                            if not actual:observations.append({'event':event,'scene':sid,'choices':[],'leaf_not_invented':True})
                            for cid in expected[sid]:
                                choose(panel.scene,sid);select_choice(cid);c=panel.result['choices'][cid]
                                require(panel.next_button.isVisible()==bool(c['next_scene_id'])and panel.battle_button.isVisible()==bool(c['stage_ids']),'special_links_only_for_corresponding_choice')
                                observations.append({'event':event,'scene':sid,'choice':cid,'text':panel.player.toPlainText(),'next_scene':c['next_scene_id'],'stage_ids':c['stage_ids']})
                                if c['next_scene_id']:
                                    QTest.mouseClick(panel.next_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id==c['next_scene_id']and panel.choice_id is None,'actual_mouse_follows_exact_documented_next_scene')
                                    QTest.mouseClick(panel.start_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id==panel.result['event']['entry_scene_id'],'actual_mouse_returns_to_entry_without_run_change')
                                if c['stage_ids']:
                                    QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=panel.battle_dialog
                                    require(battle.isVisible()and battle.panel.stage_id=='ro6_s_1'and battle.panel.map_image.pixmap() is not None and not battle.panel.map_image.pixmap().isNull(),'actual_TRADE_choice_opens_current_graypit_fixed_map')
                                    original_panel=panel;panel=battle.panel;shot('graypit-fixed-map');panel=original_panel;battle.close()
                        choose(panel.scene,panel.result['event']['entry_scene_id']);select_choice(expected[panel.scene_id][0]);shot(event+'-choice-result')
                        if event=='revive':
                            flow.resize(900,530);gui.processEvents()
                            for reader in (panel.player,panel.technical):
                                panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(14,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'both_readers_naturally_have_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.scene_id,panel.choice_id,panel.tabs.currentIndex())
                                QTest.mouseClick(ending.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.scene_id,panel.choice_id,panel.tabs.currentIndex()),'parent_refresh_preserves_flow_scene_choice_tab_and_nonzero_reading');refreshes.append({'before':prior,'after':reading(reader),'keys':keys})
                            panel.tabs.setCurrentIndex(0);flow.resize(1050,810);gui.processEvents()
                            clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                            for name in(model.MANIFEST,*manifest['files']):
                                target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                            target=clone/model.DATA;raw=target.read_bytes()
                            with patch.object(model,'ROOT',clone):
                                require(model.packet()is not None,'public_copy_valid_before_damage');target.write_bytes(raw+b' ')
                                try:
                                    QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.scene.count()==panel.choices.count()==0 and panel.technical.toPlainText()==''and not panel.next_button.isVisible()and not panel.battle_button.isVisible(),'actual_public_source_damage_clears_all_old_scene_choice_and_links');shot('source-loss-cleared')
                                finally:target.write_bytes(raw)
                                QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.scene_id is None and panel.choice_id is None,'actual_source_recovery_requires_manual_scene_selection')
                        flow.close();panel=ending
                    choose(ending.choices.branch,'线索与区域');choose(ending.combo,'entry');require(not ending.flow_button.isVisible(),'unrelated_event_has_no_special_flow_entry')
                    dialog.close();panel=main_panel
                    choose(panel.scope,False);choose(panel.category,'scenes')
                    sid='scene_ro6_end4_1';row=next(i for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.setCurrentRow(row);gui.processEvents()
                    require(panel.flow_button.isVisible(),'exact_current_scene_exposes_flow_entry');QTest.mouseClick(panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.flow_dialog;require(child.isVisible()and child.panel.scene_id==sid,'current_scene_entry_retains_exact_scene_not_other_same_title')
                    select_panel=panel;panel=child.panel;select_choice('choice_ro6_end4_3');shot('direct-scene-entry');panel=select_panel
                    QTest.mouseClick(panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not child.isVisible(),'repeat_open_closes_prior_flow');child=panel.flow_dialog;panel._unavailable();require(not child.isVisible(),'source_failure_closes_owned_flow')
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
    after=bound_files();result={'section':321,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
