"""Pinned recipient qualification must cover both skill and recharge healing."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP='char_298_susuro'

def evaluate(skill=1, **extra):
    return calculate_damage({'operator':OP,'skill':skill,'base_attack':1000,**extra})

class SusuroRecipientFactorTests(unittest.TestCase):
    def test_public_worked_skill_and_recharge_totals_share_recipient_factor(self):
        expected={('frames',1):(18360,31560),('continuous',1):(16320,28320),
                  ('frames',2):(50400,57600),('continuous',2):(50400,56400)}
        for (mode,skill),(total,cycle) in expected.items():
            r=evaluate(skill,timing_mode=mode,low_cost_healing_target=True)
            self.assertEqual(r['estimate']['skill']['total_healing'],total)
            self.assertEqual(r['estimate']['skill']['cycle_healing'],cycle)
            self.assertEqual(r['total_damage'],0)

    def test_unlocked_phase_and_potential_source_factors_apply_to_whole_reference_cycle(self):
        for elite,potential,rank,factor in ((1,1,7,1.1),(1,4,7,1.1),(1,5,7,1.13),(2,1,10,1.2),(2,4,10,1.2),(2,5,10,1.23)):
            for mode in ('frames','continuous'):
                for skill in (1,2):
                    base={'elite':elite,'potential':potential,'skill_rank':rank,'timing_mode':mode}
                    plain=evaluate(skill,**base,low_cost_healing_target=False)
                    qualified=evaluate(skill,**base,low_cost_healing_target=True)
                    a,b=plain['estimate']['skill'],qualified['estimate']['skill']
                    self.assertAlmostEqual(b['total_healing'],a['total_healing']*factor)
                    self.assertAlmostEqual(b['cycle_healing'],a['cycle_healing']*factor)
                    self.assertAlmostEqual(b['cycle_hps'],a['cycle_hps']*factor)

    def test_e0_has_no_unlocked_recipient_talent(self):
        for mode in ('frames','continuous'):
            plain=evaluate(elite=0,skill_rank=1,timing_mode=mode,low_cost_healing_target=False)
            qualified=evaluate(elite=0,skill_rank=1,timing_mode=mode,low_cost_healing_target=True)
            self.assertEqual(plain['estimate']['skill'],qualified['estimate']['skill'])
            self.assertEqual(plain['components'],qualified['components'])

    def test_same_identity_module_override_replaces_base_factor_without_multiplying_it(self):
        for stage,potential,factor in ((1,1,1.2),(1,4,1.2),(1,5,1.23),(2,1,1.23),(2,4,1.23),(2,5,1.26),(3,1,1.25),(3,4,1.25),(3,5,1.28)):
            for mode in ('frames','continuous'):
                base={'module_id':'uniequip_002_susuro','module_level':stage,'potential':potential,'timing_mode':mode}
                a=evaluate(**base,low_cost_healing_target=False)['estimate']['skill']
                b=evaluate(**base,low_cost_healing_target=True)['estimate']['skill']
                self.assertAlmostEqual(b['total_healing'],a['total_healing']*factor)
                self.assertAlmostEqual(b['cycle_healing'],a['cycle_healing']*factor)
        a=evaluate(module_id='uniequip_002_susuro',module_level=3,level=39,low_cost_healing_target=False)['estimate']['skill']
        b=evaluate(module_id='uniequip_002_susuro',module_level=3,level=39,low_cost_healing_target=True)['estimate']['skill']
        self.assertAlmostEqual(b['cycle_healing'],a['cycle_healing']*1.2)

    def test_zero_recipients_and_single_target_cap_remain(self):
        for skill in (1,2):
            for mode in ('frames','continuous'):
                zero=evaluate(skill,timing_mode=mode,low_cost_healing_target=True,healing_targets=0)
                self.assertEqual(zero['total_healing'],0)
                self.assertEqual(zero['estimate']['skill']['cycle_healing'],0)
                one=evaluate(skill,timing_mode=mode,low_cost_healing_target=True,healing_targets=1)
                many=evaluate(skill,timing_mode=mode,low_cost_healing_target=True,healing_targets=100)
                self.assertEqual(one['estimate']['skill'],many['estimate']['skill'])

    def test_qualification_does_not_change_attack_events_or_natural_sp_clocks(self):
        for skill in (1,2):
            for mode in ('frames','continuous'):
                for timing in ({},{'target_disappears_seconds':0},{'target_windows':[]},
                               {'projectile_travel_seconds':100}):
                    args={'timing_mode':mode,'timing':timing}
                    plain=evaluate(skill,**args,low_cost_healing_target=False)
                    qualified=evaluate(skill,**args,low_cost_healing_target=True)
                    self.assertEqual(plain['timing'],qualified['timing'])
                    for key in ('mode','initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second','hit_counts'):
                        self.assertEqual(plain['estimate']['skill'][key],qualified['estimate']['skill'][key])
                late=evaluate(skill,timing_mode='frames',low_cost_healing_target=True,
                    timing={'windup_frames':0,'recovery_frames':0,'projectile_travel_seconds':100})
                self.assertGreater(late['estimate']['skill']['total_healing'],0)
                self.assertEqual(late['estimate']['skill']['cycle_healing'],0)

    def test_existing_final_healing_factor_path_applies_once_to_reference(self):
        r=evaluate(low_cost_healing_target=True,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertEqual(r['estimate']['skill']['total_healing'],22032)
        self.assertEqual(r['estimate']['skill']['cycle_healing'],37872)
        baseline=evaluate(low_cost_healing_target=False,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertAlmostEqual(r['estimate']['skill']['cycle_healing'],baseline['estimate']['skill']['cycle_healing']*1.2)

    def test_skill_two_cast_limit_and_nonrepeat_reference_stay(self):
        r=evaluate(2,low_cost_healing_target=True,casts_used=1)
        self.assertEqual(r['estimate']['skill']['total_healing'],50400)
        self.assertIsNone(r['estimate']['skill']['cycle_healing'])
        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])
        with self.assertRaises(ValueError):evaluate(2,low_cost_healing_target=True,casts_used=2)

    def test_empty_observation_zero_and_friendly_acquisition_limit_are_preserved(self):
        r=evaluate(low_cost_healing_target=True,window_seconds=0)
        self.assertEqual(r['total_healing'],0)
        text=format_estimate(evaluate(low_cost_healing_target=True,timing={'target_disappears_seconds':0}))
        self.assertIn('真实友方获取时钟未核验',text)

    def test_public_input_is_not_mutated_and_returned_reference_is_independent(self):
        scenario={'operator':OP,'skill':1,'base_attack':1000,'low_cost_healing_target':True,
                  'timing':{'target_windows':[]},'relic_ids':['rogue_6_relic_legacy_81']}
        before=copy.deepcopy(scenario);expected=calculate_damage(scenario);altered=calculate_damage(scenario)
        altered['timing']['recharge_streams'].clear()
        self.assertEqual(calculate_damage(scenario),expected)
        self.assertEqual(scenario,before)

if __name__=='__main__':unittest.main()
