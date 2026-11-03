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
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-expansion-313').rglob('*')if p.is_file()}
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-battle-314').rglob('*')if p.is_file())
    portraits=json.loads((ROOT/'research/p3-current-battle-314/enemy-images.json').read_bytes())['images'];names.update(v['file']for v in portraits.values())
    names.update('tests/test_ending_event_'+name+'_316.py'for name in('reference','view'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-rewards-315').rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-ending-events-316/runtime-manifest.json').read_bytes());names.update(manifest['files']);names.add('research/p3-ending-events-316/runtime-manifest.json')
    names.update(['scripts/build_ending_events_reference_316.py','scripts/verify_ending_events_window_316.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
    images=json.loads((ROOT/'research/p3-expansion-313/map-images.json').read_bytes())['images'];names.update(v['file']for v in images.values())
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
        from rouge import app as app_module,ending_event_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge316-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第316节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'declared_choice_available');QTest.keyClick(combo,Qt.Key.Key_Home)
                        for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                        QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'actual_QTest_selects_requested_condition')
                    for group,identity in [('线索与区域','entry'),('命运所指','button'),('不期而遇','revive'),('出现类型未确认','blueprint'),('线索与区域','hidden_region')]:
                        choose(panel.choices.branch,group);choose(panel.combo,identity);require(json.loads(panel.technical.toPlainText())==panel.result,'Qt_preserves_full_selected_originals');observations.append({'event':identity,'title':panel.result['record']['title']})
                        require(panel.result['actual_event_eligible']is None and panel.result['probability']is None and not panel.result['memory_updated'],'reference_conditions_not_live_eligibility_or_memory')
                    choose(panel.combo,'entry');choose(panel.controls['floor'],1);choose(panel.controls['node_type'],'险路尽头');choose(panel.controls['post_update_clear'],True);panel.gold.setFocus();QTest.keyClicks(panel.gold,'9');gui.processEvents()
                    require(panel.result['listed_conditions_status']=='listed_matched'and panel.result['choice_conditions_status']['choice_ro6_final1_8']=='not_matched','actual_event_visible_but_cost_option_unmatched');shot('entry-cost-separate')
                    panel.gold.clear();QTest.keyClicks(panel.gold,'10');require(panel.result['choice_conditions_status']['choice_ro6_final1_8']=='listed_matched','ten_gold_boundary_visible')
                    choose(panel.combo,'side_path');choose(panel.controls['scope'],'future');choose(panel.controls['region'],'main');choose(panel.controls['floor'],3);choose(panel.controls['has_prayer'],True);choose(panel.controls['has_covenant'],True)
                    require(panel.result['listed_conditions_status']=='not_matched','future_generation_covenant_stops_new_path');choose(panel.controls['scope'],'history');require(panel.result['listed_conditions_status']=='reference_only','old_nodes_remain_reference_after_generation_stops');shot('history-not-erased')
                    choose(panel.controls['scope'],'current');choose(panel.controls['region'],'熄日余径');choose(panel.controls['node_type'],'命运所指');choose(panel.controls['adventurer_alive'],False);choose(panel.choices.branch,'命运所指');choose(panel.combo,'button')
                    require(panel.result['listed_conditions_status']=='listed_matched'and panel.result['choice_conditions_status']['choice_ro6_end4_1']=='not_matched','NPC_down_only_blocks_advance_option_not_whole_event');choose(panel.battle_combo,'ro6_s_1');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.battle_dialog;require(child.isVisible()and child.panel.stage_id=='ro6_s_1','actual_graypit_current_map_link');observations.append({'battle':'ro6_s_1'});child.close();shot('button-graypit')
                    choose(panel.choices.branch,'线索与区域');choose(panel.combo,'hidden_region')
                    for sid in ('ro6_b_7','ro6_b_7_b'):
                        choose(panel.battle_combo,sid);QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.battle_dialog;require(child.isVisible()and child.panel.stage_id==sid,'actual_two_same_name_bosses_keep_exact_configuration');observations.append({'battle':sid});child.close()
                    dialog.resize(1000,520);gui.processEvents()
                    for reader in (panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_reader_scroll_nonzero_without_padding');bar.setValue(min(5,bar.maximum()));prior=reading(reader);keys=(panel.combo.currentData(),panel.battle_combo.currentData(),panel.tabs.currentIndex(),panel.choices.branch.currentData());QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.combo.currentData(),panel.battle_combo.currentData(),panel.tabs.currentIndex(),panel.choices.branch.currentData()),'actual_same_source_preserves_reading_and_selections');refreshes.append({'before':prior,'after':reading(reader),'keys':keys,'actual_dialog_size':[dialog.width(),dialog.height()]})
                    panel.tabs.setCurrentIndex(0);shot('hidden-region-independent-configurations')
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'public_clone_valid_before_actual_byte_damage');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and not panel.technical.toPlainText()and not panel.battle_button.isEnabled()and panel.battle_combo.count()==0,'actual_source_damage_clears_conditions_and_links');shot('source-loss-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.combo.currentData()is None and not panel.battle_button.isEnabled(),'actual_source_recovery_requires_manual_reselection')
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
    after=bound_files();result={'section':316,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
