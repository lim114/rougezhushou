"""Actual current enemy entry into Sun-boss documents and fixed-map ownership."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_current_sun_boss_window_368.py'


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_sun_boss as model,current_battle_reference as battle,current_map_position as maps,current_terrain as terrain,expansion_reference as version
    from rouge import current_stage_directory as directory,current_reward_reference as rewards,current_settlement_modes_reference as settlement,boss_map_markers as boss_symbols,current_map_markers as symbols
    for provider in(model,battle,maps,terrain,version,directory,rewards,settlement,settlement.prior,boss_symbols,symbols):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    for name in('research/p3-expansion-313/map-images.json','research/p3-current-battle-314/enemy-images.json'):
        names.add(name);names.update(value['file']for value in json.loads((ROOT/name).read_bytes())['images'].values())
    names.update((CANONICAL,'scripts/verify_full_available.py','tests/test_current_sun_boss_368.py','tests/test_current_sun_boss_view_368.py'))
    if(ROOT/'verification/sections/368-preparation/scope.json').is_file():names.add('verification/sections/368-preparation/scope.json')
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Exact regular public source required: '+name)
        result[name]=sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',type=Path,required=True);parser.add_argument('--visible-ms',type=int,default=180000);args=parser.parse_args()
    dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];source_failures=[];related_readings=[];dialog_close_observations=[]
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
        import win32gui,win32process,win32con
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_sun_boss as model,current_battle_reference as battle,current_map_position as maps
        from rouge.current_sun_boss_view import CurrentSunBossDialog
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge368-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第368节 · 熄日形态与固定地形（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();main_panel=window.reference_panel('stages');panel=main_panel;dialog=None;battle_dialog=None;battle_panel=None
            state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget;hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label,widget=None):
                widget=panel if widget is None else widget;gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(widget.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native(widget.window())})
            def choose(combo,value):
                index=combo.findData(value);require(index>=0,'exact_existing_document_control_option');combo.setCurrentIndex(index);gui.processEvents()
            def select_stage(stage_id):
                window.reference_panel('stages');item=next(main_panel.entries.item(i)for i in range(main_panel.entries.count())if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==stage_id)
                main_panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(main_panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=main_panel.entries.visualItemRect(item).center());gui.processEvents()
                require(main_panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)==stage_id,'actual_exact_current_stage_mouse_selection')
            def open_battle(stage_id):
                nonlocal battle_dialog,battle_panel
                previous=battle_dialog;old_mechanism=getattr(battle_panel,'sun_boss_dialog',None)if battle_panel else None;old_map=old_mechanism.panel.map_dialog if old_mechanism else None
                select_stage(stage_id);require(main_panel.battle_button.isVisible()and main_panel.battle_button.isEnabled(),'ordinary_current_stage_battle_button_visible')
                QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle_dialog=main_panel.current_battle_dialog;battle_panel=battle_dialog.panel
                require(battle_dialog.isVisible()and battle_panel.stage_id==stage_id and battle_panel.result['id']==stage_id,'actual_MainWindow_current_battle_exact_stage')
                bar=battle_panel.tabs.tabBar();QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(1).center());gui.processEvents()
                if previous is not None:
                    require(not previous.isVisible(),'changing_stage_closes_previous_actual_battle')
                    if old_mechanism is not None:require(not old_mechanism.isVisible()and(old_map is None or not old_map.isVisible()),'changing_stage_closes_owned_sun_and_map_tree')
            def select_parent_enemy(key):
                require(battle_panel.enemy_choices.select_value(key),'actual_current_enemy_selector_exact_key');gui.processEvents()
                require(battle_panel.enemy_key==key and battle_panel.enemy_combo.currentData()==key,'actual_current_enemy_scope_matches_selected_reference')
            def open_exact(stage_id,key):
                nonlocal dialog,panel
                if battle_panel is None or battle_panel.stage_id!=stage_id:open_battle(stage_id)
                old=dialog;old_map=old.panel.map_dialog if old else None;select_parent_enemy(key)
                require(battle_panel.sun_boss_button.isVisible()and battle_panel.sun_boss_button.isEnabled()and model.target_available(stage_id,key),'only_exact_supported_current_enemy_has_sun_entry')
                QTest.mouseClick(battle_panel.sun_boss_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle_panel.sun_boss_dialog;panel=dialog.panel
                require(isinstance(dialog,CurrentSunBossDialog)and dialog.isVisible()and panel.stage_id==stage_id and panel.selected_key==key and panel.entry_key==key,'ordinary_current_enemy_button_opens_exact_sun_reference')
                require(panel.result['battle_source_identity']==battle_panel.result['source_identity']and panel.result['level_key']==battle_panel.result['level_key'],'current_parent_and_document_exact_source_agree')
                if old is not None:require(not old.isVisible()and(old_map is None or not old_map.isVisible()),'replacing_enemy_document_closes_previous_sun_map_tree')
                return model.entity(panel.result,key)
            def choose_form(key):
                require(panel.forms.select_value(key),'actual_document_form_branch_exact_selection');gui.processEvents();require(panel.selected_key==key,'form_branch_changes_only_document_selection')
            def reading(widget):
                cursor=widget.textCursor();return{'anchor':cursor.anchor(),'position':cursor.position(),'selection':cursor.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def assert_unknown():
                value=panel.result
                require(all(value[name]is None for name in('actual_form','actual_phase','actual_faith','actual_skill_time','actual_terrain','actual_altar_cells'))and not value['numeric_model_added']and not value['current_server_verified']and not value['run_updated'],'document_selection_never_actual_form_faith_phase_time_terrain_or_stats')
            def map_child():
                require(panel.map_button.isVisible()and panel.map_button.isEnabled(),'only_related_terrain_or_altar_topic_has_map_entry')
                QTest.mouseClick(panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.map_dialog;require(child is not None and child.isVisible(),'actual_owned_fixed_map_child_opened')
                mapped=child.panel.result;reference=panel.result;level=reference['data']['originals']['levels'][reference['level_key']]
                require(mapped['stage_id']==reference['stage_id']and mapped['current_level_key']==reference['level_key']and mapped['complete_current_geometry']['mapData']==level['mapData'],'fixed_map_exact_stage_level_and_complete_mapData_not_dynamic_projection')
                require(child.panel.selected is None and child.panel.grid.selected is None and not mapped['actual_combat_positions_verified']and not mapped['full_map_projection_verified']and not mapped['run_updated'],'fixed_map_no_auto_altar_terrain_selection_or_actual_position')
                require(not child.panel.original.pixmap.isNull(),'exact_fixed_original_map_image_visible');return child
            def closed_snapshot(owned,old_map):
                child=owned.panel;portrait=child.portrait.pixmap()
                return {'document':{'hidden':not owned.isVisible(),'result_cleared':child.result is None,
                    'selection_cleared':child.selected_key is None,'entry_cleared':child.entry_key is None,
                    'form_unselected':child.form_combo.currentData()is None,'cards_empty':child.card.count()==0,
                    'related_empty':child.related.count()==0,'related_disabled':not child.related_button.isEnabled(),
                    'map_pointer_cleared':child.map_dialog is None,'map_entry_hidden':child.map_button.isHidden(),
                    'portrait_hidden':child.portrait.isHidden(),'portrait_cleared':child.portrait.text()==''and(portrait is None or portrait.isNull()),
                    'player_cleared':child.player.toPlainText()==model.UNAVAILABLE,'technical_cleared':child.technical.toPlainText()==''},
                    'map':{'hidden':not old_map.isVisible(),'result_cleared':old_map.panel.result is None,
                    'selection_cleared':old_map.panel.selected is None,'grid_unselected':old_map.panel.grid.selected is None,
                    'image_bytes_cleared':old_map.panel.image_raw is None,'original_image_cleared':old_map.panel.original.pixmap.isNull()}}
            def clone_sources(provider,label):
                clone=temporary/label;manifest=json.loads((ROOT/provider.MANIFEST).read_bytes())
                for name in(provider.MANIFEST,*manifest['files']):
                    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                return clone
            def exercise():
                nonlocal done,failure,dialog,panel
                try:
                    index=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(index).center());gui.processEvents()
                    require(tabs.currentWidget()is main_panel and main_panel.scope.isHidden()and main_panel.scope.currentData()is False,'actual_common_battle_directory_not_version_only_page')
                    base=model.packet();require(base is not None and len(base['data']['bindings'])==2,'actual_pinned_two_sun_stage_bindings_available')
                    card_count=0
                    for sid in model.STAGES:
                        for binding in base['data']['bindings'][sid]['rows']:
                            row=open_exact(sid,binding['key']);require(row['entity_id']==binding['entity_id']and row['level']==binding['level']and row['enemy']['raw_binding']==binding['raw_binding'],'all_six_exact_current_form_bindings_not_name_or_ID_alias')
                            require(len(panel.result['declared_appearances'])==1 and panel.result['declared_appearances'][0]['raw']['key']=='enemy_2157_shadvr','one_declared_actor_not_sum_of_three_form_records')
                            require(len(panel.forms.groups)==2 and len(model.related_forms(panel.result,row['key']))==2,'forms_are_real_separate_branch_options_with_two_related_forms')
                            for topic,label in model.TOPICS:
                                choose(panel.topic,topic);require(not panel.card.isHidden()if topic=='skills'else panel.card.isHidden(),'only_skills_shows_current_form_card_control')
                                require(not panel.map_button.isHidden()if topic in('terrain','altar')else panel.map_button.isHidden(),'only_terrain_and_altar_show_fixed_map_control')
                                require('不是三名'in panel.player.toPlainText()and '未知'in panel.player.toPlainText(),'ordinary_player_sees_one_boss_three_forms_and_actual_unknowns')
                            choose(panel.topic,'skills');cards=model.cards(panel.result,row['key']);require(panel.card.count()==len(cards)+1,'all_and_only_selected_form_document_cards')
                            for card in cards:
                                choose(panel.card,card['index']);tech=json.loads(panel.technical.toPlainText());require(tech['complete_selected_document_card']==card and tech['selected_current_reference']['entity_id']==row['entity_id'],'every_full_original_card_and_exact_form_kept_in_source_reading')
                                require(card['title']in panel.player.toPlainText(),'all_original_card_titles_readable_in_player_page');card_count+=1
                            assert_unknown();observations.append({'stage_id':sid,'key':row['key'],'entity_id':row['entity_id'],'level':row['level'],'form':row['form'],'topics':5,'full_cards':len(cards),'actual_form':panel.result['actual_form']})
                            if sid=='ro6_b_7'and row['form']=='normal':choose(panel.topic,'faith');shot('faith-actual-damage-only')
                            if sid=='ro6_b_7'and row['form']=='sun':choose(panel.topic,'skills');choose(panel.card,3);require('不猜对应关系'in panel.player.toPlainText(),'slash_time_headers_not_guessed_into_actual_mode_clock');shot('sun-complete-skill')
                            if sid=='ro6_b_7_b'and row['form']=='eclipse':choose(panel.topic,'skills');choose(panel.card,3);require('熄日的祭仪'in panel.player.toPlainText()and '熄日的祭坛'in panel.player.toPlainText(),'game_and_document_skill_names_both_preserved');shot('eclipse-title-difference')
                    require(len(observations)==6 and card_count==30,'all_two_by_three_exact_references_and_15_unique_cards_each_config_actually_read')
                    row=open_exact('ro6_b_7','0');choose(panel.topic,'terrain');old_map=map_child();closed=dialog;close_source=panel.result['source_identity'];close_native=native(closed)
                    # This is the native system-close path used by the owned title-bar X, not a claimed physical mouse click.
                    win32gui.SendMessage(close_native['hwnd'],win32con.WM_SYSCOMMAND,win32con.SC_CLOSE,0);gui.processEvents();snapshot=closed_snapshot(closed,old_map)
                    require(all(snapshot['document'].values()),'native_titlebar_X_clears_sun_document_form_cards_portrait_related_and_map_pointer')
                    require(all(snapshot['map'].values()),'native_titlebar_X_clears_captured_owned_map_result_selection_and_image')
                    require(window.isVisible()and battle_dialog.isVisible()and battle_panel.result is not None and battle_panel.sun_boss_button.isVisible()and battle_panel.sun_boss_button.isEnabled(),'native_titlebar_X_keeps_actual_battle_and_exact_reopen_entry_usable')
                    row=open_exact('ro6_b_7','0')
                    require(dialog is not closed and panel.result['source_identity']==close_source and panel.result['battle_source_identity']==battle_panel.result['source_identity']and panel.selected_key=='0','ordinary_entry_reopens_fresh_exact_sun_document_after_native_titlebar_X')
                    choose(panel.topic,'terrain');fresh_map=map_child()
                    require(fresh_map is not old_map and fresh_map.panel.result is not None and fresh_map.panel.result['stage_id']=='ro6_b_7','native_titlebar_X_reopen_gets_new_exact_owned_map_not_old_window')
                    require(all(closed_snapshot(closed,old_map)['document'].values())and all(closed_snapshot(closed,old_map)['map'].values()),'native_titlebar_X_reopen_does_not_revive_closed_sun_or_map_contents')
                    dialog_close_observations.append({'method':'native_titlebar_X_system_close_command','native_before':close_native,'closed_snapshot':snapshot,'reopened_stage':panel.stage_id,'reopened_key':panel.selected_key,'fresh_map':True})
                    closed=dialog;old_map=fresh_map;close_source=panel.result['source_identity'];close_native=native(closed)
                    QTest.keyClick(closed,Qt.Key.Key_Escape);gui.processEvents();snapshot=closed_snapshot(closed,old_map)
                    require(all(snapshot['document'].values()),'actual_Escape_key_clears_sun_document_form_cards_portrait_related_and_map_pointer')
                    require(all(snapshot['map'].values()),'actual_Escape_key_clears_captured_owned_map_result_selection_and_image')
                    require(window.isVisible()and battle_dialog.isVisible()and battle_panel.result is not None and battle_panel.sun_boss_button.isVisible()and battle_panel.sun_boss_button.isEnabled(),'actual_Escape_keeps_actual_battle_and_exact_reopen_entry_usable')
                    row=open_exact('ro6_b_7','0')
                    require(dialog is not closed and panel.result['source_identity']==close_source and panel.result['battle_source_identity']==battle_panel.result['source_identity']and panel.selected_key=='0','ordinary_entry_reopens_fresh_exact_sun_document_after_Escape')
                    choose(panel.topic,'terrain');fresh_map=map_child()
                    require(fresh_map is not old_map and fresh_map.panel.result is not None and fresh_map.panel.result['stage_id']=='ro6_b_7','actual_Escape_reopen_gets_new_exact_owned_map_not_old_window')
                    require(all(closed_snapshot(closed,old_map)['document'].values())and all(closed_snapshot(closed,old_map)['map'].values()),'actual_Escape_reopen_does_not_revive_closed_sun_or_map_contents')
                    dialog_close_observations.append({'method':'actual_QTest_Escape_key','native_before':close_native,'closed_snapshot':snapshot,'reopened_stage':panel.stage_id,'reopened_key':panel.selected_key,'fresh_map':True})
                    row=open_exact('ro6_b_7','0');choose(panel.topic,'terrain');child=map_child();shot('fixed-terrain-no-phase-projection',child.panel)
                    choose(panel.topic,'altar');require('没有祭台预置原项'in panel.player.toPlainText()and panel.result['data']['altar_original_stage_binding']is None,'altar_document_does_not_create_missing_predefined_cell_or_entity');shot('altar-mechanism-boundary')
                    request=model.related_forms(panel.result,'0')[0];choose(panel.related,request);parent_key=battle_panel.enemy_key;QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    require(panel.selected_key==request['key']and panel.topic.currentData()=='overview'and panel.card.currentData()is None and not child.isVisible()and battle_panel.enemy_key==parent_key,'exact_related_form_switches_documents_not_actual_current_form_or_foreign_skill');related_readings.append(request)
                    choose_form('6');choose(panel.topic,'skills');choose(panel.card,5);dialog.resize(850,480);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'both_readers_have_real_nonzero_range');scroll.setValue(min(3,scroll.maximum()));old=reading(reader)
                        declared=(panel.form_combo.currentData(),panel.forms.branch.currentData(),panel.topic.currentData(),panel.card.currentData(),panel.tabs.currentIndex());same=panel
                        require(old['scroll']>0 and old['position']>old['anchor'],'both_real_readers_nonzero_scroll_and_selection');require(main_panel.refresh_reference(),'actual_common_stage_parent_refresh');gui.processEvents()
                        require(battle_panel.sun_boss_dialog.panel is same and declared==(panel.form_combo.currentData(),panel.forms.branch.currentData(),panel.topic.currentData(),panel.card.currentData(),panel.tabs.currentIndex())and reading(reader)==old,'actual_parent_keeps_instance_form_branch_topic_card_tab_and_both_readings');refreshes.append({'before':old,'after':reading(reader),'declared':declared})
                    dialog.resize(1100,850);choose(panel.topic,'terrain');child=map_child();clone=clone_sources(maps,'map-source');bad=clone/maps.DATA;raw=bad.read_bytes()
                    with patch.object(maps,'ROOT',clone):
                        bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'actual_parent_on_fixed_map_member_damage');gui.processEvents();require(not child.isVisible()and panel.map_dialog is None and panel.result is not None,'bad_map_closes_only_owned_map_retains_independent_sun_document');source_failures.append({'source':'current-map-position-DATA','map_closed':True,'document_retained':True});bad.write_bytes(raw)
                    require(main_panel.refresh_reference(),'actual_parent_map_source_recovery');gui.processEvents();child=map_child();clone=clone_sources(model,'sun-source');bad=clone/(model.PACK+'/source-materials.json');raw=bad.read_bytes();original=model.battle.version._file
                    with patch.object(model.battle.version,'_file',side_effect=lambda name:(clone/name)if name==model.MANIFEST or name.startswith(model.PACK+'/')else original(name)):
                        bad.write_bytes(raw+b'x');QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(panel.result is None and panel.selected_key is None and panel.player.toPlainText()==model.UNAVAILABLE and panel.technical.toPlainText()==''and panel.form_combo.count()<=1 and panel.card.count()==0 and not child.isVisible(),'actual_bad_source_clears_form_card_portrait_reading_and_owned_map')
                        source_failures.append({'source':'sun-source-materials','document_cleared':True,'map_closed':True});shot('source-loss')
                        bad.write_bytes(raw);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(panel.result is not None and panel.selected_key is None and panel.form_combo.currentData()is None and panel.map_dialog is None and panel.card.currentData()is None,'source_recovery_requires_manual_form_not_stale_exact_entry')
                        choose_form('0');choose(panel.topic,'terrain');child=map_child();bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'actual_parent_on_real_sun_source_damage');gui.processEvents()
                        require(panel.result is None and panel.technical.toPlainText()==''and not child.isVisible()and(not battle_panel.sun_boss_button.isVisible()or not battle_panel.sun_boss_button.isEnabled()),'actual_parent_never_authorizes_bad_source_and_clears_old_owned_document_tree');bad.write_bytes(raw)
                    require(main_panel.refresh_reference(),'actual_parent_sun_source_recovery');gui.processEvents();dialog.close()
                    row=open_exact('ro6_b_7','0');choose(panel.topic,'terrain');child=map_child();unrelated=next(e['key']for e in battle_panel.result['enemies']if e['key']not in{'0','6','7'});select_parent_enemy(unrelated)
                    require(not dialog.isVisible()and not child.isVisible()and battle_panel.sun_boss_button.isHidden(),'unrelated_current_enemy_has_no_sun_button_and_closes_owned_tree')
                    open_battle('ro6_n_7_1');select_parent_enemy(battle_panel.result['enemies'][0]['key']);require(battle_panel.sun_boss_button.isHidden(),'other_same_region_stage_cannot_borrow_sun_reader')
                    row=open_exact('ro6_b_7_b','0');choose(panel.topic,'terrain');child=map_child();battle_dialog.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_battle_parent_close_closes_sun_map_tree')
                    open_battle('ro6_b_7');row=open_exact('ro6_b_7','0');choose(panel.topic,'terrain');child=map_child();window.reference_panel('scenes');gui.processEvents();require(not battle_dialog.isVisible()and not dialog.isVisible()and not child.isVisible(),'changing_common_page_closes_actual_battle_sun_map_tree')
                    open_battle('ro6_b_7');row=open_exact('ro6_b_7','0');choose(panel.topic,'terrain');child=map_child();require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_legacy_battle_context_unchanged')
                    require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not battle_dialog.isVisible()and not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_full_current_sun_and_map_tree')
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
    result={'section':368,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),
            'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'actual_related_readings':related_readings,'same_identity_refresh_observations':refreshes,'actual_source_failure_observations':source_failures,'screenshots':images,'dialog_close_observations':dialog_close_observations,
            'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1


if __name__=='__main__':raise SystemExit(main())
