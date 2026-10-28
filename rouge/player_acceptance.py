"""Small, focused acceptance extensions for the player interface batch."""
def check(section,window,gui,require):
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
        panel.buttons['本局藏品'].click();gui.processEvents();require(window.centralWidget().currentWidget()is window.inventory_panel,'compact_inventory_shortcut')
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
        require(ws.currentWidget()is window.reference_panel('relics',activate=False),'home_items_shortcut')
        ws.setCurrentIndex(0);gui.processEvents()
        require(window.run_cards.isVisible(),'overview_cards_visible_on_home')
    if section==381:
        from .player_workspace import DEVELOPER_PAGES
        ws=window.centralWidget()
        require(all(ws.pages[p][0]=='developer'for p in ws.pages if ws.pages[p][1]in DEVELOPER_PAGES),'all_existing_developer_readers_outside_player_groups')
        ws.setCurrentWidget(window.exploration_map_tab);gui.processEvents()
        require(ws.currentWidget()is window.exploration_map_tab,'map_is_direct_player_page')
