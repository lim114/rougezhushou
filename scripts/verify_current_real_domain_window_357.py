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
    from rouge import current_real_domain as model,expansion_reference as version
    for provider in (model,version):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_current_real_domain_window_357.py','scripts/build_current_real_domain_357.py','scripts/verify_full_available.py','tests/test_current_real_domain_357.py','tests/test_current_real_domain_view_357.py','verification/sections/357-preparation/scope.json'])
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
        from rouge import app as app_module,current_real_domain as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge357-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第357节 · 实托邦理念与方针（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('scenes');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
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
                    require(main_panel.real_domain_button.isVisible(),'actual_events_real_domain_entry_visible');QTest.mouseClick(main_panel.real_domain_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.real_domain_dialog;panel=dialog.panel
                    require(dialog.isVisible()and panel.entries.count()==34 and panel.row_id is None and panel.conditions.isHidden(),'actual_all34_manual_directory')
                    def choose(combo,key):
                        idx=combo.findData(key);require(idx>=0,'exact_real_domain_condition_value');combo.setCurrentIndex(idx);gui.processEvents()
                    def select_list(widget,key):
                        item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'real_exact_ideology_or_original_mouse_selection')
                    choose(panel.kind,'policy');require(panel.entries.count()==4,'actual_four_policy_branch');choose(panel.kind,'idea');require(panel.entries.count()==30,'actual_thirty_idea_branch');choose(panel.kind,None)
                    def fact(name):return next(f['matched']for f in panel.result['comparison']['facts']if f['name']==name)
                    for key in('rogue_6_weather_1_a','rogue_6_weather_8_a',model.GAIN,'rogue_6_weather_5_a','rogue_6_weather_9_c','rogue_6_weather_10_a'):
                        select_list(panel.entries,key);require(panel.result['selected']['id']==key and model.version._plain(panel.result['selected']['original']['functionDesc'])in panel.player.toPlainText(),'exact_own_original_chinese_effect');observations.append({'id':key,'kind':panel.result['selected']['kind'],'actual_applied':panel.result['comparison']['actual_applied']})
                        if key=='rogue_6_weather_1_a':
                            require(panel.floor.isVisible()and not panel.squad.isVisible()and not panel.paired.isVisible(),'blackflow_only_own_floor_control');choose(panel.mode,'NORMAL');panel.difficulty.setValue(2);panel.floor.setValue(1);choose(panel.affected,True);choose(panel.action,'both');require(fact('不是第一主层')is False and fact('进入与经过分别核对')is True,'first_floor_exclusion_and_both_actions_not_exclusive');shot('blackflow-floor')
                        if key=='rogue_6_weather_8_a':
                            require(panel.paired.isVisible()and not panel.floor.isVisible()and not panel.squad.isVisible(),'hope_only_own_pair_control');choose(panel.paired,'rogue_6_subweather_1');require(fact('仅配增益方针')is False,'invalid_hope_pair_not_shown_as_possible');choose(panel.paired,model.GAIN);require(fact('仅配增益方针')is True,'exact_hope_gain_pair');shot('hope-pair')
                        if key==model.GAIN:
                            require(panel.squad.isVisible()and panel.paired.isVisible()and not panel.floor.isVisible(),'policy_only_own_squad_pair_controls');choose(panel.paired,model.HOPE);choose(panel.squad,'rogue_6_band_16');require(fact('文明开化方针例外')is True and fact('常规自然生成难度')is None,'gain_immunity_exception_and_early_forced_scope_unknown');choose(panel.action,'enter');require(fact('进入与经过分别核对')is None,'enter_alone_not_proof_of_passing_settlement');choose(panel.action,'both');shot('gain-exception')
                        if key=='rogue_6_weather_5_a':require('应急助力'in panel.player.toPlainText()and '应急助力'not in panel.result['selected']['original']['functionDesc'],'community_emergency_shop_supplement_not_forged_original')
                        if key=='rogue_6_weather_9_c':require('不影响节点类型自身的揭示效果'in panel.player.toPlainText()and '可重复进入的节点在进入1次后'in panel.player.toPlainText(),'fog_natural_and_own_node_reveal_exceptions')
                        if key=='rogue_6_weather_10_a':require('不等于不可选中、隐匿或无敌'in panel.player.toPlainText(),'appearance_not_inferred_as_invisibility_or_invincibility')
                        require(panel.result['comparison']['actual_applied']is None and panel.result['actual_weather']is None and not panel.result['run_updated'],'condition_matches_never_actual_node_activation')
                    select_list(panel.entries,'rogue_6_weather_8_c');panel.difficulty.setValue(12);panel.search.setText('希望的沃土');select_list(panel.entries,'rogue_6_weather_8_c');choose(panel.paired,model.GAIN);dialog.resize(800,480);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'real_nonzero_domain_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();declared_context=panel._context()
                        require(main_panel.refresh_reference(),'actual_events_parent_refresh');gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel._context()==declared_context and panel.row_id=='rogue_6_weather_8_c'and panel.search.text()=='希望的沃土','two_nonzero_readers_conditions_search_selection_and_tab_preserved');refreshes.append({'before':prior,'after':reading(reader)})
                    dialog.resize(1100,820);gui.processEvents()
                    for key in('red_controller','red_seed'):
                        choose(panel.origins,key);QTest.mouseClick(panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.event_dialog;target=model.destination(key)['target'];require(child.isVisible()and(child.panel.event_id,child.panel.scene_id,child.panel.choice_id)==(target['event_id'],target['scene_id'],target['choice_id']),'accurate_actual_red_original_'+key);require(child.panel.result['actual_eligible']is None,'related_original_not_actual_eligibility')
                    panel.search.clear();select_list(panel.entries,'rogue_6_weather_10_a');require(not child.isVisible(),'changing_idea_closes_unrelated_event');choose(panel.origins,'resting');require(panel.open_origin(),'actual_resting_original_entry');child=panel.event_dialog;require(child.panel.source_request=={'category':'scenes','key':'scene_ro6_surprise_enter'}and child.panel.choice_id is None,'resting_scene_not_fabricated_choice_or_phase');shot('resting-original',child.panel)
                    damaged=temporary/'damaged';manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())
                    path=damaged/model.DATA;raw=path.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        path.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'events_parent_independent_source_ready');require(panel.result is None and panel.entries.count()==0 and panel.player.toPlainText()==''and panel.technical.toPlainText()==''and not child.isVisible(),'actual_domain_member_damage_clears_own_readers_choices_and_event');shot('source-loss');path.write_bytes(raw);require(panel.refresh_reference()and panel.row_id is None and panel.entries.currentItem()is None,'source_recovery_requires_manual_idea_or_policy')
                    main_panel.category.setCurrentIndex(main_panel.category.findData('choices'));select_list(main_panel.entries,'choice_ro6_normal3_1');require(main_panel.real_domain_item_button.isVisible(),'exact_original_reverse_domain_entry_visible');QTest.mouseClick(main_panel.real_domain_item_button,Qt.MouseButton.LeftButton);gui.processEvents();old_dialog=dialog;dialog=main_panel.real_domain_dialog;panel=dialog.panel;require(not old_dialog.isVisible()and panel.entries.count()==3 and panel.row_id is None and panel.type_filter.currentData()==model.HOPE and panel.difficulty.value()==-1,'reverse_entry_only_filters_idea_no_auto_phase_or_run_state');shot('reverse-origin');select_list(panel.entries,'rogue_6_weather_8_a');choose(panel.origins,'red_controller');require(panel.open_origin(),'nested_event_for_actual_main_close');child=panel.event_dialog
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_domain_event_tree')
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
    after=bound_files();result={'section':357,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
