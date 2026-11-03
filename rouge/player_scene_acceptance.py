from copy import deepcopy
from PySide6.QtCore import Qt
from unittest.mock import patch

def check(window,gui,require):
    from .player_default_entry_acceptance import check as check_default_entries
    check_default_entries(window,gui,require)
    state=deepcopy(window.run.state);window.run.state['last_node_content']={'kind':'battle','title':'遗忘时间','captured_at':1}
    window.show_compact();bar=window.compact_window;bar.scene_button.click();gui.processEvents();panel=bar.scene_popup.panel
    require(bar.scene_popup.isVisible()and not window.isVisible(),'scene_enemy_opens_in_compact_popover')
    require(panel.stages.count()>=3 and panel.stages.currentData()is None,'same_name_variants_require_explicit_selection')
    panel.stages.setCurrentIndex(1);gui.processEvents();require(panel.result is not None,'exact_stage_loads_reference')
    require(sum(w.count()for w in panel.lists.values())==len(panel.result['enemies']),'all_exact_enemy_references_kept')
    kind=next(k for k,w in panel.lists.items()if w.count());widget=panel.lists[kind];panel.tabs.setCurrentWidget(widget);widget.setCurrentRow(0);gui.processEvents();item=widget.currentItem();identity=item.data(Qt.ItemDataRole.UserRole)
    require(panel.enemies[identity]['tier']==kind,'separate_enemy_tier_branch')
    require('预计面板'in panel.detail.toPlainText()and '未知'in panel.detail.toPlainText(),'no_raw_stats_substitute_for_unverified_prediction')
    text=panel.detail.toPlainText();window.run.state['last_node_content']['captured_at']=2;bar.refresh();require(widget.currentItem()is item and panel.detail.toPlainText()==text,'timestamp_refresh_keeps_enemy_reading')
    panel.open_button.click();gui.processEvents();require(panel.dialog.isVisible()and panel.dialog.panel.stage_id==panel.identity,'exact_stage_fixed_map_and_full_reference_link')
    panel.dialog.close()
    with patch('rouge.player_scene_battle.expansion_reference.packet',return_value=None):panel.refresh();require(not panel.enemies and not panel.open_button.isEnabled(),'source_loss_clears_scene_enemies_and_navigation')
    panel.refresh();panel.stages.setCurrentIndex(1)
    with patch('rouge.player_scene_battle.model.packet',return_value=None):panel.open_stage();require(not panel.enemies and panel.dialog is None and not panel.open_button.isEnabled(),'battle_source_loss_rechecked_before_opening_cached_stage')
    panel.refresh();require(panel.stages.currentData()is None,'restored_battle_source_requires_explicit_stage_selection')
    panel.refresh();panel.stages.setCurrentIndex(1);panel.tabs.setCurrentWidget(next(w for w in panel.lists.values()if w.count()));panel.tabs.currentWidget().setCurrentRow(0)
    panel.notice.setText('隔离验收示例：遗忘时间的固定资料候选；不是当前本局、必出敌人或实际战斗采集。')
    window.run.state=state
