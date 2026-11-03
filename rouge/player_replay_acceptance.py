from copy import deepcopy

def check(window,gui,require):
    before=deepcopy(window.run.state)
    window.run.state['history']=[{'at':4,'kind':'node_content_seen','title':'遗忘时间'},{'at':2,'kind':'resource_updated','resource':'gold','value':5},{'at':None,'kind':'unknown_observation'}]
    window.show_compact();bar=window.compact_window;bar.open_replay();gui.processEvents();popup=bar.replay_popup;panel=popup.panel;panel.tabs.setCurrentIndex(0)
    require(popup.isVisible()and not window.isVisible(),'read_only_replay_opens_from_compact_overview')
    require(panel.entries.count()==3 and panel.sessions.count()==1,'current_read_records_without_invented_sessions')
    panel.entries.setCurrentRow(0);gui.processEvents();require('遗忘时间'in panel.detail.toPlainText()and '不是完整游戏日志'in panel.detail.toPlainText(),'player_chinese_record_and_evidence_boundary')
    require(panel.detail.isReadOnly(),'replay_cannot_edit_run_state')
    text=panel.detail.toPlainText();window.run.state['last_read']=22;bar.refresh();require(panel.entries.currentRow()==0 and panel.detail.toPlainText()==text,'unrelated_refresh_keeps_selected_record')
    window.run.state['history'].append({'kind':'node_content_seen','title':'物欲遮天'});bar.refresh();require(panel.entries.count()==4 and panel.entries.currentRow()==0,'new_read_appended_without_jumping_to_latest')
    panel.entries.setCurrentRow(2);require('读取时间未确认'in panel.detail.toPlainText(),'missing_time_not_replaced_by_game_clock')
    window.run.state['id']='isolated-new-id';window.run.state['history']=[];bar.refresh();require(panel.entries.count()==0 and '选择一条'in panel.detail.toPlainText(),'different_run_clears_prior_record_selection')
    window.run.state=deepcopy(before);window.run.state['history']=[{'at':4,'kind':'node_content_seen','title':'遗忘时间'}];bar.refresh();panel.entries.setCurrentRow(0)
    window.player_validation_target=popup;window.run.state=before

