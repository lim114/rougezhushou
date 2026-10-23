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
    names.update('tests/test_current_battle_'+name+'_314.py'for name in('reference','view','integration'))
    names.update(['scripts/build_current_battle_reference_314.py','scripts/verify_current_battle_window_314.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
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
        from rouge import app as app_module,current_battle_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge314-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第314节 · 当前关卡预览（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('stages');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native()})
            def category(key):
                nonlocal panel
                if tabs.indexOf(panel)>=0:
                    panel=window.reference_panel(key);gui.processEvents()
                    require(tabs.currentWidget()is panel and panel.isVisible()and panel.scope.currentData()is False and panel.scope.isHidden(),'actual_common_page_for_requested_category')
                combo=panel.category;index=combo.findData(key);require(index>=0,'category_value_exists')
                QTest.keyClick(combo,Qt.Key.Key_Home)
                for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==key,'actual_QTest_category_selects_exact_branch')
            def choose(key):
                item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key)
                panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());gui.processEvents()
                require(panel.result is not None and panel.result['row']['id']==key,'actual_QTest_list_selects_exact_source_identity')
                require(json.loads(panel.technical.toPlainText())==panel.result,'actual_Qt_technical_JSON_roundtrips_complete_record')
                require(panel.result['actual_reward']is None and panel.result['actual_eligibility']is None and panel.result['mutations_applied']is False,'reading_does_not_claim_actual_reward_eligibility_or_mutate_state')
                observations.append({'category':panel.category.currentData(),'id':key,'name':panel.result['row']['name'],'image_loaded':panel.image_raw is not None})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                dialog=None
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents()
                    require(tabs.currentWidget()is panel,'actual_MainWindow_common_reference_tab_opened')
                    main_panel=panel
                    for sid in('ro6_n_2_6','ro6_b_7','ro6_n_4_1_dlc1'):
                        item=next(main_panel.entries.item(i)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid)
                        main_panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(main_panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=main_panel.entries.visualItemRect(item).center());gui.processEvents()
                        require(main_panel.result['row']['id']==sid and main_panel.battle_button.isEnabled(),'actual_current_stage_selected_with_exact_preview_entry')
                        QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.current_battle_dialog;panel=dialog.panel
                        require(dialog.isVisible()and panel.result['id']==sid,'actual_button_opens_exact_current_stage_dialog')
                        require(panel.map_image.pixmap()is not None and not panel.map_image.pixmap().isNull(),'actual_current_original_map_loaded')
                        require(json.loads(panel.technical.toPlainText())==panel.result,'complete_current_level_JSON_roundtrips_in_Qt')
                        observations.append({'stage_id':sid,'kind':'map','level_key':panel.result['level_key'],'enemy_refs':len(panel.result['enemies']),'action_rows':len(panel.result['actions'])})
                        shot(sid+'-map')
                        tabbar=panel.tabs.tabBar();QTest.mouseClick(tabbar,Qt.MouseButton.LeftButton,pos=tabbar.tabRect(1).center());gui.processEvents()
                        for tier,label in model.TIERS.items():
                            candidates=[e for e in panel.result['enemies']if e['tier']==tier]
                            if not candidates:continue
                            branch=panel.enemy_choices.branch;index=branch.findData(label);require(index>=0,'separate_enemy_tier_branch_exists')
                            QTest.keyClick(branch,Qt.Key.Key_Home)
                            for _ in range(index):QTest.keyClick(branch,Qt.Key.Key_Down)
                            QTest.keyClick(branch,Qt.Key.Key_Return);gui.processEvents();require(branch.currentData()==label,'actual_QTest_chooses_enemy_tier_branch')
                            combo=panel.enemy_combo;QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                            enemy=next(e for e in panel.result['enemies']if e['key']==combo.currentData());require(enemy['tier']==tier and enemy['name']in panel.enemy_player.toPlainText(),'actual_exact_enemy_reading_matches_selected_tier')
                            require('不以白值替代'in panel.enemy_player.toPlainText(),'unknown_final_stats_not_replaced_by_base_stats')
                            observations.append({'stage_id':sid,'kind':'enemy','id':enemy['id'],'level':enemy['level'],'tier':tier,'actual_selected_key':combo.currentData()})
                        if sid=='ro6_b_7':shot('new-boss-enemies')
                        QTest.mouseClick(tabbar,Qt.MouseButton.LeftButton,pos=tabbar.tabRect(2).center());gui.processEvents()
                        for kind in('main','branch'):
                            combo=panel.queue_kind;index=combo.findData(kind);QTest.keyClick(combo,Qt.Key.Key_Home)
                            for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                            QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();expected=[a for a in panel.result['actions']if a['queue']['kind']==kind]
                            require(panel.actions.count()==len(expected),'actual_queue_branch_filters_complete_source_rows')
                            if expected:
                                item=panel.actions.item(0);panel.actions.scrollToItem(item);QTest.mouseClick(panel.actions.viewport(),Qt.MouseButton.LeftButton,pos=panel.actions.visualItemRect(item).center());gui.processEvents()
                                require(panel.action_key==expected[0]['key']and'准确时刻：未知'in panel.action_player.toPlainText(),'actual_queue_reading_does_not_invent_global_clock')
                                observations.append({'stage_id':sid,'kind':'queue','queue':kind,'actual_selected_key':panel.action_key})
                        if sid=='ro6_b_7':
                            shot('new-boss-branches');dialog.resize(900,450);gui.processEvents()
                            for widget,index in((panel.summary,0),(panel.enemy_player,1),(panel.action_player,2),(panel.technical,3)):
                                if widget is panel.action_player:widget.parentWidget().setSizes([680,160]);gui.processEvents()
                                QTest.mouseClick(tabbar,Qt.MouseButton.LeftButton,pos=tabbar.tabRect(index).center());gui.processEvents();c=widget.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(c);scroll=widget.verticalScrollBar();require(scroll.maximum()>0,'real_current_reader_has_nonzero_scroll_without_padding');scroll.setValue(min(6,scroll.maximum()));prior=reading(widget);keys=(panel.enemy_combo.currentData(),panel.action_key,panel.queue_kind.currentData(),panel.tabs.currentIndex())
                                QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(widget)==prior and keys==(panel.enemy_combo.currentData(),panel.action_key,panel.queue_kind.currentData(),panel.tabs.currentIndex()),'refresh_preserves_current_branch_identity_tab_selection_and_nonzero_scroll')
                                refreshes.append({'reader_index':index,'before':prior,'after':reading(widget),'keys':keys,'owned_dialog_size':[dialog.width(),dialog.height()]})
                        dialog.close();panel=main_panel;gui.processEvents()
                    # Corrupt an actual temporary public source copy, never the project source or private state.
                    from rouge.current_battle_view import CurrentBattlePanel
                    panel=CurrentBattlePanel('ro6_b_7');panel.resize(950,600);panel.show();gui.processEvents()
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.PACK/'source-inputs.json';raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'temporary_complete_public_source_valid_before_damage');target.write_bytes(raw+b' ')
                        try:
                            QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.actions.count()==0 and not panel.technical.toPlainText()and not panel.enemy_player.toPlainText(),'real_current_source_damage_clears_lists_readers_and_result');shot('current-source-loss-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.enemy_combo.currentData()is None and panel.actions.currentItem()is None,'source_recovery_restores_stage_without_old_enemy_or_queue_selection')
                    panel.close();panel=main_panel
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_legacy_context_unchanged')
                    require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_actual_game_chat_credential_operations_zero')
                    native();done=True;window.close();gui.processEvents();gui.exit(0)
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
    after=bound_files();result={'section':314,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
