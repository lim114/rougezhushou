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
    from rouge import current_battle_reference as m,expansion_reference as v,current_reward_origins as n
    from rouge import current_named_reward_origins as named
    providers=[m,v]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_enemy_traits_window_351.py','scripts/verify_full_available.py','tests/test_current_enemy_traits_351.py','tests/test_current_enemy_traits_view_351.py','research/p3-current-enemy-traits-351/source-notes.json'])
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
        from rouge import app as app_module,current_battle_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge351-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第351节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel
                    def entry(stage):
                        require(main_panel.scope.currentData()is False and main_panel.scope.isHidden(),'complete_current_stage_catalog_default_without_hidden_control_input');choose(main_panel.category,'stages');select(main_panel.entries,stage)
                        require(main_panel.battle_button.isVisible(),'actual_current_stage_entry_visible')
                        QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        return main_panel.current_battle_dialog
                    subjects=[('ro6_b_2','enemy_2142_shsggd'),('ro6_b_3_b','enemy_2154_shdfb'),('ro6_n_2_3','enemy_2133_shdopl_lancer'),('ro6_b_7','enemy_2157_shadvr')]
                    for sid,eid in subjects:
                        dialog=entry(sid);panel=dialog.panel;choose(panel.enemy_combo,next(e['key']for e in panel.result['enemies']if e['id']==eid));panel.tabs.setCurrentIndex(1);gui.processEvents()
                        text=panel.enemy_player.toPlainText();row=next(e for e in panel.result['enemies']if e['id']==eid)
                        require('行动与攻击方式'in text and '不以白值替代'in text,'actual_enemy_player_reader_contains_explicit_traits_not_white_values')
                        require(not row['declared_traits']['current_immunity_or_blockability_proven'],'static_declaration_not_current_phase_claim')
                        if eid=='enemy_2142_shsggd':require('仍可能有技能或特殊行为'in text and '扣除0点'in text and '不计入总数'in text,'NONE_zero_life_and_excluded_count_explained_without_no_attack_claim')
                        if eid=='enemy_2154_shdfb':require('明确未设置这项免疫'in text and row['declared_traits']['handbook_damage_types']is None,'independent_false_immunities_do_not_borrow_handbook')
                        if eid=='enemy_2133_shdopl_lancer':require('motion'not in row['declared_traits']['values']and '未取得明确设置'in text,'undefined_constructor_placeholders_never_shown_as_ground_or_controllable')
                        if eid=='enemy_2157_shadvr':require('地面行动'in text and '无法被阻挡'in text,'ground_declaration_and_unblockable_mechanism_both_retained')
                        observations.append({'stage':sid,'enemy':eid,'reference_index':row['reference_index'],'declared_fields':list(row['declared_traits']['values'])});shot(eid)
                        dialog.close()
                    dialog=entry('ro6_b_7');panel=dialog.panel;choose(panel.enemy_combo,'0');dialog.resize(800,460);gui.processEvents()
                    for reader,tab in[(panel.enemy_player,1),(panel.technical,3)]:
                        panel.tabs.setCurrentIndex(tab);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_nonzero_reading_range');bar.setValue(min(3,bar.maximum()));prior=reading(reader)
                        require(main_panel.refresh_reference(),'real_version_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.enemy_key=='0','two_readers_selection_scroll_tab_enemy_survive_actual_parent_refresh');refreshes.append({'before':prior,'after':reading(reader)})
                    damaged=temporary/'damaged';manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())
                    path=damaged/model.PACK/'source-inputs.json';raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(not panel.refresh_reference()and panel.result is None and panel.enemy_player.toPlainText()=='','actual_source_corruption_clears_new_traits');shot('source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.enemy_key is None,'source_recovery_requires_manual_enemy_selection')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_closes_current_battle_tree')
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
    after=bound_files();result={'section':351,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
