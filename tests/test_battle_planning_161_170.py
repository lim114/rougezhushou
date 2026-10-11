import unittest
from rouge.battle_planning import action_catalog

class BattlePlanningTests(unittest.TestCase):
    def test_161_complete_actions(self):
        r=action_catalog('ro6_n_1_1')
        self.assertEqual(len(r['actions']),sum(len(f['actions']) for w in __import__('rouge.battle_preview',fromlist=['battle_data']).battle_data()['stages']['ro6_n_1_1']['waves'] for f in w['fragments']))
        self.assertIn('ACTIVATE_PREDEFINED',r['action_types'])
        self.assertTrue(all(a['absolute_seconds'] is None for a in r['actions']))
        self.assertFalse(r['actual_gameplay_verified'])

    def test_161_copied_source(self):
        a=action_catalog('ro6_n_1_1'); a['actions'][0]['action']['key']='invalid'
        self.assertNotEqual(action_catalog('ro6_n_1_1')['actions'][0]['action']['key'],'invalid')

    def test_162_alias_binding(self):
        from rouge.battle_planning import predefined_activations
        r=predefined_activations('ro6_n_1_1')
        self.assertTrue(any(a['binding_status']=='empty_key' for a in r['activations']))
        found=[a for a in r['activations'] if a['binding_status']=='exact_alias']
        self.assertTrue(found)
        for a in found:
            self.assertEqual(a['key'],a['objects'][0]['alias'])
            self.assertIsNone(a['objects'][0]['actual_activation_seconds'])

    def test_162_object_isolation(self):
        from rouge.battle_planning import predefined_activations
        r=predefined_activations('ro6_n_1_1');r['activations'].clear()
        self.assertTrue(predefined_activations('ro6_n_1_1')['activations'])
