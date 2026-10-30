def check(window,gui,require):
 from .player_map_reader import make_reader
 from .player_spawn_filters import action_rows,group_key
 from PySide6.QtCore import Qt
 dialog=make_reader('battle',{'id':'ro6_b_7','title':'熄日'},window);dialog.show();gui.processEvents();p=dialog.panel;p.tabs.setCurrentIndex(2)
 require(dialog.windowTitle().startswith(p.result['name']),'floating_stage_title_is_derived_from_exact_stage_source')
 require(p.actions.count()==len(p.result['actions']),'default_preview_retains_complete_original_action_list')
 p.queue_kind.setCurrentIndex(p.queue_kind.findData('main'));p.action_group.setCurrentIndex(1);gui.processEvents()
 group=p.action_group.currentData();expected=action_rows(p.result['actions'],'main',group)
 require(p.actions.count()==len(expected)and all(group_key(a)==group for a in expected),'selected_configuration_group_has_only_exact_original_members')
 p.action_group.setCurrentIndex(0);p.action_focus.setCurrentIndex(p.action_focus.findData('enemy'));gui.processEvents()
 require(p.actions.count()==0 and '请先在敌人页选择'in p.action_filter_notice.text(),'missing_enemy_selection_never_becomes_all_candidates')
 enemy=next(e for e in p.result['enemies']if any(e['key']==candidate['key']for a in action_rows(p.result['actions'],'main')for candidate in a['enemy_candidates']))
 p.enemy_choices.select_value(enemy['key']);gui.processEvents();expected=action_rows(p.result['actions'],'main',focus='enemy',enemy_key=enemy['key'])
 require(p.actions.count()==len(expected)and p.actions.count()>0,'enemy_reference_filter_keeps_all_matching_candidate_actions')
 p.actions.setCurrentRow(0);key=p.action_key;p.refresh_reference();gui.processEvents()
 require(p.action_focus.currentData()=='enemy'and p.action_key==key,'ordinary_reference_refresh_preserves_focus_filter_and_action')
 p.action_focus.setCurrentIndex(p.action_focus.findData('predefined'));target=next(a for a in p.result['actions']if a['raw'].get('actionType')=='SPAWN')
 require(p.focus_action(target),'explicit_action_navigation_clears_incompatible_filters')
 require(p.action_focus.currentData()is None and p.action_group.currentData()is None and p.action_key==target['key'],'revealed_action_has_exact_identity_after_filter_reset')
 require(p.open_action_positions(),'filtered_action_can_open_existing_fixed_map_position_reference');gui.processEvents()
 require(p.action_position_dialog.isVisible(),'actual_fixed_position_dialog_visible');p.action_position_dialog.close()
 require('不证明实际触发'in p.action_filter_notice.text()and'准确时刻：未知'in p.action_player.toPlainText(),'configuration_filters_do_not_invent_absolute_spawn_clock')
 window.player_validation_target=dialog
