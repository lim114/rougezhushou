import unittest
from copy import deepcopy
from rouge import public_archive
from rouge.player_inventory import inventory_rows,source_nodes

class AcquisitionLookup(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=public_archive.load()
 def rows(self,query='',**kw):return inventory_rows({},query,False,public_data=self.data,version='dlc1',**kw)
 def test_event_name_search_finds_original_acquisition_description(self):
  rows=self.rows('独活');self.assertTrue(rows);self.assertIn('同行者',{r['name']for r in rows})
  self.assertTrue(all('独活'in r['compendium']['obtainMethod']+r['compendium'].get('unlockConditionText','')or'独活'in r['name']+r['usage']for r in rows))
 def test_unlock_and_special_flags_are_reference_only(self):
  unlocked=self.rows(access='unlock');special=self.rows(access='special')
  self.assertTrue(unlocked);self.assertTrue(special)
  for row in unlocked:self.assertTrue(row['compendium'].get('unlockConditional')is True or row['compendium'].get('unlockConditionText'))
  for row in special:self.assertTrue(row['compendium'].get('specialAccess')is True or row['compendium'].get('obtainMethod'))
  self.assertTrue(all(not r['held']for r in special))
 def test_node_filter_is_exact_and_keeps_only_explicit_memberships(self):
  rows=self.rows(source_node='不期而遇');self.assertTrue(rows)
  self.assertTrue(all('不期而遇'in row['source_nodes']for row in rows))
  self.assertEqual(self.rows(source_node='不期'),[])
 def test_version_without_catalogue_never_borrows_acquisition_text(self):
  self.assertEqual(inventory_rows({},'独活',False,public_data=self.data,version='base'),[])
  self.assertEqual(inventory_rows({},held_only=False,public_data=self.data,version='dlc2',source_node='不期而遇'),[])
 def test_uncovered_is_not_a_claim_of_no_obtain_method(self):
  rows=inventory_rows({},held_only=False,public_data=self.data,version='base',access='uncovered')
  self.assertTrue(rows);self.assertTrue(all(r['compendium']is None for r in rows))
 def test_lookup_does_not_modify_source_or_run_state(self):
  data=deepcopy(self.data);state={'relics':{}};before=deepcopy(data)
  inventory_rows(state,'独活',False,public_data=data,version='dlc1',access='special')
  self.assertEqual(data,before);self.assertEqual(state,{'relics':{}})
 def test_malformed_optional_node_bindings_not_inferred(self):
  packet={'versions':{'test':[{'collectibles':['one'],'nodeBindings':None},{'collectibles':['two'],'nodeBindings':[{'nodeName':False},None,{'nodeName':'明确节点'}]}]}}
  self.assertEqual(source_nodes(packet,'test'),{'one':[],'two':['明确节点']})

if __name__=='__main__':unittest.main()
