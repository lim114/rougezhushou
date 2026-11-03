import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_1048_orchd2','skill':skill,'base_attack':1000,**extra})


def sources(result):
    return {c['name']:c for c in result['unbound_cast_reference']['conditional_components']}


class OrchidArrowReferenceTests(unittest.TestCase):
    def test_all_skills_keep_zero_short_and_long_observation_windows(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for window in (0,1,10):
                    r=evaluate(skill,timing_mode=mode,window_seconds=window)
                    self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                    self.assertEqual(r['total_damage'],0) if window==0 else self.assertIsNone(r['total_damage'])

    def test_global_zero_lifetime_excludes_current_target_damage(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,timing={'target_disappears_seconds':0})
                self.assertEqual(r['total_damage'],0)
                self.assertFalse(r['unbound_cast_reference']['source_possible'])

    def test_owner_acquisition_does_not_define_independent_projectile_coverage(self):
        for skill in (1,2,3):
            for timing in ({'target_windows':[]},{'target_windows':[[5,10]]}):
                r=evaluate(skill,timing=timing,window_seconds=10)
                self.assertIsNone(r['total_damage'])
                self.assertTrue(r['unbound_cast_reference']['source_possible'])

    def test_s1_extra_charge_selects_only_sourced_conditional_arrow_counts(self):
        single=sources(evaluate(1,double_charge=False));double=sources(evaluate(1))
        self.assertEqual(single['刚射']['hits'],4)
        self.assertNotIn('刚连射',single)
        self.assertEqual(double['刚连射']['hits'],5)
        self.assertEqual(sum(c['total'] for c in double.values()),18860)

    def test_s2_arrows_and_landing_are_separate_parameters_without_instant_marker(self):
        r=evaluate(2);ref=sources(r)
        self.assertEqual(ref['飞翔瞪射箭矢']['hits'],12)
        self.assertEqual(ref['飞翔瞪射落地']['hits'],1)
        self.assertEqual(sum(c['total'] for c in ref.values()),28290)
        parameters=r['unbound_cast_reference']['parameter_rows']
        self.assertEqual(parameters[1][1],4.2)
        for c in r['components']:
            self.assertNotIn('instant_event',c)
            self.assertNotIn('times_seconds',c)
            self.assertIsNone(c['actual_total'])

    def test_s3_count_zero_or_multiple_and_mitigation_retain_conditional_values(self):
        self.assertEqual(evaluate(3,dragon_arrow_hits=0)['total_damage'],0)
        for count in (1,3):
            r=evaluate(3,dragon_arrow_hits=count,enemy_defense=100,enemy_resistance=50)
            ref=sources(r)
            self.assertAlmostEqual(ref['龙之箭物理']['total'],(4140-100)*count)
            self.assertAlmostEqual(ref['龙之箭法术']['total'],345*count)
            self.assertIsNone(r['total_damage'])

    def test_all_skills_have_unknown_actual_end_and_complete_cycle(self):
        for skill in (1,2,3):
            r=evaluate(skill)
            for key in ('duration_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage'):
                self.assertIsNone(r['estimate']['skill'][key])
            self.assertIsNone(r['unbound_cast_reference']['actual_hit_times_seconds'])
            self.assertIsNone(r['unbound_cast_reference']['actual_end_seconds'])

    def test_report_keeps_charge_and_wait_parameters_without_inventing_release_at_three(self):
        text=format_estimate(evaluate(3,window_seconds=1))
        self.assertIn('描述蓄力时长参数：3.00',text)
        self.assertIn('原表等待参数：1.50',text)
        self.assertIn('实际命中时刻：未知',text)
        self.assertIn('伤害观察窗口：1.00',text)


if __name__=='__main__':unittest.main()
