"""Actual native MainWindow portal-rule reader; root installs/runs after review."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_current_portal_rules_window_358.py'


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_portal_rules as model,current_portal as portal,expansion_reference as version
    for provider in(model,portal,version):
        names.add(provider.MANIFEST);manifest=json.loads((ROOT/provider.MANIFEST).read_bytes());names.update(manifest['files'])
    names.update((CANONICAL,'scripts/verify_full_available.py','tests/test_current_portal_rules_358.py','tests/test_current_portal_rules_view_358.py'))
    # Bind actual installed build/scope artifacts only; no nonexistent candidate is presumed installed.
    for name in('scripts/build_current_portal_rules_358.py','verification/sections/358-preparation/scope.json'):
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
    before=bound_files();checks=[];images=[];observations=[];refreshes=[]
    calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
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
        from PySide6.QtWidgets import QApplication,QTabWidget,QPlainTextEdit
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_portal_rules as model,current_portal as portal
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge358-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第358节 · 秘境乌托邦规则与原区域表（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();main_panel=window.reference_panel('scenes');panel=main_panel
            state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget;hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label,widget=None):
                gui.processEvents();widget=panel if widget is None else widget;file=dest.with_name('window-'+label+'.png');assert not file.exists()
                require(widget.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native(widget.window())})
            def choose(combo,key):
                index=combo.findData(key);require(index>=0,'exact_portal_rule_or_condition_value');combo.setCurrentIndex(index);gui.processEvents()
            def select_list(widget,key):
                item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key)
                widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents()
                require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_exact_rule_region_or_parent_original_mouse_selection')
            def reading(widget):
                cursor=widget.textCursor();return{'anchor':cursor.anchor(),'position':cursor.position(),'selection':cursor.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def declared():
                return{'branch':panel.branch.currentData(),'fog':panel.fog.currentData(),'selection':panel.selected_key,
                       'floor':panel.floor.currentData(),'node_type':panel.node_type.currentData(),'moved':panel.moved.currentData(),
                       'passed':panel.passed.currentData(),'completed_shop':panel.completed_shop.currentData(),'source':panel.source_combo.currentData()}
            def source(kind,key):
                request=next(panel.source_combo.itemData(i)for i in range(panel.source_combo.count())if panel.source_combo.itemData(i)and panel.source_combo.itemData(i)['kind']==kind and panel.source_combo.itemData(i)['key']==key)
                choose(panel.source_combo,request);require(panel.source_button.isVisible()and panel.source_button.isEnabled(),'accurate_source_button_visible')
                QTest.mouseClick(panel.source_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.link_dialog
                require(child is not None and child.isVisible(),'actual_owned_original_source_window_opened');return child
            def raw_source(child,expected):
                source_tabs=child.findChildren(QTabWidget);require(len(source_tabs)==1,'raw_original_has_two_actual_reading_tabs')
                source_tabs=source_tabs[0];require(source_tabs.count()==2,'raw_original_has_two_actual_reading_tabs')
                player=source_tabs.widget(0);technical=source_tabs.widget(1)
                require(isinstance(player,QPlainTextEdit)and isinstance(technical,QPlainTextEdit)and player.isReadOnly()and technical.isReadOnly(),'raw_original_readers_readonly')
                value=json.loads(technical.toPlainText());require(value['original']==expected and value['reference_only']is True and value['actual_held']is None and not value['run_updated'],'actual_popup_complete_exact_original_and_unknown_outcome')
                return player.toPlainText()
            def reverse(category,key):
                nonlocal main_panel,panel
                previous=getattr(main_panel,'portal_rules_dialog',None)
                main_panel=window.reference_panel(category);gui.processEvents()
                if category=='relics':choose(main_panel.item_kind,'NODE_BUOY')
                select_list(main_panel.entries,key);require(main_panel.portal_rules_item_button.isVisible(),'exact_selected_parent_original_reverse_button_visible')
                QTest.mouseClick(main_panel.portal_rules_item_button,Qt.MouseButton.LeftButton);gui.processEvents()
                dialog=main_panel.portal_rules_dialog;panel=dialog.panel
                require(dialog.isVisible()and panel.result is not None and(previous is None or previous is not dialog and not previous.isVisible()),'reverse_entry_uses_new_owned_source_not_stale_dialog')
                return dialog
            def exercise():
                nonlocal done,failure,panel,main_panel
                dialog=None;child=None
                try:
                    bar=tabs.tabBar();index=tabs.indexOf(main_panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(index).center());gui.processEvents()
                    require(tabs.currentWidget()is main_panel,'actual_MainWindow_common_node_event_page_opened')
                    require(main_panel.portal_rules_button.isVisible(),'ordinary_portal_rule_entry_visible');QTest.mouseClick(main_panel.portal_rules_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    dialog=main_panel.portal_rules_dialog;panel=dialog.panel
                    require(dialog.isVisible()and panel.entries.count()==9 and panel.selected_key is None,'actual_all9_manual_rules_directory')
                    require(panel.floor_controls.isHidden()and panel.refresh_controls.isHidden()and panel.shop_controls.isHidden(),'overview_has_no_foreign_specific_conditions')
                    require(len(panel.result['data']['fogs'])==6 and len(panel.result['data']['original_enter_scenes'])==19,'all6_fog_and19_exact_enter_sources_retained')
                    for fog in model.FOGS:
                        choose(panel.fog,fog);require(panel.entries.count()==(4 if fog=='红雾'else 1)and panel.selected_key is None,'each_fog_filters_real_rules_without_auto_selection')
                        observations.append({'kind':'fog','fog':fog,'actual_visible_candidates':panel.entries.count(),'selected_rule':panel.selected_key})
                    choose(panel.fog,None)
                    for rule_id,row in panel.result['data']['rules'].items():
                        select_list(panel.entries,rule_id)
                        require(row['original']['functionDesc']in panel.player.toPlainText(),'own_rule_original_chinese_description_preserved')
                        require(panel.floor_controls.isVisible()==bool(row['documented_main_floors'])and panel.refresh_controls.isVisible()==(rule_id=='variation_5'),'only_related_rule_specific_controls_visible')
                        if rule_id=='variation_5':
                            choose(panel.node_type,'BATTLE_SHOP');choose(panel.moved,True);choose(panel.passed,False);choose(panel.completed_shop,True)
                            comparison=json.loads(panel.technical.toPlainText())['condition_comparison']
                            require(panel.shop_controls.isVisible()and comparison['status']=='documented_completed_shop_exception'and comparison['actual_will_refresh']is None,'completed_blue_fog_shop_exception_not_predicted_refresh')
                            shot('blue-completed-shop')
                            choose(panel.completed_shop,False);require(json.loads(panel.technical.toPlainText())['condition_comparison']['status']=='matches_listed_conditions_only','uncompleted_shop_only_matches_written_conditions')
                            choose(panel.node_type,'BATTLE_NORMAL');choose(panel.passed,True)
                            require(panel.shop_controls.isHidden()and json.loads(panel.technical.toPlainText())['condition_comparison']['status']=='outside_unpassed_wording','passed_node_and_hidden_shop_state_not_reused')
                        if rule_id in('variation_7','variation_8','variation_9'):
                            allowed=row['documented_main_floors'];choose(panel.floor,allowed[0]);require('条件相符'in panel.player.toPlainText(),'listed_main_floor_match_not_actual_access')
                            rejected=next(value for value in range(1,6)if value not in allowed);choose(panel.floor,rejected);require('不在文献列出的'in panel.player.toPlainText(),'listed_main_floor_exclusion_not_server_result')
                        if rule_id=='variation_8':
                            choose(panel.floor,4);text=panel.player.toPlainText();require('获胜的'in text and '正式'in text and '原文与补充'in text and row['original']['functionDesc']in text,'consumption_original_and_community_disambiguation_separate');shot('consumption-original')
                        observations.append({'kind':'rule','id':rule_id,'fog':row['fog'],'original':row['original'],'actual_rule':panel.result['actual_current_rule'],'actual_rewards':panel.result['actual_rewards']})
                        require(panel.result['actual_current_rule']is None and panel.result['actual_rewards']is None and panel.result['actual_zone_to_fog_mapping']is None and not panel.result['run_updated']and not panel.result['calculation_applied'],'rules_never_apply_live_run_or_numerical_calculation')
                    select_list(panel.entries,'variation_8');choose(panel.floor,4);dialog.resize(740,470);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
                        scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'both_portal_readers_have_real_nonzero_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();conditions=declared()
                        require(prior['scroll']>0 and prior['position']>prior['anchor'],'both_readers_actual_nonzero_scroll_and_text_selection')
                        require(main_panel.refresh_reference(),'actual_ordinary_parent_refresh');gui.processEvents()
                        require(reading(reader)==prior and panel.tabs.currentIndex()==tab and declared()==conditions,'parent_refresh_preserves_two_nonzero_readers_rule_conditions_and_tab');refreshes.append({'before':prior,'after':reading(reader)})
                    dialog.resize(1100,840);gui.processEvents();choose(panel.branch,'refresh')
                    require(panel.entries.count()==19 and panel.fog.isHidden()and panel.floor_controls.isHidden()and panel.refresh_controls.isHidden(),'actual19_separate_regions_without_fog_or_foreign_rule_controls')
                    tables=panel.result['data']['original_roll_node_data'];require(len(tables)==3,'three_original_refresh_tables_retained')
                    for zone_id,original in panel.result['data']['original_portal_zones'].items():
                        select_list(panel.entries,zone_id);technical=json.loads(panel.technical.toPlainText())
                        require(technical['selected']==original and technical['original_refresh_table']==tables.get(zone_id),'every_exact_region_and_own_table_or_unknown_preserved')
                        if zone_id in tables:
                            require(list(tables[zone_id]['groups'])==['INCIDENT','BATTLE_NORMAL','BATTLE_ELITE','BATTLE_SHOP','WISH']and '不是所有乌托邦的通用节点池'in panel.player.toPlainText(),'table_only_five_types_no_event_pool_or_probability')
                        else:require('未列独立刷新表'in panel.player.toPlainText(),'missing_region_table_not_filled_from_same_name_or_suffix')
                        observations.append({'kind':'region','id':zone_id,'table_present':zone_id in tables,'actual_fog':panel.result['actual_zone_to_fog_mapping']})
                    select_list(panel.entries,'zone_portal_normal_5_1');shot('region-table')
                    child=source('region','zone_portal_normal_5_1');require('实际雾色'in raw_source(child,panel.result['data']['original_portal_zones']['zone_portal_normal_5_1']),'exact_region_original_no_fog_guess');child.close()
                    select_list(panel.entries,'zone_portal_normal_1_1');shot('region-no-table')
                    choose(panel.branch,'rules');select_list(panel.entries,'variation_5');child=source('portal_fog','蓝雾')
                    require(child.panel.scene_id=='fog:蓝雾'and child.panel.scene.currentData()=='fog:蓝雾'and child.panel.choice_id is None,'accurate341_blue_dialogue_no_auto_choice')
                    exact=portal.reference()['scenes']['fog:蓝雾'];require(child.panel.result['scenes']['fog:蓝雾']==exact and model.version._plain(exact['description'])in child.panel.player.toPlainText(),'complete341_exact_blue_scene_and_original_text')
                    require(child.panel.result['actual_eligible']is None and child.panel.result['actual_entered']is None,'341_source_not_actual_entry_or_payment')
                    old_child=child;select_list(panel.entries,'variation_6');require(not old_child.isVisible(),'changing_rule_closes_unrelated341_source')
                    child=source('item','rogue_6_bubble_01');original=panel.result['data']['original_items']['rogue_6_bubble_01'];text=raw_source(child,original)
                    require(original['type']=='NODE_BUOY'and '地图标志'in text and '不是收藏品'in text,'exact_resident_marker_source_not_fabricated_relic');shot('resident-marker-source',child)
                    old_child=child;child=source('node_type','PORTAL');require(not old_child.isVisible(),'changing_open_source_closes_previous_owned_window')
                    require('准确节点类型'in raw_source(child,panel.result['data']['original_nodes']['PORTAL']),'accurate_PORTAL_node_original_source')
                    damaged=temporary/'damaged-public';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/name).read_bytes())
                    data_name=model.PACK+'/reference-data.json';bad=damaged/data_name;raw=bad.read_bytes();original_file=model.version._file
                    def own_file(name):return damaged/name if name==model.MANIFEST or name in manifest['files']else original_file(name)
                    with patch.object(model.version,'_file',side_effect=own_file):
                        bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'ordinary_parent_own_version_remains_available_on_member_damage');gui.processEvents()
                        require(panel.result is None and panel.entries.count()==0 and panel.selected_key is None and panel.technical.toPlainText()==''and panel.player.toPlainText()==model.UNAVAILABLE and not child.isVisible(),'actual_member_damage_clears_old_rule_regions_readers_and_source_tree')
                        require(panel.floor_controls.isHidden()and panel.refresh_controls.isHidden()and panel.shop_controls.isHidden()and panel.source_combo.count()==0 and not panel.source_button.isEnabled(),'bad_source_clears_all_specific_controls_and_entries');shot('source-loss')
                        bad.write_bytes(raw);require(main_panel.refresh_reference(),'actual_parent_recovery_refresh');gui.processEvents();require(panel.result is not None and panel.selected_key is None and panel.entries.currentItem()is None,'restored_source_requires_manual_rule_not_old_selection')
                    red_scene=next(key for key,row in panel.result['data']['original_enter_scenes'].items()if row['fog']=='红雾')
                    old_dialog=dialog;dialog=reverse('scenes',red_scene)
                    require(not old_dialog.isVisible()and panel.fog.currentData()=='红雾'and panel.entries.count()==4 and panel.selected_key is None and panel.floor.currentData()is None,'exact_scene_reverse_red_stays_four_candidates_no_auto_rule');shot('reverse-red-candidates')
                    dialog=reverse('regions','zone_portal_normal_5_1')
                    require(panel.branch.currentData()=='refresh'and panel.selected_key=='zone_portal_normal_5_1'and panel.fog.currentData()is None and panel.result['actual_zone_to_fog_mapping']is None,'exact_region_reverse_only_selects_own_table_without_suffix_fog')
                    dialog=reverse('relics','rogue_6_bubble_01')
                    require(panel.target['source_request']=={'category':'items','key':'rogue_6_bubble_01'}and panel.selected_key=='variation_6'and panel.fog.currentData()=='绿雾','NODE_BUOY_reverse_uses_exact_items_identity_not_relic_effect')
                    child=source('item','rogue_6_bubble_01');old_dialog=dialog
                    choose(main_panel.item_kind,None);unrelated=next(main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)!='rogue_6_bubble_01')
                    select_list(main_panel.entries,unrelated);require(main_panel.portal_rules_item_button.isHidden()and not old_dialog.isVisible()and not child.isVisible(),'changing_actual_parent_item_closes_tree_and_unrelated_item_has_no_button')
                    dialog=reverse('scenes',red_scene);select_list(panel.entries,'variation_1');child=source('portal_fog','红雾')
                    old_dialog=dialog;old_child=child;window.reference_panel('stages');gui.processEvents();require(not old_dialog.isVisible()and not old_child.isVisible(),'changing_common_page_closes_portal_and341_source_tree')
                    dialog=reverse('scenes',red_scene);select_list(panel.entries,'variation_1');child=source('portal_fog','红雾')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_battle_context_unchanged')
                    require(all(value==0 for value in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native()
                    window.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_portal_rules_and341_source_tree')
                    require(sum(row['kind']=='fog'for row in observations)==6 and sum(row['kind']=='rule'for row in observations)==9 and sum(row['kind']=='region'for row in observations)==19,'all6_fog9_rules19_regions_actually_exercised')
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
    result={'section':358,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),
            'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),
            'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,
            'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,
            'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,
            'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1


if __name__=='__main__':raise SystemExit(main())
