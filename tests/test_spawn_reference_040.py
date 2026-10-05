import copy,json,math,unittest
from pathlib import Path
from rouge.spawn_reference import local_sequence,ordinal_offset,movement_reference,sequence_text
from rouge.battle_preview import battle_data,spawn_rows,enemy_preview,enemy_text

ROOT=Path(__file__).resolve().parents[1]

def row(count=7,delay=10,interval=15,**flags):
    return {'branch':None,'wave':2,'fragment':1,
        'action':{'count':count,'preDelay':delay,'interval':interval,**flags}}

class LocalSpawnReferenceTests(unittest.TestCase):
    def test_source_example_per_instance(self):
        actual=next(r for r in spawn_rows('ro6_n_1_2') if r['action']['key']=='enemy_1093_ccsbr')
        seq=local_sequence(actual)
        self.assertEqual([x['offset_seconds'] for x in seq['occurrences']],[10,25,40,55,70,85,100])
        self.assertEqual(seq['anchor'],'fragment_action_queue_start')
        self.assertIsNone(actual['absolute_time'])

    def test_decimal_offsets_do_not_accumulate_error(self):
        result=local_sequence(row(count=4,delay=.1,interval=.1))
        self.assertEqual([x['offset_seconds'] for x in result['occurrences']],[.1,.2,.3,.4])
        self.assertEqual(ordinal_offset(row(count=4,delay=.1,interval=.1),3),.3)

    def test_fragment_predelay_not_added_twice(self):
        r=row();r['fragment_pre_delay']=50;r['wave_pre_delay']=100
        self.assertEqual(local_sequence(r)['first_offset'],10)
        self.assertIn('锚点已在片段/阶段开始前延迟之后',sequence_text(r))

    def test_different_fragments_have_independent_anchors(self):
        first=row();second=row();second['fragment']=7
        self.assertEqual(local_sequence(first)['first_offset'],local_sequence(second)['first_offset'])
        self.assertFalse(local_sequence(second)['global_times_verified'])

    def test_branch_phase_not_assumed_triggered(self):
        r=row(count=2,delay=2,interval=3);r.update(branch='branchA',phase=3,phase_pre_delay=13)
        seq=local_sequence(r)
        self.assertEqual(seq['anchor'],'branch_phase_action_queue_start')
        self.assertEqual(seq['last_offset'],5);self.assertTrue(seq['conditional'])
        self.assertIn('实际启用/入选',sequence_text(r))

    def test_condition_and_random_not_guaranteed(self):
        for flags in ({'hiddenGroup':'raid'},{'randomSpawnGroupKey':'r'},
                      {'randomSpawnGroupPackKey':'p'}):
            self.assertTrue(local_sequence(row(**flags))['conditional'])
        self.assertFalse(local_sequence(row())['conditional'])

    def test_missing_fields_remain_unknown(self):
        for key in ('count','preDelay','interval'):
            r=row();r['action'].pop(key)
            self.assertTrue(local_sequence(r)['pending'])
            self.assertIsNone(ordinal_offset(r,1))

    def test_bad_counts_do_not_default_one(self):
        for n in (-1,True,2.2,'3',None,1000001):
            self.assertTrue(local_sequence(row(count=n))['pending'])

    def test_zero_count_has_no_instances(self):
        seq=local_sequence(row(count=0));self.assertFalse(seq['pending'])
        self.assertEqual(seq['occurrences'],[]);self.assertIsNone(seq['first_offset'])
        self.assertIsNone(ordinal_offset(row(count=0),1))

    def test_bad_time_values_are_not_zeroed(self):
        for value in (-1,True,'1',None,float('nan'),float('inf'),10**500):
            for r in (row(delay=value),row(interval=value)):
                self.assertTrue(local_sequence(r)['pending'])
                self.assertIsNone(local_sequence(r)['first_offset'])

    def test_zero_interval_keeps_each_ordinal(self):
        seq=local_sequence(row(count=3,delay=2,interval=0))
        self.assertEqual(seq['occurrences'],[{'ordinal':i,'offset_seconds':2} for i in (1,2,3)])
        self.assertFalse(seq['frame_execution_verified'])

    def test_single_count_does_not_add_interval(self):
        self.assertEqual(local_sequence(row(count=1,delay=4,interval=999))['last_offset'],4)

    def test_bounded_sequence_and_direct_last_selection(self):
        r=row(count=1000000,delay=.5,interval=.25);seq=local_sequence(r,limit=3)
        self.assertEqual(len(seq['occurrences']),3);self.assertTrue(seq['truncated'])
        self.assertEqual(seq['last_offset'],250000.25)
        self.assertEqual(ordinal_offset(r,1000000),250000.25)

    def test_invalid_display_limit_rejected(self):
        for value in (-1,4097,True,2.5):
            with self.assertRaises(ValueError):local_sequence(row(),value)

    def test_bad_ordinals_do_not_wrap_or_clamp(self):
        for value in (0,-1,8,True,None,2.5):self.assertIsNone(ordinal_offset(row(),value))

    def test_overflow_offsets_not_reported_finite(self):
        seq=local_sequence(row(count=20,delay=1e308,interval=1e308))
        self.assertTrue(seq['pending']);self.assertEqual(seq['occurrences'],[])

    def test_actual_times_remain_unverified(self):
        seq=local_sequence(row())
        for key in ('global_times_verified','visible_entry_times_verified','frame_execution_verified'):
            self.assertFalse(seq[key])
        self.assertIn('名义偏移不是开局绝对时刻',sequence_text(row()))

    def test_all_raw_count_instances_and_times_preserved(self):
        counts={'main':0,'branch':0};rows=0
        for sid in battle_data()['stages']:
            for r in spawn_rows(sid):
                seq=local_sequence(r);self.assertFalse(seq['pending'],(sid,r['id']))
                self.assertEqual(len(seq['occurrences']),r['action']['count'])
                self.assertIsNone(r['absolute_time']);self.assertIsNone(r['probability'])
                counts['branch' if r['branch'] else 'main']+=len(seq['occurrences']);rows+=1
        self.assertEqual(rows,3938);self.assertEqual(counts,{'main':5314,'branch':334})

    def test_sequence_input_not_mutated(self):
        r=row();before=copy.deepcopy(r);local_sequence(r);ordinal_offset(r,4);sequence_text(r)
        self.assertEqual(r,before)

