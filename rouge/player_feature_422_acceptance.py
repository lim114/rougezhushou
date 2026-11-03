def check(window,gui,require):
 from copy import deepcopy
 from .map_recognition import map_data,predict_map
 from .player_floor_resources import snapshot_text
 before=deepcopy(window.run.state)
 try:
  from .player_map_acceptance import fixtures
  graph=fixtures()[0][0];window.run.state['maps']={'zone_1':graph}
  window.run.state['history']=[{'kind':'floor_resources_read','source':'same_frame_zone_and_resources','at':100,'zone_id':'zone_1','template_id':graph['template_id'],'values':{'gold':7,'parts_count':2}}]
  window.run.state['resources']={'gold':{'value':99,'captured_at':200}}
  window.show_compact();c=window.compact_window;c.open_map();gui.processEvents();panel=c.map_popup.panel
  require('源石锭 7'in panel.floor_resources.text()and '99'not in panel.floor_resources.text(),'floor_label_uses_snapshot_not_current_gold')
  require('不是入层'in panel.floor_resources.text(),'floor_snapshot_not_complete_settlement_claim')
  c.open_replay();gui.processEvents();replay=c.replay_popup.panel;replay.tabs.setCurrentWidget(replay.floor_resources);replay.floor_resources.entries.setCurrentRow(0);gui.processEvents()
  require(replay.floor_resources.entries.count()==1,'same_floor_snapshot_available_in_readonly_replay')
  require('源石锭 7'in replay.floor_resources.detail.text(),'replay_exact_record_quantities')
  old=replay.floor_resources.entries.currentRow();replay.refresh();require(replay.floor_resources.entries.currentRow()==old,'refresh_preserves_floor_snapshot_selection');window.player_validation_target=c.replay_popup
 finally:window.run.state=before
