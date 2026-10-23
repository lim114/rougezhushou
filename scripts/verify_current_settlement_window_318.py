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
    names.update(['tests/test_current_settlement_reference_318.py','tests/test_current_settlement_view_318.py','tests/test_current_settlement_integration_318.py','scripts/build_current_settlement_318.py','scripts/verify_current_settlement_window_318.py','research/p3-current-settlement-318/runtime-manifest.json']);names.update(json.loads((ROOT/'research/p3-current-settlement-318/runtime-manifest.json').read_bytes())['files'])
    from rouge import current_settlement_modes_reference as modes
    names.add(modes.MANIFEST);names.update(json.loads((ROOT/modes.MANIFEST).read_bytes())['files'])
    names.update(('scripts/build_current_settlement_modes_362.py','tests/test_current_settlement_modes_362.py','tests/test_current_settlement_modes_view_362.py'))
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
        from rouge import app as app_module,current_settlement_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge318-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第318节 · 通关基础奖励（公开隔离验收）');window.show();gui.processEvents()
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
                    main_panel=panel;require(panel.scope.isHidden(),'common_page_has_no_update_scope_control');require(panel.scope.currentData()is False,'all_current_stage_catalog_for_exact_selection')
                    def choose(combo,value):
                        idx=combo.findData(value);require(idx>=0,'reference_context_option_exists');QTest.keyClick(combo,Qt.Key.Key_Home)
                        for _ in range(idx):QTest.keyClick(combo,Qt.Key.Key_Down)
                        QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'actual_QTest_entrance_or_region_selected')
                    def open_stage(sid):
                        nonlocal dialog,panel
                        if dialog is not None:dialog.close()
                        panel=main_panel;item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.current_battle_dialog;require(dialog.isVisible()and dialog.panel.stage_id==sid,'actual_MainWindow_opens_exact_current_battle');panel=dialog.panel.settlement;bar=dialog.panel.tabs.tabBar();idx=dialog.panel.tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(dialog.panel.tabs.currentIndex()==5,'actual_base_rewards_tab_preserves_first_five_indices');require(panel.result['conditional_base_gold']is None,'unconfirmed_entrance_does_not_auto_accept_base_amount')
                    def observe(label):
                        require(json.loads(panel.technical.toPlainText())==json.loads(json.dumps(panel.result,ensure_ascii=False)),'Qt_technical_roundtrip_keeps_all_source_and_conditions');require(panel.result['actual_reward_total']is None and not panel.result['inventory_updated']and not panel.result['reward_modifiers_applied'],'no_full_total_inventory_or_unsupported_modifiers');observations.append({'label':label,'stage':panel.stage_id,'entry':panel.entry.currentData(),'region':panel.region.currentData(),'base_gold':panel.result['conditional_base_gold'],'current_experience':panel.result['conditional_current_experience'],'base_experience':panel.result['conditional_base_experience'],'full_technology_experience':panel.result['conditional_full_technology_experience'],'actual_player_technology':panel.result['actual_player_technology'],'current_panel':'CurrentSettlementModesPanel362'})
                    open_stage('ro6_n_1_2');choose(panel.entry,'map');require(panel.result['conditional_base_gold']=={'minimum':1,'maximum':1}and panel.result['conditional_current_experience']is None and panel.result['conditional_base_experience']==10 and panel.result['conditional_full_technology_experience']==13 and'1013'not in panel.player.toPlainText(),'base_gold_current_experience_not_collapsed1013');observe('normal-main');shot('base-gold-and-historical-xp');choose(panel.region,'portal');require(panel.result['conditional_base_gold']=={'minimum':1,'maximum':1},'portal_only_documented_normal_origin_column');observe('portal-normal')
                    dialog.resize(900,450);gui.processEvents()
                    for reader in (panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_base_reader_nonzero_scroll');bar.setValue(min(5,bar.maximum()));before_read=reading(reader);keys=(panel.entry.currentData(),panel.region.currentData(),panel.tabs.currentIndex());QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==before_read and keys==(panel.entry.currentData(),panel.region.currentData(),panel.tabs.currentIndex()),'actual_context_tab_and_nonzero_reading_preserved');refreshes.append({'before':before_read,'after':reading(reader),'keys':keys,'actual_dialog_size':[dialog.width(),dialog.height()]})
                    ref=model.packet();sid=next(sid for sid,r in ref['directory']['data']['rows'].items()if r['name']=='“闹乐”'and r['original_stage']['difficulty']=='NORMAL');open_stage(sid);choose(panel.entry,'event');require(panel.result['conditional_base_gold']=={'minimum':3,'maximum':3},'same_name_special_event_has_three_base_gold');observe('same-name-event');shot('same-name-event');choose(panel.entry,'pursuit');require(panel.result['conditional_base_gold']=={'minimum':0,'maximum':0}and panel.result['conditional_current_experience']is None and panel.result['conditional_base_experience']==0 and panel.result['conditional_full_technology_experience']==0 and'1张招募券'in panel.player.toPlainText(),'same_name_ordinary_pursuit_is_zero_with_ticket');observe('same-name-pursuit');shot('same-name-pursuit')
                    open_stage('ro6_t_1');choose(panel.entry,'event');require(panel.result['conditional_base_gold']=={'minimum':2,'maximum':3},'special_gold_range_not_midpoint');observe('special-range');shot('special-range')
                    open_stage('ro6_b_7');choose(panel.entry,'map');require(panel.result['conditional_base_gold']is None and'同层另一特殊区域'in panel.player.toPlainText(),'hidden_sixth_layer_does_not_borrow_source_zero_rewards');observe('hidden-sixth-unknown');shot('hidden-sixth-unknown')
                    open_stage('ro6_n_4_1_dlc1');choose(panel.entry,'map');choose(panel.region,'side_path');require(panel.result['conditional_base_gold']is None and panel.result['documented_side_path_bonus']['random_relics']==1,'side_path_base_unknown_extra_relic_separate');observe('side-path-normal');shot('side-path-extra-separate')
                    open_stage('ro6_s_1');choose(panel.entry,'event');require(panel.result['conditional_base_gold']is None,'unlisted_graypit_not_zero');observe('graypit-unknown')
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'public_clone_valid_before_actual_corruption');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and not panel.technical.toPlainText()and'旧版经验'not in panel.player.toPlainText(),'actual_base_source_corruption_clears_numbers_and_legacy_reference');shot('base-source-loss')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.entry.currentData()=='event'and panel.result['conditional_base_gold']is None,'manual_recheck_retains_declared_context_without_inventing_graypit_gold')
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
    after=bound_files();result={'section':318,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
