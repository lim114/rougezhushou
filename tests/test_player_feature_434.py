import unittest
from copy import deepcopy
from rouge.player_spawn_filters import action_rows,group_key,group_label

def actions():
 return [
  {'key':'first','queue':{'kind':'main','wave':1,'fragment':1},'raw':{'actionType':'SPAWN','count':3},'enemy_candidates':[{'key':'e0'},{'key':'e1'}]},
  {'key':'hidden','queue':{'kind':'main','wave':1,'fragment':2},'raw':{'hiddenGroup':'source-group'},'enemy_candidates':[{'key':'e0'}]},
  {'key':'random','queue':{'kind':'branch','branch_index':2,'phase':1},'raw':{'randomSpawnGroupKey':'source-random'},'enemy_candidates':[{'key':'e1'}]},
  {'key':'object','queue':{'kind':'main','wave':1,'fragment':1},'raw':{'actionType':'ACTIVATE_PREDEFINED'},'enemy_candidates':[]}]

class SpawnConfigurationFilters(unittest.TestCase):
 def test_source_order_and_duplicate_group_members_retained(self):
  raw=actions();before=deepcopy(raw);rows=action_rows(raw,group=('main',1,1))
  self.assertEqual([a['key']for a in rows],['first','object']);self.assertEqual(raw,before)
 def test_current_enemy_filter_is_candidate_membership_not_level_selection(self):
  rows=action_rows(actions(),focus='enemy',enemy_key='e1');self.assertEqual([a['key']for a in rows],['first','random'])
  self.assertEqual(len(rows[0]['enemy_candidates']),2);self.assertEqual(rows[0]['raw']['count'],3)
  self.assertEqual(action_rows(actions(),focus='enemy'),[])
 def test_hidden_random_predefined_are_separate_literal_markers(self):
  for focus,expected in(('hidden','hidden'),('random','random'),('predefined','object')):
   self.assertEqual([a['key']for a in action_rows(actions(),focus=focus)],[expected])
  self.assertEqual(action_rows(actions(),'main',focus='random'),[])
 def test_group_numbers_match_existing_configuration_not_clock(self):
  self.assertEqual(group_key(actions()[0]),('main',1,1));self.assertIn('第1波',group_label(('main',1,1)))
  self.assertIsNone(group_key({'queue':{'kind':'main','wave':True,'fragment':1}}))
  self.assertEqual(group_key(actions()[2]),('branch',2,1))
 def test_missing_group_and_unknown_filter_do_not_fall_back_to_all(self):
  self.assertEqual(action_rows(actions(),group=('main',99,99)),[]);self.assertEqual(action_rows(actions(),focus='unsupported'),[])

if __name__=='__main__':unittest.main()
