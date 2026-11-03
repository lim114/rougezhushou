def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 before=deepcopy(window.run.state)
 try:
  gs,node,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in gs};window.show_compact();bar=window.compact_window;bar.open_map();p=bar.map_popup.panel;p.view.select_node(node);p.select_interactive(node);gui.processEvents();root=next(p.entries.topLevelItem(i)for i in range(p.entries.topLevelItemCount())if p.entries.topLevelItem(i).text(0).startswith('已列条件排除'));require(not root.isExpanded(),'excluded_references_collapsed_by_default');root.setExpanded(True);p.entries.setCurrentItem(root.child(0));require('排除依据'in p.detail.toPlainText()and'不属于本节点当前资料候选'in p.detail.toPlainText(),'excluded_reference_has_plain_reason_and_scope');key=p.selected_reference;p.refresh();require(p.selected_reference==key,'excluded_reference_selection_survives_refresh');require(p.open_button.isEnabled(),'excluded_original_reference_readable_without_candidate_claim');window.player_validation_target=bar.map_popup
 finally:window.run.state=before
