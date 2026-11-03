import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_2027_wang','skill':skill,'base_attack':1000,**extra})


class WangPassiveReferenceTests(unittest.TestCase):
    def test_all_skills_keep_declared_zero_and_short_window(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for window in (0,1):
                    r=evaluate(skill,timing_mode=mode,window_seconds=window,skill_duration_seconds=10)
                    self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                    self.assertEqual(r['total_damage'],0) if window==0 else self.assertIsNone(r['total_damage'])

    def test_passive_damage_is_not_active_stone_acquisition_damage(self):
        for skill in (1,2):
            r=evaluate(skill)
            self.assertEqual(r['estimate']['skill']['total_damage'],0)
            self.assertEqual(r['active_resource_reference']['direct_enemy_damage'],0)
            self.assertEqual(r['active_resource_reference']['granted_stones_parameter'],2)
            self.assertFalse(r['active_resource_reference']['passive_event_attribution_verified'])
            self.assertIsNone(r['total_damage'])

    def test_zero_current_target_lifetime_excludes_passive_damage_in_both_modes(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,timing={'target_disappears_seconds':0})
                self.assertEqual(r['total_damage'],0)
                self.assertFalse(r['unbound_cast_reference']['source_possible'])

    def test_body_range_does_not_bind_trap_coverage(self):
        for skill in (1,2,3):
            r=evaluate(skill,timing={'target_windows':[]},window_seconds=1)
            self.assertIsNone(r['total_damage'])
            self.assertTrue(r['unbound_cast_reference']['source_possible'])

    def test_s1_tick_declaration_is_only_a_conditional_count(self):
        for ticks in (0,6,7):
            r=evaluate(1,trap_dot_ticks=ticks,trap_triggers=2)
            ref=r['unbound_cast_reference']['conditional_components'][0]
            self.assertAlmostEqual(ref['total'],1485*2*ticks)
            self.assertEqual(r['total_damage'],0) if ticks==0 else self.assertIsNone(r['total_damage'])
            self.assertIn(('持续伤害时长参数',6.5,'秒'),r['unbound_cast_reference']['parameter_rows'])
            self.assertNotIn('times_seconds',r['components'][0])

    def test_s2_s3_counts_only_change_retained_conditional_sources(self):
        for skill,per in ((2,6380),(3,4180)):
            for count in (0,1,3):
                r=evaluate(skill,trap_triggers=count)
                self.assertAlmostEqual(r['unbound_cast_reference']['conditional_components'][0]['total'],per*count)
                self.assertEqual(r['total_damage'],0) if count==0 else self.assertIsNone(r['total_damage'])

    def test_s3_keeps_unknown_complete_ammo_output_and_lifecycle(self):
        r=evaluate(3,skill_duration_seconds=10)
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['duration_seconds'])
        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])
        self.assertEqual(r['active_resource_reference']['granted_stones_parameter'],8)
        self.assertIsNone(r['unbound_cast_reference']['actual_end_seconds'])
        self.assertIsNone(r['known_damage_subtotals']['total_damage'])

    def test_line_and_resistance_parameters_remain_conditional(self):
        r=evaluate(2,connected_stones=3,enemy_resistance=50)
        # Original E2 talent: line factor1.3, resistance penetration3*9 leaves23.
        conditional=r['unbound_cast_reference']['conditional_components'][0]['total']
        self.assertAlmostEqual(conditional,5800*1.3*.77)
        self.assertIsNone(r['total_damage'])

    def test_report_explains_active_passive_separation_and_unknown_hits(self):
        text=format_estimate(evaluate(1,window_seconds=1))
        self.assertIn('主动获得棋子不产生对敌直接伤害',text)
        self.assertIn('实际命中时刻：未知',text)
        self.assertIn('单次技能总伤：0',text)
        self.assertIn('观察窗口总伤：未知',text)
        self.assertIn('伤害观察窗口：1.00',text)


if __name__=='__main__':unittest.main()
