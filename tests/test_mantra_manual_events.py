import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_4204_mantra','skill':skill,'base_attack':1000,**extra})


def manual(result):
    return {c['name']:c for c in result['external_event_reference']['conditional_components']}


class MantraManualEventsTests(unittest.TestCase):
    def test_zero_window_excludes_declared_manual_events_in_both_modes(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,window_seconds=0,palsy_triggers=1,palsy_overflow_hits=1)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['estimate']['skill']['window_seconds'],0)

    def test_zero_global_target_lifetime_cannot_create_damage_or_buildup(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,palsy_triggers=1,palsy_overflow_hits=1,
                           timing={'target_disappears_seconds':0},enemy_in_neural_break=True)
                self.assertEqual(r['total_damage'],0)
                self.assertTrue(all(c['total']==0 for c in r['components']))

    def test_manual_palsy_count_retains_elemental_reference_with_mitigation(self):
        for skill in (1,2):
            r=evaluate(skill,palsy_triggers=2,enemy_elemental_resistance=50)
            self.assertEqual(manual(r)['麻痹触发天赋']['total'],1350)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['estimate']['skill']['cycle_damage'])
            self.assertIsNone(r['external_event_reference']['actual_event_times_seconds'])

    def test_s3_current_phase_attack_is_only_conditional_snapshot(self):
        r=evaluate(3,palsy_triggers=1,palsy_overflow_hits=1)
        refs=manual(r)
        self.assertEqual(refs['麻痹触发天赋']['total'],5062.5)
        self.assertEqual(refs['无言为真溢出跳跃']['total'],6937.5)
        self.assertIsNone(r['total_damage'])
        self.assertIn(('溢出跳跃间隔原表参数',1.5,'秒'),r['external_event_reference']['parameter_rows'])
        for c in r['components']:
            if c['name'] in refs:
                self.assertNotIn('times_seconds',c)
                self.assertIsNone(c['actual_total'])
                self.assertIsNone(r['estimate']['skill']['hit_counts'][c['name']])

    def test_body_range_does_not_cancel_global_conditional_events(self):
        r=evaluate(3,palsy_triggers=1,palsy_overflow_hits=1,timing={'target_windows':[]})
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
        self.assertEqual(sum(c['total'] for c in manual(r).values()),12000)

    def test_zero_manual_counts_keep_existing_s2_direct_neural_chain(self):
        baseline=evaluate(2,palsy_triggers=0,palsy_overflow_hits=0,enemy_in_neural_break=True)
        r=evaluate(2,palsy_triggers=1,enemy_in_neural_break=True)
        names={c['name'] for c in baseline['components'] if 'actual_total' not in c}
        for name in names:
            if name=='麻痹触发天赋':continue
            expected=[c for c in baseline['components'] if c['name']==name]
            actual=[c for c in r['components'] if c['name']==name]
            self.assertEqual(actual,expected)
        self.assertEqual(r['known_damage_subtotals']['window_damage'],baseline['total_damage'])

    def test_short_window_is_preserved_and_events_do_not_prove_actual_amount(self):
        for skill in (1,2,3):
            r=evaluate(skill,window_seconds=1,palsy_triggers=3,palsy_overflow_hits=2)
            self.assertEqual(r['estimate']['skill']['window_seconds'],1)
            self.assertIsNone(r['total_damage'])

    def test_report_distinguishes_unplaced_events_and_current_phase_reference(self):
        text=format_estimate(evaluate(3,window_seconds=1,palsy_triggers=1,palsy_overflow_hits=1))
        self.assertIn('独立条件来源 · 事件时钟待核验',text)
        self.assertIn('实际事件时刻：未知',text)
        self.assertIn('观察窗口总伤：未知',text)
        self.assertIn('快照未知',text)


if __name__=='__main__':unittest.main()
