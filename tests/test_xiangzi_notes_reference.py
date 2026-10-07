import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator':'char_4182_oblvns','skill':1,'base_attack':1000,**extra})


class XiangziNotesReferenceTests(unittest.TestCase):
    def test_zero_and_short_observation_keep_requested_horizon(self):
        for mode in ('frames','continuous'):
            for window in (0,1,5):
                r=evaluate(timing_mode=mode,window_seconds=window)
                self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                self.assertEqual(r['total_damage'],0) if window==0 else self.assertIsNone(r['total_damage'])

    def test_global_empty_target_lifetime_has_known_zero_damage(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,timing={'target_disappears_seconds':0})
            self.assertEqual(r['total_damage'],0)
            self.assertFalse(r['unbound_cast_reference']['source_possible'])

    def test_owner_range_and_interrupts_do_not_bind_note_collisions(self):
        for timing in ({'target_windows':[]},{'interruptions':[[0,100]]},{'target_windows':[[5,10]]}):
            r=evaluate(timing=timing,window_seconds=10)
            self.assertIsNone(r['total_damage'])
            self.assertTrue(r['unbound_cast_reference']['source_possible'])

    def test_all_eight_source_multipliers_are_retained(self):
        r=evaluate()
        sources=r['unbound_cast_reference']['conditional_components']
        self.assertEqual(len(sources),8)
        self.assertEqual([c['per_hit'] for c in sources],[800,736,600,464,336,264,136,40])
        self.assertEqual(sum(c['total'] for c in sources),3376)
        self.assertEqual(r['unbound_cast_reference']['parameter_rows'][1][1],2)
        for c in r['components']:
            self.assertNotIn('times_seconds',c)
            self.assertNotIn('instant_event',c)
            self.assertIsNone(c['actual_total'])
            self.assertIsNone(r['estimate']['skill']['hit_counts'][c['name']])

    def test_lifecycle_and_complete_cycle_stay_unknown(self):
        r=evaluate()
        for key in ('duration_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertIsNone(r['unbound_cast_reference']['actual_hit_times_seconds'])
        self.assertIsNone(r['unbound_cast_reference']['actual_end_seconds'])
        self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)

    def test_zero_window_does_not_erase_counterfactual_parameters(self):
        r=evaluate(window_seconds=0)
        self.assertEqual(sum(c['total'] for c in r['unbound_cast_reference']['conditional_components']),3376)
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['window_dps'],None)

    def test_damage_mitigation_and_declared_note_conditions_still_apply(self):
        r=evaluate(enemy_resistance=50,ranged_attack=False)
        self.assertEqual(sum(c['total'] for c in r['unbound_cast_reference']['conditional_components']),2110)
        self.assertIsNone(r['total_damage'])

    def test_report_distinguishes_conditional_parameters_from_actual_output(self):
        text=format_estimate(evaluate(window_seconds=1))
        self.assertIn('多段技能 · 实际时钟待核验',text)
        self.assertIn('实际命中时刻：未知',text)
        self.assertIn('伤害观察窗口：1',text)
        self.assertIn('单次技能总伤：未知',text)


if __name__=='__main__':unittest.main()
