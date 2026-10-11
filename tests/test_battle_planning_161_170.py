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

    def test_163_queue_groups(self):
        from rouge.battle_planning import candidate_groups
        r=candidate_groups('ro6_n_1_1')
        self.assertTrue(r['groups'])
        self.assertTrue(all(g['actual_choice'] is None and g['probabilities'] is None for g in r['groups']))
        self.assertTrue(any(c['empty_key'] for g in r['groups'] for c in g['candidates']))
        self.assertEqual(len({(g['queue_id'],g['group_key']) for g in r['groups']}),len(r['groups']))

    def test_163_packages_preserved(self):
        from rouge.battle_planning import candidate_groups
        from rouge.battle_preview import battle_data
        sid=next(s for s in battle_data()['stages'] if candidate_groups(s)['packages'])
        r=candidate_groups(sid)
        self.assertTrue(r['packages'])
        self.assertTrue(all(p['members'] for p in r['packages']))

    def test_164_local_window(self):
        from rouge.battle_planning import local_time_window
        r=local_time_window('ro6_n_1_1',0,0)
        self.assertTrue(r['queues'])
        self.assertTrue(any(a['type']=='ACTIVATE_PREDEFINED' for q in r['queues'] for a in q['occurrences']))
        self.assertTrue(all(a['offset_seconds']==0 for q in r['queues'] for a in q['occurrences']))
        self.assertTrue(all(q['absolute_start_seconds'] is None for q in r['queues']))

    def test_164_window_bounds_and_truncation(self):
        from rouge.battle_planning import local_time_window
        r=local_time_window('ro6_n_1_1',0,10000,limit=1)
        self.assertTrue(any(q['truncated'] for q in r['queues']))
        self.assertTrue(all(len(q['occurrences'])<=1 for q in r['queues']))
        with self.assertRaises(ValueError):local_time_window('ro6_n_1_1',3,2)

    def test_164_earliest_results_before_serialized_order(self):
        from rouge.battle_planning import local_time_window, action_catalog
        from unittest.mock import patch
        rows=action_catalog('ro6_n_1_1')['actions'][:2]
        for r in rows:
            r['action']['count']=1;r['action']['interval']=1
        rows[0]['action']['preDelay']=10;rows[1]['action']['preDelay']=1
        with patch('rouge.battle_planning.action_catalog',return_value={'actions':rows}):
            result=local_time_window('ro6_n_1_1',0,20,limit=1)
        self.assertEqual(result['queues'][0]['occurrences'][0]['offset_seconds'],1)
        self.assertEqual(result['queues'][0]['matching_declared_occurrences'],2)
