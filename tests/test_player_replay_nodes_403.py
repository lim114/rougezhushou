from copy import deepcopy
import unittest
from rouge.map_recognition import map_data
from rouge.player_replay_nodes import node_steps,template_graph,zone_label

class ReplayNodeTests(unittest.TestCase):
    def setUp(self):
        self.template=next(row for row in map_data()['templates']if row['nodes'])
        self.zone=self.template['zone_id'];self.node=self.template['nodes'][0]['id']
    def test_current_map_does_not_backfill_missing_historical_template(self):
        state={'maps':{self.zone:self.template},'history':[{'kind':'map_node_passed','zone_id':self.zone,'node_id':self.node,'original_type':'诡意行商'}]}
        row=node_steps(state)[0];self.assertIsNone(row['template']);self.assertIsNone(template_graph(row))
    def test_exact_past_template_and_passed_original_type_are_kept(self):
        state={'history':[{'kind':'map_confirmed','zone_id':self.zone,'template_id':self.template['id']},{'kind':'map_node_passed','zone_id':self.zone,'node_id':self.node,'original_type':'诡意行商'}]};before=deepcopy(state)
        row=node_steps(state)[0];graph=template_graph(row);node=next(n for n in graph['nodes']if n['id']==self.node)
        self.assertEqual(node['observed_type'],'林间空地');self.assertEqual(node['remembered_type'],'诡意行商');self.assertEqual(state,before)
        self.assertEqual(sum('observed_type'in n for n in graph['nodes']),1)
    def test_wrong_zone_identity_and_unknown_node_never_borrow_geometry(self):
        events=[{'kind':'map_confirmed','zone_id':'unverified-zone','template_id':self.template['id']},{'kind':'map_node_revealed','zone_id':'unverified-zone','node_id':self.node,'type':'作战'}]
        self.assertIsNone(node_steps({'history':events})[0]['template'])
        events=[{'kind':'map_confirmed','zone_id':self.zone,'template_id':self.template['id']},{'kind':'map_node_passed','zone_id':self.zone,'node_id':'not-a-source-node'}]
        self.assertIsNone(node_steps({'history':events})[0]['template'])
    def test_later_layout_replaces_only_later_records_in_same_zone(self):
        events=[{'kind':'map_confirmed','zone_id':self.zone,'template_id':self.template['id']},{'kind':'map_node_revealed','zone_id':self.zone,'node_id':self.node,'type':'作战'}, {'kind':'map_layout_changed','zone_id':self.zone,'current_template':'unverified-template'},{'kind':'map_node_revealed','zone_id':self.zone,'node_id':self.node,'type':'不期而遇'}]
        first,later=node_steps({'history':events});self.assertIsNotNone(first['template']);self.assertIsNone(later['template']);self.assertEqual(next(n for n in template_graph(first)['nodes']if n['id']==self.node)['observed_type'],'作战')
    def test_unknown_original_type_is_not_presented_as_recovered_known_type(self):
        row={'template':self.template,'node_id':self.node,'event':{'kind':'map_node_passed','original_type':'未知的诡秘'}}
        node=next(n for n in template_graph(row)['nodes']if n['id']==self.node);self.assertNotIn('remembered_type',node)
        self.assertIn('未确认',zone_label(None))

if __name__=='__main__':unittest.main()
