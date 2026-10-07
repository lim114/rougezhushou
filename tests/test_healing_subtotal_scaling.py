import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill=1,**extra):
    return calculate_damage({'operator':'char_4202_haruka','skill':skill,'base_attack':1000,'bubble_bursts':1,**extra})


class HealingSubtotalScalingTests(unittest.TestCase):
    def test_known_body_matches_healing_component_after_each_accepted_relic(self):
        for relic in ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):
            r=evaluate(relic_ids=[relic]);body=next(c for c in r['components'] if c['name']=='护佑者普通治疗')
            self.assertEqual(r['known_healing_subtotals']['window_healing'],body['total'])
            self.assertIsNone(r['total_healing'])
            self.assertIsNone(r['estimate']['skill']['window_healing'])

    def test_full_phase_and_cycle_preserve_existing_scalar_arithmetic(self):
        baseline=evaluate();r=evaluate(relic_ids=['rogue_6_relic_legacy_81'])
        for key,number in baseline['known_healing_subtotals'].items():
            if number is None:self.assertIsNone(r['known_healing_subtotals'][key])
            else:self.assertAlmostEqual(r['known_healing_subtotals'][key],number*1.2)
        for key in ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps'):
            self.assertIsNone(r['estimate']['skill'][key])

    def test_repeat_cast_does_not_turn_unknown_full_subtotal_into_number(self):
        r=evaluate(2,haruka_repeat=True,window_seconds=1,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertIsNone(r['known_healing_subtotals']['total_healing'])
        self.assertIsNone(r['total_healing'])

    def test_known_zero_and_empty_observation_remain_numerical_zero(self):
        r=evaluate(window_seconds=0,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertEqual(r['total_healing'],0)
        self.assertEqual(r['estimate']['skill']['window_healing'],0)
        r=calculate_damage({'operator':'char_437_mizuki','skill':2,'base_attack':1000,'elite':2,'level':60,'module_id':'uniequip_003_mizuki','module_level':2,'relic_ids':['rogue_6_relic_legacy_81']})
        self.assertEqual(r['known_healing_subtotals']['window_healing'],0)
        self.assertIsNone(r['total_healing'])

    def test_regular_healing_without_pending_events_retains_output(self):
        baseline=evaluate(bubble_bursts=0);r=evaluate(bubble_bursts=0,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertAlmostEqual(r['total_healing'],baseline['total_healing']*1.2)
        self.assertNotIn('known_healing_subtotals',r)

    def test_public_report_prints_scaled_subtotal_and_unknown_total(self):
        text=format_estimate(evaluate(relic_ids=['rogue_6_relic_legacy_81']))
        self.assertIn('观察窗口已计治疗小计：17,100',text)
        self.assertIn('单次技能总治疗：未知',text)


if __name__=='__main__':unittest.main()
