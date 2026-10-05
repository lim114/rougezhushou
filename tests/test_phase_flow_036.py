"""Public request isolation and deployment clock behavior after reuse.

Native timer receipt: p1-native-runtime-054/timer-book-sniper-summary.json.
"""
import copy
import unittest
from concurrent.futures import ThreadPoolExecutor
from rouge.damage import calculate_damage

WINE='rogue_6_relic_legacy_95'
TARGET={'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0}


class PhaseFlowTests(unittest.TestCase):
    def scenario(self,**extra):
        return {'operator':'mechanist','skill':1,'relic_ids':[WINE],**extra}

    def test_input_and_repeated_results_remain_independent(self):
        s=self.scenario(target_enemy=TARGET.copy(),run_config={'difficulty':{'value':9}},
            char_buff_ids=['rogue_6_from_relic_9'],timing={'initial_target_windows':[[0,30]]})
        before=copy.deepcopy(s)
        first=calculate_damage(s);saved=copy.deepcopy(first)
        self.assertEqual(calculate_damage(s),saved)
        self.assertEqual(first,saved)
        self.assertEqual(s,before)

    def test_one_request_does_not_retain_another_recipients_buff(self):
        s=self.scenario();baseline=calculate_damage(s)
        enhanced=calculate_damage({**s,'char_buff_ids':['rogue_6_from_relic_9']})
        self.assertEqual(enhanced['estimate']['base_stats']['attack_speed'],150)
        self.assertEqual(calculate_damage(s),baseline)
        self.assertEqual(baseline['estimate']['base_stats']['attack_speed'],100)

    def test_cultivation_changes_invalidate_preparation_between_requests(self):
        s=self.scenario(elite=1,skill_rank=7,level=40,potential=1,trust=0)
        low=calculate_damage(s)
        high=calculate_damage({**s,'level':80,'potential':6,'trust':100})
        self.assertGreater(high['estimate']['base_stats']['attack'],low['estimate']['base_stats']['attack'])
        self.assertNotEqual(high['deployment_cost'],low['deployment_cost'])
        self.assertEqual(calculate_damage(s),low)

    def test_run_environment_is_fresh_and_not_repeatedly_multiplied(self):
        s=self.scenario(target_enemy=TARGET.copy(),run_config={'difficulty':{'value':0}},
            relic_ids=[WINE,'rogue_6_start_4','rogue_6_relic_fight_25'])
        first=calculate_damage(s)
        harder=calculate_damage({**s,'run_config':{'difficulty':{'value':15}}})
        self.assertGreater(harder['run_resolution']['enemy']['stats']['maxHp'],
                           first['run_resolution']['enemy']['stats']['maxHp'])
        self.assertEqual(calculate_damage(s),first)
        self.assertNotIn('phase_estimate',first['relic_resolution'])
        self.assertEqual(first['deployment_clock_reference']['origin'],'deployment')
        self.assertFalse(first['deployment_clock_reference']['live_state_verified'])

    def test_returned_result_mutation_does_not_poison_later_requests(self):
        s=self.scenario();expected=calculate_damage(s);result=calculate_damage(s)
        result['relic_resolution']['rules'][0]['value']=999
        result['estimate']['notes'].append('external mutation')
        result['estimate']['base_stats']['attack']=0
        self.assertEqual(calculate_damage(s),expected)

    def test_explicit_lockout_and_supply_windows_are_not_reused_as_history(self):
        s=self.scenario();baseline=calculate_damage(s)
        absent=calculate_damage({**s,'timing':{'target_windows':[],'initial_target_windows':[],
                                            'sp_lockout_extra_seconds':2}})
        self.assertEqual(absent['estimate']['skill']['total_damage'],0)
        self.assertIsNone(absent['estimate']['skill']['cycle_seconds'])
        self.assertNotIn('cycle_seconds_range',absent['estimate']['skill'])
        blocked=calculate_damage({**s,'timing':{'sp_lockout_extra_seconds':2}})
        self.assertAlmostEqual(blocked['estimate']['skill']['cycle_seconds']-
                               baseline['estimate']['skill']['cycle_seconds'],2)
        self.assertEqual(blocked['estimate']['skill']['initial_seconds'],
                         baseline['estimate']['skill']['initial_seconds'])
        self.assertEqual(calculate_damage(s),baseline)

    def test_multiple_verified_wines_keep_independent_timers_and_birth_additions(self):
        r=calculate_damage(self.scenario(relic_ids=[WINE,'rogue_6_relic_legacy_97']))
        self.assertNotIn('phase_estimate',r['relic_resolution'])
        self.assertEqual(r['estimate']['skill']['initial_sp'],7)
        self.assertEqual(r['estimate']['skill']['initial_seconds'],0)
        self.assertEqual(sorted(x['interval'] for x in r['relic_resolution']['rules']
                                if x['kind']=='periodic_sp'),[1.5,3])
        self.assertTrue(r['relic_resolution']['complete'])
        self.assertIsNotNone(r['estimate']['skill']['cycle_seconds'])

    def test_verified_wine_clock_does_not_replace_unknown_neural_lifecycle(self):
        r=calculate_damage({'operator':'char_1042_phatm2','skill':3,'relic_ids':[WINE],
                           'initial_neural_buildup':1000})
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_dps'])
        self.assertNotIn('cycle_damage_range',r['estimate']['skill'])
        self.assertTrue(r['known_damage_subtotals'])

    def test_parallel_requests_have_independent_preparations(self):
        scenarios=[self.scenario(),self.scenario(char_buff_ids=['rogue_6_from_relic_9']),
                   self.scenario(timing={'initial_target_windows':[]}),
                   self.scenario(target_enemy=TARGET.copy(),run_config={'difficulty':{'value':12}})]
        expected=[calculate_damage(s) for s in scenarios]
        with ThreadPoolExecutor(max_workers=2) as executor:
            actual=list(executor.map(calculate_damage,scenarios))
        self.assertEqual(actual,expected)


if __name__=='__main__':unittest.main()
