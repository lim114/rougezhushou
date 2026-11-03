from copy import deepcopy

def check(window,gui,require):
    from .catalog import catalog,tactical_tools
    before=deepcopy(window.run.state);relic=next(iter(catalog()['relics']));tool=next(iter(tactical_tools()))
    window.run.state['history']=[{'kind':'relic_confirmed','id':relic,'at':3},{'kind':'tool_confirmed','id':tool,'at':3},{'kind':'operator_updated','id':'mechanist','fields':{'elite':1,'level':80},'at':3},{'kind':'node_content_seen','title':'同时读到的节点','at':3}]
    window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.evidence);gui.processEvents();page=panel.evidence
    require(page.tabs.count()==3 and all(widget.count()==1 for widget in page.lists.values()),'relic_tool_and_team_are_separate_real_branches')
    page.lists['relic'].setCurrentRow(0);require('确认持有不是本次获得'in page.detail.toPlainText(),'possession_does_not_claim_new_drop')
    require('同时读到的节点'in page.detail.toPlainText()and '不能证明该节点发放'in page.detail.toPlainText(),'same_frame_context_never_claims_reward_source')
    page.tabs.setCurrentIndex(2);page.lists['operator'].setCurrentRow(0);gui.processEvents();require('机械师'in page.detail.toPlainText()and '等级：80'in page.detail.toPlainText(),'qualified_historical_training_has_chinese_name')
    require(not page.lists['operator'].currentItem().icon().isNull(),'actual_operator_portrait_in_history')
    before_text=page.detail.toPlainText();window.run.state['last_read']=11;bar.refresh();require(page.tabs.currentIndex()==2 and page.detail.toPlainText()==before_text,'sampling_refresh_preserves_evidence_branch_and_record')
    require(page.detail.isReadOnly(),'evidence_history_has_no_state_edit');window.player_validation_target=bar.replay_popup;window.run.state=before

