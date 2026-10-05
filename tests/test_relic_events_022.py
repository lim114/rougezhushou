from tests.offline_scope_retirement import historical_combat_test
"""Public calculation regressions for ordered collectible damage events."""
import unittest

from rouge.damage import calculate_damage


class RelicEventTests(unittest.TestCase):
    @historical_combat_test
    def test_summon_damage_does_not_consume_owners_first_hit_in_recharge(self):
        args={'operator':'char_110_deepcl','skill':1,'enemy_resistance':0,
              'timing':{'target_windows':[[30,100]]}}
        plain=calculate_damage(args)
        crown=calculate_damage({**args,'relic_ids':['rogue_6_relic_fight_1'],
            'relic_context':{'enemy_first_damage_unused':1}})
        # The tentacle attacks during the 30-second skill, while its owner
        # only acquires the target afterwards. Her first 403 hit is still free.
        self.assertEqual(crown['total_damage'],plain['total_damage'])
        self.assertAlmostEqual(crown['estimate']['skill']['cycle_damage']-
            plain['estimate']['skill']['cycle_damage'],806)
        self.assertTrue(crown['relic_resolution']['complete'])

    @historical_combat_test
    def test_source_free_neural_burst_cannot_consume_operator_first_damage(self):
        args={'operator':'char_1042_phatm2','skill':3,'initial_neural_buildup':999,
              'enemy_resistance':0}
        plain=calculate_damage(args)
        crown=calculate_damage({**args,'relic_ids':['rogue_6_relic_fight_1'],
            'relic_context':{'enemy_first_damage_unused':1}})
        # The opening 1192.5 arts hit gets the bonus; the concurrent 6000
        # source-free neural burst neither receives nor consumes it.
        self.assertAlmostEqual(crown['total_damage']-plain['total_damage'],2385)
        self.assertTrue(crown['relic_resolution']['complete'])
        for result in (plain,crown):
            burst=next(c for c in result['components'] if c['name']=='神经损伤爆发')
            self.assertEqual(burst['per_hit'],6000)
            self.assertNotIn('first_damage_relic',burst)
        self.assertAlmostEqual(crown['estimate']['skill']['cycle_damage']-
            plain['estimate']['skill']['cycle_damage'],2385)

    def test_continuous_ammo_refill_extends_full_skill_and_cycle_duration(self):
        args={'operator':'kaltsit','skill':2,'timing_mode':'continuous'}
        plain=calculate_damage(args)
        refilled=calculate_damage({**args,'relic_ids':['rogue_6_relic_legacy_140']})
        skill=refilled['estimate']['skill']
        # Ten 2.85-second attacks become fifteen after the once-only 50% refill.
        self.assertEqual(refilled['hits'],15)
        self.assertAlmostEqual(skill['duration_seconds'],42.75)
        self.assertAlmostEqual(skill['cycle_seconds'],77.75)
        self.assertAlmostEqual(skill['recharge_seconds'],35)
        self.assertAlmostEqual(skill['total_damage'],72675)
        self.assertAlmostEqual(skill['cycle_dps'],934.7266881028939)
        self.assertEqual(plain['estimate']['skill']['duration_seconds'],28.5)

    @historical_combat_test
    def test_simultaneous_distinct_damage_sources_do_not_invent_first_hit_order(self):
        for skill in (1,2):
            with self.subTest(skill=skill):
                args={'operator':'char_437_mizuki','skill':skill,'enemy_defense':100}
                plain=calculate_damage(args)
                selected={**args,'relic_ids':['rogue_6_relic_fight_2']}
                unresolved=calculate_damage({**selected,
                    'relic_context':{'enemy_first_damage_unused':1}})
                self.assertEqual(unresolved['total_damage'],plain['total_damage'])
                self.assertFalse(unresolved['relic_resolution']['complete'])
                self.assertEqual(unresolved['relic_resolution']['records'][0]['status'],'incomplete')
                self.assertTrue(any('首伤藏品' in warning for warning in unresolved['warnings']))
                used=calculate_damage({**selected,'relic_context':{'enemy_first_damage_unused':0}})
                self.assertEqual(used['total_damage'],plain['total_damage'])
                self.assertTrue(used['relic_resolution']['complete'])

    @historical_combat_test
    def test_first_damage_also_updates_incantation_medic_damage_based_healing(self):
        for skill,extra in ((1,1154),(2,2308)):
            with self.subTest(skill=skill):
                args={'operator':'char_1037_amiya3','skill':skill,
                      'enemy_defense':100,'enemy_resistance':0}
                plain=calculate_damage(args)
                crown=calculate_damage({**args,'relic_ids':['rogue_6_relic_fight_1'],
                    'relic_context':{'enemy_first_damage_unused':1}})
                self.assertEqual(crown['total_damage']-plain['total_damage'],extra)
                self.assertEqual(crown['total_healing']-plain['total_healing'],extra/2)
                for field in ('total_healing','phase_healing','cycle_healing'):
                    before=plain['estimate']['skill'][field]
                    after=crown['estimate']['skill'][field]
                    if before is not None:self.assertEqual(after-before,extra/2)
                empty=calculate_damage({**args,'healing_targets':0,
                    'relic_ids':['rogue_6_relic_fight_1'],
                    'relic_context':{'enemy_first_damage_unused':1}})
                self.assertEqual(empty['total_healing'],0)
                rose=calculate_damage({**args,'relic_ids':['rogue_6_relic_fight_1',
                    'rogue_6_relic_legacy_81'],'relic_context':{'enemy_first_damage_unused':1}})
                self.assertAlmostEqual(rose['total_healing'],crown['total_healing']*1.2)
                for field in ('total_healing','phase_healing','cycle_healing'):
                    expected=crown['estimate']['skill'][field]
                    if expected is not None:
                        self.assertAlmostEqual(rose['estimate']['skill'][field],expected*1.2)
                linked=next(c for c in rose['components'] if c['name']=='咒愈师伤害转治疗')
                self.assertAlmostEqual(sum(linked['event_amounts']),linked['total'])

    @historical_combat_test
    def test_first_damage_healing_respects_projectile_window_boundary(self):
        args={'operator':'char_1037_amiya3','skill':1,'enemy_resistance':0,
              'timing':{'windup_frames':6,'recovery_frames':0,'projectile_travel_seconds':.5}}
        for window,damage,healing in ((.7,0,0),(.8,1154,577)):
            with self.subTest(window=window):
                selected={**args,'window_seconds':window}
                plain=calculate_damage(selected)
                crown=calculate_damage({**selected,'relic_ids':['rogue_6_relic_fight_1'],
                    'relic_context':{'enemy_first_damage_unused':1}})
                self.assertEqual(crown['total_damage']-plain['total_damage'],damage)
                self.assertEqual(crown['total_healing']-plain['total_healing'],healing)
                # Selecting a smaller display window cannot truncate the complete
                # skill or consume the first hit in the full-cycle calculation.
                self.assertEqual(crown['estimate']['skill']['total_healing']-
                    plain['estimate']['skill']['total_healing'],577)
                self.assertEqual(crown['estimate']['skill']['cycle_healing']-
                    plain['estimate']['skill']['cycle_healing'],577)
