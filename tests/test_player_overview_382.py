import unittest
from copy import deepcopy
from rouge.player_overview import overview_facts
class OverviewTests(unittest.TestCase):
 def test_unknown_is_not_zero(self):
  r=overview_facts({});self.assertEqual(r['保密等级'],'尚未确认');self.assertIn('未核对',r['收藏品完整性'])
 def test_query_does_not_modify_state(self):
  s={'config':{},'operators':{},'relics':{}};before=deepcopy(s);overview_facts(s);self.assertEqual(s,before)
 def test_count_not_completeness(self):
  r=overview_facts({'relic_count':4,'inventory_verified':False});self.assertEqual(r['已读收藏品'],'0件 / 共4件');self.assertNotEqual(r['收藏品完整性'],'已核对完整')
 def test_complete_only_explicit_true(self):
  self.assertEqual(overview_facts({'inventory_verified':True,'relic_count':0})['收藏品完整性'],'已核对完整')
  self.assertNotEqual(overview_facts({'inventory_verified':True})['收藏品完整性'],'已核对完整')
  self.assertNotEqual(overview_facts({'inventory_verified':1,'relic_count':0})['收藏品完整性'],'已核对完整')
if __name__=='__main__':unittest.main()
