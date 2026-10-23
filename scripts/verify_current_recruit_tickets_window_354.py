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
    from rouge import current_recruit_tickets as model,expansion_reference as version
    for provider in (model,version):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_recruit_tickets_window_354.py','scripts/build_current_recruit_tickets_354.py','scripts/verify_full_available.py','tests/test_current_recruit_tickets_354.py','tests/test_current_recruit_tickets_view_354.py','verification/sections/354-preparation/scope.json'])
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
        from rouge import app as app_module,current_recruit_tickets as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge354-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第354节 · 招募券用途与留存（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('relics');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
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
                    require(main_panel.tickets_button.isVisible() and main_panel.tickets_button.isEnabled(),'actual_common_items_ticket_button_visible')
                    QTest.mouseClick(main_panel.tickets_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.tickets_dialog;panel=dialog.panel
                    require(dialog.isVisible() and panel.entries.count()==47 and panel.ticket_id is None,'actual_main_entry_all47_manual_choices')
                    require(panel.profession.count()==9 and panel.family.count()==6,'actual_profession_and_ticket_family_branches')
                    def choose(combo,value):
                        idx=combo.findData(value);require(idx>=0,'exact_ticket_branch_value');combo.setCurrentIndex(idx);gui.processEvents()
                    def select(key):
                        item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());gui.processEvents();require(panel.ticket_id==key,'real_exact_ticket_mouse_selection')
                    choose(panel.profession,'PIONEER');choose(panel.family,'protocol')
                    require(panel.entries.count()==len(model.reference(profession='PIONEER',ticket_family='protocol')['rows']),'actual_intersection_filter')
                    choose(panel.profession,None);choose(panel.family,None)
                    for key in ('rogue_6_recruit_ticket_pioneer_sp','rogue_6_recruit_ticket_temp_5_up','rogue_6_recruit_ticket_temp_6','rogue_6_recruit_ticket_all_discount'):
                        select(key);expected=model.reference(key);require(panel.result==expected and model.version._plain(expected['selected']['original_item']['usage'])in panel.player.toPlainText(),'exact_chinese_usage_own_professions_and_stars');observations.append({'id':key,'stars':expected['selected']['stars'],'professions':expected['selected']['professions']})
                        if key in ('rogue_6_recruit_ticket_temp_5_up','rogue_6_recruit_ticket_temp_6'):shot(key)
                    require('初始留存上限为3张'in panel.player.toPlainText() and '不能把15解释成初始上限'in panel.player.toPlainText(),'three_initial_capacity_not_fifteen')
                    panel.search.setText('高级人事资深');select('rogue_6_recruit_ticket_all_discount');dialog.resize(760,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'real_nonzero_ticket_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();key=panel.ticket_id
                        require(main_panel.refresh_reference(),'actual_items_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.ticket_id==key and panel.search.text()=='高级人事资深','two_nonzero_readers_filter_selection_and_tab_preserved');refreshes.append({'before':prior,'after':reading(reader)})
                    dialog.resize(1100,800);gui.processEvents()
                    for kind,button,cid in [('exit',panel.exit_button,'choice_ro6_final1_2'),('rest',panel.rest_button,'choice_ro6_rest_7')]:
                        QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.event_dialog;link=model.destination(kind);require(child is not None and child.isVisible() and child.panel.source_request=={'category':'choices','key':cid},'exact_actual_existing_event_source_'+kind);require(child.panel.result is not None and link['actual_inventory']is None and link['actual_eligible']is None,'no_inventory_or_actual_eligibility_inference_'+kind);shot('exact-'+kind)
                    panel.search.clear();gui.processEvents();require(panel.ticket_id is None,'overview_is_manual_no_auto_ticket');require(panel.open_event('exit'),'overview_original_event_entry');child=panel.event_dialog
                    require(main_panel.refresh_reference() and child.isVisible(),'overview_child_survives_same_source_parent_refresh')
                    damaged=temporary/'damaged';manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())
                    path=damaged/model.DATA;raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'items_parent_independent_source_stays_available');require(panel.result is None and panel.entries.count()==0 and panel.player.toPlainText()=='' and panel.technical.toPlainText()=='' and not panel.exit_button.isEnabled()and not child.isVisible(),'actual_ticket_member_damage_clears_old_readers_list_links_and_child');shot('ticket-source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.ticket_id is None and panel.entries.currentItem()is None,'recovery_restores_list_manual_ticket_selection')
                    require(panel.open_event('rest'),'rest_entry_after_manual_source_recovery');child=panel.event_dialog
                    window.reference_panel('scenes');gui.processEvents();require(not dialog.isVisible() and not child.isVisible(),'main_page_navigation_closes_owned_ticket_event_tree')
                    main_panel=window.reference_panel('relics');require(main_panel.open_recruit_tickets(),'reopen_actual_common_items_ticket_reader');dialog=main_panel.tickets_dialog;panel=dialog.panel;require(panel.open_event('exit'),'reopen_nested_original_event');child=panel.event_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_owned_ticket_and_event_tree')
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
    after=bound_files();result={'section':354,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
