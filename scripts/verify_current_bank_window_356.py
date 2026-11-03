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
    from rouge import current_bank_reference as model,expansion_reference as version
    for provider in (model,version):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_bank_window_356.py','scripts/build_current_bank_356.py','scripts/verify_full_available.py','tests/test_current_bank_356.py','tests/test_current_bank_view_356.py','verification/sections/356-preparation/scope.json'])
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
        from rouge import app as app_module,current_bank_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge356-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第356节 · 投资解锁说明（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('initial');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
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
                    require(main_panel.bank_button.isVisible()and main_panel.bank_button.isEnabled(),'actual_exploration_setup_bank_entry_visible');QTest.mouseClick(main_panel.bank_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.bank_dialog;panel=dialog.panel
                    require(dialog.isVisible()and panel.entries.count()==5 and panel.selected_id()is None and panel.values()=={'cumulative':None,'peak_balance':None},'actual_bank_directory_five_manual_unknowns');shot('directory')
                    def select_list(widget,key):
                        item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'real_exact_reward_or_item_mouse_selection')
                    for row in list(panel.result['rows']):
                        select_list(panel.entries,row['id'])
                        for value in(row['threshold']-1,row['threshold'],row['threshold']+1):
                            panel.cumulative.setValue(value);gui.processEvents();actual=next(r for r in panel.result['rows']if r['id']==row['id']);require(actual['cumulative_condition_matches']==(value>=row['threshold'])and actual['actual_unlocked']is None and actual['actual_received']is None,'all_five_threshold_boundaries_not_actual_unlock');observations.append({'id':row['id'],'declared_cumulative':value,'condition_matches':actual['cumulative_condition_matches'],'actual_unlocked':None})
                        require(panel.peak_row.isVisible()==(row['id']=='bank_reward_4')and panel.item_button.isVisible()==(row['id']=='bank_reward_4'),'only_exact250_own_peak_and_item_controls')
                    select_list(panel.entries,'bank_reward_4');panel.cumulative.setValue(250);panel.peak_balance.setValue(249);gui.processEvents();row=next(r for r in panel.result['rows']if r['id']=='bank_reward_4');require(row['cumulative_condition_matches']is True and row['legacy_peak_condition_matches']is False,'two_conflicting_counters_kept_independent');shot('counter-conflict')
                    panel.cumulative.setValue(249);panel.peak_balance.setValue(250);gui.processEvents();row=next(r for r in panel.result['rows']if r['id']=='bank_reward_4');require(row['cumulative_condition_matches']is False and row['legacy_peak_condition_matches']is True,'reverse_conflict_never_fills_other_counter')
                    QTest.mouseClick(panel.item_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.item_dialog;require(child.isVisible()and child.panel.result['target']=={'category':'relics','key':model.ITEM_ID}and child.panel.image_raw is not None,'actual_exact_gold_cup_item_image_and_original_unlock');shot('gold-cup',child.panel)
                    dialog.resize(800,480);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'real_nonzero_bank_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();values=panel.values()
                        require(main_panel.refresh_reference(),'actual_setup_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.values()==values and panel.selected_id()=='bank_reward_4'and child.isVisible(),'two_nonzero_readers_values_selection_and_item_child_preserved');refreshes.append({'before':prior,'after':reading(reader)})
                    select_list(panel.entries,'bank_reward_3');require(not child.isVisible()and not panel.peak_row.isVisible(),'other_reward_hides_special_peak_and_closes_item');panel.tabs.setCurrentIndex(0);shot('other-reward');select_list(panel.entries,'bank_reward_4');require(panel.open_item(),'item_for_source_loss');child=panel.item_dialog
                    damaged=temporary/'damaged';manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())
                    path=damaged/model.DATA;raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'setup_independent_source_still_ready');require(panel.result is None and panel.entries.count()==0 and panel.technical.toPlainText()=='' and not child.isVisible()and not panel.item_button.isVisible(),'actual_bank_member_damage_clears_old_text_and_item_tree');shot('source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.selected_id()is None,'source_recovery_requires_manual_reward_selection')
                    items=window.reference_panel('relics');gui.processEvents();require(not dialog.isVisible(),'main_page_navigation_closes_setup_bank');select_list(items.entries,model.ITEM_ID);require(items.bank_item_button.isVisible(),'only_gold_cup_reverse_unlock_entry_visible');QTest.mouseClick(items.bank_item_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=items.bank_dialog;panel=dialog.panel;require(panel.selected_id()=='bank_reward_4'and panel.values()=={'cumulative':None,'peak_balance':None},'exact_reverse250_not_acquisition_or_cached_private_values');shot('reverse-entry')
                    other=next(items.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(items.entries.count())if items.entries.item(i).data(Qt.ItemDataRole.UserRole)!=model.ITEM_ID);select_list(items.entries,other);require(not dialog.isVisible()and not items.bank_item_button.isVisible(),'other_item_hides_unrelated_unlock_controls')
                    select_list(items.entries,model.ITEM_ID);require(items.open_bank_reference(from_item=True),'reopen_reverse_exact_item');dialog=items.bank_dialog;panel=dialog.panel;require(panel.open_item(),'reopen_nested_gold_cup_item');child=panel.item_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_bank_and_item_tree')
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
    after=bound_files();result={'section':356,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
