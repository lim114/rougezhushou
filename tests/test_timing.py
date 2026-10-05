import unittest
from rouge.damage import calculate_damage


class FrameTimingTests(unittest.TestCase):
    def test_mixed_sp_ignores_attack_credits_inside_post_skill_sp_lockout(self):
        r=calculate_damage({'operator':'char_002_amiya','skill':1,
            'timing':{'windup_frames':0,'recovery_frames':0,'target_windows':[[30,40]],
                      'sp_lockout_extra_seconds':10}})
        # S1 lasts30s, then ten blocked seconds. With no target after40,
        # thirty required SP comes from natural recovery during [40,70].
        self.assertEqual(r['estimate']['skill']['recharge_seconds'],40)
        self.assertEqual(r['estimate']['skill']['cycle_seconds'],70)

    def test_mechanist_shield_skill_normal_attacks_use_the_same_frame_clock(self):
        r=calculate_damage({'operator':'mechanist','skill':2,'skill_duration_seconds':1,
            'timing':{'windup_frames':6,'recovery_frames':9}})
        self.assertGreater(r['estimate']['skill']['total_damage'],0)
        idle=calculate_damage({'operator':'mechanist','skill':2,'skill_duration_seconds':1,
            'timing':{'target_windows':[]}})
        self.assertEqual(idle['estimate']['skill']['total_damage'],0)

    def test_next_attack_skill_ends_after_release_and_keeps_normal_cadence(self):
        r=calculate_damage({'operator':'char_133_mm','skill':1,
            'timing':{'windup_frames':0,'recovery_frames':0}})
        skill=r['estimate']['skill']
        self.assertEqual(skill['hit_counts'][skill['name']],1)
        self.assertEqual(skill['duration_seconds'],1/30)
        #3SP,28-frame normal cadence; next skill attack starts at112.
        self.assertEqual(skill['cycle_seconds'],112/30)

    def test_healing_projectiles_are_cast_attribution_but_not_in_window_or_cycle(self):
        s={'operator':'char_298_susuro','skill':1,
            'timing':{'windup_frames':0,'recovery_frames':0,'projectile_travel_seconds':100}}
        r=calculate_damage(s)
        skill=r['estimate']['skill']
        self.assertGreater(skill['total_healing'],0)
        self.assertEqual(skill['phase_healing'],0)
        self.assertEqual(skill['window_healing'],0)
        self.assertEqual(skill['cycle_healing'],0)
        section=next(x for x in r['report']['sections'] if x['id']=='healing')
        self.assertEqual(next(x for x in section['metrics'] if x['key']=='active_hps')['value'],0)

    def test_cast_damage_and_cycle_damage_place_projectile_impacts_on_their_actual_clock(self):
        s={'operator':'mechanist','skill':3,'base_attack':1000,'window_seconds':1,
            'timing':{'windup_frames':6,'recovery_frames':9,'projectile_travel_seconds':2}}
        r=calculate_damage(s)
        self.assertEqual(r['total_damage'],0)  # .2 release + .8 intrinsic +2 preview =3s
        self.assertEqual(r['estimate']['skill']['total_damage'],118560)  # twelve9880 shots
        late=calculate_damage({**s,'timing':{**s['timing'],'projectile_travel_seconds':100}})
        self.assertEqual(late['estimate']['skill']['total_damage'],118560)
        self.assertEqual(late['estimate']['skill']['cycle_damage'],0)  # all impacts after75s

    def test_mechanist_burst_landing_delay_and_pellet_spacing_clip_short_window(self):
        r=calculate_damage({'operator':'mechanist','skill':1,'window_seconds':2,
            'timing':{'windup_frames':0,'recovery_frames':0}})
        # Snapshot BB: delay1.3s,5 pellets0.2s apart =>1.3,1.5,1.7,1.9,2.1.
        # [0,2) sees four; this interpretation is marked as a data reference.
        self.assertEqual(r['hits'],4)
        self.assertEqual(r['timing']['streams'][0]['impact_frames'],[39,45,51,57])

    def test_amiya_attack_sp_talent_does_not_generate_sp_during_initial_idle(self):
        r=calculate_damage({'operator':'char_002_amiya','skill':1,
            'timing':{'initial_target_windows':[]}})
        # S1M3 needs30-15=15SP. Without targets only natural1SP/s remains.
        self.assertEqual(r['estimate']['skill']['initial_seconds'],15)

    def test_sp_lockout_and_animation_lock_overlap_instead_of_being_added_twice(self):
        r=calculate_damage({'operator':'mechanist','skill':3,
            'timing':{'sp_lockout_extra_seconds':.05,'post_skill_lock_frames':1200}})
        #40s skill; SP ready35s+2ticks after it, but own40s end lock is longer.
        # Actual next activation at80s, not40+35+40s.
        self.assertEqual(r['estimate']['skill']['cycle_seconds'],80)

    def test_ammo_waits_for_targets_and_does_not_gain_more_ammo_from_attack_speed(self):
        s={'operator':'char_1041_angel2','skill':3,
            'timing':{'windup_frames':6,'recovery_frames':9,'target_windows':[[5,100]]}}
        r=calculate_damage(s)
        main=next(c for c in r['components'] if c['name']=='技能攻击')
        self.assertEqual(main['hits'],50)  # ten five-round attacks, not a timed refill
        self.assertGreater(r['estimate']['skill']['duration_seconds'],5)
        short=calculate_damage({**s,'window_seconds':2})
        self.assertEqual(next(c for c in short['components'] if c['name']=='技能攻击')['hits'],0)

    def test_gnosis_short_window_excludes_skill_end_detonation(self):
        r=calculate_damage({'operator':'char_206_gnosis','skill':3,'window_seconds':1})
        self.assertFalse(any(c['name']=='失温症终结' and c['hits'] for c in r['components']))

    def test_attack_recharge_initial_delay_follows_attacks_and_initial_target_gaps(self):
        # E2 Mechanical S1 costs7SP; normal interval36frames. Release at6,42,
        # gap[60,150), then156,192,228,264,300: seventh credit at300,
        # usable next simulated logic tick301. This is explicit preview ordering.
        r=calculate_damage({'operator':'mechanist','skill':1,
            'timing':{'windup_frames':6,'recovery_frames':9,
                'initial_target_windows':[[0,2],[5,100]]}})
        self.assertEqual(r['estimate']['skill']['initial_seconds'],301/30)

    def test_moving_during_windup_cancels_release_but_not_an_already_fired_projectile(self):
        s={'operator':'mechanist','skill':3,'base_attack':1000,'window_seconds':2,
            'timing':{'windup_frames':6,'recovery_frames':9,'projectile_travel_seconds':.4,
                'movement_windows':[[.1,.5]]}}
        r=calculate_damage(s)
        stream=r['timing']['streams'][0]
        self.assertEqual(stream['release_frames'],[21])  # canceled0→6, restart15→21
        self.assertEqual(stream['impact_frames'],[57])  #21+24 intrinsic+12 preview
        fired=calculate_damage({**s,'timing':{**s['timing'],'movement_windows':[[.3,.8]],
            'target_windows':[[0,.3]]}})
        self.assertEqual(fired['timing']['streams'][0]['release_frames'],[6])
        self.assertEqual(fired['components'][0]['hits'],1)  # range exit is not disappearance
        vanished=calculate_damage({**s,'timing':{**s['timing'],'movement_windows':[],
            'target_disappears_seconds':.3}})
        self.assertEqual(vanished['components'][0]['hits'],0)

    def test_frame_rounding_and_target_gaps_use_reacquisition_not_damage_discount(self):
        # Mechanist S3 (1.2+2.3)/2=1.75s=52.5frames, half-up53.
        # 6-frame windup; windows[0,12),[90,120) permit starts0,90.
        # An uptime multiplier cannot reproduce releases6,96.
        s={'operator':'mechanist','skill':3,'base_attack':1000,'window_seconds':4,
            'effects':[{'kind':'attack_speed','value':100}],
            'timing':{'windup_frames':6,'recovery_frames':9,'target_windows':[[0,.4],[3,4]]}}
        r=calculate_damage(s)
        stream=r['timing']['streams'][0]
        self.assertEqual(stream['interval_frames'],53)
        self.assertEqual(stream['release_frames'],[6,96])
        self.assertEqual(r['components'][0]['hits'],1)  # delayed second impact at120 is excluded

    def test_first_release_is_windup_not_one_entire_attack_interval(self):
        # Explicit scenario:6-frame windup,9-frame recovery.
        # In [0,30) a bombardment releases at6; its delayed impact at30 is excluded.
        r=calculate_damage({'operator':'mechanist','skill':3,'base_attack':1000,
            'window_seconds':1,'timing':{'windup_frames':6,'recovery_frames':9}})
        self.assertEqual(r['components'][0]['hits'],0)
        self.assertEqual(r['timing']['streams'][0]['release_frames'],[6])


if __name__=='__main__':unittest.main()
