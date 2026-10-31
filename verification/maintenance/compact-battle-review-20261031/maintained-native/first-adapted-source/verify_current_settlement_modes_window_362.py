"""Actual current battle replaces its settlement reader with two documented modes."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_current_settlement_modes_window_362.py'


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_settlement_modes_reference as model,current_battle_reference as battle,current_reward_reference as rewards,expansion_reference as version
    for provider in(model,model.prior,model.prior.directory,battle,rewards,version):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    for name in('research/p3-expansion-313/map-images.json','research/p3-current-battle-314/enemy-images.json'):
        names.add(name);names.update(value['file']for value in json.loads((ROOT/name).read_bytes())['images'].values())
    names.update((CANONICAL,'scripts/verify_full_available.py','scripts/build_current_settlement_modes_362.py',
                  'tests/test_current_settlement_modes_362.py','tests/test_current_settlement_modes_view_362.py',
                  'tests/test_current_settlement_integration_318.py','scripts/verify_current_settlement_window_318.py'))
    if(ROOT/'verification/sections/362-preparation/scope.json').is_file():names.add('verification/sections/362-preparation/scope.json')
    names.update(('scripts/verify_current_settlement_window_318.py','tests/test_current_settlement_integration_318.py'))
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Exact regular installed public source required: '+name)
        result[name]=sha256(path.read_bytes()).hexdigest()
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=120000);args=p.parse_args()
    dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];source_failures=[]
    calls={name:0 for name in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    failure=None;window=None;gui=None;exitcode=None;done=False
    def require(value,name):
        if not value:raise AssertionError(name)
        if name not in checks:checks.append(name)
    def forbidden(name):
        def fail(*args,**kwargs):calls[name]+=1;raise AssertionError('Forbidden real operation: '+name)
        return fail
    try:
        if sys.platform!='win32':raise RuntimeError('Actual Windows required')
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication,QComboBox
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_settlement_modes_reference as model,current_battle_reference as battle
        from rouge.current_settlement_modes_view import CurrentSettlementModesPanel
        from rouge.current_settlement_view import CurrentSettlementPanel
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge362-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第362节 · 当前作战经验与源石锭分项（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();main_panel=window.reference_panel('stages');panel=main_panel;dialog=None;battle_panel=None
            state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget;hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native(panel.window())})
            def choose(combo,value):
                index=combo.findData(value);require(index>=0,'exact_settlement_entry_or_region_option');combo.setCurrentIndex(index);gui.processEvents()
            def select_stage(stage_id):
                item=next(main_panel.entries.item(i)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==stage_id)
                main_panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(main_panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=main_panel.entries.visualItemRect(item).center());gui.processEvents()
                require(main_panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)==stage_id,'actual_exact_current_stage_mouse_selection')
            def open_stage(stage_id):
                nonlocal dialog,panel,battle_panel
                old_dialog=dialog;old_panel=panel if dialog is not None else None
                window.reference_panel('stages');select_stage(stage_id);require(main_panel.battle_button.isVisible()and main_panel.battle_button.isEnabled(),'ordinary_current_stage_battle_button_visible')
                QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.current_battle_dialog;battle_panel=dialog.panel;panel=battle_panel.settlement
                require(dialog.isVisible()and battle_panel.stage_id==stage_id and panel.stage_id==stage_id,'actual_MainWindow_opens_exact_current_battle_settlement')
                require(isinstance(panel,CurrentSettlementModesPanel)and len(battle_panel.findChildren(CurrentSettlementModesPanel))==1 and not battle_panel.findChildren(CurrentSettlementPanel),'new_modes_replace_single_current_settlement_not_parallel_old_unknown_panel')
                index=battle_panel.tabs.indexOf(battle_panel.rewards);require(index==3 and battle_panel.tabs.count()==4 and battle_panel.tabs.tabText(index)=='奖励与条件','grouped_reward_reader_keeps_first_three_player_categories')
                bar=battle_panel.tabs.tabBar();QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center());gui.processEvents()
                sections=battle_panel.rewards.sections;index=sections.indexOf(panel);require(index==1 and sections.tabText(index)=='通关收入','base_modes_keep_their_own_reward_subsection');bar=sections.tabBar();QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center());gui.processEvents();require(sections.currentWidget()is panel and panel.isVisible(),'actual_modes_reader_tab_opened')
                require(len(panel.findChildren(QComboBox))==2 and panel.entry.currentData()=='unknown'and panel.region.currentData()=='catalog','only_entry_region_declarations_no_auto_player_technology')
                require(panel.result['conditional_base_experience']is None and panel.result['conditional_full_technology_experience']is None and panel.result['conditional_base_gold']is None,'opening_exact_stage_does_not_guess_entry_from_ID')
                if old_dialog is not None:require(not old_dialog.isVisible()and old_panel.result is None and old_panel.technical.toPlainText()=='','changing_current_stage_closes_and_clears_previous_modes_reader')
            def observe(label):
                value=panel.result;require(json.loads(panel.technical.toPlainText())==json.loads(json.dumps(value,ensure_ascii=False)),'actual_technical_reading_preserves_complete_source_and_conditions')
                require(value['actual_reward_total']is None and value['actual_player_technology']is None and value['conditional_current_experience']is None and not value['inventory_updated']and not value['reward_modifiers_applied']and not value['actual_victory_verified']and not value['actual_entry_verified'],'reference_modes_never_actual_reward_technology_victory_or_inventory')
                text=panel.player.toPlainText()
                require('不能相加'in text and all(token not in text for token in('1013','is-fulltech','mw-collapsible','旧版经验资料参考','当前指挥经验：还需核对')),'player_gets_separate_current_modes_not_collapsed_HTML_or_parallel_legacy_unknown')
                observations.append({'label':label,'stage_id':panel.stage_id,'entry':panel.entry.currentData(),'region':panel.region.currentData(),
                                     'base_experience':value['conditional_base_experience'],'full_technology_experience':value['conditional_full_technology_experience'],
                                     'base_gold':deepcopy(value['conditional_base_gold']),'actual_player_technology':value['actual_player_technology'],'actual_reward_total':value['actual_reward_total']})
            def reading(widget):
                cursor=widget.textCursor();return{'anchor':cursor.anchor(),'position':cursor.position(),'selection':cursor.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def independent_battle():
                pixmap=battle_panel.map_image.pixmap()
                return{'stage_id':battle_panel.result['id']if battle_panel.result else None,'enemy_refs':deepcopy(battle_panel.result['enemies'])if battle_panel.result else None,
                       'reward_result':deepcopy(battle_panel.rewards.result),'summary':battle_panel.summary.toPlainText(),'map_visible':pixmap is not None and not pixmap.isNull()}
            def clone_sources(provider,label):
                clone=temporary/label;manifest=json.loads((ROOT/provider.MANIFEST).read_bytes())
                for name in(provider.MANIFEST,*manifest['files']):
                    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                return clone
            def exercise():
                nonlocal done,failure,panel,dialog,battle_panel
                try:
                    bar=tabs.tabBar();index=tabs.indexOf(main_panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center());gui.processEvents()
                    require(tabs.currentWidget()is main_panel and main_panel.scope.isHidden()and main_panel.scope.currentData()is False,'actual_common_current_stage_page_without_version_only_scope')
                    for stage_id,base,full,gold in(('ro6_n_1_2',10,13,1),('ro6_e_1_2',12,15,2),('ro6_n_6_1',20,26,5)):
                        open_stage(stage_id);choose(panel.entry,'map');require((panel.result['conditional_base_experience'],panel.result['conditional_full_technology_experience'],panel.result['conditional_base_gold'])==(base,full,{'minimum':gold,'maximum':gold}),'normal_emergency_source0_two_independent_experience_values')
                        require('基础指挥经验：'+str(base)+' 点'in panel.player.toPlainText()and '满级生命游戏的经验参考：'+str(full)+' 点'in panel.player.toPlainText(),'ordinary_player_reads_both_named_experience_values_and_units');observe(stage_id)
                        if stage_id=='ro6_n_1_2':
                            shot('normal-base-and-full');choose(panel.region,'portal');require(panel.result['conditional_base_experience']==10 and panel.result['conditional_full_technology_experience']==13,'portal_only_documented_normal_stage_origin_column');observe('portal-normal')
                    for stage_id in('ro6_t_16','ro6_c_9'):
                        open_stage(stage_id);require(panel.result['stage_name']=='晶矿惊蝗','two_exact_crystal_stage_configs_retained')
                        choose(panel.entry,'event');require((panel.result['conditional_base_experience'],panel.result['conditional_full_technology_experience'],panel.result['conditional_base_gold'])==(30,39,{'minimum':3,'maximum':3}),'both_crystal_event_configs_30_39_3_without_prefix_inference');observe(stage_id+'-event')
                        if stage_id=='ro6_t_16':shot('crystal-event')
                        choose(panel.entry,'pursuit');require((panel.result['conditional_base_experience'],panel.result['conditional_full_technology_experience'],panel.result['conditional_base_gold'])==(0,0,{'minimum':0,'maximum':0})and '1张招募券'in panel.player.toPlainText(),'same_exact_crystal_normal_pursuit_zero_modes_and_one_ticket_separate');observe(stage_id+'-pursuit')
                        if stage_id=='ro6_c_9':shot('crystal-pursuit')
                        choose(panel.entry,'unknown');require(panel.result['conditional_base_experience']is None and panel.result['conditional_full_technology_experience']is None,'crystal_unknown_entry_keeps_candidates_not_added')
                        choose(panel.entry,'event');choose(panel.region,'portal');require(panel.result['conditional_base_experience']is None and panel.result['conditional_full_technology_experience']is None and panel.result['conditional_base_gold']is None,'crystal_wrong_region_not_silently_event_total');observe(stage_id+'-wrong-region')
                    open_stage('ro6_t_1');choose(panel.entry,'event');require(panel.result['conditional_base_gold']=={'minimum':2,'maximum':3},'documented_gold_range_not_midpoint_or_single_guarantee');observe('special-gold-range');shot('special-gold-range')
                    for stage_id in('ro6_b_7','ro6_b_7_b','ro6_n_7_1','ro6_e_7_1'):
                        open_stage(stage_id);choose(panel.entry,'map');require(panel.result['conditional_base_experience']is None and panel.result['conditional_full_technology_experience']is None and panel.result['conditional_base_gold']is None,'both_hidden_sixth_families_do_not_borrow_source0_or_main_floor_rewards');observe(stage_id+'-unknown')
                        if stage_id=='ro6_b_7':shot('hidden-sixth-unknown')
                    open_stage('ro6_n_4_1_dlc1');choose(panel.entry,'map');choose(panel.region,'side_path')
                    require(panel.result['conditional_base_experience']is None and panel.result['conditional_full_technology_experience']is None and panel.result['conditional_base_gold']is None and panel.result['documented_side_path_bonus']['random_relics']==1,'side_path_unknown_base_and_independent_one_random_relic')
                    observe('side-path-independent-bonus');shot('side-path-separate-bonus');choose(panel.entry,'event');require(panel.result['documented_side_path_bonus']is None,'side_path_bonus_not_attached_to_every_entry')
                    open_stage('ro6_s_1');choose(panel.entry,'event');require(panel.result['conditional_base_gold']is None,'unlisted_special_gold_remains_unknown_not_zero');observe('unlisted-special-unknown')
                    open_stage('ro6_t_16');choose(panel.entry,'event');dialog.resize(850,480);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
                        scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'both_modes_readers_have_real_nonzero_range');scroll.setValue(min(3,scroll.maximum()));prior_read=reading(reader);declared=(panel.entry.currentData(),panel.region.currentData(),panel.tabs.currentIndex());same_panel=panel
                        require(prior_read['scroll']>0 and prior_read['position']>prior_read['anchor'],'both_modes_readers_actual_nonzero_scroll_and_selection')
                        require(main_panel.refresh_reference(),'actual_common_stage_parent_refresh');gui.processEvents()
                        require(battle_panel.settlement is same_panel and reading(reader)==prior_read and declared==(panel.entry.currentData(),panel.region.currentData(),panel.tabs.currentIndex())and panel.result['conditional_base_experience']==30,'actual_parent_keeps_replacement_instance_two_readings_entry_region_tab');refreshes.append({'before':prior_read,'after':reading(reader),'declared':declared})
                    dialog.resize(1120,820);gui.processEvents()
                    for provider,label in((model,'new362'),(model.prior,'prior318')):
                        clone=clone_sources(provider,label);path=clone/provider.DATA;raw=path.read_bytes();independent=independent_battle();declared=(panel.entry.currentData(),panel.region.currentData())
                        with patch.object(provider,'ROOT',clone):
                            path.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'parent_source_still_valid_on_settlement_member_damage');gui.processEvents()
                            require(panel.result is None and panel.player.toPlainText()==model.UNAVAILABLE and panel.technical.toPlainText()=='','both_old_and_new_required_source_failures_clear_new_modes_not_keep_old_unknown_panel')
                            require(independent_battle()==independent,'settlement_source_failure_does_not_invalidate_independent_map_enemy_reward_pool')
                            source_failures.append({'source':label,'settlement_cleared':panel.result is None,'other_battle_data_unchanged':True})
                            if label=='new362':shot('settlement-source-loss')
                            path.write_bytes(raw);require(main_panel.refresh_reference(),'actual_parent_settlement_source_recovery');gui.processEvents()
                            require(panel.result is not None and(panel.entry.currentData(),panel.region.currentData())==declared and panel.result['conditional_base_experience']==30 and panel.result['actual_reward_total']is None,'source_recovery_rechecks_same_manual_declarations_without_actual_total')
                    clone=clone_sources(battle,'battle314');path=clone/(battle.PACK+'/source-inputs.json');raw=path.read_bytes()
                    with patch.object(battle,'ROOT',clone):
                        path.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'ordinary_stage_source_owns_unavailable_battle_child');gui.processEvents()
                        require(battle_panel.result is None and panel.result is None and panel.technical.toPlainText()=='','actual_battle_source_loss_parent_clear_also_clears_replacement_settlement')
                        path.write_bytes(raw);require(main_panel.refresh_reference(),'actual_parent_battle_source_recovery');gui.processEvents();require(battle_panel.result is not None and panel.result is not None,'battle_and_settlement_recover_from_actual_current_source')
                    old_dialog=dialog;old_panel=panel;window.reference_panel('scenes');gui.processEvents();require(not old_dialog.isVisible()and old_panel.result is None and old_panel.technical.toPlainText()=='','changing_common_page_closes_and_clears_current_settlement_reader')
                    open_stage('ro6_n_1_2');choose(panel.entry,'map');observe('main-close-reference')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_legacy_battle_context_unchanged')
                    require(all(value==0 for value in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native()
                    old_panel=panel;window.close();gui.processEvents();require(not dialog.isVisible()and old_panel.result is None and old_panel.technical.toPlainText()=='','actual_MainWindow_closes_and_clears_current_battle_settlement')
                    require(len(images)==7,'only_seven_necessary_actual_screenshots');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            QTimer.singleShot(250,exercise);QTimer.singleShot(args.visible_ms,lambda:gui.exit(2)if not done else None)
            exitcode=gui.exec();require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    after=bound_files()
    result={'section':362,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),
            'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),
            'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'actual_source_failure_observations':source_failures,
            'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,
            'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,
            'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1


if __name__=='__main__':raise SystemExit(main())
