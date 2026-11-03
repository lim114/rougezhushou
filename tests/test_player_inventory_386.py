import unittest
from unittest.mock import patch
from copy import deepcopy
from rouge.player_inventory import inventory_rows
class Inventory(unittest.TestCase):
 def test_confirmed_only(self):
  state={'relics':{'rogue_6_relic_legacy_1':{},'rogue_6_relic_legacy_2':{'held':False}}};before=deepcopy(state)
  self.assertEqual([x['id']for x in inventory_rows(state)],['rogue_6_relic_legacy_1']);self.assertEqual(state,before)
 def test_effect_search(self):
  rows=inventory_rows({},'希望',False);self.assertTrue(rows);self.assertTrue(all('希望'in x['name']+x['usage']for x in rows))
 def test_source_loss_clears(self):
  with patch('rouge.player_inventory.reference.packet',return_value=None):self.assertIsNone(inventory_rows({}))
 def test_unknown_flag_not_held(self):self.assertEqual(inventory_rows({'relics':{'rogue_6_relic_legacy_1':{'held':'true'}}}),[])
