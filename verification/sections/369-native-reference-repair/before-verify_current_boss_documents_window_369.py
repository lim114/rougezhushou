"""Actual current enemy entry into four-family documents and fixed-map ownership."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_current_boss_documents_window_369.py'


def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_boss_documents as model,current_battle_reference as battle,current_map_position as maps,current_terrain as terrain,expansion_reference as version
    from rouge import boss_phase_reference as phase,boss_cycle_reference as cycle,boss_hunt_reference as hunt,gold_boss_reference as gold
    from rouge import current_stage_directory as directory,current_reward_reference as rewards,current_settlement_modes_reference as settlement,boss_map_markers as boss_symbols,current_map_markers as symbols
    for provider in(model,battle,maps,terrain,version,directory,rewards,settlement,settlement.prior,boss_symbols,symbols):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    for provider in(phase,cycle,hunt,gold):
        document=json.loads((ROOT/provider.MANIFEST).read_bytes())
        if type(document['runtime_files'])is not dict or type(document['data_file'])is not str:
            raise ValueError('Exact historical runtime manifest schema required: '+provider.MANIFEST)
        names.add(provider.MANIFEST);names.add(document['data_file']);names.update(document['runtime_files'])
        if 'build_authority_files'in document:
            if type(document['build_authority_files'])is not dict:
                raise ValueError('Exact historical build-source map required: '+provider.MANIFEST)
            names.update(document['build_authority_files'])
    for name in('research/p3-expansion-313/map-images.json','research/p3-current-battle-314/enemy-images.json'):
        names.add(name);names.update(value['file']for value in json.loads((ROOT/name).read_bytes())['images'].values())
    names.update((CANONICAL,'scripts/verify_full_available.py','tests/test_current_boss_documents_369.py','tests/test_current_boss_documents_view_369.py'))
    if(ROOT/'verification/sections/369-preparation/scope.json').is_file():names.add('verification/sections/369-preparation/scope.json')
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
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_boss_documents as model,current_battle_reference as battle,current_map_position as maps
        from rouge.current_boss_documents_view import CurrentBossDocumentsDialog
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge369-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第369节 · 当前准确首领机制与版本边界（公开隔离验收）');window.show();gui.processEvents()
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
                previous=battle_dialog;old_mechanism=getattr(battle_panel,'boss_documents_dialog',None)if battle_panel else None;old_map=old_mechanism.panel.map_dialog if old_mechanism else None
                select_stage(stage_id);require(main_panel.battle_button.isVisible()and main_panel.battle_button.isEnabled(),'ordinary_current_stage_battle_button_visible')
                QTest.mouseClick(main_panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();battle_dialog=main_panel.current_battle_dialog;battle_panel=battle_dialog.panel
                require(battle_dialog.isVisible()and battle_panel.stage_id==stage_id and battle_panel.result['id']==stage_id,'actual_MainWindow_current_battle_exact_stage')
                bar=battle_panel.tabs.tabBar();QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(1).center());gui.processEvents()
                if previous is not None:
                    require(not previous.isVisible(),'changing_stage_closes_previous_actual_battle')
                    if old_mechanism is not None:require(not old_mechanism.isVisible()and(old_map is None or not old_map.isVisible()),'changing_stage_closes_owned_document_and_map_tree')
            def select_parent_enemy(key):
                require(battle_panel.enemy_choices.select_value(key),'actual_current_enemy_selector_exact_key');gui.processEvents()
                require(battle_panel.enemy_key==key and battle_panel.enemy_combo.currentData()==key,'actual_current_enemy_scope_matches_selected_reference')
            def open_exact(stage_id,key):
                nonlocal dialog,panel
                if battle_panel is None or battle_panel.stage_id!=stage_id:open_battle(stage_id)
                old=dialog;old_map=old.panel.map_dialog if old else None;select_parent_enemy(key)
                require(battle_panel.boss_documents_button.isVisible()and battle_panel.boss_documents_button.isEnabled()and model.target_available(stage_id,key),'only_exact_supported_current_enemy_has_complete_document_entry')
                QTest.mouseClick(battle_panel.boss_documents_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=battle_panel.boss_documents_dialog;panel=dialog.panel
                require(isinstance(dialog,CurrentBossDocumentsDialog)and dialog.isVisible()and panel.stage_id==stage_id and panel.selected_key==key and panel.entry_key==key,'ordinary_current_enemy_button_opens_exact_current_document_reference')
                require(panel.result['battle_source_identity']==battle_panel.result['source_identity']and panel.result['level_key']==battle_panel.result['level_key'],'current_parent_and_document_exact_source_agree')
                if old is not None:require(not old.isVisible()and(old_map is None or not old_map.isVisible()),'replacing_enemy_document_closes_previous_document_map_tree')
                return model.entity(panel.result,key)
            def reading(widget):
                cursor=widget.textCursor();return{'anchor':cursor.anchor(),'position':cursor.position(),'selection':cursor.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def assert_unknown():
                value=panel.result
                require(all(value[name]is None for name in('actual_phase','actual_skill_time','expected_stats'))and not value['numeric_model_added']and not value['actual_server_verified']and not value['run_updated'],'document_reading_never_actual_phase_skill_time_stats_or_server_execution')
            def select_document(key):
                require(panel.enemies.select_value(key),'actual_document_enemy_branch_exact_selection');gui.processEvents();require(panel.selected_key==key,'document_branch_selects_exact_current_reference')
            def map_child():
                require(panel.map_button.isVisible()and panel.map_button.isEnabled(),'actual_selected_document_has_fixed_map_entry')
                QTest.mouseClick(panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();child=panel.map_dialog;require(child is not None and child.isVisible(),'actual_owned_fixed_map_child_opened')
                mapped=child.panel.result;reference=panel.result
                require(mapped['stage_id']==reference['stage_id']and mapped['current_level_key']==reference['level_key']and mapped['complete_current_geometry']['mapData']==reference['complete_current_level']['mapData'],'fixed_map_exact_stage_level_complete_mapData_not_old_legacy_map_or_actual_position')
                require(child.panel.selected is None and child.panel.grid.selected is None and not mapped['actual_combat_positions_verified']and not mapped['full_map_projection_verified']and not mapped['run_updated'],'fixed_map_no_automatic_boss_position_or_full_projection')
                require(not child.panel.original.pixmap.isNull(),'exact_current_fixed_original_map_image_visible');return child
            def clone_sources(provider,label):
                clone=temporary/label;manifest=json.loads((ROOT/provider.MANIFEST).read_bytes())
                for name in(provider.MANIFEST,*manifest['files']):
                    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                return clone
            def verify_cleared(child):
                require(panel.result is None and panel.selected_key is None and panel.player.toPlainText()==model.UNAVAILABLE and panel.technical.toPlainText()==''and panel.enemy_combo.count()<=1 and panel.topic.count()==0 and not panel.map_button.isEnabled()and not panel.related_button.isEnabled()and not child.isVisible(),'real_bad_source_clears_enemy_topic_portrait_text_related_entry_and_owned_map')
            def owned_close_state(document_panel,captured_map):
                picture=document_panel.portrait.pixmap();mapped=captured_map.panel
                document_state={
                    'result_cleared':document_panel.result is None,
                    'selected_cleared':document_panel.selected_key is None,
                    'entry_cleared':document_panel.entry_key is None,
                    'view_key_cleared':document_panel._view_key is None,
                    'enemy_selection_cleared':document_panel.enemy_combo.currentData()is None,
                    'enemy_branch_items_cleared':document_panel.enemies.groups==[],
                    'player_is_unavailable_notice':document_panel.player.toPlainText()==model.UNAVAILABLE,
                    'technical_empty':document_panel.technical.toPlainText()=='',
                    'portrait_hidden':document_panel.portrait.isHidden(),
                    'portrait_pixels_empty':picture is None or picture.isNull(),
                    'topic_empty':document_panel.topic.count()==0,
                    'related_empty':document_panel.related.count()==0,
                    'related_disabled':not document_panel.related_button.isEnabled(),
                    'map_disabled':not document_panel.map_button.isEnabled(),
                    'map_pointer_cleared':document_panel.map_dialog is None}
                map_state={
                    'hidden':not captured_map.isVisible(),
                    'result_cleared':mapped.result is None,
                    'selected_cleared':mapped.selected is None,
                    'image_raw_cleared':mapped.image_raw is None,
                    'grid_result_cleared':mapped.grid.result is None,
                    'grid_selection_cleared':mapped.grid.selected is None,
                    'original_pixels_empty':mapped.original.pixmap.isNull(),
                    'original_point_cleared':mapped.original.point is None,
                    'player_is_unavailable_notice':mapped.player.toPlainText()==maps.UNAVAILABLE,
                    'technical_empty':mapped.technical.toPlainText()==''}
                return document_state,map_state
            def exercise():
                nonlocal done,failure,dialog,panel
                try:
                    index=tabs.indexOf(main_panel);QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(index).center());gui.processEvents()
                    require(tabs.currentWidget()is main_panel and main_panel.scope.isHidden()and main_panel.scope.currentData()is False,'actual_common_stage_directory_without_version_only_page')
                    base=model.packet();require(base is not None and len(model.TARGETS)==9,'actual_pinned_nine_current_document_targets')
                    total_topics=0;family_shots=set()
                    for sid,key,eid,level,family in model.TARGETS:
                        row=open_exact(sid,key);require(row['enemy_id']==eid and row['level']==level and row['enemy']['id']==eid and row['enemy']['raw_binding']==row['raw_binding'],'all_nine_current_exact_references_keep_ID_level_and_raw_binding')
                        old=row['legacy_document'];require((old['stage_id'],old['enemy_id'],old['level'])==(sid,eid,level)and old['source_valid']is True,'authentic_legacy_document_identity_not_rewritten_to_current_tuple')
                        require(panel.enemies.branch.findData(model.LABELS[family])>=0,'mechanism_family_is_actual_separate_branch_option')
                        tech=json.loads(panel.technical.toPlainText());require(tech['selected_current_reference_and_authentic_legacy_document']==json.loads(json.dumps(row,ensure_ascii=False)),'complete_guarded_document_and_original_current_binding_retained_in_source_tab')
                        topics=model.topics(panel.result,key);require(len(topics)==(6 if family=='phase'else 4)and panel.topic.count()==len(topics)+1,'all_and_only_qualified_family_topics_available')
                        for topic in topics:
                            choose(panel.topic,topic['id']);require(topic['name']in panel.player.toPlainText()and '未知'in panel.player.toPlainText(),'every_complete_original_topic_readable_with_actual_result_unknown');total_topics+=1
                        assert_unknown();observations.append({'stage_id':sid,'key':key,'enemy_id':eid,'level':level,'family':family,'topics':[r['id']for r in topics],'legacy_identity':[old['stage_id'],old['enemy_id'],old['level']],'legacy_source_identity':deepcopy(old['source_identity']),'actual_phase':panel.result['actual_phase'],'expected_stats':panel.result['expected_stats']})
                        choose(panel.topic,None)
                        if family not in family_shots:shot(family+'-complete-document');family_shots.add(family)
                        if sid=='ro6_b_2_b':
                            require(panel.result['qualification']['changed_top_fields']==['runes']and panel.result['qualification']['differences'][0]['current']is None and len(panel.result['qualification']['differences'][0]['previous'])==2,'gold_current_null_and_two_old_runes_exactly_separated')
                            text=panel.player.toPlainText();require('版本差异'in text and '不沿用旧关卡'in text and '1.3'not in text and '1.4'not in text,'plain_player_gold_warning_precedes_document_and_no_old_rune_numeric_effects');shot('gold-current-rune-difference')
                    require(len(observations)==9 and total_topics==38 and family_shots=={'phase','cycle','hunt','gold'},'all_nine_references_38_topics_four_families_actually_read')
                    row=open_exact('ro6_b_5','0');child=map_child();shot('exact-current-fixed-map',child.panel)
                    for related_key in('1','2'):
                        row=open_exact('ro6_b_5','0');child=map_child();old_dialog=dialog;request=next(r for r in model.related_entities(panel.result,'0')if r['key']==related_key)
                        choose(panel.related,request);QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(battle_panel.enemy_key==related_key and battle_panel.enemy_combo.currentData()==related_key and battle_panel.stage_id=='ro6_b_5'and not old_dialog.isVisible()and not child.isVisible(),'related_entity_signal_selects_exact_same_stage_real_enemy_and_closes_owned_tree')
                        supported=model.target_available('ro6_b_5',related_key);require(battle_panel.boss_documents_button.isVisible()==supported,'related_module_without_document_has_no_fake_complete_mechanism_button');related_readings.append({'source_stage':'ro6_b_5','request':request,'actual_selected_key':battle_panel.enemy_key,'complete_document_available':supported})
                    row=open_exact('ro6_b_4','0')
                    requests=[r for r in model.related_entities(panel.result,'0')if r['entity_id']in('enemy_2146_cadesd_2','enemy_2146_cadesd_3')]
                    require(len(requests)==2,'both_independent_hunt_related_entities_kept_without_DB_alias')
                    for request in requests:
                        row=open_exact('ro6_b_4','0');choose(panel.related,request);old_dialog=dialog;QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(battle_panel.enemy_key==request['key']and not old_dialog.isVisible()and battle_panel.boss_documents_button.isHidden(),'independent_hunt_entity_opens_only_exact_current_enemy_without_alias_document');related_readings.append({'source_stage':'ro6_b_4','request':request,'actual_selected_key':battle_panel.enemy_key,'complete_document_available':False})
                    row=open_exact('ro6_b_6','0');require(panel.enemies.select_branch(model.LABELS['phase']),'actual_family_branch_selection');choose(panel.topic,model.topics(panel.result,'0')[0]['id']);dialog.resize(850,480);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'both_readers_have_real_nonzero_range');scroll.setValue(min(3,scroll.maximum()));old=reading(reader)
                        declared=(panel.enemy_combo.currentData(),panel.enemies.branch.currentData(),panel.topic.currentData(),panel.tabs.currentIndex());same=panel
                        require(old['scroll']>0 and old['position']>old['anchor'],'both_real_readers_nonzero_scroll_and_selection');require(main_panel.refresh_reference(),'actual_common_stage_parent_refresh');gui.processEvents()
                        require(battle_panel.boss_documents_dialog.panel is same and declared==(panel.enemy_combo.currentData(),panel.enemies.branch.currentData(),panel.topic.currentData(),panel.tabs.currentIndex())and reading(reader)==old,'actual_parent_preserves_same_document_instance_enemy_branch_topic_tab_and_both_readings');refreshes.append({'before':old,'after':reading(reader),'declared':declared})
                    dialog.resize(1100,850);child=map_child();clone=clone_sources(maps,'map-source');bad=clone/maps.DATA;raw=bad.read_bytes()
                    with patch.object(maps,'ROOT',clone):
                        bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'actual_parent_on_fixed_map_source_damage');gui.processEvents();require(not child.isVisible()and panel.map_dialog is None and panel.result is not None,'map_source_damage_closes_only_map_keeps_independent_full_document');source_failures.append({'source':'current-map-position-DATA','map_closed':True,'document_retained':True});bad.write_bytes(raw)
                    require(main_panel.refresh_reference(),'actual_parent_map_source_recovery');gui.processEvents();child=map_child();clone=clone_sources(model,'document-source');bad=clone/(model.PACK+'/qualified-current-records.json');raw=bad.read_bytes();original=model.battle.version._file
                    with patch.object(model.battle.version,'_file',side_effect=lambda name:(clone/name)if name==model.MANIFEST or name.startswith(model.PACK+'/')else original(name)):
                        bad.write_bytes(raw+b'x');QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();verify_cleared(child);shot('source-loss');source_failures.append({'source':'qualified-current-records','cleared':True,'owned_map_closed':True})
                        bad.write_bytes(raw);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.selected_key is None and panel.enemy_combo.currentData()is None and panel.map_dialog is None,'source_recovery_manual_enemy_not_stale_exact_entry')
                        select_document('0');child=map_child();bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'actual_parent_on_qualified_current_source_damage');gui.processEvents();verify_cleared(child);require(not battle_panel.boss_documents_button.isVisible()or not battle_panel.boss_documents_button.isEnabled(),'bad_current_source_never_authorizes_mechanism_entry');bad.write_bytes(raw)
                    require(main_panel.refresh_reference(),'actual_parent_current_document_recovery');gui.processEvents();dialog.close()
                    from rouge import boss_phase_reference as phase,boss_cycle_reference as cycle,boss_hunt_reference as hunt,gold_boss_reference as gold
                    for provider,sid,key,family in((phase,'ro6_b_6','0','phase'),(cycle,'ro6_b_5','0','cycle'),(hunt,'ro6_b_4','0','hunt'),(gold,'ro6_b_2','1','gold')):
                        row=open_exact(sid,key);child=map_child();clone=clone_sources(provider,'legacy-'+family);bad=clone/provider.DATA;raw=bad.read_bytes()
                        with patch.object(provider,'ROOT',clone):
                            bad.write_bytes(raw+b'x');QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();verify_cleared(child);source_failures.append({'source':'authentic-legacy-'+family+'-DATA','cleared':True,'owned_map_closed':True})
                            bad.write_bytes(raw);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is not None and panel.selected_key is None and panel.enemy_combo.currentData()is None,'all_four_authentic_legacy_source_recoveries_require_manual_enemy')
                            select_document(key);child=map_child();bad.write_bytes(raw+b'x');require(main_panel.refresh_reference(),'actual_parent_on_authentic_legacy_source_damage');gui.processEvents();verify_cleared(child);require(not battle_panel.boss_documents_button.isVisible()or not battle_panel.boss_documents_button.isEnabled(),'all_four_invalid_legacy_chains_remove_current_entry_not_keep_prior_result');bad.write_bytes(raw)
                        require(main_panel.refresh_reference(),'actual_parent_authentic_legacy_source_recovery');gui.processEvents();dialog.close()
                    for close_mode in('native_system_close_command','qtest_escape'):
                        row=open_exact('ro6_b_6','0');captured_map=map_child();old_dialog=dialog;old_document=panel;owned=native(old_dialog)
                        if close_mode=='native_system_close_command':
                            # The owned HWND receives the caption-X equivalent system
                            # close command; this is explicitly not a physical mouse click.
                            import win32con
                            win32gui.SendMessage(owned['hwnd'],win32con.WM_SYSCOMMAND,win32con.SC_CLOSE,0)
                        else:
                            QTest.keyClick(old_dialog,Qt.Key.Key_Escape)
                        gui.processEvents();QTest.qWait(10);gui.processEvents()
                        document_state,map_state=owned_close_state(old_document,captured_map)
                        require(not old_dialog.isVisible()and all(document_state.values()),close_mode+'_mechanism_result_identity_text_picture_controls_and_map_pointer_cleared')
                        require(all(map_state.values()),close_mode+'_captured_map_child_result_pixels_selection_cleared_and_hidden')
                        require(window.isVisible()and battle_dialog.isVisible()and battle_panel.result is not None and battle_panel.stage_id=='ro6_b_6'and battle_panel.enemy_key=='0'and battle_panel.boss_documents_button.isVisible(),close_mode+'_actual_parent_battle_and_MainWindow_remain_alive')
                        row=open_exact('ro6_b_6','0')
                        require(dialog is not old_dialog and panel is not old_document and dialog.isVisible()and panel.result is not None and panel.selected_key=='0'and panel.entry_key=='0'and row['enemy_id']=='enemy_2150_shchmr',close_mode+'_ordinary_entry_reopens_fresh_exact_document')
                        fresh_map=map_child();require(fresh_map is not captured_map and fresh_map.isVisible()and fresh_map.panel.result is not None and fresh_map.panel.stage_id=='ro6_b_6',close_mode+'_fresh_exact_owned_map_reopens')
                        after_document,after_map=owned_close_state(old_document,captured_map)
                        require(not old_dialog.isVisible()and all(after_document.values())and all(after_map.values()),close_mode+'_old_document_and_captured_map_remain_cleared_after_reopen')
                        dialog_close_observations.append({'mode':close_mode,'owned_mechanism_hwnd':owned['hwnd'],'owned_process_id':owned['pid'],'stage_id':'ro6_b_6','enemy_key':'0','physical_titlebar_mouse_click_claimed':False,'physical_keyboard_claimed':False,'actual_event_method':'WM_SYSCOMMAND/SC_CLOSE sent to verified owned HWND'if close_mode=='native_system_close_command'else'QTest Escape sent to actual mechanism QDialog with map open','document_state_after_close':document_state,'captured_map_state_after_close':map_state,'fresh_exact_document_reopened':True,'fresh_exact_map_reopened':True,'old_document_state_after_reopen':after_document,'old_captured_map_state_after_reopen':after_map})
                    for sid in('ro6_b_4_b','ro6_b_5_b','ro6_b_2_dlc1','ro6_b_2_b_dlc1'):
                        open_battle(sid);select_parent_enemy(battle_panel.result['enemies'][0]['key']);require(battle_panel.boss_documents_button.isHidden(),'unsupported_pursuit_or_DLC1_same_name_stage_has_no_migrated_entry')
                    row=open_exact('ro6_b_5','0');child=map_child();unrelated=next(e['key']for e in battle_panel.result['enemies']if(e['key']not in{'0','1'}));select_parent_enemy(unrelated)
                    require(not dialog.isVisible()and not child.isVisible()and battle_panel.boss_documents_button.isHidden(),'unrelated_current_enemy_hides_entry_and_closes_full_owned_tree')
                    row=open_exact('ro6_b_6','0');child=map_child();battle_dialog.close();gui.processEvents();require(not dialog.isVisible()and not child.isVisible(),'actual_current_battle_parent_close_closes_document_map_tree')
                    open_battle('ro6_b_6');row=open_exact('ro6_b_6','0');child=map_child();window.reference_panel('scenes');gui.processEvents();require(not battle_dialog.isVisible()and not dialog.isVisible()and not child.isVisible(),'changing_common_page_closes_actual_battle_document_map_tree')
                    open_battle('ro6_b_6');row=open_exact('ro6_b_6','0');child=map_child();require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_battle_context_unchanged')
                    require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');native();window.close();gui.processEvents();require(not battle_dialog.isVisible()and not dialog.isVisible()and not child.isVisible(),'actual_MainWindow_closes_entire_current_document_map_tree')
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
    result={'section':369,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),
            'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'actual_related_readings':related_readings,'same_identity_refresh_observations':refreshes,'actual_source_failure_observations':source_failures,'owned_dialog_close_observations':dialog_close_observations,'screenshots':images,
            'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1


if __name__=='__main__':raise SystemExit(main())
