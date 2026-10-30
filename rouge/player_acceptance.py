"""Small, focused acceptance extensions for the player interface batch."""
def check(section,window,gui,require):
    if section==438:
        from .player_feature_438_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==437:
        from .player_feature_437_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==436:
        from .player_feature_436_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==435:
        from .player_feature_435_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==434:
        from .player_feature_434_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==433:
        from .player_feature_433_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==432:
        from .player_feature_432_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==431:
        from .player_feature_431_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==430:
        from .player_feature_430_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==429:
        from .player_feature_429_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==428:
        from .player_feature_428_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==427:
        from .player_feature_427_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==426:
        from .player_feature_426_acceptance import check as check_feature
        return check_feature(window,gui,require)
    if section==425:
        from .player_feature_425_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==424:
        from .player_feature_424_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==423:
        from .player_feature_423_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==422:
        from .player_feature_422_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==421:
        from .player_feature_421_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==420:
        from .player_feature_420_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==419:
        from .player_feature_419_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==418:
        from .player_feature_418_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==417:
        from .player_feature_417_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==416:
        from .player_feature_416_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==415:
        from .player_feature_415_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==414:
        from .player_feature_414_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==413:
        from .player_compendium_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==412:
        from .player_toolbar_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==411:
        from .player_recent_notes_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==410:
        from .player_reference_notes_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==409:
        from .player_exchange_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==408:
        from .player_statistics_card_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==407:
        from .player_cohort_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==406:
        from .player_statistics_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==405:
        from .player_evidence_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==404:
        from .player_resource_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==403:
        from .player_replay_nodes_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==402:
        from .player_history_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==401:
        from .player_replay_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==400:
        from .player_note_export_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==399:
        from .player_note_library_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==398:
        from .player_note_preview_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==397:
        from .player_parts_acceptance import check as check_feature
        check_feature(window,gui,require)
    if section==396:
        from .player_team_acceptance import check as check_team
        check_team(window,gui,require)
    if section==395:
        from .player_scene_acceptance import check as check_scene
        check_scene(window,gui,require)
    if section==394:
        from .player_item_acceptance import check as check_item_sources
        check_item_sources(window,gui,require)
    if section==393:
        from .player_hotkey_acceptance import check as check_hotkey
        check_hotkey(window,gui,require)
    if section==392:
        from .player_map_acceptance import check as check_map_interaction
        check_map_interaction(window,gui,require)
    if section==391:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        window.show_compact();gui.processEvents();bar=window.compact_window
        require(bar.height()<=100 and bool(bar.windowFlags()&Qt.WindowType.FramelessWindowHint),'video_form_frameless_horizontal_toolbar')
        require(len([b for b in bar.buttons if b!='节点统计'])==7,'seven_icon_tools_not_dashboard_cards')
        bar.buttons['地图与节点'].click();gui.processEvents();require(bar.map_popup.isVisible()and not window.isVisible(),'map_opens_local_popover_without_main_window')
        bar.buttons['本局藏品'].click();gui.processEvents();require(bar.inventory_popup.isVisible()and not bar.map_popup.isVisible(),'only_selected_tool_panel_expanded')
        inventory=bar.inventory_popup.panel;inventory.held.setChecked(False);inventory.search.setText('攻击');query=inventory.search.text()
        bar.refresh();require(inventory.search.text()==query,'toolbar_refresh_keeps_inventory_query')
        bar.open_archive();gui.processEvents();panel=window.public_archive
        require(panel.isVisible()and not bar.inventory_popup.isVisible(),'public_reference_opens_from_toolbar')
        require(panel.version.currentData()=='dlc1','source_default_version_is_explicit')
        panel.pool_search.setText('报废轮子');gui.processEvents()
        target=next(i for i in range(panel.pools.count())if panel.pools.item(i).data(256)=='rogue_6:node_battle_boss_scrap')
        panel.pools.setCurrentRow(target);gui.processEvents()
        require(panel.members.rowCount()>0 and any(panel.members.item(i,1).text()!='未知'for i in range(panel.members.rowCount())),'real_source_drop_counts_render')
        require('不表示最终领取概率'in panel.pool_note.toPlainText(),'candidate_frequency_distinguished_from_claimed_reward')
        selection=panel.pools.currentItem().data(256);panel.install();require(panel.pools.currentItem().data(256)==selection,'public_refresh_preserves_exact_pool_selection')
        panel.tabs.setCurrentIndex(1);panel.floor.setCurrentIndex(0);panel.treehole.setChecked(True);gui.processEvents();require(panel.events.count()==0,'treehole_not_available_from_first_floor')
        panel.floor.setCurrentIndex(2);require(panel.events.count()>0,'treehole_third_floor_has_source_events')
        panel.events.setCurrentRow(0);require('未确认'in panel.event_note.toPlainText(),'event_source_candidate_not_actual_eligibility')
        panel.treehole.setChecked(False);panel.floor.setCurrentIndex(0);panel.events.setCurrentRow(0);identity=panel.events.currentItem().data(256).split(':',1)[-1]
        panel.event_button.click();gui.processEvents();reference=window.reference_panel('scenes',activate=False)
        require(reference.result is not None and reference.result['row']['id']==identity,'exact_event_reference_link')
        notes=window.player_notes;notes.set_context({'title':'临时测试关卡','kind':'battle'});bar.open_owner_dialog(notes.show,'player_notes');notes.editor.setPlainText('尚未保存的测试笔记')
        require(not bar.open_inventory()and notes.isVisible(),'dirty_note_not_hidden_by_toolbar_switch');notes.discard()
        window.show_compact();bar.open_archive();panel.tabs.setCurrentIndex(0);QTest.qWait(120);gui.processEvents()
        require(not window.isVisible(),'reference_lookup_keeps_large_window_hidden')
        from copy import deepcopy
        from pathlib import Path
        import json
        templates=json.loads((Path(__file__).with_name('data')/'map-templates.json').read_text('utf8'))
        graphs=[]
        for zone in ('zone_1','zone_2'):
            t=next(t for t in templates['templates']if t['zone_id']==zone)
            nodes=[{**n,'template_type':n.get('fixed_type'),'visible':False,'center':[.5,.5]}for n in t['nodes']]
            graphs.append({'zone_id':zone,'template_id':t['id'],'nodes':nodes,'grid':{'rows':t['rows'],'cols':t['cols']},'edges':t['edges'],'source':templates['source']})
        old_state=deepcopy(window.run.state);window.run.state['maps']={g['zone_id']:g for g in graphs}
        bar.open_map();mp=bar.map_popup.panel;gui.processEvents()
        require(mp.floors.count()==2,'recorded_floors_have_separate_tabs')
        require(not mp.view.atlas.isNull()and not mp.view.background.isNull(),'real_game_art_loaded_without_network')
        mp.details_toggle.click();mp.view.select_node(graphs[0]['nodes'][0]['id']);gui.processEvents();selected=mp.view.selected
        require(mp.drawer.isVisible()and mp.entries.topLevelItemCount()>0,'node_click_has_grouped_events_or_battles')
        require(all(mp.entries.topLevelItem(i).text(0).startswith('作战预览')for i in range(mp.entries.topLevelItemCount())),'template_battle_not_all_event_types')
        root=mp.entries.topLevelItem(0);mp.entries.setCurrentItem(root.child(0));identity=mp.selected_reference
        mp.refresh();gui.processEvents();require(mp.view.selected==selected and mp.selected_reference==identity,'map_refresh_preserves_node_and_reading')
        mp.floors.setCurrentIndex(1);gui.processEvents();require(mp.view.graph['zone_id']=='zone_2','floor_switch_changes_whole_map')
        mp.floors.setCurrentIndex(0);gui.processEvents();require(mp.view.selected==selected and mp.selected_reference==identity,'return_to_floor_restores_reading')
        mp.zoom.setCurrentIndex(3);gui.processEvents();require(not mp.scroll.widgetResizable(),'zoom_uses_scrollable_full_map')
        mp.zoom.setCurrentIndex(0);require(mp.scroll.widgetResizable(),'fit_restores_whole_floor')
        before=dict(mp.view.graph);mp.graphs['zone_1']={**before,'template_id':'different-layout'};mp.show_floor();require(mp.view.selected is None,'changed_layout_does_not_reuse_same_coordinate')
        mp.graphs['zone_1']=graphs[0];mp.show_floor();mp.view.select_node(selected);mp.details_toggle.setChecked(False)
        mp.status.setText('隔离验收示例：公开一层模板；不是本局游戏读取。点击节点展开事件、奖励与作战资料。')
        from PySide6.QtCore import QPoint
        QTest.mouseClick(mp.view,Qt.MouseButton.LeftButton,pos=mp.view._positions()[1][selected].toPoint());gui.processEvents()
        require(mp.drawer.isVisible(),'actual_node_click_expands_dossier')
        battle=next((mp.entries.topLevelItem(i).child(j)for i in range(mp.entries.topLevelItemCount())for j in range(mp.entries.topLevelItem(i).childCount())if mp.entries.topLevelItem(i).child(j).data(0,Qt.ItemDataRole.UserRole)[1]=='battle'),None)
        require(battle is not None,'fixed_battle_node_has_stage_previews');mp.entries.setCurrentItem(battle);stage=mp.rows[mp.selected_reference]['id'];mp.open_button.click();gui.processEvents()
        require(window.battle_preview.current_stage==stage,'map_battle_link_opens_exact_stage')
        window.show_compact();mp.details_toggle.setChecked(False)
        mp.status.setText('隔离验收示例：公开模板；不是本局游戏读取。点击节点展开事件、奖励与作战资料。')

        window.run.state=old_state;window.public_archive.show();QTest.qWait(150);gui.processEvents()

    if section==390:
        ws=window.centralWidget();panel=window.inventory_panel;ws.setCurrentWidget(panel);panel.search.setText('攻击');query=panel.search.text()
        ws.setCurrentWidget(window.exploration_map_tab);window.back_button.click();gui.processEvents()
        require(ws.currentWidget()is panel and panel.search.text()==query,'back_preserves_inventory_query')
        window.sync_run_config();gui.processEvents();require(ws.currentWidget()is panel and panel.search.text()==query,'run_refresh_keeps_current_reading')
        for owner in (385,386,387,388):check(owner,window,gui,require)
        window.player_notes.close();window.public_statistics.close()
        require(window.charge_timeline_button.isHidden()and window.shield_timeline_button.isHidden(),'mechanist_tools_absent_without_mechanist')
        require(not window.damage_tools_fold.content.isVisible(),'additional_calculation_tools_collapsed')
        check(389,window,gui,require);window.compact_window.pin.setChecked(True);gui.processEvents()
        import win32gui,win32con
        handle=int(window.compact_window.winId())
        require(win32gui.IsWindowVisible(handle)and bool(win32gui.GetWindowLong(handle,win32con.GWL_EXSTYLE)&win32con.WS_EX_TOPMOST),'actual_native_companion_topmost')
        require(ws.map_node_workspace.splitter.orientation()==__import__('PySide6.QtCore',fromlist=['Qt']).Qt.Orientation.Vertical,'map_node_column_readable_at_standard_window_width')
    if section==389:
        window.show_compact();gui.processEvents();panel=window.compact_window
        require(panel.isVisible()and not window.isVisible(),'compact_mode_has_visible_companion')
        require(panel.width()<=480 and panel.height()<=600,'compact_logical_size')
        from PySide6.QtCore import Qt
        require(bool(panel.windowFlags()&Qt.WindowType.WindowStaysOnTopHint),'companion_topmost_enabled')
        panel.pin.click();gui.processEvents();require(not bool(panel.windowFlags()&Qt.WindowType.WindowStaysOnTopHint),'topmost_can_be_disabled')
        panel.buttons['本局藏品'].click();gui.processEvents();require(window.centralWidget().currentWidget()is window.inventory_panel or bool(getattr(panel,'inventory_popup',None)and panel.inventory_popup.isVisible()),'compact_inventory_shortcut')
        window.show_compact();gui.processEvents();require(panel.isVisible(),'return_to_same_companion_instance')
    if section==388:
        window.open_public_statistics();gui.processEvents();panel=window.public_statistics
        require(panel.isVisible(),'actual_public_statistics_reader_visible')
        require(panel.table.rowCount()>0,'offline_public_aggregate_available')
        require('历史'in panel.status.text()and'未核验'in panel.status.text(),'old_distribution_not_current_DLC_prediction')
        panel.distance.setValue(100);require(panel.table.rowCount()==0 and'未知'in panel.status.text(),'no_sample_not_zero_probability')
        panel.distance.setValue(3);gui.processEvents();require(panel.table.rowCount()>0,'local_query_computes_without_network')
    if section==387:
        notes=window.player_notes;require(notes.set_context({'kind':'battle','title':'测试关卡','variant_id':'fixture-a'}),'notes_bind_explicit_context')
        notes.show();notes.editor.setPlainText('# 测试笔记\n注意第二阶段的机制。');gui.processEvents()
        require(not notes.set_context({'kind':'event','title':'另一事件'}),'dirty_note_not_rebound')
        notes.save_button.click();require(not notes.dirty,'note_explicitly_saved')
        require(notes.set_context({'kind':'event','title':'另一事件'}),'saved_note_can_change_context')
        require(notes.editor.toPlainText()=='','new_context_does_not_borrow_note')
        notes.set_context({'kind':'battle','title':'测试关卡','variant_id':'fixture-a'});gui.processEvents()
        require('第二阶段'in notes.editor.toPlainText(),'local_note_restored_by_exact_context')
    if section==386:
        panel=window.inventory_panel;window.centralWidget().setCurrentWidget(panel);gui.processEvents()
        require(panel.entries.count()==0,'empty_run_not_filled_from_reference')
        panel.held.setChecked(False);gui.processEvents();require(panel.entries.count()>0,'reference_inventory_available')
        panel.search.setText('希望');gui.processEvents();require(panel.entries.count()>0,'effect_search_returns_results')
        panel.entries.setCurrentRow(0);gui.processEvents();identity=panel.entries.currentItem().data(256)
        panel.reference_button.click();gui.processEvents()
        require(window.reference_panel('relics',activate=False).result['row']['id']==identity,'inventory_exact_reference_navigation')
        window.centralWidget().setCurrentWidget(panel);require(panel.search.text()=='希望','inventory_query_kept_after_navigation')
    if section==385:
        ws=window.centralWidget();ws.groups['本局'].setCurrentIndex(0);ws.setCurrentIndex(0);gui.processEvents()
        require(window.context_bar.isVisible(),'context_shortcuts_visible_across_pages')
        require(not window.context_bar.open_button.isEnabled(),'no_fabricated_recent_content_link')
        require(not window.capture_details.content.isVisible(),'technical_capture_details_collapsed')
        from PySide6.QtTest import QTest
        QTest.qWait(120);gui.processEvents()
        require(window.capture_details.toggle.visibleRegion().boundingRect().height()>0,'capture_settings_toggle_in_viewport')
        window.capture_details.toggle.click();gui.processEvents()
        require(window.windows.isVisible(),'connection_settings_expand')
        window.capture_details.toggle.click();gui.processEvents()
        require(window.run_cards.isVisible(),'run_facts_remain_visible')
    if section==384:
        panel=window.reference_panel('stages');gui.processEvents();menu=panel.query_menu
        actions=menu.visible_actions();require(any('敌人' in a.text()for a in actions),'enemy_lookup_available_in_query_menu')
        require(any('地形' in a.text()for a in actions),'terrain_lookup_available_in_query_menu')
        require(not panel.enemy_directory_button.isVisible(),'scattered_query_buttons_removed_from_default_layout')
        menu.menu.popup(menu.button.mapToGlobal(menu.button.rect().bottomLeft()));gui.processEvents()
        require(menu.menu.isVisible(),'actual_query_menu_opens');menu.menu.hide();gui.processEvents()
        require(panel.search.isVisible()and panel.entries.isVisible(),'main_search_and_results_remain_visible')
    if section==383:
        ws=window.centralWidget();ws.setCurrentWidget(window.node_catalog);gui.processEvents()
        require(window.exploration_map_tab.isVisible()and window.node_catalog.isVisible(),'map_and_node_readers_visible_together')
        require(ws.currentWidget()is window.node_catalog,'exact_node_alias_routes_to_shared_workspace')
        require(ws.groups['地图与节点'].count()==3,'duplicate_node_top_subpage_removed')
        ws.setCurrentWidget(window.exploration_map_tab);gui.processEvents()
        require(ws.currentWidget()is window.exploration_map_tab,'existing_map_link_routes_preserved')
    if section==382:
        ws=window.centralWidget();ws.groups['本局'].setCurrentIndex(0);ws.setCurrentIndex(0);gui.processEvents()
        require(window.run_cards.cards['保密等级'].text()=='尚未确认','unknown_grade_card_not_zero')
        window.run_cards.map_button.click();gui.processEvents()
        require(ws.currentWidget()is window.exploration_map_tab,'home_map_shortcut')
        window.run_cards.items_button.click();gui.processEvents()
        require(ws.currentWidget()is window.inventory_panel,'home_items_shortcut')
        ws.groups['本局'].setCurrentIndex(0);ws.setCurrentIndex(0);gui.processEvents()
        require(window.run_cards.isVisible(),'overview_cards_visible_on_home')
    if section==381:
        from .player_workspace import DEVELOPER_PAGES
        ws=window.centralWidget()
        require(all(ws.pages[p][0]=='developer'for p in ws.pages if ws.pages[p][1]in DEVELOPER_PAGES),'all_existing_developer_readers_outside_player_groups')
        ws.setCurrentWidget(window.exploration_map_tab);gui.processEvents()
        require(ws.currentWidget()is window.exploration_map_tab,'map_is_direct_player_page')
