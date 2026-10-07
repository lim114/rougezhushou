import copy
import unittest
from rouge.damage import calculate_damage

def evaluate(**extra):
    return calculate_damage({'operator':'char_1037_amiya3','skill':2,'base_attack':1000,**extra})

class AmiyaInputQualificationTests(unittest.TestCase):
    def test_zero_opening_count_is_outside_current_supported_scenario(self):
        for mode in ('frames','continuous'):
            with self.assertRaisesRegex(ValueError,'amiya_hit_targets'):
                evaluate(timing_mode=mode,amiya_hit_targets=0)

    def test_invalid_counts_are_rejected_before_producing_output(self):
        for count in (-1,.5,101,float('nan'),float('inf')):
            with self.subTest(count=count),self.assertRaises(ValueError):
                evaluate(amiya_hit_targets=count)

    def test_valid_counts_retain_existing_parameter_cap_and_unknown_phase(self):
        for mode in ('frames','continuous'):
            for count in (1,5,100):
                r=evaluate(timing_mode=mode,amiya_hit_targets=count)
                self.assertEqual(r['amiya_phase_reference']['declared_opening_hit_targets'],count)
                self.assertEqual(r['amiya_phase_reference']['strengthened_attack_reference'],1000+300*min(count,5))
                self.assertEqual(r['amiya_phase_reference']['opening_damage_reference'],2000)
                self.assertIsNone(r['total_damage'])
                self.assertIsNone(r['total_healing'])

    def test_empty_observation_does_not_require_a_zero_declared_count(self):
        for args in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}}):
            r=evaluate(amiya_hit_targets=1,**args)
            self.assertEqual((r['total_damage'],r['total_healing']),(0,0))
            self.assertEqual(r['amiya_phase_reference']['declared_opening_hit_targets'],1)

    def test_omitted_count_keeps_the_existing_default(self):
        self.assertEqual(evaluate(),evaluate(amiya_hit_targets=1))

    def test_validation_does_not_mutate_public_input(self):
        for count in (0,1,100):
            scenario={'operator':'char_1037_amiya3','skill':2,'amiya_hit_targets':count}
            before=copy.deepcopy(scenario)
            if count==0:
                with self.assertRaises(ValueError):calculate_damage(scenario)
            else:calculate_damage(scenario)
            self.assertEqual(scenario,before)
