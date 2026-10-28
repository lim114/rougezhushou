"""Small, focused acceptance extensions for the player interface batch."""
def check(section,window,gui,require):
    if section==381:
        from .player_workspace import DEVELOPER_PAGES
        ws=window.centralWidget()
        require(all(ws.pages[p][0]=='developer'for p in ws.pages if ws.pages[p][1]in DEVELOPER_PAGES),'all_existing_developer_readers_outside_player_groups')
        ws.setCurrentWidget(window.exploration_map_tab);gui.processEvents()
        require(ws.currentWidget()is window.exploration_map_tab,'map_is_direct_player_page')
