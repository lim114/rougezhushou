"""Actual native MainWindow exact-region resource reader; root reviews and runs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_current_region_resources_window_359.py'


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_region_reference as model,expansion_reference as version
    for provider in(model,version):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update((CANONICAL,'scripts/verify_full_available.py','tests/test_current_regions_359.py','tests/test_current_region_view_359.py'))
    for name in('scripts/build_current_regions_359.py','verification/sections/359-preparation/scope.json'):
        if(ROOT/name).is_file():names.add(name)
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Exact regular installed public source required: '+name)
        result[name]=sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',type=Path,required=True);parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
    dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];reverse_readings=[]
    calls={key:0 for key in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
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
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_region_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge359-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第359节 · 区域行动力分项与耗尽条件（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();main_panel=window.reference_panel('regions');panel=main_panel
            state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget;hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native(panel.window())})
            def choose(combo,key):
                index=combo.findData(key);require(index>=0,'exact_region_branch_or_boolean_value');combo.setCurrentIndex(index);gui.processEvents()
            def select_list(widget,key):
                item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key)
                widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents()
                require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_exact_region_or_parent_original_mouse_selection')
            def reading(widget):
                cursor=widget.textCursor();return{'anchor':cursor.anchor(),'position':cursor.position(),'selection':cursor.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def unknown_outcomes():
                value=panel.selected_result
                require(all(value[name]is None for name in('actual_final_entry_ap','actual_exhaustion_triggered','actual_destination_zone','actual_return_node'))and not value['old_budget_replaced']and not value['route_recommended']and not value['run_updated'],'partial_conditions_never_actual_AP_exhaustion_return_or_route')
            def reverse(key):
                nonlocal main_panel,panel
                old=getattr(main_panel,'region_resources_dialog',None);main_panel=window.reference_panel('regions');gui.processEvents()
                select_list(main_panel.entries,key);require(main_panel.region_resources_item_button.isVisible()and main_panel.result['row']['id']==key,'exact_region_original_reverse_button_visible')
                QTest.mouseClick(main_panel.region_resources_item_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=main_panel.region_resources_dialog;panel=dialog.panel
                require(dialog.isVisible()and panel.selected_id()==key and panel.selected_result['row']['id']==key,'actual_reverse_selects_exact_region_not_same_name')
                require(old is None or old is dialog or not old.isVisible(),'reverse_entry_does_not_leave_previous_owned_dialog_visible')
                require(panel.selected_result['declared']=={'action_points':None,'goal_completed':None,'wings':None},'reverse_entry_does_not_infer_run_or_account_declarations')
                reverse_readings.append({'requested':key,'observed':panel.selected_id(),'declarations':deepcopy(panel.selected_result['declared'])});return dialog
            def exercise():
                nonlocal done,failure,panel,main_panel
                dialog=None
                try:
                    bar=tabs.tabBar();index=tabs.indexOf(main_panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center());gui.processEvents()
                    require(tabs.currentWidget()is main_panel,'actual_MainWindow_ordinary_region_page_opened')
                    require(main_panel.region_resources_button.isVisible(),'ordinary_region_resources_entry_visible');QTest.mouseClick(main_panel.region_resources_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    dialog=main_panel.region_resources_dialog;panel=dialog.panel
                    require(dialog.isVisible()and panel.entries.count()==27 and panel.selected_id()is None and panel.selected_result is None,'all27_directory_requires_manual_region_choice')
                    require(panel.declarations.isHidden()and panel.goal_row.isHidden()and panel.wings_row.isHidden(),'overview_has_no_unrelated_condition_controls')
                    for group,count in(('exit',4),('boss',4),('return',19)):
                        choose(panel.group,group);require(panel.entries.count()==count and panel.selected_id()is None,'actual_4_exit4_boss19_return_branches')
                    choose(panel.group,None)
                    source=model.version.packet()['current'];rows=deepcopy(panel.result['rows']);grants=source['details']['relics'][model.AP_FEATURE]['buffs']
                    for row in rows:
                        zone_id=row['id'];select_list(panel.entries,zone_id);actual=panel.selected_result;technical=json.loads(panel.technical.toPlainText())
                        require(actual['row']['id']==zone_id and technical['row']==actual['row'],'actual_exact_selected_region_and_full_technical_source')
                        require(actual['row']['zone']==source['details']['zones'][zone_id]and actual['row']['mission']==source['modules']['gridZone']['zoneMissionBannerData'][zone_id]and actual['row']['exhaustion']==source['modules']['gridZone']['scrapSideBarStepZeroHintBannerData'][zone_id],'all27_exact_region_mission_exhaustion_bindings')
                        originals=[buff for buff in grants if any(value['key']=='zone'and value['valueStr']==zone_id for value in buff['blackboard'])]
                        require(len(originals)==1 and actual['row']['entry_grant']['original']==originals[0],'all27_independent_entry_grant_zone_binding')
                        text=panel.player.toPlainText();require('当前固定资料列示：'+str(row['entry_grant']['amount'])+' 点。'in text and '完整最终入区行动力：未知'in text,'parameter_and_unknown_full_entry_value_not_current_AP')
                        require(panel.declarations.isVisible()and panel.wings_row.isVisible()==(zone_id=='zone_1')and panel.goal_row.isVisible()==(row['group']!='return'),'only_first_region_wings_and_nonportal_goal_controls')
                        require(actual['declared']=={'action_points':None,'goal_completed':None,'wings':None},'region_change_resets_all_page_local_declarations')
                        if row['document_ap_evidence']=='name_shared_not_variant_specific':require('不能把文献当成具体变体的证明'in text,'shared_name_document_not_specific_variant_evidence')
                        if row['document_ap_evidence']=='parameter_only':require('独立数量文献尚未取得，仅列参数'in text,'missing_independent_document_stays_parameter_only')
                        if row['group']=='return':require('不是“进入下一主层”'in text and '不指定真实返回坐标'in text,'portal_return_not_next_floor_or_fabricated_coordinates')
                        unknown_outcomes();observations.append({'zone_id':zone_id,'name':row['name'],'group':row['group'],'entry_parameter':row['entry_grant']['amount'],'document_evidence':row['document_ap_evidence'],'declared':deepcopy(actual['declared']),'actual_final_entry_ap':actual['actual_final_entry_ap']})
                    require(len(observations)==27 and len({r['zone_id']for r in observations})==27,'all27_regions_actually_viewed_with_distinct_ids')
                    select_list(panel.entries,'zone_1')
                    for wings,addition,subtotal in((None,None,None),(False,0,5),(True,1,6)):
                        choose(panel.wings,wings);require(panel.selected_result['wings_reference_addition']==addition and panel.selected_result['base_and_wings_reference_subtotal']==subtotal and panel.selected_result['actual_final_entry_ap']is None,'first_region_wings_unknown0_or1_is_only_partial_subtotal')
                    panel.action_points.setValue(0);choose(panel.goal_completed,False);require(panel.selected_result['exhaustion_description_conditions_match']is True,'zero_AP_unfinished_exit_only_matches_exhaustion_text')
                    shot('first-region-wings')
                    choose(panel.goal_completed,True);require(panel.selected_result['exhaustion_description_conditions_match']is False,'completed_goal_not_unfinished_pursuit_condition')
                    panel.action_points.setValue(1);choose(panel.goal_completed,False);require(panel.selected_result['exhaustion_description_conditions_match']is False,'one_AP_not_exhausted')
                    panel.action_points.setValue(-1);require(panel.selected_result['exhaustion_description_conditions_match']is None,'unknown_AP_not_invented_zero')
                    for zone_id in('zone_4','zone_4_1'):
                        select_list(panel.entries,zone_id);require(panel.selected_result['row']['entry_grant']['amount']==8 and panel.selected_result['row']['document_ap_evidence']=='name_shared_not_variant_specific','both_humus_exact8_parameters_document_not_variant_proof')
                    shot('same-name-variants')
                    select_list(panel.entries,'zone_7');require(panel.goal_row.isVisible()and '击败险路恶敌'in panel.goal_label.text()and '仅抵达其节点不能算目标完成'in panel.player.toPlainText(),'boss_goal_requires_victory_not_merely_arrival')
                    require(panel.selected_result['row']['name']=='盲目者所见'and panel.selected_result['row']['document_ap_evidence']=='parameter_only'and '第七层'not in panel.player.toPlainText(),'new_exact_zone7_not_guessed_seventh_floor')
                    panel.action_points.setValue(0);choose(panel.goal_completed,False);require(panel.selected_result['exhaustion_description_conditions_match']is True,'zero_AP_undefeated_boss_matches_only_warning')
                    choose(panel.goal_completed,True);require(panel.selected_result['exhaustion_description_conditions_match']is False,'defeated_boss_excluded_from_undefeated_warning');choose(panel.goal_completed,False);shot('new-region-boss-goal')
                    portal_id=next(row['id']for row in rows if row['group']=='return');select_list(panel.entries,portal_id)
                    require(panel.goal_row.isHidden()and panel.wings_row.isHidden()and panel.selected_result['declared']['goal_completed']is None,'portal_has_no_main_goal_or_wings_control')
                    for points,status in((-1,None),(0,True),(1,False)):
                        panel.action_points.setValue(points);require(panel.selected_result['exhaustion_description_conditions_match']is status and panel.selected_result['actual_return_node']is None,'portal_unknown_zero_one_boundary_never_actual_return')
                    panel.action_points.setValue(0);shot('portal-return')
                    select_list(panel.entries,'zone_1');panel.action_points.setValue(0);choose(panel.goal_completed,False);choose(panel.wings,True);dialog.resize(740,500);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
                        scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'two_region_readers_have_real_scroll_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();declared=deepcopy(panel.selected_result['declared'])
                        require(prior['scroll']>0 and prior['position']>prior['anchor'],'two_readers_actual_nonzero_scroll_and_selection')
                        require(main_panel.refresh_reference(),'actual_region_parent_refresh');gui.processEvents()
                        require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.selected_id()=='zone_1'and panel.selected_result['declared']==declared,'actual_parent_preserves_region_declarations_tab_and_two_nonzero_readers');refreshes.append({'before':prior,'after':reading(reader),'declared':declared})
                    dialog.resize(1060,840);gui.processEvents()
                    damaged=temporary/'damaged-public';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=damaged/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=damaged/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        target.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'ordinary_parent_source_independent_of_region_member_damage');gui.processEvents()
                        require(panel.result is None and panel.selected_result is None and panel.selected_id()is None and panel.entries.count()==0 and panel.player.toPlainText()==model.UNAVAILABLE and panel.technical.toPlainText()=='','actual_member_damage_clears_old_parameters_conditions_and_reading')
                        require(panel.declarations.isHidden()and panel.goal_row.isHidden()and panel.wings_row.isHidden()and panel.action_points.value()==-1 and panel.goal_completed.currentData()is None and panel.wings.currentData()is None,'source_loss_resets_all_page_local_declarations');shot('source-loss')
                        target.write_bytes(raw);require(main_panel.refresh_reference(),'actual_parent_recovery_refresh');gui.processEvents()
                        require(panel.entries.count()==27 and panel.selected_id()is None and panel.selected_result is None,'restored_source_requires_manual_region_choice')
                    for key in('zone_4','zone_4_1','zone_7',portal_id):
                        dialog=reverse(key);unknown_outcomes()
                    dialog=reverse('zone_4_1');shot('reverse-exact-variant')
                    old_dialog=dialog;old_panel=panel;main_panel.category.setCurrentIndex(main_panel.category.findData('scenes'));gui.processEvents()
                    require(main_panel.region_resources_item_button.isHidden()and not old_dialog.isVisible()and old_panel.result is None and old_panel.entries.count()==0,'changing_parent_category_closes_and_clears_owned_region_dialog')
                    dialog=reverse('zone_7');old_dialog=dialog;old_panel=panel;window.reference_panel('stages');gui.processEvents()
                    require(not old_dialog.isVisible()and old_panel.result is None and old_panel.selected_result is None,'changing_common_page_closes_and_clears_owned_region_dialog')
                    dialog=reverse('zone_1');panel.action_points.setValue(0);choose(panel.goal_completed,False);choose(panel.wings,True)
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_battle_context_unchanged')
                    require(all(value==0 for value in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native()
                    old_panel=panel;window.close();gui.processEvents();require(not dialog.isVisible()and old_panel.result is None and old_panel.selected_result is None and old_panel.entries.count()==0,'actual_MainWindow_closes_and_clears_owned_region_dialog')
                    require(len(images)==6,'only_six_necessary_actual_screenshots');done=True;gui.exit(0)
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
    result={'section':359,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),
            'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),
            'unique_checks':len(checks),'checks':checks,'actual_region_readings':observations,'actual_reverse_readings':reverse_readings,
            'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,
            'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,
            'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,
            'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1


if __name__=='__main__':raise SystemExit(main())
