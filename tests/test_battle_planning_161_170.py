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

    def test_165_enemy_reverse_sources(self):
        from rouge.battle_planning import enemy_entry_sources
        r=enemy_entry_sources('ro6_n_1_1','enemy_2152_shezlc',0)
        self.assertTrue(any(e['kind']=='conditional_branch' for e in r['entry_sources']))
        self.assertIsNone(r['actual_enemy_count'])
        self.assertTrue(all(e['action']['key']==r['enemy_id'] for e in r['entry_sources']))
        with self.assertRaises(ValueError):enemy_entry_sources('ro6_n_1_1','enemy_2152_shezlc',999)

    def test_165_main_sources(self):
        from rouge.battle_planning import enemy_entry_sources, action_catalog
        a=next(a for a in action_catalog('ro6_n_1_1')['actions'] if a['type']=='SPAWN')
        from rouge.battle_preview import battle_data
        e=next(e for e in battle_data()['stages']['ro6_n_1_1']['enemies'] if e['id']==a['action']['key'])
        r=enemy_entry_sources('ro6_n_1_1',e['id'],e['level'])
        self.assertTrue(any(s['id']==a['id'] for s in r['entry_sources']))

    def test_166_full_branch_phase(self):
        from rouge.battle_planning import branch_phase_catalog
        r=branch_phase_catalog('ro6_n_1_1')
        self.assertEqual({b['branch_id'] for b in r['branches']},{'shsbox1','shsbox2'})
        self.assertTrue(all(b['trigger_mechanism'] is None for b in r['branches']))
        self.assertEqual(len(branch_phase_catalog('ro6_n_1_1','shsbox1')['branches']),1)
        with self.assertRaises(ValueError):branch_phase_catalog('ro6_n_1_1','missing')

    def test_166_empty_and_nonspawn_preserved(self):
        from rouge.battle_planning import branch_phase_catalog
        from rouge.battle_preview import battle_data
        all_phases=[p for sid in battle_data()['stages'] for b in branch_phase_catalog(sid)['branches'] for p in b['phases']]
        self.assertTrue(any(a['action']['actionType']!='SPAWN' for p in all_phases for a in p['actions']))
        from unittest.mock import patch
        source=battle_data()['stages']['ro6_n_1_1']['level_source']
        synthetic={'stages':{'ro6_n_1_1':{'source':source,'branches':{'declared_empty':{'phases':[{'preDelay':3,'actions':[]}]}}}}}
        with patch('rouge.battle_planning._branch_data',return_value=synthetic):
            result=branch_phase_catalog('ro6_n_1_1')['branches'][0]
            self.assertTrue(result['phases'][0]['empty_configuration'])
            self.assertEqual(result['phases'][0]['pre_delay_parameter'],3)

    def test_167_discontinuous_route(self):
        from rouge.battle_planning import route_segments
        r=route_segments('ro6_n_1_3',10)
        self.assertGreater(len(r['segments']),1)
        self.assertTrue(any(t['kind']=='disappear' for t in r['transitions']))
        self.assertTrue(all(w['display_cell'] is None and w['arrival_seconds'] is None for w in r['waits']))
        self.assertIsNone(r['actual_path'])

    def test_167_endpoints_and_invalid_route(self):
        from rouge.battle_planning import route_segments
        r=route_segments('ro6_n_1_3',10)
        self.assertEqual(r['segments'][0][0]['kind'],'start')
        self.assertEqual(r['segments'][-1][-1]['kind'],'end')
        with self.assertRaises(ValueError):route_segments('ro6_n_1_3',True)

    def test_168_inverse_cell_reference(self):
        from rouge.battle_planning import cell_planning_references,route_segments
        cell=route_segments('ro6_n_1_3',10)['segments'][0][0]['cell']
        r=cell_planning_references('ro6_n_1_3',**cell)
        self.assertTrue(any(x['route_index']==10 for x in r['route_references']))
        self.assertIsNone(r['actual_occupants'])
        self.assertIn('tileKey',r['tile'])

    def test_168_cell_origin_and_bounds(self):
        from rouge.battle_planning import cell_planning_references
        from rouge.battle_preview import battle_data
        r=cell_planning_references('ro6_n_1_1',0,0)
        self.assertEqual(r['source_position']['row'],len(battle_data()['stages']['ro6_n_1_1']['map'])-1)
        with self.assertRaises(ValueError):cell_planning_references('ro6_n_1_1',-1,0)

    def test_169_mechanism_stage_override(self):
        from rouge.battle_planning import mechanism_provenance
        r=mechanism_provenance('ro6_n_1_1','enemy_2133_shdopl',0)
        self.assertEqual(r['records'][-1]['origin'],'stage_override')
        self.assertTrue(r['records'][-1]['fields']['talentBlackboard'])
        self.assertIsNone(r['effective_merged_mechanism'])

    def test_169_null_empty_zero_distinct(self):
        from rouge.battle_planning import _field_diff
        r=_field_diff({'s':None,'v':0,'a':[]},{'s':[],'v':None})
        self.assertEqual(next(x for x in r if x['path']=='$.s')['left']['state'],'null')
        self.assertEqual(next(x for x in r if x['path']=='$.s')['right']['state'],'empty_list')
        self.assertEqual(next(x for x in r if x['path']=='$.a')['right']['state'],'absent')
        self.assertTrue(_field_diff({'s':False},{'s':0}))
