import unittest
from copy import deepcopy
from rouge.player_map_find import NodeFinder
from rouge.player_map_acceptance import fixtures
class Finder(unittest.TestCase):
 def test_all_recorded_floors_and_exact_identity(self):
  gs,*_=fixtures();graphs={g['zone_id']:g for g in gs};before=deepcopy(graphs);finder=NodeFinder(graphs);r=finder.find();self.assertEqual(len(r),sum(len(g['nodes'])for g in gs));self.assertEqual(graphs,before);self.assertTrue(finder.find('第2层'))
 def test_unbound_content_never_becomes_searchable_title(self):
  gs,*_=fixtures();g=gs[0];n=g['nodes'][0];n['content']={'title':'独有标题','source':'unbound'};self.assertEqual(NodeFinder({g['zone_id']:g}).find('独有标题'),[]);n['content']['source']='same_frame_selected_node';self.assertEqual(NodeFinder({g['zone_id']:g}).find('独有标题')[0]['key'][-1],n['id'])
 def test_title_entry_filters_bad_records_and_deduplicates_bound_history(self):
  gs,*_=fixtures();g=gs[0];n=g['nodes'][0]
  n['content']={'source':'same_frame_selected_node','title':'Alpha 当前'}
  n['remembered_content']={'source':'same_frame_selected_node','title':'Alpha 当前'}
  n['content_history']=[None,[],{'source':'unbound','title':'不可搜索'},
    {'source':'same_frame_selected_node','title':17},
    {'source':'same_frame_selected_node','title':'Beta 历史'}]
  before=deepcopy(g);finder=NodeFinder({g['zone_id']:g})
  row=next(r for r in finder.entries if r['key'][-1]==n['id'])
  self.assertEqual(row['label'].count('Alpha 当前'),1)
  self.assertIn('Alpha 当前、Beta 历史',row['label']);self.assertEqual(g,before)
  self.assertEqual(finder.find('不可搜索'),[])
  self.assertIn(row,finder.find('  ALPHA 当前  '))
  self.assertIn(row,finder.find('beta 历史',row['evidence']))
  n['content']['title']='Changed'
  self.assertEqual(finder.find('Changed'),[])
  self.assertTrue(NodeFinder({g['zone_id']:g}).find('Changed'))
if __name__=='__main__':unittest.main()
