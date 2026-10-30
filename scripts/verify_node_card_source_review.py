"""Public source updates and retained node history in an isolated Windows app."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import argparse,json,sys,os
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


def example(trader):
    return {'schema':'rouge-public-node-frequency-v1','metadata':{'sourceSchemaVersion':'merged-node-distance@1',
        'updatedAt':'2026-10-20T00:00:00Z','sampleCount':100},
        'counts':{'rogue-trader':{'0':{'2':trader}},'encounter':{'0':{'2':100-trader}}},
        'scope':'Isolated synthetic example, not real website statistics.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check;images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.player_map_acceptance import fixtures
        original(section,window,gui,require)
        before=deepcopy(window.run.state);source=window.node_statistics_source();old_data=deepcopy(source.data)
        bar=window.compact_window
        def save(widget,name):
            import win32gui,win32process
            h=int(widget.winId())
            require(widget.isVisible() and win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_visible_owned_window')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_snapshot_saved')
            images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        try:
            graphs,node_id,old_id,*_=fixtures();node=next(n for n in graphs[0]['nodes']if n['id']==node_id);node['distance']=2
            window.run.state['maps']={g['zone_id']:g for g in graphs};source.accept(example(70))
            bar.open_map();gui.processEvents();panel=bar.map_popup.panel;panel.floors.setCurrentIndex(0);panel.set_type_filter('诡意行商')
            graph=panel.view.graph;binding=(panel.epoch,graph['zone_id'],graph['template_id'],node_id)
            card=panel.hover_card;card.install(binding,graph,node_id,{},panel.view);card.show();card.pin.setChecked(True);gui.processEvents()
            require(card.type_values['诡意行商']=='历史 70.00%','card_uses_accepted_public_source_not_bundled_snapshot')
            card.title.setText('隔离样例 · 模拟统计70%，不是实际网站计数');save(card,'source-before')
            window.open_public_statistics();stats=window.public_statistics;stats.set_map_node(graph,node_id);gui.processEvents()
            require(stats.source is source and panel.statistics_source is source,'statistics_and_map_share_one_source')
            stats.accept_data({'data':example(80)});gui.processEvents()
            require(card.type_values['诡意行商']=='历史 80.00%' and card.pinned and card.binding==binding,'accepted_update_refreshes_pinned_card_without_rebinding')
            require(panel.view.overlay[node_id]['frequency']['frequency']==.8,'map_highlight_uses_same_accepted_frequency')
            require(bar.game_overlay.surface.frequencies is source.index and bar.game_overlay.current is None,'disabled_game_overlay_receives_public_data_without_sampling')
            require(stats.table.item(0,1).text()=='80.00%','statistics_table_agrees_with_map_and_card')
            card.title.setText('隔离样例 · 模拟更新80%，不是实际网站计数');save(card,'source-after')
            stats.context.setText('隔离样例：模拟公开统计；未联网、未上传本局。');save(stats,'statistics');stats.close()
            reading=panel.view.selected;bar.map_popup.hide()
            with patch.object(panel,'refresh',wraps=panel.refresh)as refresh:
                source.accept(example(90));require(refresh.call_count==0,'hidden_map_does_not_rebuild_on_public_update')
            bar.open_map();gui.processEvents()
            require(panel.view.overlay[node_id]['frequency']['frequency']==.9,'reopened_map_loads_latest_accepted_source')
            require(panel.view.selected==reading,'public_update_does_not_reset_map_selection')
            old=next(n for n in window.run.state['maps'][graphs[0]['zone_id']]['nodes']if n['id']==old_id)
            old.update(observed_type='林间空地',remembered_type='不期而遇',
                remembered_content={'kind':'event','title':'桑尼的邀请'},
                content_history=[{'kind':'battle','title':'遗忘时间','variant_id':'ro6_n_1_2'}])
            panel.refresh();panel.view.select_node(old_id);panel.select_interactive(old_id);gui.processEvents()
            graph=panel.view.graph;binding=(panel.epoch,graph['zone_id'],graph['template_id'],old_id)
            card.install(binding,graph,old_id,{},panel.view,force=True);card.show();gui.processEvents()
            require(card.entry_buttons and all(b.property('referenceScope')=='history'for _,_,b in card.entry_buttons),'passed_node_card_has_saved_history_separate_from_candidates')
            require(card.type_values=={'林间空地':'已读'},'passed_node_does_not_get_a_new_generation_probability')
            card.title.setText('隔离样例 · 已通过节点的本局历史');save(card,'passed-history')
            kind,identity,button=next(r for r in card.entry_buttons if r[0]=='event')
            QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(panel.selected_reference[1:]==(kind,identity),'history_card_opens_exact_history_event_inside_map')
            require(panel.selected_reference[0]=='已读历史事件','history_entry_is_not_reclassified_as_current_candidate')
            old['observed_type']='未知的诡秘';panel.refresh();panel.view.select_node(old_id);panel.select_interactive(old_id);gui.processEvents()
            labels=[panel.entries.topLevelItem(i).text(0)for i in range(panel.entries.topLevelItemCount())]
            require(labels and all(s.startswith('已读历史')for s in labels),'unconfirmed_type_with_history_keeps_only_saved_readings')
            panel.status.setText('隔离样例：当前类型未确认，只回看保存的历史，不填入全目录。');save(bar.map_popup,'unknown-history')
            old.pop('remembered_content');old['content_history']=[];panel.refresh();gui.processEvents()
            require(panel.entries.topLevelItemCount()==0,'old_type_without_read_title_does_not_fill_all_events')
            require('类型尚未确认' in panel.detail.toPlainText(),'unknown_type_is_explained_in_player_language')
            window.player_validation_target=bar.map_popup
        finally:
            window.run.state=before
            if old_data is not None:source.accept(old_data)

    player_acceptance.check=check
    code=run(392,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'temporary_public_fixtures_only':True,
        'synthetic_percentages_not_real_website_counts':True,'whole_video_parity_claimed':False,
        'base_harness_node_hover_png':'Diagnostic grab after temporary run restoration, not evidence of a visible hover card.'},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)
