from copy import deepcopy
from unittest.mock import patch

def check(window,gui,require):
    before=deepcopy(window.run.state)
    window.run.state['resources']={'parts_count':{'value':6}}
    from . import expansion_reference
    from .player_parts import part_rows
    from .player_tools import tool_rows
    tools=tool_rows({},held_only=False);identity=tools[0]['id']
    window.run.state['tactical_tools']={identity:{'held':True}}
    window.show_compact();bar=window.compact_window;bar.open_inventory();gui.processEvents();popup=bar.inventory_popup
    require(popup.isVisible()and popup.pages.count()==4,'collection_tool_and_parts_have_real_distinct_pages')
    require(popup.panel is popup.pages.widget(0),'original_collection_panel_and_navigation_retained')
    popup.pages.setCurrentIndex(2);parts=popup.parts;gui.processEvents()
    require(parts.entries.count()==44 and '6件'in parts.notice.text(),'parts_directory_not_inferred_inventory')
    require('不把数量当作成员名单'in parts.notice.text(),'parts_count_does_not_claim_member_list')
    parts.entries.setCurrentRow(0);gui.processEvents();require(not parts.entries.currentItem().icon().isNull(),'real_part_picture_visible')
    require(parts.detail.isReadOnly()and '效果资料'in parts.detail.toPlainText(),'part_effects_read_only')
    require('本局是否持有'in parts.detail.toPlainText(),'part_trigger_and_remaining_uses_not_invented')
    for i in range(1,parts.kind.count()):
        parts.kind.setCurrentIndex(i);gui.processEvents();require(parts.entries.count()==len(part_rows(kind=parts.kind.currentData())),f'exact_source_part_category_{i}')
    parts.kind.setCurrentIndex(0);parts.search.setText('报废轮子');gui.processEvents();require(parts.entries.count()==1,'parts_chinese_search')
    parts.entries.setCurrentRow(0);old=parts.entries.currentItem();bar.refresh();require(parts.entries.currentItem()is old and popup.pages.currentIndex()==2,'refresh_keeps_selected_parts_page_and_item')
    popup.pages.setCurrentIndex(1);tools_panel=popup.tools;gui.processEvents();require(tools_panel.entries.count()==1,'tools_only_qualified_current_possession')
    tools_panel.entries.setCurrentRow(0);require('不自动使用'in tools_panel.detail.toPlainText(),'tools_have_no_game_use_action')
    tools_panel.held.setChecked(False);require(tools_panel.entries.count()==len(tools),'explicit_all_tool_reference_switch')
    with patch.object(expansion_reference,'packet',return_value=None):
        bar.refresh();require(parts.entries.count()==0 and tools_panel.entries.count()==0,'missing_source_clears_both_old_lists')
        require('暂不可用'in parts.notice.text()and '不可用'in tools_panel.notice.text(),'source_loss_explained_without_inventory_reset')
    bar.refresh();require(parts.entries.currentItem()is None and tools_panel.entries.currentItem()is None,'source_recovery_requires_explicit_selection')
    parts.search.clear();parts.entries.setCurrentRow(0);popup.pages.setCurrentIndex(2)
    window.player_validation_target=popup;window.run.state=before

