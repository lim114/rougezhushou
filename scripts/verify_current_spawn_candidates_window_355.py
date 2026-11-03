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
    from rouge import current_spawn_candidates as model,expansion_reference as version,current_battle_reference as battle,current_map_position as positions,current_terrain as terrain
    for provider in (model,version,battle,positions,terrain):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_spawn_candidates_window_355.py','scripts/verify_full_available.py','tests/test_current_spawn_candidates_355.py','tests/test_current_spawn_candidates_view_355.py','verification/sections/355-preparation/scope.json'])
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=120000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
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
        from rouge import app as app_module,current_spawn_candidates as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge355-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第355节 · 出怪候选与关联（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('stages');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label,widget=None):
                gui.processEvents();widget=panel if widget is None else widget;file=dest.with_name('window-'+label+'.png');assert not file.exists();require(widget.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native(widget.window())})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                dialog=None
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is panel,'actual_MainWindow_common_reference_tab_opened')
                    main_panel=panel
                    def choose(combo,value):
                        idx=combo.findData(value);require(idx>=0,'exact_candidate_branch_value');combo.setCurrentIndex(idx);gui.processEvents();require(combo.currentData()==value,'real_candidate_control_selection')
                    def entry(sid):
                        nonlocal dialog,panel,battle
                        item=next(main_panel.entries.item(i)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);main_panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(main_panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=main_panel.entries.visualItemRect(item).center());gui.processEvents();QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=main_panel.current_battle_dialog.panel;battle.tabs.setCurrentIndex(2);gui.processEvents();require(battle.spawn_candidates_button.isVisible(),'actual_battle_candidates_entry_visible');QTest.mouseClick(battle.spawn_candidates_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle.spawn_candidates_dialog;panel=dialog.panel;require(dialog.isVisible()and panel.result is not None,'actual_MainWindow_battle_candidate_dialog_opened')
                    battle=None;entry('ro6_n_1_1');require(panel.relation_combo.currentData()is None and panel.member_combo.currentData()is None,'manual_candidate_and_member_initial_selection')
                    def member(predicate):
                        rows=panel.result['groups']if panel.relation_kind.currentData()=='group'else panel.result['packages']
                        for rel in rows:
                            for m in rel['members']:
                                if predicate(m):choose(panel.relation_combo,rel['key']);choose(panel.member_combo,m['action_key']);return rel,m
                        raise AssertionError('No exact fixed candidate member')
                    for typ,predicate in [('empty',lambda m:m['action_type']=='EMPTY'),('unnamed-device',lambda m:m['action_type']=='ACTIVATE_PREDEFINED'and not m['action']['raw'].get('key')),('enemy',lambda m:m['action_type']=='SPAWN')]:
                        rel,m=member(predicate);require(m['name']in panel.player.toPlainText(),'own_member_chinese_reading_'+typ);require(panel.position_button.isEnabled()==m['can_request_position'],'position_availability_for_exact_member_'+typ);observations.append({'stage':panel.stage_id,'kind':typ,'relation':rel['key'],'action_key':m['action_key'],'can_request_position':m['can_request_position']});shot(typ)
                    rel,m=member(lambda m:m['action_type']=='SPAWN'and m['can_request_position']);QTest.mouseClick(panel.action_button,Qt.MouseButton.LeftButton);gui.processEvents();require(battle.action_key==m['action_key']and battle.queue_kind.currentData()==m['action']['queue']['kind'],'real_parent_action_exact_key_navigation')
                    QTest.mouseClick(panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();position=battle.action_position_dialog;require(position.isVisible()and position.panel.action_key==m['action_key']and position.panel.result==model.position_reference(panel.result,rel['key'],m['action_key']),'real_parent_owned_exact_position_reader');shot('exact-map',position.panel)
                    dialog.resize(760,430);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'real_nonzero_candidate_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();key=panel.member_combo.currentData();group=panel.relation_combo.currentData()
                        require(main_panel.refresh_reference(),'actual_common_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.member_combo.currentData()==key and panel.relation_combo.currentData()==group,'two_nonzero_readers_member_relation_and_tab_preserved');refreshes.append({'before':prior,'after':reading(reader)})
                    damaged=temporary/'damaged';name=model.PACK+'/scope-inventory.json';path=damaged/name;path.parent.mkdir(parents=True);raw=(ROOT/name).read_bytes();path.write_bytes(raw+b'x');original_file=model.battle.version._file
                    with patch.object(model.battle.version,'_file',side_effect=lambda n:path if n==name else original_file(n)):
                        require(main_panel.refresh_reference(),'battle_independent_source_ready_after_candidate_loss');require(panel.result is None and not panel.action_button.isEnabled()and not panel.position_button.isEnabled()and panel.member_combo.count()==1 and panel.technical.toPlainText()=='' and panel.portrait.isHidden()and not position.isVisible(),'actual_candidate_member_damage_clears_old_content_and_owned_map');shot('source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.member_combo.currentData()is None and panel.relation_combo.currentData()is None,'source_recovery_requires_manual_relation_and_member')
                    entry('ro6_n_1_4');choose(panel.relation_kind,'package');rel,m=member(lambda m:True);require(len(panel.result['groups'])==5 and len(panel.result['packages'])==2,'actual_group_and_package_are_separate_directories');observations.append({'stage':panel.stage_id,'kind':'package','relation':rel['key'],'action_key':m['action_key'],'members':len(rel['members'])});shot('package');choose(panel.queue_kind,'branch');require(panel.relation_combo.count()==1 and not panel.member_combo.isEnabled(),'fixed_current_branch_has_no_invented_relation')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_closes_candidate_tree')
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
    after=bound_files();result={'section':355,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
