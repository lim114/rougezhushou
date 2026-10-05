from tests.offline_scope_retirement import historical_combat_test
"""Truthful Mantra damage chains through public calculate_damage."""
import unittest

from rouge.damage import calculate_damage


class MantraEventTests(unittest.TestCase):
    def test_s1_short_window_excludes_later_hit_and_burst(self):
        result=calculate_damage({'operator':'char_4204_mantra','skill':1,
            'enemy_resistance':0,'initial_neural_buildup':999,'window_seconds':1})
        self.assertEqual(result['total_damage'],0)
        self.assertTrue(all(t<1 for c in result['components'] for t in c.get('times_seconds',[])))
        self.assertGreater(result['estimate']['skill']['total_damage'],0)

    def test_s2_same_hit_burst_attaches_element_after_buildup_and_clips_impact(self):
        args={'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
              'initial_neural_buildup':999,
              'timing':{'windup_frames':6,'recovery_frames':0,'projectile_travel_seconds':.5}}
        for window,total in ((.7,0),(.8,8000.75)):
            with self.subTest(window=window):
                result=calculate_damage({**args,'window_seconds':window})
                # 755*2.4 arts, 6000 source-free burst, then 755*.25 element.
                self.assertAlmostEqual(result['total_damage'],total)
                positive=[c for c in result['components'] if c['total']>0 and c['damage_type']!='buildup']
                for component in positive:
                    self.assertEqual(component['times_seconds'],[.7])

    @historical_combat_test
    def test_s2_first_damage_changes_buildup_before_burst_without_reusing_bonus(self):
        for initial in (600,999):
            with self.subTest(initial=initial):
                args={'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
                      'initial_neural_buildup':initial,'window_seconds':1}
                plain=calculate_damage(args)
                crown=calculate_damage({**args,'relic_ids':['rogue_6_relic_fight_1'],
                    'relic_context':{'enemy_first_damage_unused':1}})
                self.assertAlmostEqual(plain['total_damage'],1812 if initial==600 else 8000.75)
                # First arts 1812*3, its 18% buildup 978.48, one 6000 burst,
                # then 188.75 element. The latter must not consume crown again.
                self.assertAlmostEqual(crown['total_damage'],11624.75)
                buildup=next(c for c in crown['components'] if c['damage_type']=='buildup')
                self.assertAlmostEqual(buildup['total'],978.48)
                attached=next(c for c in crown['components'] if c['name']=='爆发期间附带元素')
                self.assertAlmostEqual(attached['total'],188.75)
                self.assertNotIn('first_damage_relic',attached)
                self.assertTrue(crown['relic_resolution']['complete'])

    @historical_combat_test
    def test_s1_same_hit_order_stays_explicitly_unverified(self):
        args={'operator':'char_4204_mantra','skill':1,'enemy_resistance':0,
              'initial_neural_buildup':999,'window_seconds':2}
        result=calculate_damage(args)
        self.assertAlmostEqual(result['total_damage'],8453.75)
        self.assertFalse(result['estimate']['complete'])
        self.assertTrue(any('共鸣溃缩' in warning and '顺序' in warning for warning in result['warnings']))
        self.assertFalse(any(c['name']=='爆发期间附带元素' and c['total']>0 for c in result['components']))
        # Already breaking is a known condition. The elemental quantity is
        # known, but which same-time source consumes crown remains unknown.
        existing={**args,'initial_neural_buildup':0,'enemy_in_neural_break':True}
        plain=calculate_damage(existing)
        crown=calculate_damage({**existing,'relic_ids':['rogue_6_relic_fight_1'],
            'relic_context':{'enemy_first_damage_unused':1}})
        self.assertAlmostEqual(plain['total_damage'],3963.75)
        self.assertEqual(crown['total_damage'],plain['total_damage'])
        self.assertFalse(crown['relic_resolution']['complete'])

    @historical_combat_test
    def test_s2_full_skill_and_cycle_do_not_depend_on_display_window(self):
        args={'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
              'initial_neural_buildup':600,'relic_ids':['rogue_6_relic_fight_1'],
              'relic_context':{'enemy_first_damage_unused':1}}
        for window in (.7,.8,1,25):
            with self.subTest(window=window):
                result=calculate_damage({**args,'window_seconds':window})
                skill=result['estimate']['skill']
                # 31 arts impacts, first +3624; two 6000 bursts; 26 attached
                # elemental hits. Recharge has 15 plain 755 attacks, no reset.
                self.assertAlmostEqual(skill['total_damage'],76703.5)
                self.assertAlmostEqual(skill['cycle_damage'],88028.5)
                self.assertEqual(skill['cycle_seconds'],50)
                self.assertAlmostEqual(skill['cycle_dps'],1760.57)

    def test_s2_delayed_skill_hits_share_burst_cooldown_across_recharge(self):
        args={'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
              'initial_neural_buildup':999,
              'timing':{'projectile_travel_seconds':10}}
        for window in (1,25):
            with self.subTest(window=window):
                result=calculate_damage({**args,'window_seconds':window})
                skill=result['estimate']['skill']
                # Emitted skill hits land at 10.8..34.8. Its second burst at
                # 23.6 keeps the post-skill impacts in break through 33.2.
                self.assertAlmostEqual(skill['total_damage'],73079.5)
                self.assertAlmostEqual(skill['phase_damage'],47447.25)
                # Only nine recharge projectiles land before cycle end 50.
                self.assertAlmostEqual(skill['cycle_damage'],79874.5)

    def test_s1_full_skill_keeps_a_slow_first_release_beyond_one_attack_interval(self):
        args={'operator':'char_4204_mantra','skill':1,'enemy_resistance':0,
              'initial_neural_buildup':999,
              'timing':{'windup_frames':60,'recovery_frames':0,'projectile_travel_seconds':.5}}
        for window,expected in ((2.5,0),(2.6,8453.75)):
            with self.subTest(window=window):
                result=calculate_damage({**args,'window_seconds':window})
                self.assertAlmostEqual(result['total_damage'],expected)
                self.assertAlmostEqual(result['estimate']['skill']['total_damage'],8453.75)
                self.assertAlmostEqual(result['estimate']['skill']['duration_seconds'],61/30)
                self.assertEqual(result['estimate']['skill']['phase_damage'],0)

    @historical_combat_test
    def test_s2_buildup_events_follow_each_final_damage_amount(self):
        result=calculate_damage({'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
            'initial_neural_buildup':600,'window_seconds':2,
            'relic_ids':['rogue_6_relic_fight_1'],'relic_context':{'enemy_first_damage_unused':1}})
        potential=next(c for c in result['components'] if c['damage_type']=='buildup')
        self.assertEqual(potential['times_seconds'],[.8,1.6])
        self.assertAlmostEqual(potential['event_amounts'][0],978.48)
        self.assertAlmostEqual(potential['event_amounts'][1],326.16)
        self.assertAlmostEqual(sum(potential['event_amounts']),potential['total'])
        burst=next(c for c in result['components'] if c['name']=='神经损伤爆发')
        self.assertEqual(burst['times_seconds'],[.8])
        # The second potential buildup is correctly blocked during the burst.
        self.assertEqual(burst['total'],6000)


if __name__=='__main__':unittest.main()
