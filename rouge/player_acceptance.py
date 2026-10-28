"""Small, focused acceptance extensions for the player interface batch."""
def check(section,window,gui,require):
    if section==385:
        ws=window.centralWidget();ws.setCurrentIndex(0);gui.processEvents()
        require(window.context_bar.isVisible(),'context_shortcuts_visible_across_pages')
        require(not window.context_bar.open_button.isEnabled(),'no_fabricated_recent_content_link')
        require(not window.capture_details.content.isVisible(),'technical_capture_details_collapsed')
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
        ws=window.centralWidget();ws.setCurrentIndex(0);gui.processEvents()
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
