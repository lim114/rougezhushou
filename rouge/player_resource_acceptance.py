from copy import deepcopy

def check(window,gui,require):
    before=deepcopy(window.run.state);window.run.state['history']=[{'kind':'resource_updated','resource':key,'value':value,'at':index+1}for index,(key,value)in enumerate([('gold',10),('parts_count',2),('gold',0),('gold',None),('gold',7),('parts_count',3)])]
    window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.resources);gui.processEvents();page=panel.resources
    require(page.entries.count()==6,'resource_reads_have_separate_history_page')
    page.entries.setCurrentRow(0);require('变化：未知'in page.detail.toPlainText()or '相对上次已读数量：未知'in page.detail.toPlainText(),'first_resource_read_is_not_gain_from_zero')
    page.entries.setCurrentRow(2);require('读到数量：0'in page.detail.toPlainText()and '-10'in page.detail.toPlainText(),'valid_zero_and_negative_difference_preserved')
    page.entries.setCurrentRow(4);require('未知'in page.detail.toPlainText(),'unread_intermediate_breaks_difference_chain')
    page.filter.setCurrentIndex(page.filter.findData('parts_count'));require(page.entries.count()==2,'resource_filters_do_not_mix_baselines')
    page.entries.setCurrentRow(1);require('+1'in page.detail.toPlainText()and '不能据此确定'in page.detail.toPlainText(),'resource_difference_not_attributed_to_a_drop')
    old=page.entries.currentItem();bar.refresh();require(page.entries.currentItem()is old and page.filter.currentData()=='parts_count','unchanged_refresh_keeps_resource_reading')
    require(page.detail.isReadOnly(),'resource_history_is_read_only');window.player_validation_target=bar.replay_popup;window.run.state=before

