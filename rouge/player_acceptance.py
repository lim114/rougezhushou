"""Small, focused acceptance extensions for the player interface batch."""
def check(section,window,gui,require):
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
