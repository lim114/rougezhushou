import unittest
from copy import deepcopy
from rouge.player_map_find import rows
from rouge.player_map_acceptance import fixtures
class Finder(unittest.TestCase):
 def test_all_recorded_floors_and_exact_identity(self):
  gs,*_=fixtures();graphs={g['zone_id']:g for g in gs};before=deepcopy(graphs);r=rows(graphs);self.assertEqual(len(r),sum(len(g['nodes'])for g in gs));self.assertEqual(graphs,before);self.assertTrue(rows(graphs,'第2层'))
 def test_unbound_content_never_becomes_searchable_title(self):
  gs,*_=fixtures();g=gs[0];n=g['nodes'][0];n['content']={'title':'独有标题','source':'unbound'};self.assertEqual(rows({g['zone_id']:g},'独有标题'),[]);n['content']['source']='same_frame_selected_node';self.assertEqual(rows({g['zone_id']:g},'独有标题')[0]['key'][-1],n['id'])
if __name__=='__main__':unittest.main()
