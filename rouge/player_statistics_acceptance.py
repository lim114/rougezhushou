from copy import deepcopy

def populate(window):
    from .player_history_store import RunHistoryStore
    from .catalog import catalog
    store=RunHistoryStore(window.run.file.parent/'run-history');identity=next(iter(catalog()['relics']))
    for name,value,count,verified in [('a',0,1,True),('b',10,0,True),('c',None,None,False)]:
        state=deepcopy(window.run.state);state.update(id='owned-stat-'+name,history=[{'kind':'node_content_seen','title':'统计隔离示例'}],resources={}if value is None else{'gold':{'value':value}},relics={identity:{'held':True}}if count==1 else{},tactical_tools={},inventory_verified=verified,relic_count=count)
        store.archive(state)
    return store,identity

def check(window,gui,require):
    from unittest.mock import patch
    store,identity=populate(window);window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.statistics);gui.processEvents();page=panel.statistics
    require(page.result['archive_count']==3,'personal_statistics_uses_only_owned_archive_records')
    measure=page.result['measures']['gold'];require(measure['mean']==5 and measure['sample_count']==2 and measure['missing_count']==1,'zero_included_missing_excluded_from_mean')
    require('不是掉落概率'not in page.detail.toPlainText()or '胜率'in page.detail.toPlainText(),'statistics_boundary_explained_in_player_words')
    page.relic.setCurrentIndex(page.relic.findData(identity));gui.processEvents();row=page.result['relic'];require(row['fraction']==.5 and row['sample_count']==2 and row['excluded_incomplete_count']==1,'holding_fraction_uses_complete_inventory_denominator')
    require('不是掉落概率'in page.detail.toPlainText()and '不上传'in page.detail.toPlainText(),'holding_fraction_and_privacy_scope_visible')
    selected=page.relic.currentData();text=page.detail.toPlainText();bar.refresh();require(page.relic.currentData()==selected and page.detail.toPlainText()==text,'game_frame_refresh_does_not_reload_or_jump_statistics')
    with patch.object(type(store),'records',side_effect=OSError('隔离模拟：历史暂不可读')):
        page.refresh();require(page.result is None and '统计未知'in page.detail.toPlainText(),'history_failure_clears_statistic_instead_of_zero_or_old_result')
    page.refresh();require(page.relic.currentData()==selected and page.result['relic']['fraction']==.5,'explicit_reload_retains_relic_filter')
    window.player_validation_target=bar.replay_popup

