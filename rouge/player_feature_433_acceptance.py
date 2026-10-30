def check(window,gui,require):
 from .player_map_reader import make_reader
 from . import current_battle_reference as model
 from unittest.mock import patch
 window.show_compact();dialog=make_reader('battle',{'id':'ro6_b_5_b','title':'失恒常量'},window.compact_window);dialog.show();gui.processEvents();p=dialog.panel;p.tabs.setCurrentIndex(1)
 enemy=next(e for e in p.result['enemies']if e['id']=='enemy_1250_lyengs_2');p.enemy_search.setText(enemy['name']);gui.processEvents()
 require(p.enemy_combo.count()==2,'enemy_name_search_retains_one_exact_reference_and_placeholder')
 require(p.enemy_choices.select_branch('领袖')and p.enemy_combo.currentData()is None,'empty_filtered_branch_is_retained_without_switching_to_other_tier')
 require(not p.enemy_combo.isEnabled(),'empty_branch_cannot_select_different_tier')
 p.enemy_choices.select_branch('普通');p.enemy_choices.select_value(enemy['key']);gui.processEvents()
 require(p.enemy_key==enemy['key']and not p.enemy_portrait.pixmap().isNull(),'exact_recovered_portrait_visible_in_selected_enemy_reader')
 require('不以白值替代'in p.enemy_player.toPlainText(),'portrait_recovery_does_not_invent_predicted_stats')
 p.refresh_reference();gui.processEvents();require(p.enemy_search.text()==enemy['name']and p.enemy_key==enemy['key'],'ordinary_refresh_keeps_enemy_query_and_exact_reference')
 p.enemy_search.setText('不存在的未公开机制');gui.processEvents()
 require(p.enemy_combo.currentData()is None and p.enemy_key is None and '未匹配不表示没有'in p.enemy_search_notice.text(),'no_match_is_not_proof_of_mechanism_absence')
 with patch('rouge.current_battle_reference.stage_reference',return_value=None):
  require(not p.refresh_reference()and '旧搜索结果已清除'in p.enemy_search_notice.text(),'source_loss_clears_search_result_and_notice')
 p.enemy_search.setText(enemy['name']);p.refresh_reference();p.enemy_choices.select_branch('普通');p.enemy_choices.select_value(enemy['key']);p.tabs.setCurrentIndex(1);gui.processEvents()
 require(model.picture_for_enemy(enemy)is not None,'exact_public_picture_available_without_network_during_use')
 window.player_validation_target=dialog
