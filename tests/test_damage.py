import unittest
from rouge.damage import calculate_damage as evaluate_damage


def calculate_damage(scenario):
    # These independent damage/mechanism examples specify the continuous
    # reference model. Default frame scheduling is exercised in test_timing.
    return evaluate_damage({**scenario,'timing_mode':'continuous'})


class DamageTests(unittest.TestCase):
    def test_wine_single_cast_burst_does_not_invent_unverified_recharge_cycle(self):
        result=calculate_damage({'operator':'char_1042_phatm2','skill':1,'base_attack':2000})
        # Two3000 arts hits are independent of the unresolved first buff
        # attachment; no burst schedule or complete cycle is proven.
        self.assertEqual(result['known_damage_subtotals']['total_damage'],6000)
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        self.assertIsNone(result['estimate']['skill']['cycle_damage'])

    def test_deepcolor_global_relics_apply_to_token_without_inheriting_operator_stats(self):
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,'base_attack':1000,
            'enemy_defense':100,'relic_ids':['rogue_6_relic_fight_25','rogue_6_relic_legacy_23_c','rogue_6_relic_legacy_5']})
        token=next(c for c in result['components'] if c['name']=='触手')
        # Rune write: round-even(462*1.3)=601, then skill MULTIPLIER +60%.
        # floor(30/(1.25*100/107))=25; (601*1.6-100)*1.15 per hit.
        self.assertEqual(token['hits'],25)
        self.assertAlmostEqual(token['total'],24771)
        specialist=calculate_damage({'operator':'char_110_deepcl','skill':1,'base_attack':1000,
            'enemy_defense':100,'relic_ids':['rogue_6_relic_legacy_142']})
        self.assertAlmostEqual(next(c for c in specialist['components'] if c['name']=='触手')['total'],15340.8)

    def test_susuro_cannot_cast_a_third_time(self):
        with self.assertRaisesRegex(ValueError,'两次'):
            calculate_damage({'operator':'char_298_susuro','skill':2,'casts_used':2})

    def test_new_exusiai_ammo_and_proc_expectation_do_not_grow_with_attack_speed(self):
        scenario={'operator':'char_1041_angel2','skill':3,'base_attack':1000,'enemy_defense':200}
        result=calculate_damage(scenario)
        # Pot1: own Laterano ammo ATK +18%; S3 +30% =>1480.
        # 50*(1480*1.6-200) + 50*.25*(1480*1.5-200) + (1480*2.5-200).
        self.assertIsNone(result['total_damage'])
        def conditional_total(r):
            return r['known_damage_subtotals']['window_damage']+r['external_event_reference']['conditional_components'][0]['total']
        self.assertEqual(conditional_total(result),137150)
        faster=calculate_damage({**scenario,'effects':[{'kind':'attack_speed','value':100}]})
        self.assertIsNone(faster['total_damage'])
        self.assertEqual(conditional_total(faster),conditional_total(result))
        self.assertLess(faster['estimate']['skill']['duration_seconds'],result['estimate']['skill']['duration_seconds'])

    def test_infinite_skill_uses_window_output_without_inventing_cast_total_or_rotation(self):
        result=calculate_damage({'operator':'char_1042_phatm2','skill':2,'window_seconds':15})
        skill=result['estimate']['skill']
        self.assertIsNone(skill['cycle_seconds'])
        self.assertIsNone(skill['total_damage'])
        self.assertIsNone(skill['duration_seconds'])
        self.assertEqual(skill['window_seconds'],15)
        self.assertGreater(skill['window_dps'],0)

    def test_closure_module_talent_replaces_instead_of_stacking_with_old_talent(self):
        result=calculate_damage({'operator':'char_4228_closur','skill':2,
            'module_id':'uniequip_002_closur','module_level':3})
        # E2 90 480 + trust60 + module30=570; module replaces 4% with8%.
        self.assertAlmostEqual(result['estimate']['base_stats']['attack'],615.6)
        self.assertFalse(result['estimate']['complete'])  # conditional module traits not silently marked complete

    def test_mantra_s2_uses_newly_triggered_neural_break_for_same_and_later_hits(self):
        result=calculate_damage({'operator':'char_4204_mantra','skill':2,'base_attack':1000,
                                 'window_seconds':3.2})
        # 0.8s interval: four 2400 hits, 432 buildup each. Third hit bursts;
        # S2 resolves arts -> neural -> elemental, so hits three and four add 250 each.
        self.assertEqual(result['total_damage'],16100)

    def test_s1_unresolved_buildup_is_not_counted_as_hp_damage_for_either_threshold(self):
        scenario={'operator':'char_1042_phatm2','skill':1,'base_attack':1000,'enemy_resistance':0}
        result=calculate_damage(scenario)
        # Two1500 arts hits and two1000*.30 base neural references. The
        # buff parameter1.8 alone does not prove either hit receives it.
        self.assertEqual(result['known_damage_subtotals']['total_damage'],3000)
        self.assertIsNone(result['total_damage'])
        boss=calculate_damage({**scenario,'enemy_is_boss':True})
        self.assertEqual(boss['known_damage_subtotals']['total_damage'],3000)
        self.assertIsNone(boss['total_damage'])

    def test_chen_weakness_chooses_type_before_type_specific_injury_bonus(self):
        scenario={'operator':'char_1050_chen3','skill':2,'base_attack':1000,
                  'enemy_defense':500,'enemy_resistance':50}
        result=calculate_damage(scenario)
        # Pot1 E2 +13% ATK; ten 480% hits: 5424 - 500 > 5424 * .5.
        slashes=next(c for c in result['unbound_cast_reference']['conditional_components'] if c['name']=='绝影斩击')
        self.assertAlmostEqual(slashes['total'],49240)
        bonus=calculate_damage({**scenario,'effects':[{'kind':'damage_taken','damage_type':'magic','value':2}]})
        self.assertEqual(slashes['total'],next(c for c in bonus['unbound_cast_reference']['conditional_components'] if c['name']=='绝影斩击')['total'])

    def test_gummy_cooking_delay_and_healing_interval_are_included(self):
        result=calculate_damage({'operator':'char_196_sunbr','skill':2,'base_attack':1000})
        # First 10s cooking, then 20s / 2.5s = 8 heals of 1800.
        self.assertEqual(result['estimate']['skill']['total_healing'],14400)
        self.assertEqual(result['estimate']['skill']['total_damage'],0)

    def test_yato_fixed_slashes_are_not_multiplied_by_attack_speed(self):
        scenario={'operator':'char_1029_yato2','skill':2,'base_attack':1000,'enemy_defense':100,'enemy_resistance':50}
        result=calculate_damage(scenario)
        # Pot1 E2: +13% ATK, 16 slashes, 150% physical + 75% arts.
        # 16 * ((1130*1.5-100) + 1130*.75*.5) = 32300.
        refs=result['unbound_cast_reference']['conditional_components']
        self.assertAlmostEqual(sum(c['total'] for c in refs),32300)
        self.assertIsNone(result['total_damage'])
        faster=calculate_damage({**scenario,'effects':[{'kind':'attack_speed','value':100}]})
        self.assertEqual(refs,faster['unbound_cast_reference']['conditional_components'])

    def test_deepcolor_summon_uses_own_level_curve_without_operator_trust_attack(self):
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,'base_attack':1000,
            'summon_count':1,'enemy_defense':100})
        # E2 70 tentacle ATK 462, 1.25s interval; S1 M3 +60%, 30s.
        # 24 tentacle hits of (462 * 1.6 - 100) = 15340.8.
        summon=next(c for c in result['components'] if c['name']=='触手')
        self.assertAlmostEqual(summon['total'],15340.8)
        # Regeneration is shown separately, never counted as direct healing.
        self.assertEqual(result['estimate']['skill']['total_healing'],0)

    def test_myrtle_skill_two_heals_each_second_without_attack_damage(self):
        result=calculate_damage({'operator':'char_151_myrtle','skill':2,'base_attack':1000})
        skill=result['estimate']['skill']
        self.assertEqual(skill['total_damage'],0)
        self.assertEqual(skill['total_healing'],8000)
        self.assertEqual(skill['initial_seconds'],14)
        self.assertEqual(skill['cycle_seconds'],40)

    def test_may_talent_and_relic_are_additive_before_each_physical_hit(self):
        result=calculate_damage({'operator':'char_133_mm','skill':1,'base_attack':1000,
            'enemy_defense':200,'effects':[{'kind':'attack_pct','value':.5}]})
        # E2 potential 1: +7% ATK/+7 ASPD; S1 M3 = 200% ATK.
        # (1000 * (1 + .07 + .5)) * 2 - 200 = 2940.
        self.assertAlmostEqual(result['mei_s1_reference']['parameter_clock_reference']['total_damage'],2940)
        self.assertEqual(result['estimate']['base_stats']['attack_speed'],107)

    def test_partial_run_inventory_is_not_reported_as_complete_or_empty(self):
        result=calculate_damage({'operator':'kaltsit','skill':2,'base_attack':1000,
            'relic_ids':['rogue_6_relic_legacy_3'],
            'inventory_status':{'source':'run_capture','complete':False,'recognized':1,'expected_count':3}})
        self.assertFalse(result['estimate']['complete'])
        self.assertTrue(any('藏品' in note and '未完整' in note for note in result['estimate']['notes']))

    def test_module_attributes_are_derived_from_the_equipped_module_level(self):
        result=calculate_damage({'operator':'mechanist','skill':3,
            'module_id':'uniequip_002_mcnist','module_level':3})
        self.assertEqual(result['estimate']['base_stats']['attack'],673)
        self.assertEqual(result['estimate']['base_stats']['defense'],845)

    def test_shield_skill_can_estimate_a_cast_with_an_explicit_end_time(self):
        skill=calculate_damage({'operator':'mechanist','skill':2,'base_attack':1000,
            'shield_break_count':2,'skill_duration_seconds':20})['estimate']['skill']
        # Two 5000 explosions and 16 ordinary 2500 hits during the skill;
        # 41 ordinary 1000 hits during its 50-second recharge.
        self.assertEqual(skill['total_damage'],50000)
        self.assertEqual(skill['cycle_seconds'],70)
        self.assertEqual(skill['cycle_dps'],1300)

    def test_silverash_shield_skill_is_not_misreported_as_healing(self):
        skill=calculate_damage({'operator':'silverash','skill':1})['estimate']['skill']
        self.assertEqual(skill['initial_seconds'],6)
        self.assertEqual(skill['cycle_seconds'],29)
        self.assertEqual(skill['total_damage'],0)
        self.assertEqual(skill['total_healing'],0)

    def test_kaltsit_skill_three_caps_simultaneous_healing_at_two_allies(self):
        skill=calculate_damage({'operator':'kaltsit','skill':3,'base_attack':1000,
                                'healing_targets':3})['estimate']['skill']
        self.assertEqual(skill['initial_seconds'],15)
        self.assertEqual(skill['cycle_seconds'],85)
        self.assertEqual(skill['total_healing'],130000)
        self.assertEqual(skill['cycle_healing'],147000)

    def test_kaltsit_healing_skill_has_separate_base_and_skill_attack_speed(self):
        result=calculate_damage({'operator':'kaltsit','skill':1,'base_attack':1000,'healing_targets':3})
        stats=result['estimate']['base_stats'];skill=result['estimate']['skill']
        self.assertEqual(stats['attack_speed'],100)
        self.assertEqual(result['attack_speed'],150)
        self.assertEqual(skill['total_damage'],0)
        self.assertEqual(skill['total_healing'],34200)
        self.assertEqual(skill['cycle_hps'],660)

    def test_area_skill_healing_does_not_make_ordinary_healing_hit_multiple_allies(self):
        skill=calculate_damage({'operator':'kaltsit','skill':2,'base_attack':1000,
                                'healing_targets':3})['estimate']['skill']
        self.assertEqual(skill['total_healing'],150000)
        self.assertEqual(skill['cycle_healing'],162000)

    def test_defense_resistance_and_recovery_relics_change_the_matching_fields(self):
        result=calculate_damage({'operator':'mechanist','skill':3,'base_attack':1000,
            'relic_ids':['rogue_6_relic_legacy_69','rogue_6_relic_legacy_2']})
        stats=result['estimate']['base_stats'];skill=result['estimate']['skill']
        self.assertAlmostEqual(stats['hp'],5083)  # rune integer writer: round-even(3631*1.4)
        self.assertAlmostEqual(stats['defense'],1071)
        self.assertEqual(stats['resistance'],20)
        self.assertEqual(stats['attack'],1000)
        self.assertAlmostEqual(skill['initial_seconds'],8.333333333333334)
        self.assertAlmostEqual(skill['recharge_seconds'],29.166666666666668)
        self.assertAlmostEqual(skill['cycle_seconds'],69.16666666666667)
        self.assertTrue(result['complete'])

    def test_attack_recovery_requires_targets_and_is_not_natural_sp_recovery(self):
        scenario={'operator':'mechanist','skill':1,'base_attack':1000,
                  'relic_ids':['rogue_6_relic_legacy_2'],'effects':[{'kind':'attack_speed','value':100}]}
        skill=calculate_damage(scenario)['estimate']['skill']
        self.assertAlmostEqual(skill['initial_seconds'],4.2)
        self.assertAlmostEqual(skill['cycle_seconds'],7.95)
        unknown=calculate_damage({**scenario,'continuous_attacks':False})['estimate']['skill']
        self.assertIsNone(unknown['cycle_seconds'])
        self.assertIsNone(unknown['initial_seconds'])
        self.assertIsNone(unknown['cycle_dps'])

    def test_silverash_self_talents_and_potential_affect_attributes_and_initial_sp(self):
        estimate=calculate_damage({'operator':'silverash','skill':3,'potential':4,
                                   'deployment_elapsed_seconds':15})['estimate']
        self.assertEqual(estimate['base_stats']['hp'],2498)
        self.assertEqual(estimate['base_stats']['defense'],582)
        self.assertEqual(estimate['base_stats']['redeploy_seconds'],56)
        self.assertEqual(estimate['skill']['initial_seconds'],5)
        self.assertEqual(estimate['skill']['cycle_seconds'],103)

    def test_window_damage_does_not_replace_full_single_skill_total(self):
        result=calculate_damage({'operator':'kaltsit','skill':2,'base_attack':1000,'window_seconds':5.7})
        self.assertEqual(result['total_damage'],19000)
        self.assertEqual(result['estimate']['skill']['total_damage'],95000)
        self.assertEqual(result['estimate']['skill']['total_healing'],50000)

    def test_shield_break_count_is_not_enough_to_infer_a_full_cycle(self):
        result=calculate_damage({'operator':'mechanist','skill':2,'base_attack':1000,'shield_break_count':2})
        self.assertEqual(result['total_damage'],10000)
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
        self.assertEqual(result['estimate']['skill']['initial_seconds'],15)

    def test_kaltsit_estimate_reports_attributes_healing_and_full_cycle(self):
        result=calculate_damage({'operator':'kaltsit','skill':2,'skill_rank':10,
            'base_attack':1000,'enemy_defense':9999})
        estimate=result['estimate']
        self.assertEqual(estimate['base_stats']['hp'],2650)
        self.assertAlmostEqual(estimate['base_stats']['defense'],382.5)
        self.assertEqual(estimate['base_stats']['block_count'],2)
        self.assertEqual(estimate['base_stats']['attack_speed'],100)
        skill=estimate['skill']
        self.assertEqual(skill['initial_seconds'],7)
        self.assertEqual(skill['recharge_seconds'],35)
        self.assertEqual(skill['cycle_seconds'],63.5)
        self.assertEqual(skill['total_damage'],95000)
        self.assertEqual(skill['total_healing'],50000)
        # One injured ally: 12 ordinary heals during recharge plus 10 skill heals.
        self.assertAlmostEqual(skill['cycle_hps'],976.3779527559055)
        self.assertAlmostEqual(skill['cycle_dps'],1496.0629921259842)

    def test_invalid_scenario_parameters_are_rejected_before_producing_damage(self):
        for field,value in [('enemy_defense',-1),('enemy_resistance',float('nan')),
                            ('enemy_resistance',101),('window_seconds',-1),
                            ('shield_break_count',-1),('charge_count',1.5),
                            ('deployment_stacks',3),('skill_rank',7.5)]:
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                calculate_damage({'operator':'mechanist','skill':3,'base_attack':1000,field:value})
    def test_attack_speed_interval_is_capped_at_six_times_base(self):
        result=calculate_damage({'operator':'kaltsit','skill':2,'skill_rank':10,'base_attack':1000,
            'effects':[{'kind':'attack_speed','value':1000}]})
        self.assertAlmostEqual(result['interval_seconds'],.475)
    def test_invalid_effect_cannot_produce_a_plausible_result(self):
        for value in [float('nan'), float('inf'), -2]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
                    'base_attack': 1000, 'effects': [{'kind':'attack_pct','value':value}]})
    def test_silverash_skill_two_companion_uses_recipient_attack(self):
        result = calculate_damage({'operator': 'silverash', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_defense': 300, 'activation_count': 1,
            'companion_attack': 2000, 'deployment_stacks': 2})
        # Own 3800-300=3500; recipient two (7600-300) =>18100.
        self.assertAlmostEqual(result['total_damage'], 18100)
    def test_mechanist_shield_explosion_requires_observed_break_count(self):
        result = calculate_damage({'operator': 'mechanist', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_resistance': 50, 'shield_break_count': 2})
        # 2500 ATK * 200% * 50% RES * two observed shield breaks.
        self.assertAlmostEqual(result['total_damage'], 5000)
    def test_skill_rank_seven_uses_non_mastery_profile(self):
        result = calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 7, 'base_attack': 1000})
        # Rank 7: ATK +125%; 350% true damage, ten shots => 78750.
        self.assertAlmostEqual(result['total_damage'], 78750)
    def test_shorter_window_caps_kaltsit_ammunition(self):
        result = calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'window_seconds': 5.7})
        # Steady estimate: two complete 2.85-second firing intervals, 9500 each.
        self.assertEqual(result['hits'], 2)
        self.assertAlmostEqual(result['total_damage'], 19000)
    def test_unknown_collectible_marks_result_incomplete_instead_of_silently_ignoring(self):
        result = calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'relic_ids': ['rogue_6_relic_artifact_7']})
        self.assertFalse(result['complete'])
        self.assertIn('仇名录', ' '.join(result['warnings']))
    def test_physical_relics_stack_in_their_group_after_defense(self):
        result = calculate_damage({'operator': 'mechanist', 'skill': 1, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_defense': 550,
            'relic_ids': ['rogue_6_relic_legacy_5', 'rogue_6_relic_legacy_6']})
        # 1000 after DEF, two same-group +15/+25 => 1400, 15 pellets.
        self.assertAlmostEqual(result['total_damage'], 21000)
    def test_mechanist_magic_bombardment_and_physical_charge_are_separate(self):
        result = calculate_damage({'operator': 'mechanist', 'skill': 3, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_defense': 400, 'enemy_resistance': 50,
            'window_seconds': 3.5, 'charge_count': 1})
        # ATK 3800; bombardment 9880 * .5 = 4940; charge 11400-400=11000.
        self.assertAlmostEqual(result['total_damage'], 15940)
        self.assertEqual({c['damage_type'] for c in result['components']}, {'magic', 'physical'})
    def test_attack_speed_reduces_ammo_time_without_inventing_more_ammo(self):
        result = calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'relic_ids': ['rogue_6_relic_legacy_75']})
        self.assertAlmostEqual(result['total_damage'], 95000)
        self.assertAlmostEqual(result['interval_seconds'], 2.85 / 1.7)
        self.assertEqual(result['hits'], 10)
    def test_silverash_cooperation_uses_silverash_attack_and_separate_stream(self):
        result = calculate_damage({'operator': 'silverash', 'skill': 3, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_defense': 1000, 'cooperative': True,
            'preexisting_fragile': True, 'window_seconds': 2.4, 'companion_attack': 9999})
        # Two hits per stream: (2000-1000)*1.3*2*2 = 5200.
        self.assertAlmostEqual(result['total_damage'], 5200)
        self.assertEqual(len(result['components']), 2)
    def test_collectible_scope_and_type_do_not_leak_into_true_damage(self):
        result = calculate_damage({'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'relic_ids': ['rogue_6_relic_legacy_18', 'rogue_6_relic_legacy_15', 'rogue_6_relic_legacy_5']})
        # Ranged rune +15% precedes skill +150%: 1150*2.5*3.8*10.
        # Melee +15% and physical damage +15% do not apply to true damage.
        self.assertAlmostEqual(result['total_damage'], 109250)
        self.assertIn('rogue_6_relic_legacy_15', result['inapplicable_relics'])
    def test_mechanist_each_pellet_is_reduced_by_defense(self):
        # 1000 ATK, 155% pellet = 1550; DEF 550 leaves 1000.
        # Three ammunition, five pellets each => 15000, not one DEF subtraction.
        result = calculate_damage({'operator': 'mechanist', 'skill': 1, 'skill_rank': 10,
            'base_attack': 1000, 'enemy_defense': 550, 'enemy_resistance': 0})
        self.assertAlmostEqual(result['total_damage'], 15000)
    def test_true_ammo_damage_with_attack_collectible(self):
        # Independent worked example: 1000 base ATK; S2M3 +150% and relic
        # +20% in the same additive ATK group => 2700 ATK; 380% per shot,
        # ten shots => 102600 true damage regardless of DEF/RES.
        result = calculate_damage({
            'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
            'base_attack': 1000, 'base_interval': 2.85,
            'enemy_defense': 9999, 'enemy_resistance': 95,
            'effects': [{'id': 'worked-example', 'kind': 'attack_pct', 'value': 0.20}],
        })
        self.assertAlmostEqual(result['total_damage'], 102600)


if __name__ == '__main__':
    unittest.main()
