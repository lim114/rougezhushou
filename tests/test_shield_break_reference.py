"""Whole-skill shield-break declarations do not locate an actual event."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.shield_break_reference import NAME


def evaluate(**extra):
    return calculate_damage({'operator':'mechanist','skill':2,'base_attack':1000,
                             'shield_break_count':2,**extra})


class ShieldBreakReferenceTests(unittest.TestCase):
    def test_zero_observation_excludes_actual_hit_and_keeps_isolated_amount(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,window_seconds=0)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['estimate']['skill']['window_damage'],0)
            self.assertEqual(r['shield_break_reference']['declared_count_damage_reference'],10000)
            self.assertFalse(r['shield_break_reference']['source_possible']['window'])
            self.assertFalse(any(c['hits'] or 'actual_total' in c for c in r['components']))

    def test_numeric_string_zero_observation_and_lifetime_match_normalized_zero(self):
        for mode in ('frames','continuous'):
            for extra in ({'window_seconds':'0'}, {'window_seconds':10,'timing':{'target_disappears_seconds':'0'}},
                          {'window_seconds':10,'skill_duration_seconds':20,'timing':{'target_disappears_seconds':'0'}}):
                r=evaluate(timing_mode=mode,**extra)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['estimate']['skill']['window_damage'],0)
                self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
                self.assertFalse(r['shield_break_reference']['source_possible']['window'])
                if 'skill_duration_seconds' in extra:
                    for key in ('total_damage','phase_damage','cycle_damage','cycle_dps'):
                        self.assertEqual(r['estimate']['skill'][key],0)

    def test_positive_observation_is_unknown_without_a_synthetic_event(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,window_seconds=10)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['estimate']['skill']['window_damage'])
            self.assertIsNone(r['estimate']['skill']['window_dps'])
            self.assertFalse(r['complete']);self.assertFalse(r['estimate']['complete'])
            c=next(c for c in r['components'] if c['name']==NAME)
            self.assertIsNone(c['actual_total'])
            self.assertNotIn('times_seconds',c)
            self.assertFalse(r['timing']['resource_and_damage_shared_clock'])

    def test_manual_end_preserves_old_ordinary_cast_phase_and_cycle_subtotals(self):
        for mode in ('frames','continuous'):
            plain=evaluate(timing_mode=mode,skill_duration_seconds=20,shield_break_count=0)
            r=evaluate(timing_mode=mode,skill_duration_seconds=20)
            for key in ('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage'):
                self.assertEqual(r['known_damage_subtotals'][key],plain['estimate']['skill'][key])
            self.assertEqual(r['known_damage_subtotals']['total_damage'],40000)
            self.assertEqual(r['known_damage_subtotals']['cycle_damage'],81000)
            for key in ('initial_seconds','recharge_seconds','duration_seconds','cycle_seconds'):
                self.assertEqual(r['estimate']['skill'][key],plain['estimate']['skill'][key])
            self.assertIsNone(r['estimate']['skill']['total_damage'])
            self.assertIsNone(r['estimate']['skill']['phase_damage'])
            self.assertIsNone(r['estimate']['skill']['cycle_damage'])
            self.assertEqual(r['shield_break_reference']['manual_duration_parameter_seconds'],20)
            self.assertIsNone(r['shield_break_reference']['actual_end_seconds'])

    def test_explicit_short_window_does_not_add_new_ordinary_clock(self):
        r=evaluate(window_seconds=10,skill_duration_seconds=20)
        plain=evaluate(window_seconds=10,skill_duration_seconds=20,shield_break_count=0)
        self.assertEqual(r['known_damage_subtotals']['window_damage'],plain['estimate']['skill']['window_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
        self.assertEqual(r['known_damage_subtotals']['total_damage'],40000)
        self.assertIsNone(r['total_damage'])

    def test_empty_owner_range_does_not_locate_independent_structure_explosion(self):
        for timing in ({'target_windows':[]},{'interrupt_windows':[[0,100]]}):
            r=evaluate(window_seconds=10,skill_duration_seconds=20,timing=timing)
            self.assertIsNone(r['total_damage'])
            self.assertTrue(r['shield_break_reference']['source_possible']['window'])
            self.assertIsNone(r['shield_break_reference']['actual_collision_times_seconds'])

    def test_enemy_zero_lifetime_keeps_condition_and_zero_actual_damage(self):
        for mode in ('frames','continuous'):
            for manual in ({},{'skill_duration_seconds':20}):
                r=evaluate(timing_mode=mode,window_seconds=10,
                           timing={'target_disappears_seconds':0},**manual)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['shield_break_reference']['declared_count_damage_reference'],10000)
                self.assertFalse(r['shield_break_reference']['source_possible']['cast'])
                self.assertFalse(r['shield_break_reference']['source_possible']['window'])
                if manual:self.assertEqual(r['known_damage_subtotals']['total_damage'],0)

    def test_resistance_and_supported_effects_stay_in_conditional_per_hit(self):
        r=evaluate(enemy_defense=9999,enemy_resistance=50)
        self.assertEqual(r['shield_break_reference']['per_hit_damage_reference'],2500)
        self.assertEqual(r['shield_break_reference']['declared_count_damage_reference'],5000)
        e=evaluate(effects=[{'kind':'attack_pct','value':.1},
                            {'kind':'damage_taken','damage_type':'magic','value':.2}])
        self.assertEqual(e['shield_break_reference']['per_hit_damage_reference'],6240)
        self.assertIsNone(e['total_damage'])

    def test_healing_relic_does_not_scale_magic_condition_or_ordinary_subtotal(self):
        plain=evaluate(skill_duration_seconds=20)
        r=evaluate(skill_duration_seconds=20,relic_ids=['rogue_6_relic_legacy_81'])
        self.assertEqual(r['shield_break_reference'],plain['shield_break_reference'])
        self.assertEqual(r['known_damage_subtotals'],plain['known_damage_subtotals'])
        self.assertIsNone(r['total_damage'])

    def test_zero_break_count_keeps_ordinary_numerical_reference(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode,shield_break_count=0,skill_duration_seconds=20)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['estimate']['skill']['total_damage'],40000)
            self.assertNotIn('known_damage_subtotals',r)
            self.assertFalse(r['complete']);self.assertFalse(r['estimate']['complete'])
            self.assertEqual(r['shield_break_reference']['hits_requested'],0)
            self.assertNotIn('components',r)

    def test_already_validated_decimal_counts_preserve_legacy_numeric_equivalence(self):
        for mode in ('frames','continuous'):
            for count in (0,1,2):
                for extra in ({},{'window_seconds':0},{'window_seconds':10,'skill_duration_seconds':20}):
                    plain=evaluate(timing_mode=mode,shield_break_count=count,**extra)
                    for raw in (float(count),f'{count}.0',f'{count}e0'):
                        r=evaluate(timing_mode=mode,shield_break_count=raw,**extra)
                        self.assertEqual(r,plain)

    def test_ammunition_is_a_parameter_not_a_cap_or_schedule_for_both_sources(self):
        r=evaluate(shield_break_count=30)
        ref=r['shield_break_reference']
        self.assertEqual(ref['hits_requested'],30)
        self.assertEqual(ref['nominal_ammunition_parameter'],8)
        self.assertEqual(ref['declared_count_damage_reference'],150000)
        self.assertFalse(ref['owner_and_structure_count_mapping_verified'])
        self.assertFalse(ref['events_scheduled'])
        self.assertIsNone(ref['actual_ammunition_consumption_times_seconds'])

    def test_report_distinguishes_condition_actual_unknown_and_ordinary_subtotal(self):
        for mode in ('frames','continuous'):
            for count in (0,2):
                r=evaluate(timing_mode=mode,skill_duration_seconds=20,shield_break_count=count)
                text=format_estimate(r)
                self.assertNotIn('仅实际屏障破碎',text)
                self.assertIn('声明总破屏次数的法术爆炸条件参考，事件时刻未知',text)
                self.assertIn('已计普通攻击仅为手动结束参数参考',text)
                self.assertEqual(r['scope'],r['estimate']['scenario_scope'])
                self.assertIn('实际破屏/爆炸时刻：未知',text)
                self.assertIn('实际结束时刻：未知',text)
                self.assertIn('不完整',text)
                if count:
                    self.assertIn('给定总次数条件伤害参考：10,000',text)
                    self.assertIn('单次技能已计伤害小计：40,000',text)
                    self.assertIn('单次技能总伤：未知',text)

    def test_public_first_damage_relic_stays_reference_only_and_keeps_zero_values(self):
        for mode in ('frames','continuous'):
            for count in (0,2):
                plain=evaluate(timing_mode=mode,shield_break_count=count,skill_duration_seconds=20)
                for rid in ('rogue_6_relic_fight_1','rogue_6_relic_fight_2'):
                    r=evaluate(timing_mode=mode,shield_break_count=count,skill_duration_seconds=20,
                               relic_ids=[rid],relic_context={'enemy_first_damage_unused':1})
                    self.assertEqual(r['total_damage'],plain['total_damage'])
                    self.assertEqual(r['estimate']['skill'],plain['estimate']['skill'])
                    self.assertEqual(r.get('components'),plain.get('components'))
                    self.assertEqual(r.get('known_damage_subtotals'),plain.get('known_damage_subtotals'))
                    self.assertFalse(any(c.get('first_damage_relic') for c in r.get('components',[])))
                    self.assertFalse(any(a['kind']=='first_damage_scale'
                                         for record in r['relic_resolution']['records'] for a in record['applied']))

    def test_public_input_remains_unchanged_and_other_skills_have_no_new_reference(self):
        s={'operator':'mechanist','skill':2,'base_attack':1000,'shield_break_count':1,
           'window_seconds':10,'skill_duration_seconds':20,'timing':{'target_windows':[]}}
        before=copy.deepcopy(s);calculate_damage(s);self.assertEqual(s,before)
        for op,skill in (('mechanist',1),('mechanist',3),('kaltsit',2),('silverash',2)):
            self.assertNotIn('shield_break_reference',calculate_damage({'operator':op,'skill':skill}))


if __name__=='__main__':unittest.main()
