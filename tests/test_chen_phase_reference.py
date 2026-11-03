"""Pinned Chen source parameters without fabricated slash/projectile clocks."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_1050_chen3','skill':skill,
                             'base_attack':1000,**extra})


def sources(result):
    return {c['name']:c for c in result['unbound_cast_reference']['conditional_components']}


class ChenPhaseReferenceTests(unittest.TestCase):
    def test_explicit_observation_keeps_zero_and_short_windows_in_both_modes(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                for window in (0,.1,1,10):
                    with self.subTest(skill=skill,mode=mode,window=window):
                        r=evaluate(skill,timing_mode=mode,window_seconds=window)
                        self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                        if window==0:self.assertEqual(r['total_damage'],0)
                        else:self.assertIsNone(r['total_damage'])

    def test_global_zero_lifetime_excludes_all_actual_sources_in_both_modes(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,timing={'target_disappears_seconds':0})
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['estimate']['skill']['total_damage'],0)
                for c in r['components']:
                    self.assertEqual(c['hits'],0)
                    self.assertEqual(c['total'],0)
                self.assertEqual(r['timing']['streams'],[])

    def test_positive_manual_parameters_do_not_create_damage_in_empty_boundaries(self):
        for mode in ('frames','continuous'):
            s2=evaluate(2,timing_mode=mode,window_seconds=0,slash_kills=1)
            self.assertEqual(s2['total_damage'],0)
            self.assertEqual(sources(s2)['绝影斩击']['hits'],11)
            self.assertEqual(sources(s2)['绝影斩击']['total'],59664)
            s3=evaluate(3,timing_mode=mode,window_seconds=0,enemy_current_hp=200000)
            self.assertEqual(s3['total_damage'],0)
            self.assertEqual(s3['chen_phase_reference']['conditional_components'][0]['total'],12000)

    def test_s2_original_ten_slashes_and_isolated_strengthening_remain_conditionals(self):
        for mode in ('frames','continuous'):
            r=evaluate(2,timing_mode=mode)
            ref=sources(r)
            self.assertEqual(ref['绝影斩击']['hits'],10)
            self.assertEqual(ref['绝影斩击']['per_hit'],5424)
            self.assertEqual(ref['绝影斩击']['total'],54240)
            self.assertEqual(ref['斩击后的6秒强化']['hits'],5)
            self.assertEqual(ref['斩击后的6秒强化']['per_hit'],4130)
            self.assertEqual(sum(c['total'] for c in ref.values()),74890)
            phase=r['chen_phase_reference']
            self.assertEqual(phase['strengthening_duration_parameter_seconds'],6)
            self.assertEqual(phase['attack_bonus_parameter'],3)
            self.assertEqual(phase['strengthened_attack_reference'],4130)
            self.assertEqual(phase['isolated_attack_phase_reference']['conditional_damage'],20650)
            self.assertEqual(phase['isolated_attack_phase_reference']['phase_seconds'],6)
            self.assertIsNone(phase['actual_slash_end_seconds'])
            self.assertIsNone(phase['actual_strengthening_start_seconds'])
            self.assertFalse(phase['phase_clock_verified'])

    def test_s2_does_not_publish_isolated_clock_as_activation_clock_or_complete_end(self):
        r=evaluate(2)
        self.assertEqual(r['timing']['streams'],[])
        self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
        isolated=r['chen_phase_reference']['isolated_attack_phase_reference']['timing']['streams']
        self.assertEqual(isolated[0]['times_seconds'],[1.1,2.2,3.3,4.4,5.5])
        for c in r['components']:
            self.assertNotIn('times_seconds',c)
            self.assertNotIn('instant_event',c)
            self.assertIsNone(c['actual_total'])
        skill=r['estimate']['skill']
        for key in ('duration_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage'):
            self.assertIsNone(skill[key])
        self.assertEqual(skill['initial_seconds'],5)

    def test_s2_attack_speed_does_not_change_sourced_slash_count(self):
        for count in (0,1,100):
            r=evaluate(2,slash_kills=count,effects=[{'kind':'attack_speed','value':100}])
            self.assertEqual(sources(r)['绝影斩击']['hits'],10+count)
            self.assertEqual(sources(r)['绝影斩击']['total'],5424*(10+count))
            self.assertIsNone(r['total_damage'])
        for count in (-1,1.5,101):
            with self.assertRaises(ValueError):evaluate(2,slash_kills=count)

    def test_s2_declared_long_window_does_not_extend_six_second_isolated_phase(self):
        r=evaluate(2,window_seconds=10)
        phase=r['chen_phase_reference']['window_reference']['isolated_attack_phase_reference']
        self.assertEqual(r['estimate']['skill']['window_seconds'],10)
        self.assertEqual(phase['phase_seconds'],6)
        self.assertEqual(phase['conditional_damage'],20650)
        self.assertIsNone(r['total_damage'])

    def test_s3_masks_only_wave_and_preserves_default_body_subtotals_and_clock(self):
        for mode in ('frames','continuous'):
            r=evaluate(3,timing_mode=mode)
            wave=next(c for c in r['components'] if c['name']=='天喟剑气')
            body=next(c for c in r['components'] if c['name']=='技能攻击')
            self.assertEqual(wave['per_hit'],6554)
            self.assertIsNone(wave['actual_total'])
            self.assertNotIn('times_seconds',wave)
            self.assertNotIn('instant_event',wave)
            self.assertNotIn('actual_total',body)
            self.assertEqual(body['hits'],54)
            self.assertEqual(body['per_hit'],2373)
            self.assertEqual(body['total'],128142)
            self.assertEqual(len(body['times_seconds']),54)
            self.assertEqual(r['known_damage_subtotals']['total_damage'],128142)
            self.assertEqual(r['known_damage_subtotals']['phase_damage'],128142)
            self.assertEqual(r['known_damage_subtotals']['cycle_damage'],153002)
            skill=r['estimate']['skill']
            self.assertEqual(skill['duration_seconds'],20)
            self.assertEqual(skill['initial_seconds'],7)
            self.assertEqual(skill['recharge_seconds'],25)
            self.assertEqual(skill['cycle_seconds'],45)
            for key in ('total_damage','phase_damage','cycle_damage','cycle_dps'):
                self.assertIsNone(skill[key])
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(skill['hit_counts']['天喟剑气'])
            self.assertEqual(skill['hit_counts']['技能攻击'],54)

    def test_s3_hp_and_floor_are_single_wave_conditionals(self):
        for hp,amount in ((0,6554),(200000,12000)):
            r=evaluate(3,enemy_current_hp=hp,window_seconds=1)
            ref=r['chen_phase_reference']
            self.assertEqual(ref['declared_current_hp'],hp)
            self.assertEqual(ref['hp_ratio_parameter'],.06)
            self.assertEqual(ref['minimum_attack_scale_parameter'],5.8)
            self.assertEqual(ref['conditional_components'][0]['hits'],1)
            self.assertEqual(ref['conditional_components'][0]['total'],amount)
            self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
            self.assertIsNone(ref['actual_collision_times_seconds'])
            self.assertFalse(ref['collision_clock_verified'])

    def test_owner_supply_and_interrupt_do_not_prove_independent_wave_or_slash_coverage(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                for timing in ({'target_windows':[]},{'target_windows':[[5,10]]},
                               {'interrupt_windows':[[0,3600]]}):
                    r=evaluate(skill,timing_mode=mode,window_seconds=10,timing=timing)
                    self.assertIsNone(r['total_damage'])
                    ref=r['unbound_cast_reference'] if skill==2 else r['chen_phase_reference']
                    self.assertTrue(ref['source_possible'])
                    self.assertEqual(ref['conditional_components'][0]['hits'],10 if skill==2 else 1)
        empty=evaluate(3,window_seconds=10,timing={'target_windows':[]})
        self.assertEqual(empty['known_damage_subtotals']['window_damage'],0)

    def test_s3_weakness_is_selected_before_type_specific_vulnerability(self):
        r=evaluate(3,enemy_defense=500,enemy_resistance=50)
        base=r['chen_phase_reference']['conditional_components'][0]['per_hit']
        self.assertEqual(base,6054)
        bonus=evaluate(3,enemy_defense=500,enemy_resistance=50,
                       effects=[{'kind':'damage_taken','damage_type':'magic','value':2}])
        self.assertEqual(bonus['chen_phase_reference']['conditional_components'][0]['per_hit'],base)

    def test_body_travel_override_does_not_place_special_wave(self):
        r=evaluate(3,window_seconds=2,timing={'projectile_travel_seconds':.5})
        wave=next(c for c in r['components'] if c['name']=='天喟剑气')
        body=next(c for c in r['components'] if c['name']=='技能攻击')
        self.assertNotIn('times_seconds',wave)
        self.assertIsNone(wave['actual_total'])
        self.assertEqual(body['times_seconds'],[1.6,1.6,1.6])

    def test_report_distinguishes_s2_isolation_and_s3_wave_from_body(self):
        s2=format_estimate(evaluate(2,window_seconds=1))
        self.assertIn('绝影 · 孤立强化阶段参考',s2)
        self.assertIn('斩击后强化持续参数：6.00',s2)
        self.assertIn('实际强化起点：未知',s2)
        self.assertIn('持续时间：未知',s2)
        s3=format_estimate(evaluate(3))
        self.assertIn('天喟 · 剑气碰撞待核验',s3)
        self.assertIn('剑气单次伤害条件参考：6,554',s3)
        self.assertIn('实际剑气碰撞时刻：未知',s3)
        self.assertIn('单次技能总伤：未知',s3)
        self.assertIn('单次技能已计伤害小计：128,142',s3)
        self.assertNotIn('河谷祭祈未排程',s3)

    def test_public_input_and_returned_references_are_independent(self):
        scenario={'operator':'char_1050_chen3','skill':3,'base_attack':1000,
                  'timing':{'target_windows':[[5,10]]}}
        before=copy.deepcopy(scenario)
        expected=calculate_damage(scenario)
        modified=calculate_damage(scenario)
        modified['chen_phase_reference']['conditional_components'][0]['total']=999
        self.assertEqual(calculate_damage(scenario),expected)
        self.assertEqual(scenario,before)


if __name__=='__main__':unittest.main()
