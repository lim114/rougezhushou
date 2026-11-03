import unittest
from PySide6.QtCore import QRect
from rouge.player_game_map import hit_node
class NodeHitTests(unittest.TestCase):
 def sample(self):return {'rect':QRect(-100,20,640,360),'points':[('one',160,180),('two',480,180)]},{'physical_client':(-150,30,960,540),'cursor':(90,300),'cursor_on_game':True}
 def test_node_hit_uses_physical_to_logical_dpi(self):
  data,s=self.sample();self.assertEqual(hit_node(data,s),'one');s['cursor']=(570,300);self.assertEqual(hit_node(data,s),'two')
 def test_off_game_far_and_ambiguous_hits_refused(self):
  data,s=self.sample();s['cursor_on_game']=False;self.assertIsNone(hit_node(data,s));s['cursor_on_game']=True;s['cursor']=(300,100);self.assertIsNone(hit_node(data,s));s['cursor']=(90,300);data['points'].append(('ambiguous',162,180));self.assertIsNone(hit_node(data,s))

class SavedRecordBoundaryTests(unittest.TestCase):
 def test_malformed_new_history_records_are_ignored_not_repaired(self):
  from rouge.player_shop_memory import qualified
  from rouge.player_floor_resources import snapshots
  self.assertIsNone(qualified({'source':'fresh_shop_exact_names','complete':False,'items':[{'id':[],'name':'x'}]}))
  self.assertEqual(snapshots({'history':[{'kind':'floor_resources_read','source':'same_frame_zone_and_resources','zone_id':[],'values':{}}]}),[])
