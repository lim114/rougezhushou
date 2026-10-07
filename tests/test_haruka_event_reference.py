import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_4202_haruka','skill':skill,'base_attack':1000,**extra})


def refs(result):
    return {c['name']:c for c in result['external_event_reference']['conditional_components']}


class HarukaEventReferenceTests(unittest.TestCase):
    def test_zero_window_excludes_independent_damage_and_healing(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,window_seconds=0,bubble_bursts=2,levitate_triggers=1)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['total_healing'],0)
                self.assertEqual(r['estimate']['skill']['window_seconds'],0)

    def test_declared_bursts_are_conditional_healing_not_actual_timestamps(self):
        for skill in (1,2):
            r=evaluate(skill,window_seconds=1,bubble_bursts=2)
            self.assertEqual(refs(r)['扶摇花火']['total'],500)
            self.assertIsNone(r['total_healing'])
            self.assertIsNone(r['external_event_reference']['actual_event_times_seconds'])
            self.assertIsNone(r['estimate']['skill']['cycle_healing'])
            c=next(c for c in r['components'] if c['name']=='扶摇花火')
            self.assertNotIn('times_seconds',c)
            self.assertIsNone(c['actual_total'])

    def test_global_enemy_lifetime_does_not_cancel_friend_bubble_healing(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,bubble_bursts=1,levitate_triggers=1,
                           timing={'target_disappears_seconds':0})
                self.assertEqual(r['total_damage'],0)
                self.assertIsNone(r['total_healing'])
                self.assertGreater(refs(r)['扶摇花火']['total'],0)

    def test_owner_range_does_not_locate_independent_bubbles(self):
        r=evaluate(2,bubble_bursts=2,timing={'target_windows':[]})
        self.assertEqual(refs(r)['浮泡治疗衍生伤害']['total'],1000)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['total_healing'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)

    def test_damage_based_on_bubble_treatment_preserves_mitigation(self):
        r=evaluate(2,bubble_bursts=2,enemy_resistance=50)
        self.assertEqual(refs(r)['扶摇花火']['total'],500)
        self.assertEqual(refs(r)['浮泡治疗衍生伤害']['total'],500)
        self.assertIsNone(r['total_damage'])

    def test_levitate_duration_does_not_manufacture_four_ticks(self):
        r=evaluate(3,levitate_triggers=1,window_seconds=1)
        dot=refs(r)['浮泡浮空持续伤害']
        self.assertEqual(dot['per_hit'],1240)
        self.assertIsNone(dot['hits'])
        self.assertIsNone(dot['total'])
        self.assertIsNone(r['total_damage'])
        params=r['external_event_reference']['parameter_rows']
        self.assertIn(('浮空持续参数',4,'秒'),params)
        self.assertIn(('跳伤间隔参数',1,'秒'),params)
        self.assertIsNone(r['estimate']['skill']['hit_counts']['浮泡浮空持续伤害'])

    def test_zero_manual_counts_do_not_make_known_reference_output_unknown(self):
        for skill in (1,2,3):
            r=evaluate(skill,bubble_bursts=0,levitate_triggers=0)
            self.assertIsInstance(r['total_damage'],(int,float))
            self.assertIsInstance(r['total_healing'],(int,float))
            self.assertNotIn('known_healing_subtotals',r)
            self.assertNotIn('known_damage_subtotals',r)

    def test_known_body_healing_subtotal_is_distinct_from_unplaced_treatment(self):
        r=evaluate(1,bubble_bursts=2)
        body=next(c['total'] for c in r['components'] if c['name']=='护佑者普通治疗')
        self.assertEqual(r['known_healing_subtotals']['window_healing'],body)
        self.assertIsNone(r['total_healing'])

    def test_repeat_s2_does_not_publish_window_subtotal_as_full_cast(self):
        r=evaluate(2,haruka_repeat=True,bubble_bursts=1,window_seconds=1)
        self.assertIsNone(r['known_healing_subtotals']['total_healing'])
        self.assertIsNone(r['known_damage_subtotals']['total_damage'])
        self.assertEqual(r['estimate']['skill']['window_seconds'],1)

    def test_report_retains_unknown_event_and_tick_parameters(self):
        text=format_estimate(evaluate(3,levitate_triggers=1,window_seconds=1))
        self.assertIn('独立条件来源 · 事件时钟待核验',text)
        self.assertIn('浮空每跳伤害条件参考：1,240',text)
        self.assertIn('实际事件时刻：未知',text)
        self.assertIn('观察窗口总伤：未知',text)


if __name__=='__main__':unittest.main()
