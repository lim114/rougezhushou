import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP='char_1042_phatm2'


def evaluate(**extra):
    return calculate_damage({'operator':OP,'skill':2,'base_attack':1000,**extra})


class NeuralIncomingClockTests(unittest.TestCase):
    def test_count_cannot_invent_burst_times_without_any_operator_hits(self):
        for skill in (1,2,3):
            with self.subTest(skill=skill):
                r=evaluate(skill=skill,enemy_attack_count=20,timing={'target_windows':[]})
                self.assertIsNone(r['total_damage'])
                self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
                self.assertFalse(any(c['name']=='神经损伤爆发' for c in r['components']))
                self.assertIsNone(r['neural_incoming_reference']['attack_times_seconds'])
                self.assertFalse(r['neural_incoming_reference']['events_scheduled'])

    def test_varying_window_does_not_redistribute_a_count_into_events(self):
        for window in (.1,1,30,60):
            r=evaluate(enemy_attack_count=20,window_seconds=window)
            self.assertIsNone(r['total_damage'])
            arts=sum(c['total'] for c in r['components'] if c['damage_type']=='magic')
            self.assertEqual(r['known_damage_subtotals']['window_damage'],arts)

    def test_zero_count_preserves_complete_result(self):
        self.assertEqual(evaluate(),evaluate(enemy_attack_count=0))

    def test_zero_window_keeps_known_zero(self):
        r=evaluate(enemy_attack_count=20,window_seconds=0)
        self.assertEqual(r['total_damage'],0)
        self.assertFalse(r['neural_incoming_reference']['affected_damage_phases']['window'])

    def test_immediate_disappearance_and_buildup_immunity_have_no_pending_source(self):
        for extra in ({'timing':{'target_disappears_seconds':0}}, {'enemy_buildup_resistance':100}):
            r=evaluate(enemy_attack_count=20,**extra)
            self.assertNotIn('neural_incoming_reference',r)
            self.assertEqual(r['total_damage'],evaluate(**extra)['total_damage'])

    def test_locked_talent_does_not_create_a_source(self):
        r=evaluate(enemy_attack_count=20,elite=1,level=80,skill_rank=7)
        self.assertNotIn('neural_incoming_reference',r)

    def test_s1_binding_and_missing_talent_clock_preserve_one_arts_subtotal(self):
        r=evaluate(skill=1,enemy_attack_count=20,initial_neural_buildup=999)
        self.assertEqual(r['known_damage_subtotals']['total_damage'],3000)
        self.assertIsNone(r['total_damage'])
        self.assertIn('neural_s1_reference',r)

    def test_s3_sources_do_not_double_subtract_bursts_or_erase_subtotals(self):
        r=evaluate(skill=3,enemy_attack_count=20,initial_neural_buildup=999)
        self.assertIn('neural_skill_reference',r)
        self.assertEqual(r['known_damage_subtotals']['window_damage'],
                         sum(c['total'] for c in r['components'] if c['damage_type']=='magic'))
        self.assertIsNotNone(r['known_damage_subtotals']['cycle_damage'])

    def test_river_combines_affected_phases_from_all_unresolved_sources(self):
        r=evaluate(skill=1,enemy_attack_count=20,window_seconds=.1,
                   relic_ids=['rogue_6_relic_fight_22'])
        self.assertIsNone(r['neural_relic_reference']['window_burst_times'])
        self.assertTrue(r['neural_relic_reference']['affected_damage_phases']['window'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)

    def test_report_explains_count_and_clock_boundary(self):
        text=format_estimate(evaluate(enemy_attack_count=20))
        self.assertIn('堕梦 · 目标攻击时间待确认',text)
        self.assertIn('目标首个普通攻击时刻：未知',text)
        self.assertIn('当前情景损伤爆发次数：未知',text)


if __name__=='__main__':unittest.main()
