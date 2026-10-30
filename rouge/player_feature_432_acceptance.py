def check(window,gui,require):
 from copy import deepcopy
 from .player_replay_archive import reload_history,open_statistics_archive
 from .player_statistics_samples import sample_binding
 before=deepcopy(window.run.state)
 try:
  window.show_compact();compact=window.compact_window;compact.open_replay();p=compact.replay_popup.panel
  for identity,value in(('isolated-zero',0),('isolated-ten',10),('isolated-unread',None)):
   archived=deepcopy(before);archived['id']=identity;archived['resources']={'gold':{'value':value}}if value is not None else{};archived['history']=[{'kind':'resource_updated','resource':'gold','value':value,'at':100}];p.history_store.archive(archived)
  reload_history(p);stats=p.statistics;stats.refresh();p.tabs.setCurrentWidget(stats);samples=stats.samples;stats.card_controls.pages.setCurrentWidget(samples);gui.processEvents()
  require(samples.table.rowCount()==3 and sum(r['included']for r in samples.rows)==2,'sample_page_explains_two_effective_and_one_unread_archive')
  require(stats.result['measures']['gold']['mean']==5,'drilldown_and_displayed_mean_use_same_values')
  require({samples.table.item(i,1).text()for i in range(3)}=={'0','10','未知（未计入）'},'zero_and_unknown_are_visibly_distinct')
  samples.table.selectRow(0);binding=sample_binding(samples.rows[0]);samples.open_button.click();gui.processEvents()
  require(p.sessions.currentData()=='archive:'+binding['id']and p.tabs.currentIndex()==0,'statistics_row_opens_exact_saved_archive')
  require(window.run.state==before,'statistics_navigation_never_restores_archived_run')
  stale={**binding,'state_sha256':'0'*64};require(not open_statistics_archive(p,stale),'changed_or_unverifiable_archive_is_not_silently_substituted')
  require(not open_statistics_archive(p,None),'malformed_sample_navigation_refused')
  stats.refresh();p.tabs.setCurrentWidget(stats);stats.card_controls.pages.setCurrentWidget(samples);samples.table.selectRow(0);gui.processEvents();row=samples.table.currentRow();stats.render()
  require(samples.table.currentRow()==row,'unchanged_statistics_refresh_keeps_sample_selection')
  window.player_validation_target=compact.replay_popup
 finally:window.run.state=before
