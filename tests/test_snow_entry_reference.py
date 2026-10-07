import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_1046_sbell2','skill':skill,'base_attack':1000,**extra})


def entry_reference(result):
    return result['external_event_reference']['conditional_components'][0]


class SnowEntryReferenceTests(unittest.TestCase):
    def test_s1_explicit_empty_short_and_long_observation_are_preserved(self):
        for mode in ('frames','continuous'):
            for window in (0,1,20):
                r=evaluate(1,timing_mode=mode,window_seconds=window)
                self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                self.assertEqual(r['total_damage'],0 if window==0 else 5200)

    def test_zero_observation_excludes_manual_entries_for_all_skills(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,window_seconds=0,snow_entries=2)
                self.assertEqual(r['total_damage'],0)
                self.assertFalse(r['external_event_reference']['window_reference']['source_possible'])
                self.assertEqual(next(c['total'] for c in r['components'] if c['name']=='积雪经过伤害'),0)

    def test_zero_current_enemy_lifetime_excludes_all_enemy_damage(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for entries in (0,2):
                    r=evaluate(skill,timing_mode=mode,snow_entries=entries,
                               timing={'target_disappears_seconds':0})
                    self.assertEqual(r['total_damage'],0)
                    self.assertTrue(all(c['total']==0 for c in r['components']))

    def test_entry_count_is_not_a_cast_stage_or_collision_clock(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for window in (1,20):
                    r=evaluate(skill,timing_mode=mode,window_seconds=window,snow_entries=2)
                    self.assertIsNone(r['total_damage'])
                    self.assertIsNone(r['estimate']['skill']['total_damage'])
                    self.assertIsNone(r['estimate']['skill']['cycle_damage'])
                    self.assertIsNone(r['external_event_reference']['actual_event_times_seconds'])
                    c=next(c for c in r['components'] if c['name']=='积雪经过伤害')
                    self.assertNotIn('times_seconds',c)
                    self.assertNotIn('instant_event',c)
                    self.assertIsNone(c['actual_total'])
                    self.assertIsNone(r['estimate']['skill']['hit_counts'][c['name']])

    def test_owner_empty_range_does_not_prove_empty_snow_coverage(self):
        for skill in (1,2,3):
            r=evaluate(skill,snow_entries=2,timing={'target_windows':[]})
            self.assertIsNone(r['total_damage'])
            self.assertTrue(r['external_event_reference']['source_possible'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
            self.assertGreater(entry_reference(r)['total'],0)

    def test_declared_entry_count_is_not_repeated_in_recharge_subtotal(self):
        for mode in ('frames','continuous'):
            r=evaluate(3,timing_mode=mode,snow_entries=2)
            body=evaluate(3,timing_mode=mode,snow_entries=0)
            self.assertEqual(entry_reference(r)['total'],3000)
            self.assertEqual(r['known_damage_subtotals']['cycle_damage'],body['estimate']['skill']['cycle_damage'])
            self.assertEqual(r['known_damage_subtotals']['total_damage'],body['estimate']['skill']['total_damage'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],body['total_damage'])

    def test_existing_s2_snow_dot_unknown_and_entry_unknown_coexist(self):
        r=evaluate(2,window_seconds=20,snow_entries=2,snow_coverage=.5)
        body=next(c['total'] for c in r['components'] if c['name']=='技能攻击')
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],body)
        self.assertIsNone(r['snow_field_reference']['actual_tick_times_seconds'])
        self.assertEqual(r['snow_field_reference']['per_tick_damage_reference'],200)
        self.assertEqual(entry_reference(r)['total'],1500)
        self.assertIsNone(r['known_damage_subtotals']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['hit_counts']['积雪持续伤害'])

    def test_e1_e2_potential_and_mitigation_keep_source_parameters(self):
        for elite,rank,potential,expected in ((1,7,1,1000),(1,7,5,1100),(2,10,1,1500),(2,10,5,1600)):
            r=evaluate(1,elite=elite,skill_rank=rank,potential=potential,snow_entries=2,
                       window_seconds=1,enemy_resistance=50)
            self.assertEqual(entry_reference(r)['total'],expected/2)
            self.assertEqual(r['known_damage_subtotals']['window_damage'],(4800 if elite==1 else 5200)/2)

    def test_existing_no_entry_default_damage_and_clock_references_are_retained(self):
        expected={'frames':{1:5200,2:None,3:114400},'continuous':{1:5200,2:None,3:114400}}
        for mode in ('frames','continuous'):
            for skill in (1,2,3):
                r=evaluate(skill,timing_mode=mode,snow_entries=0)
                self.assertEqual(r['total_damage'],expected[mode][skill])
                if skill==1:
                    ref=r['sbell_instant_reference']['parameter_clock_reference']
                    self.assertEqual(ref['duration_seconds'],0)
                    self.assertEqual(ref['recharge_seconds'],12)
                    self.assertEqual(ref['cycle_seconds'],12)
                    self.assertEqual(ref['cycle_damage'],5200)
                    self.assertAlmostEqual(ref['cycle_dps'],5200/12)
                elif skill==3:
                    self.assertEqual(r['estimate']['skill']['duration_seconds'],35)
                    self.assertEqual(r['estimate']['skill']['recharge_seconds'],50)
                    self.assertEqual(r['estimate']['skill']['cycle_seconds'],85)

    def test_s1_actual_end_and_complete_cycle_are_not_inferred_from_instant(self):
        r=evaluate(1)
        for key in ('duration_seconds','recharge_seconds','cycle_seconds','phase_damage','cycle_damage','cycle_dps'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertIsNone(r['sbell_instant_reference']['actual_skill_end_seconds'])
        self.assertFalse(r['sbell_instant_reference']['skill_lifecycle_binding_verified'])
        self.assertEqual(r['sbell_instant_reference']['charge_count_parameter'],2)

    def test_report_distinguishes_observation_entries_and_unknown_lifecycle(self):
        text=format_estimate(evaluate(1,window_seconds=1,snow_entries=2))
        self.assertIn('伤害观察窗口：1',text)
        self.assertIn('观察窗口总伤：未知',text)
        self.assertIn('声明观察窗口内积雪经过次数：2',text)
        self.assertIn('积雪经过伤害条件总量：1,500',text)
        self.assertIn('实际事件时刻：未知',text)
        self.assertIn('铃音吹雪 · 立即来源与结束待核验',text)
        self.assertIn('实际技能结束时刻：未知',text)
        self.assertIn('快照未知',text)


if __name__=='__main__':unittest.main()
