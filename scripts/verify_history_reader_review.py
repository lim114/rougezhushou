"""History-prefix map and archived/live isolation in a native temporary-state app."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,sys,os
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check;images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.player_replay_archive import reload_history
        from tests.test_history_reader_review import history_example
        import win32gui,win32process
        original(section,window,gui,require);before=deepcopy(window.run.state)
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_visible_owned')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_image_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        try:
            fixture,template,(a,b,c)=history_example();state={**deepcopy(before),**fixture,'maps':{}};state['id']='isolated-prefix-history'
            bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.history_store.archive(state);reload_history(panel)
            require(bar.replay_popup.objectName()=='historyWindow'and '#f5f5f7'in bar.replay_popup.styleSheet(),'history_uses_existing_light_video_palette')
            panel.sessions.setCurrentIndex(panel.sessions.findData('archive:'+state['id']));panel.tabs.setCurrentWidget(panel.nodes);gui.processEvents();page=panel.nodes
            page.entries.setCurrentRow(2);gui.processEvents();nodes={n['id']:n for n in page.view.graph['nodes']}
            require(nodes[a]['observed_type']=='诡意行商'and nodes[b]['observed_type']=='不期而遇'and 'observed_type'not in nodes[c],'map_accumulates_only_two_reads_before_selected_step')
            require(page.view.graph['last_confirmed_current_node']==a and page.view.selected==b,'selected_node_and_latest_historical_position_are_distinct')
            point=page.view._positions()[1][a];require(point.y()-page.view.icon_size()/2-30>=0,'historical_position_caption_stays_inside_visible_map')
            require('源石锭 7'in page.resources.text()and'999'not in page.resources.text(),'historical_resource_is_saved_zone_snapshot_not_final_or_current_amount')
            panel.notice.setText('隔离历史示例 · 截至所选记录，非实机对局');save(bar.replay_popup,'history-middle')
            QTest.keyClick(page.entries,Qt.Key.Key_Home);gui.processEvents()
            require(page.entries.currentRow()==0 and len([n for n in page.view.graph['nodes']if n.get('observed_type')])==1,'native_keyboard_backtracks_without_later_node_leak')
            require('尚未记录'in page.resources.text(),'earliest_record_does_not_backfill_later_resources');save(bar.replay_popup,'history-earlier')
            QTest.keyClick(page.entries,Qt.Key.Key_End);gui.processEvents();nodes={n['id']:n for n in page.view.graph['nodes']}
            require(nodes[a]['observed_type']=='林间空地'and nodes[a]['remembered_type']=='诡意行商'and nodes[c]['observed_type']=='作战','latest_history_keeps_passed_original_and_later_exact_read')
            require(nodes[b]['remembered_content']['title']=='桑尼的邀请'and'源石锭 99'in page.resources.text(),'latest_history_retains_bound_content_and_latest_saved_resources');save(bar.replay_popup,'history-later')
            selection=page.entries.currentRow();graph=deepcopy(page.view.graph)
            window.run.state['history'].append({'kind':'resource_updated','resource':'gold','value':500,'at':200});bar.refresh();gui.processEvents()
            require(page.entries.currentRow()==selection and page.view.graph==graph and panel.snapshot['id']==state['id'],'live_update_preserves_selected_archive_and_past_map')
            state['history']+=[{'kind':'map_layout_changed','zone_id':template['zone_id'],'current_template':'unverified-template','at':201},
                {'kind':'map_node_passed','zone_id':template['zone_id'],'node_id':a,'at':202}]
            panel.history_store.archive(state);reload_history(panel);gui.processEvents()
            require(page.entries.currentRow()==selection and page.view.graph==graph,'new_archive_version_preserves_existing_reading_before_layout_change')
            page.entries.setCurrentRow(page.entries.count()-1);gui.processEvents();require(page.view.graph is None,'unknown_later_layout_uses_no_current_or_previous_geometry')
            require('尚未记录'in page.resources.text(),'new_layout_does_not_borrow_prior_layout_resources');save(bar.replay_popup,'history-unknown-layout')
            page.entries.setCurrentRow(2);gui.processEvents();require(page.view.graph['template_id']==template['id'],'known_earlier_map_remains_readable_after_unknown_layout')
            panel.sessions.setCurrentIndex(0);gui.processEvents();require(page.view.graph is None and page.entries.count()==0,'return_to_current_does_not_restore_archive_map')
            require(window.run.state['id']==before['id'],'reading_archive_does_not_change_current_run_identity')
            panel.sessions.setCurrentIndex(panel.sessions.findData('archive:'+state['id']));page.entries.setCurrentRow(2);window.player_validation_target=bar.replay_popup
        finally:window.run.state=before
    player_acceptance.check=check;code=run(403,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixture_only':True,'game_observation_claimed':False,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
