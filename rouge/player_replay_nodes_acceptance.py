from copy import deepcopy

def check(window,gui,require):
    from .map_recognition import map_data
    before=deepcopy(window.run.state);template=next(row for row in map_data()['templates']if row['nodes']);identity=template['nodes'][0]['id'];zone=template['zone_id']
    window.run.state['history']=[{'kind':'map_confirmed','zone_id':zone,'template_id':template['id'],'at':1},{'kind':'map_node_revealed','zone_id':zone,'node_id':identity,'type':'诡意行商','at':2},{'kind':'map_node_passed','zone_id':zone,'node_id':identity,'original_type':'诡意行商','at':3}]
    window.show_compact();bar=window.compact_window;bar.open_replay();gui.processEvents();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.nodes);page=panel.nodes
    require(page.entries.count()==2 and page.floors.count()==2,'node_reads_grouped_in_real_floor_filter')
    page.entries.setCurrentRow(1);gui.processEvents();require(page.view.graph is not None and page.view.selected==identity,'selected_past_record_mapped_to_exact_template_node')
    node=next(n for n in page.view.graph['nodes']if n['id']==identity);require(node['observed_type']=='林间空地'and node['remembered_type']=='诡意行商','passed_node_retains_its_explicit_original_type')
    window.run.state['last_read']=9;bar.refresh();require(page.entries.currentRow()==1 and panel.tabs.currentWidget()is panel.nodes,'frame_refresh_preserves_historical_node_reading')
    window.run.state['history'].append({'kind':'map_layout_changed','zone_id':zone,'current_template':'not-known','at':4});window.run.state['history'].append({'kind':'map_node_passed','zone_id':zone,'node_id':identity,'at':5});bar.refresh();page.entries.setCurrentRow(2);gui.processEvents()
    require(page.view.graph is None,'missing_historical_template_never_borrows_current_map')
    page.entries.setCurrentRow(1);require(page.view.graph is not None,'older_exact_template_survives_later_unknown_layout')
    require('不把后来的节点状态填回过去'in page.notice.text(),'past_map_evidence_boundary_readable')
    window.player_validation_target=bar.replay_popup;window.run.state=before

