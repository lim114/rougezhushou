"""History-prefix maps, resource provenance, and one-pass archive filtering."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.map_recognition import map_data
from rouge.player_replay_nodes import node_steps,template_graph,NodeReplayPage

def history_example():
    t=next(t for t in map_data()['templates']if t['zone_id']=='zone_1'and len(t['nodes'])>=3)
    a,b,c=[n['id']for n in t['nodes'][:3]];zone=t['zone_id']
    events=[{'kind':'map_confirmed','zone_id':zone,'template_id':t['id'],'at':100},
        {'kind':'map_node_revealed','zone_id':zone,'node_id':a,'type':'诡意行商','at':101},
        {'kind':'floor_resources_read','zone_id':zone,'template_id':t['id'],'source':'same_frame_zone_and_resources','values':{'gold':7},'at':102},
        {'kind':'map_position_updated','zone_id':zone,'current':a,'at':103},
        {'kind':'map_node_revealed','zone_id':zone,'node_id':b,'type':'不期而遇','at':104},
        {'kind':'map_node_passed','zone_id':zone,'node_id':a,'original_type':'诡意行商','at':105},
        {'kind':'map_node_content_confirmed','zone_id':zone,'node_id':b,'content':{'kind':'event','title':'桑尼的邀请','source':'same_frame_selected_node'},'at':106},
        {'kind':'floor_resources_read','zone_id':zone,'template_id':t['id'],'source':'same_frame_zone_and_resources','values':{'gold':99},'at':107},
        {'kind':'map_node_revealed','zone_id':zone,'node_id':c,'type':'作战','at':108}]
    return {'id':'isolated-history','history':events,'maps':{zone:{'not':'used'}},'resources':{'gold':{'value':999}}},t,(a,b,c)

class PrefixMapTests(unittest.TestCase):
    def rows(self):
        state,t,ids=history_example();return state,t,ids,node_steps(state)
    def test_previously_read_nodes_accumulate_without_later_values(self):
        state,t,(a,b,c),rows=self.rows();before=deepcopy(state)
        first=template_graph(rows[0]);middle=template_graph(rows[2]);last=template_graph(rows[-1])
        types=lambda g:{n['id']:n.get('observed_type')for n in g['nodes']if n.get('observed_type')}
        self.assertEqual(types(first),{a:'诡意行商'});self.assertEqual(types(middle),{a:'诡意行商',b:'不期而遇'})
        self.assertEqual(types(last),{a:'林间空地',b:'不期而遇',c:'作战'});self.assertEqual(state,before)
        self.assertNotIn('prediction',next(n for n in middle['nodes']if n['id']==c))
    def test_resources_and_position_are_from_the_selected_prefix_not_final_state(self):
        state,t,(a,b,c),rows=self.rows()
        self.assertIsNone(rows[0]['resource_snapshot']);self.assertEqual(rows[2]['resource_snapshot']['values'],{'gold':7})
        self.assertEqual(rows[-1]['resource_snapshot']['values'],{'gold':99})
        self.assertIsNone(template_graph(rows[0])['last_confirmed_current_node']);self.assertEqual(template_graph(rows[2])['last_confirmed_current_node'],a)
    def test_content_has_same_node_and_same_frame_origin_and_keeps_prior_names(self):
        state,t,(a,b,c),rows=self.rows();self.assertNotIn('remembered_content',rows[2]['observed_nodes'][b])
        self.assertEqual(rows[4]['observed_nodes'][b]['remembered_content']['title'],'桑尼的邀请')
        other=deepcopy(state['history'][6]);other['content']['title']='色味不同源';state['history'].append(deepcopy(other))
        newest=node_steps(state)[-1]['observed_nodes'][b];self.assertEqual(newest['content_history'][0]['title'],'桑尼的邀请')
        other['content']['source']='guessed';other['content']['title']='不可归属';state['history'].append(other)
        self.assertEqual(node_steps(state)[-1]['observed_nodes'][b]['remembered_content']['title'],'色味不同源')
    def test_layout_replacement_expires_only_future_memory_and_resources(self):
        state,t,(a,b,c),rows=self.rows();zone=t['zone_id']
        state['history']+=[{'kind':'map_layout_changed','zone_id':zone,'current_template':t['id']},
            {'kind':'map_node_revealed','zone_id':zone,'node_id':c,'type':'作战'}]
        allrows=node_steps(state);self.assertEqual(set(allrows[-1]['observed_nodes']),{c});self.assertIsNone(allrows[-1]['resource_snapshot'])
        self.assertEqual(allrows[2],rows[2]);self.assertIsNone(allrows[-1]['last_confirmed_current_node'])
    def test_missing_template_and_wrong_zone_never_borrow_live_maps(self):
        state,t,ids=history_example();state['history']=state['history'][1:]
        self.assertTrue(all(r['template']is None for r in node_steps(state)))
        state['history'].insert(0,{'kind':'map_confirmed','zone_id':'zone_2','template_id':t['id']})
        self.assertTrue(all(r['template']is None for r in node_steps(state)))
    def test_saved_order_not_timestamp_controls_the_history_and_snapshots_detach(self):
        state,t,(a,b,c)=history_example();state['history'][1]['at']=99999;state['history'][4]['at']=1
        rows=node_steps(state);self.assertNotIn(b,rows[0]['observed_nodes']);rows[-1]['observed_nodes'][a]['remembered_type']='mutated'
        self.assertNotIn('remembered_type',rows[0]['observed_nodes'][a]);self.assertEqual(node_steps(state)[-1]['observed_nodes'][a]['remembered_type'],'诡意行商')
    def test_unknown_original_passed_type_retains_earlier_actual_read(self):
        state,t,(a,b,c)=history_example();state['history'][5]['original_type']='未知的诡秘'
        node=node_steps(state)[3]['observed_nodes'][a];self.assertEqual(node['remembered_type'],'诡意行商');self.assertTrue(node['visited'])

class HistoryReaderUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_append_keeps_selected_past_map_and_resource_value_until_user_moves(self):
        state,t,ids=history_example();page=NodeReplayPage();self.addCleanup(page.close);page.show();page.refresh(state);page.entries.setCurrentRow(2)
        graph=deepcopy(page.view.graph);self.assertIn('源石锭 7',page.resources.text());before=deepcopy(state)
        page.resize(720,500);self.qt.processEvents()
        point=page.view._positions()[1][ids[0]];self.assertGreaterEqual(point.y()-page.view.icon_size()/2-30,0)
        self.assertNotIn('1970',page.entries.item(0).text());self.assertIn('1970',page.entries.item(0).toolTip())
        state['history'].append({'kind':'map_position_updated','zone_id':t['zone_id'],'current':ids[-1],'at':109});page.refresh(state)
        self.assertEqual(page.entries.currentRow(),2);self.assertEqual(page.view.graph,graph);self.assertIn('源石锭 7',page.resources.text())
        page.entries.setCurrentRow(page.entries.count()-1);self.assertIn('源石锭 99',page.resources.text());self.assertEqual(state['history'][:-1],before['history'])
        state['id']='new-isolated';page.refresh(state);self.assertEqual(page.entries.currentRow(),-1);self.assertIsNone(page.view.graph)
    def test_statistics_page_selects_archives_once_for_both_views(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from rouge.player_history_store import RunHistoryStore
        from rouge.player_personal_statistics import PersonalStatisticsPage
        from rouge import player_cohort_ui as ui
        with TemporaryDirectory()as folder:
            page=PersonalStatisticsPage(RunHistoryStore(Path(folder)));self.addCleanup(page.close)
            with patch.object(ui,'selected_records',wraps=ui.selected_records)as selection:
                page.render();self.assertEqual(selection.call_count,1)
    def test_unrelated_history_append_does_not_rebuild_map_projection(self):
        from rouge import player_replay_nodes as model
        state,t,ids=history_example();page=NodeReplayPage();self.addCleanup(page.close);page.refresh(state)
        with patch.object(model,'node_steps',wraps=model.node_steps)as projection:
            page.refresh(state);state['history'].append({'kind':'resource_updated','resource':'gold','value':120});page.refresh(state)
            self.assertEqual(projection.call_count,0)
            state['history'].append({'kind':'map_position_updated','zone_id':t['zone_id'],'current':ids[-1]});page.refresh(state)
            self.assertEqual(projection.call_count,1)
    def test_cohort_selection_does_not_requalify_every_archive_for_redundant_guard(self):
        from rouge import player_statistics_cohorts as model
        from tests.test_player_statistics_cohorts_407 import record
        records=[record('a',15,'rogue_6_band_1'),record('b',0,'rogue_6_band_3'),record('a',0)]
        with patch.object(model,'cohort',wraps=model.cohort)as qualified:
            self.assertEqual([r['state']['id']for r in model.select_cohort(records,difficulty=15)],['a']);self.assertEqual(qualified.call_count,2)

if __name__=='__main__':unittest.main()
