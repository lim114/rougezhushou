import unittest
from rouge.damage import calculate_damage
from rouge.reporting import format_report

OP='char_1042_phatm2'


def calculate(**extra):return calculate_damage({'operator':OP,'skill':2,**extra})


class BaitUnknown048Tests(unittest.TestCase):
    def test_count_does_not_invent_twenty_five_second_events_or_snapshot(self):
        base=calculate(window_seconds=50)
        for count in (1,2,4):
            r=calculate(bait_triggers=count,window_seconds=50)
            self.assertIsNone(r['total_damage']);self.assertFalse(r['complete'])
            self.assertIsNone(r['estimate']['skill']['window_dps'])
            ref=r['neural_bait_reference']
            self.assertEqual(ref['triggers_requested'],count);self.assertFalse(ref['events_scheduled'])
            self.assertEqual(ref['attack_snapshot'],'deployment');self.assertIsNone(ref['snapshot_attack'])
            self.assertIsNone(ref['first_tick_seconds']);self.assertTrue(ref['buildup_ignores_resistance'])
            self.assertFalse(any(c['name'] in ('本能的召唤持续法术','神经损伤爆发') for c in r['components']))
            direct=sum(c['total'] for c in base['components'] if c['damage_type']=='magic')
            self.assertEqual(r['known_damage_subtotals']['window_damage'],direct)

    def test_no_bait_keeps_default_and_other_skill_panels_free_of_bait_section(self):
        for op,skill in ((OP,1),(OP,2),(OP,3),('mechanist',3)):
            r=calculate_damage({'operator':op,'skill':skill})
            self.assertNotIn('neural_bait_reference',r)
            self.assertNotIn('本能的召唤 · 诱饵持续效果待核验',format_report(r))

    def test_resistance_does_not_restore_a_fake_bait_sequence(self):
        for resistance in (0,50,100):
            r=calculate(bait_triggers=2,enemy_buildup_resistance=resistance)
            self.assertTrue(r['neural_bait_reference']['buildup_ignores_resistance'])
            self.assertIsNone(r['total_damage'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],calculate(bait_triggers=1)['known_damage_subtotals']['window_damage'])

    def test_empty_regular_supply_does_not_dismiss_explicit_bait_trigger(self):
        r=calculate(bait_triggers=1,timing={'target_windows':[]})
        self.assertIsNone(r['total_damage']);self.assertEqual(r['known_damage_subtotals']['window_damage'],0)

    def test_immediate_target_disappearance_retains_known_zero(self):
        r=calculate(bait_triggers=1,timing={'target_disappears_seconds':0})
        self.assertEqual(r['total_damage'],0)
        self.assertFalse(r['neural_bait_reference']['affected_damage_phases']['window'])

    def test_river_reference_has_unknown_burst_times_and_cannot_make_bait_output_finite(self):
        r=calculate(bait_triggers=1,relic_ids=['rogue_6_relic_fight_22'])
        self.assertIsNone(r['total_damage']);self.assertIsNone(r['neural_relic_reference']['window_burst_times'])
        self.assertTrue(r['neural_relic_reference']['periodic_damage_possible'])

    def test_report_discloses_known_parameters_and_missing_timeline(self):
        r=calculate(bait_triggers=1);text=format_report(r)
        self.assertIn('本能的召唤 · 诱饵持续效果待核验',text)
        self.assertIn('诱饵部署时攻击力快照：未知',text)
        self.assertIn('受影响的完整总伤',text);self.assertIn('已建模伤害小计',text)
        self.assertIn('当前情景损伤爆发次数：未知',text)
        self.assertNotIn('河谷持续伤害',text)
        self.assertIsNotNone(r['estimate']['base_stats']['attack'])
        self.assertIsNotNone(r['estimate']['skill']['initial_seconds'])


if __name__=='__main__':unittest.main()
