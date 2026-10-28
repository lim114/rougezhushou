from copy import deepcopy
from unittest.mock import patch

def check(window,gui,require):
    before=deepcopy(window.run.state)
    window.run.state['id']='current';window.run.state['history']=[{'at':2,'kind':'node_content_seen','title':'归档示例关卡'}]
    old_id=window.run.state['id'];window.run.save()
    window.show_compact();bar=window.compact_window;bar.open_replay();gui.processEvents();panel=bar.replay_popup.panel
    from .player_history_store import RunHistoryStore
    store=RunHistoryStore(window.run.file.parent/'run-history')
    with patch.object(RunHistoryStore,'archive',side_effect=OSError('隔离模拟：磁盘暂不可写')):
        epoch=window.sample_epoch;state=deepcopy(window.run.state);window.reset_run()
        require(window.run.state==state and window.sample_epoch==epoch,'archive_failure_keeps_run_and_sampling_epoch')
        require('未开始新局'in window.capture_status.text(),'archive_failure_explained_before_reset')
    window.reset_run();gui.processEvents();require(window.run.state['id']!=old_id,'only_explicit_manual_reset_starts_new_run')
    records,issues=store.records();require(len(records)==1 and not issues,'previous_nonempty_run_archived_once_locally')
    require(records[0]['state']['id']==old_id and records[0]['outcome']is None,'archive_keeps_old_identity_without_inventing_outcome')
    from .player_replay_archive import reload_history
    reload_history(panel);require(panel.sessions.count()==2,'manual_reload_shows_current_and_archived_run')
    require(panel.sessions.findData('archive:'+old_id)!=panel.sessions.findData('current'),'literal_old_run_id_cannot_collide_with_current_view_choice')
    panel.sessions.setCurrentIndex(panel.sessions.findData('archive:'+old_id));gui.processEvents();panel.entries.setCurrentRow(0)
    require('归档示例关卡'in panel.detail.toPlainText(),'archived_record_can_be_read_without_restore')
    current=deepcopy(window.run.state);bar.refresh();require(window.run.state==current and panel.snapshot['id']==old_id,'sampling_refresh_does_not_replace_selected_archive_or_current_run')
    with patch.object(RunHistoryStore,'records',side_effect=OSError('隔离模拟：历史暂不可读')):
        reload_history(panel);require(panel.entries.count()==0 and '没有用当前对局冒充历史'in panel.notice.text(),'missing_archive_clears_old_content_without_current_fallback')
    reload_history(panel);require(panel.entries.count()==0,'archive_recovery_requires_explicit_selection')
    panel.sessions.setCurrentIndex(panel.sessions.findData('archive:'+old_id));panel.entries.setCurrentRow(0);window.player_validation_target=bar.replay_popup;window.run.state=before