class MovementReferenceTests(unittest.TestCase):
    def test_known_base_multiplier_and_panel(self):
        e=enemy_preview('ro6_n_1_2','enemy_1093_ccsbr',0)
        self.assertEqual(e['reference_stats']['moveSpeed'],.8)
        self.assertEqual(e['movement_reference']['stage_multiplier'],.5)
        self.assertEqual(e['movement_reference']['base_times_stage_speed'],.4)
        text=enemy_text(e)
        self.assertNotIn('基础移速属性',text)
        self.assertNotIn('速度参考（格/秒）',text)
        self.assertIn('预计有效移速：未知',text)

    def test_unknown_multiplier_not_assumed_half(self):
        self.assertIsNone(movement_reference({},.8)['base_times_stage_speed'])

    def test_bad_speed_or_multiplier_not_assumed_zero(self):
        for value in (None,True,-1,float('inf'),float('nan'),'0.5',10**500):
            self.assertIsNone(movement_reference({'movement_multiplier':.5},value)['base_times_stage_speed'])
            self.assertIsNone(movement_reference({'movement_multiplier':value},.8)['base_times_stage_speed'])

    def test_zero_speed_explicit_valid(self):
        self.assertEqual(movement_reference({'movement_multiplier':.5},0)['base_times_stage_speed'],0)

    def test_effective_speed_not_claimed_verified(self):
        r=movement_reference({'movement_multiplier':.5},.8)
        self.assertFalse(r['complete_effective_speed_verified'])

    def test_all_options_and_extra_routes_match_pinned_levels(self):
        from rouge.catalog import catalog
        for sid,s in battle_data()['stages'].items():
            p=ROOT/'.cache/game-data/levels'/(catalog()['stages'][sid]['levelId'].lower()+'.json')
            raw=json.loads(p.read_text(encoding='utf-8'))
            self.assertEqual(s['movement_multiplier'],raw['options'].get('moveMultiplier'))
            self.assertEqual(s['extra_routes'],raw.get('extraRoutes') or [])

    def test_missing_selector_does_not_map_branch(self):
        for sid in battle_data()['stages']:
            for r in spawn_rows(sid):
                if r['branch']:
                    self.assertNotIn('useExtraRoute',r['action'])
                    self.assertIsNone(r['route']['start'])
                    self.assertIn('useExtraRoute',r['route']['pending'][0])

if __name__=='__main__':unittest.main()
