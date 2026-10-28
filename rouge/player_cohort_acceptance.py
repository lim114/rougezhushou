from copy import deepcopy

def check(window,gui,require):
    from .player_history_store import RunHistoryStore
    from .run_config import config_data
    store=RunHistoryStore(window.run.file.parent/'run-history')
    for identity,grade,squad,value in [('a',15,'rogue_6_band_1',4),('b',15,'rogue_6_band_2',8),('c',0,'rogue_6_band_3',0),('d',None,None,100)]:
        state=deepcopy(window.run.state);state.update(id='owned-cohort-'+identity,history=[{'kind':'node_content_seen','title':'筛选隔离示例'}],resources={'gold':{'value':value}},config={})
        if grade is not None:state['config']['difficulty']={'value':grade,'captured_at':1}
        if squad is not None:state['config']['squad']={'id':squad,'name':config_data()['squads'][squad]['name'],'captured_at':1}
        store.archive(state)
    window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.statistics);page=panel.statistics;gui.processEvents()
    require(page.grade_filter.count()==4 and page.squad_filter.count()==4,'known_zero_fifteen_and_unread_are_separate_choices')
    page.grade_filter.setCurrentIndex(page.grade_filter.findData(15));page.squad_filter.setCurrentIndex(page.squad_filter.findData('rogue_6_band_1'));gui.processEvents()
    require(page.result['archive_count']==2 and page.result['measures']['gold']['mean']==6,'base_and_strength_stage_grouped_by_exact_source_family')
    require('不表示效果完全相同'in page.detail.toPlainText(),'squad_family_grouping_boundary_visible')
    page.squad_filter.setCurrentIndex(0);page.grade_filter.setCurrentIndex(page.grade_filter.findData(0));require(page.result['measures']['gold']['mean']==0,'real_zero_grade_not_mixed_with_unread')
    from .player_statistics_cohorts import UNREAD
    page.grade_filter.setCurrentIndex(page.grade_filter.findData(UNREAD));require(page.result['archive_count']==1 and page.result['measures']['gold']['mean']==100,'unread_configuration_is_explicit_separate_cohort')
    old=page.grade_filter.currentData();page.refresh();require(page.grade_filter.currentData()==old,'manual_statistics_reload_preserves_configuration_filter')
    page.grade_filter.setCurrentIndex(page.grade_filter.findData(15));page.squad_filter.setCurrentIndex(page.squad_filter.findData('rogue_6_band_3'));require(page.result['archive_count']==0 and page.result['measures']['gold']['mean']is None,'empty_combined_cohort_does_not_revert_to_all_records')
    page.squad_filter.setCurrentIndex(page.squad_filter.findData('rogue_6_band_1'));window.player_validation_target=bar.replay_popup

