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
    names.update('tests/test_current_reward_'+name+'_315.py'for name in('reference','view','integration'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-rewards-315').rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-rewards-315/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_reward_reference_315.py','scripts/verify_current_rewards_window_315.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
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
        from rouge import app as app_module,current_reward_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge315-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第315节 · 当前奖励条件（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel;combo=main_panel.scope;QTest.keyClick(combo,Qt.Key.Key_End);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()is False,'actual_scope_choice_shows_complete_current_stage_catalog')
                    for sid in('ro6_n_2_6','ro6_t_7','ro6_n_4_1_dlc1'):
                        item=next(main_panel.entries.item(i)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid)
                        main_panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(main_panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=main_panel.entries.visualItemRect(item).center());QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.current_battle_dialog;current=dialog.panel;panel=current.rewards
                        require(dialog.isVisible()and panel.result['stage_id']==sid,'actual_current_preview_contains_exact_reward_tab')
                        t=current.tabs.tabBar();idx=current.tabs.indexOf(panel);QTest.mouseClick(t,Qt.MouseButton.LeftButton,pos=t.tabRect(idx).center());gui.processEvents()
                        require(current.tabs.currentWidget()is panel and panel.combo.currentData()is None and not panel.source_button.isEnabled(),'actual_reward_tab_starts_with_manual_summary_no_jump')
                        for kind,label in(('device','宝箱与装置'),('moving','移动恶笼草'),('rare','稀有敌人')):
                            wanted=[r for r in panel.result['rows']if r['kind']==kind]
                            if not wanted:continue
                            branch=panel.choices.branch;index=branch.findData(label);require(index>=0,'real_reward_category_branch_available');QTest.keyClick(branch,Qt.Key.Key_Home)
                            for _ in range(index):QTest.keyClick(branch,Qt.Key.Key_Down)
                            QTest.keyClick(branch,Qt.Key.Key_Return);gui.processEvents();require(branch.currentData()==label,'actual_QTest_selects_real_reward_category')
                            # Choose an exact desired current source, including the opening cost or shop rule.
                            desired=next((r for r in wanted if r['entity_id']==('trap_327_shchst'if sid=='ro6_t_7'else'trap_320_shtlbx')),wanted[0]);combo=panel.combo;index=combo.findData(desired['id']);QTest.keyClick(combo,Qt.Key.Key_Home)
                            for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                            QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                            require(panel.row_id==desired['id']and desired['name']in panel.player.toPlainText(),'actual_QTest_reads_exact_reward_identity')
                            require(json.loads(panel.technical.toPlainText())=={'result':panel.result,'selected_row':desired},'Qt_roundtrip_preserves_complete_reward_and_all_group_members')
                            require(panel.result['all_actual_rewards']is None and not panel.result['complete_reward_pool_known'],'no_actual_total_or_complete_pool_claimed')
                            observations.append({'stage_id':sid,'kind':kind,'selected_row_id':desired['id'],'entity_id':desired['entity_id'],'candidate_groups':len(desired['candidate_groups'])})
                            if kind=='device'and sid=='ro6_n_2_6':require('50点部署费用'in panel.player.toPlainText()and'1个随机零件'in panel.player.toPlainText(),'current_opening_cost_and_reward_resource_are_separate');shot('toolbox-cost-and-candidates')
                            if sid=='ro6_t_7':require('1–2个商店物品'in panel.player.toPlainText()and'无法再部署'in panel.player.toPlainText(),'current_shop_theft_range_and_redeploy_restriction_visible');shot('shop-theft')
                            if kind=='moving':require('+10源石锭'in panel.player.toPlainText()and'-10源石锭'in panel.player.toPlainText()and'互斥结果'in panel.player.toPlainText(),'moving_gain_loss_are_conditional_exclusive_not_summed');shot(sid+'-moving')
                            if kind=='rare'and sid=='ro6_n_2_6':require('固定版本的社区敌人文献'in panel.player.toPlainText(),'rare_quantity_keeps_community_document_boundary');shot('rare-document-boundary')
                            if desired['source_action_keys']:
                                combo=panel.source_combo;QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();key=combo.currentData();require(key in desired['source_action_keys'],'source_choice_is_an_exact_supported_action_key');QTest.mouseClick(panel.source_button,Qt.MouseButton.LeftButton);gui.processEvents()
                                require(current.tabs.currentIndex()==2 and current.action_key==key,'actual_reward_button_jumps_to_exact_current_queue')
                                observations.append({'stage_id':sid,'kind':'source_jump','key':key,'row':desired['id']})
                                QTest.mouseClick(t,Qt.MouseButton.LeftButton,pos=t.tabRect(idx).center());gui.processEvents()
                        if sid=='ro6_n_2_6':
                            row=next(r for r in panel.result['rows']if r['kind']=='device'and r['candidate_groups']);panel.choices.select_value(row['id']);panel.source_combo.setCurrentIndex(1);dialog.resize(900,430);gui.processEvents()
                            for reader in(panel.player,panel.technical):
                                panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'actual_reward_reader_has_nonzero_scroll_without_padding');scroll.setValue(min(7,scroll.maximum()));prior=reading(reader);keys=(panel.combo.currentData(),panel.source_combo.currentData(),panel.tabs.currentIndex(),panel.choices.branch.currentData());QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.combo.currentData(),panel.source_combo.currentData(),panel.tabs.currentIndex(),panel.choices.branch.currentData()),'reward_refresh_preserves_branch_row_source_tab_scroll_and_selection');refreshes.append({'before':prior,'after':reading(reader),'keys':keys,'actual_dialog_size':[dialog.width(),dialog.height()]})
                        dialog.close();panel=main_panel;gui.processEvents()
                    from rouge.current_reward_view import CurrentRewardPanel
                    panel=CurrentRewardPanel('ro6_n_2_6');panel.resize(950,600);panel.show();gui.processEvents();panel.choices.select_value(panel.result['rows'][0]['id']);panel.source_combo.setCurrentIndex(1)
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.PACK/'selected-originals.json';raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'actual_public_reward_clone_valid_before_corruption');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and not panel.technical.toPlainText()and not panel.source_button.isEnabled()and'+10'not in panel.player.toPlainText(),'real_reward_source_corruption_clears_old_quantities_and_links');shot('reward-source-loss-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.combo.currentData()is None and panel.source_combo.currentData()is None and not panel.source_button.isEnabled(),'reward_recovery_is_manual_without_previous_target_or_jump')
                    panel.close();panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();done=True;window.close();gui.processEvents();gui.exit(0)
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
    after=bound_files();result={'section':315,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
