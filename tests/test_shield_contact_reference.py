import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator':'char_1044_hsgma2','skill':2,'base_attack':1000,**extra})


class ShieldContactReferenceTests(unittest.TestCase):
    def test_zero_window_excludes_damage_and_its_healing_in_both_modes(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,window_seconds=0)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['total_healing'],0)
            self.assertEqual(r['estimate']['skill']['window_seconds'],0)

    def test_no_current_target_has_no_actual_contact_or_damage_based_healing(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,timing={'target_disappears_seconds':0},shield_contact_ticks=3)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['total_healing'],0)

    def test_owner_range_does_not_cancel_independent_contact_reference(self):
        r=evaluate(timing={'target_windows':[]},shield_contact_ticks=1)
        refs={c['name']:c for c in r['unbound_cast_reference']['conditional_components']}
        self.assertEqual(refs['环绕盾牌']['total'],1300)
        self.assertEqual(refs['盾牌伤害转治疗']['total'],195)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['total_healing'])

    def test_positive_window_is_preserved_without_a_fabricated_circle_duration(self):
        r=evaluate(window_seconds=1)
        self.assertEqual(r['estimate']['skill']['window_seconds'],1)
        for key in ('duration_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertIsNone(r['unbound_cast_reference']['actual_end_seconds'])

    def test_contact_counts_only_change_conditional_sources(self):
        for count in (0,1,3):
            r=evaluate(shield_contact_ticks=count)
            refs={c['name']:c for c in r['unbound_cast_reference']['conditional_components']}
            self.assertEqual(refs['盾击三连']['total'],2700)
            self.assertEqual(refs['环绕盾牌']['total'],1300*count)
            self.assertEqual(refs['盾牌伤害转治疗']['total'],195*count)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['total_healing']) if count else self.assertEqual(r['total_healing'],0)
            self.assertEqual(r['unbound_cast_reference']['parameter_rows'][1][1],.5)

    def test_healing_depends_on_adjusted_contact_damage(self):
        r=evaluate(enemy_resistance=50,shield_contact_ticks=2)
        refs={c['name']:c for c in r['unbound_cast_reference']['conditional_components']}
        self.assertEqual(refs['环绕盾牌']['total'],1300)
        self.assertEqual(refs['盾牌伤害转治疗']['total'],195)
        self.assertEqual(r['known_healing_subtotals']['window_healing'],0)

    def test_no_unverified_component_has_actual_hit_time_or_count(self):
        r=evaluate()
        for c in r['components']:
            self.assertNotIn('times_seconds',c)
            self.assertNotIn('instant_event',c)
            self.assertIsNone(c['actual_total'])
            self.assertIsNone(r['estimate']['skill']['hit_counts'][c['name']])

    def test_report_shows_both_unknown_damage_and_healing(self):
        text=format_estimate(evaluate(window_seconds=1))
        self.assertIn('多段技能 · 实际时钟待核验',text)
        self.assertIn('观察窗口总伤：未知',text)
        self.assertIn('观察窗口治疗：未知',text)
        self.assertIn('接触判定间隔参数：0.50',text)


if __name__=='__main__':unittest.main()
