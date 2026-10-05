import unittest
from rouge.damage import calculate_damage
from rouge.timing import AttackTimeline


class FixedImpactDelayTests(unittest.TestCase):
    def scenario(self,**values):
        return {'operator':'mechanist','skill':3,'base_attack':1000,
            'timing':{'windup_frames':6,'recovery_frames':9},**values}

    def test_impact_on_window_end_is_excluded_then_included_next_frame(self):
        # Release6 + documented delay24 = impact30. Windows are [0,end).
        edge=calculate_damage(self.scenario(window_seconds=1))
        after=calculate_damage(self.scenario(window_seconds=31/30))
        self.assertEqual(edge['timing']['streams'][0]['release_frames'],[6])
        self.assertEqual(edge['components'][0]['hits'],0)
        self.assertEqual(edge['total_damage'],0)
        self.assertEqual(after['timing']['streams'][0]['impact_frames'],[30])
        self.assertEqual(after['total_damage'],9880)

    def test_extra_travel_is_added_once_to_fixed_delay(self):
        s=self.scenario(window_seconds=2)
        s['timing']['projectile_travel_seconds']=.4
        r=calculate_damage(s);stream=r['timing']['streams'][0]
        self.assertEqual(stream['release_frames'],[6])
        self.assertEqual(stream['impact_frames'],[42])
        self.assertEqual(stream['fixed_impact_delay_frames'],24)

    def test_fixed_delay_does_not_scale_with_attack_speed(self):
        for bonus in (0,100,500):
            with self.subTest(bonus=bonus):
                r=calculate_damage(self.scenario(window_seconds=10,
                    effects=[{'kind':'attack_speed','value':bonus}]))
                stream=r['timing']['streams'][0]
                self.assertTrue(stream['emitted_impact_frames'])
                self.assertEqual([hit-release for hit,release in zip(
                    stream['emitted_impact_frames'],stream['emitted_release_frames'])],
                    [24]*len(stream['emitted_impact_frames']))

    def test_initial_and_recharge_do_not_wait_for_last_projectile(self):
        r=calculate_damage(self.scenario());skill=r['estimate']['skill']
        self.assertEqual(skill['initial_seconds'],10)
        self.assertEqual(skill['duration_seconds'],40)
        self.assertEqual(skill['recharge_seconds'],35)
        self.assertEqual(skill['cycle_seconds'],75)

    def test_late_cast_damage_is_attributed_separately_from_skill_phase(self):
        s=self.scenario(timing={'windup_frames':0,'recovery_frames':0,'start_delay_frames':24})
        r=calculate_damage(s);skill=r['estimate']['skill']
        # Twelve releases .8,4.3,...39.3; final impact40.1 is after skill end.
        self.assertEqual(r['components'][0]['hits'],12)
        self.assertEqual(skill['total_damage'],12*9880)
        self.assertEqual(skill['phase_damage'],11*9880)
        self.assertEqual(skill['window_damage'],11*9880)
        self.assertEqual(r['components'][0]['times_seconds'][-1],40.1)

    def test_late_projectile_is_excluded_from_this_cycle_but_keeps_cast_total(self):
        s=self.scenario(timing={'windup_frames':0,'recovery_frames':0,
            'start_delay_frames':24,'projectile_travel_seconds':35.1})
        r=calculate_damage(s);skill=r['estimate']['skill']
        # Impacts36.7,40.2,...75.2: one in40s phase, eleven in75s cycle.
        # Recharge normals land after75 due to explicitly supplied35.1s travel.
        self.assertEqual(skill['total_damage'],12*9880)
        self.assertEqual(skill['phase_damage'],9880)
        self.assertEqual(skill['cycle_damage'],11*9880)
        self.assertEqual(skill['cycle_dps'],11*9880/75)

    def test_all_ten_ranks_use_the_delay_without_claiming_animation_verified(self):
        for rank in range(1,11):
            with self.subTest(rank=rank):
                r=calculate_damage(self.scenario(skill_rank=rank,window_seconds=2))
                stream=r['timing']['streams'][0]
                self.assertEqual(stream['impact_frames'],[30])
                self.assertEqual(stream['fixed_impact_delay_seconds'],.8)
                self.assertFalse(stream['exact_binding'])
                self.assertFalse(r['estimate']['complete'])
                self.assertIn('https://prts.wiki/w/机械师',stream['fixed_impact_delay_source'])
        unknown=calculate_damage({'operator':'mechanist','skill':3})
        self.assertFalse(unknown['timing']['streams'][0]['known_animation'])

    def test_windup_interruption_reschedules_release_before_delay(self):
        s=self.scenario(window_seconds=2)
        s['timing']['movement_windows']=[[.1,.5]]
        stream=calculate_damage(s)['timing']['streams'][0]
        self.assertEqual(stream['release_frames'],[21])
        self.assertEqual(stream['impact_frames'],[45])

    def test_movement_after_release_does_not_cancel_the_in_flight_projectile(self):
        s=self.scenario(window_seconds=31/30)
        s['timing']['movement_windows']=[[.3,.8]]
        r=calculate_damage(s)
        self.assertEqual(r['components'][0]['hits'],1)
        self.assertEqual(r['timing']['streams'][0]['impact_frames'],[30])

    def test_disappeared_target_has_no_damage_at_the_delayed_impact(self):
        s=self.scenario(window_seconds=2)
        for disappearance in (.9,1):
            with self.subTest(disappearance=disappearance):
                s['timing']['target_disappears_seconds']=disappearance
                r=calculate_damage(s)
                self.assertEqual(r['components'][0]['hits'],0)
                self.assertEqual(r['timing']['streams'][0]['emitted_impact_frames'],[])

    def test_emitted_and_windowed_release_pairs_stay_aligned(self):
        s=self.scenario(window_seconds=40,timing={'windup_frames':0,
            'recovery_frames':0,'start_delay_frames':24})
        r=calculate_damage(s);stream=r['timing']['streams'][0]
        self.assertEqual(len(stream['emitted_impact_frames']),12)
        self.assertEqual(len(stream['impact_frames']),11)
        self.assertEqual(stream['hit_release_frames'][-1],1074)
        self.assertEqual(stream['emitted_release_frames'][-1],1179)
        self.assertEqual(stream['emitted_impact_frames'][-1],1203)
        self.assertEqual(r['total_damage'],11*9880)

    def test_delay_is_not_inherited_by_recharge_normals_or_an_independent_unit(self):
        s=self.scenario()
        normal=AttackTimeline(s,normal=True)
        stream=normal.attacks(2,1.2)
        self.assertNotIn('fixed_impact_delay_seconds',stream)
        self.assertEqual(stream['impact_frames'],stream['release_frames'])
        independent=AttackTimeline(s)
        stream=independent.attacks(3,1.25,unit='char_110_deepcl')
        self.assertNotIn('fixed_impact_delay_seconds',stream)
        self.assertEqual(stream['impact_frames'],stream['release_frames'])

    def test_continuous_comparison_retains_its_original_reference_model(self):
        r=calculate_damage(self.scenario(timing_mode='continuous',window_seconds=1))
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['total_damage'],11*9880)
        self.assertFalse(any(m['key']=='fixed_impact_delay' for block in r['report']['sections']
            for m in block['metrics']))

    def test_report_discloses_delay_only_on_supported_skill(self):
        for op,skill in (('mechanist',1),('mechanist',2),('mechanist',3),('silverash',3),('kaltsit',1)):
            with self.subTest(op=op,skill=skill):
                r=calculate_damage({'operator':op,'skill':skill})
                metrics=[m for block in r['report']['sections'] for m in block['metrics']
                    if m['key']=='fixed_impact_delay']
                self.assertEqual(len(metrics),int(op=='mechanist' and skill==3))
                if metrics:self.assertEqual(metrics[0]['value'],.8)


if __name__=='__main__':unittest.main()
