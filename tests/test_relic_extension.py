from tests.offline_scope_retirement import historical_combat_test
"""Out-of-battle collectible scenarios through the shared calculation/report interface."""
import unittest
from rouge.damage import calculate_damage

class RelicExtensionTests(unittest.TestCase):
    @historical_combat_test
    def test_city_wall_condition_does_not_buff_tokens_or_increase_damage(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_58']}
        missing=calculate_damage(args)
        self.assertIn('near_protection_point',missing['relic_resolution']['records'][0]['missing_conditions'])
        outside=calculate_damage({**args,'relic_context':{'near_protection_point':0}})
        near=calculate_damage({**args,'relic_context':{'near_protection_point':1}})
        self.assertEqual(near['estimate']['base_stats']['block_count'],outside['estimate']['base_stats']['block_count']+2)
        self.assertAlmostEqual(near['estimate']['base_stats']['hp'],3631*1.5)
        self.assertEqual(near['estimate']['skill']['total_damage'],outside['estimate']['skill']['total_damage'])
        with self.assertRaises(ValueError):calculate_damage({**args,'relic_context':{'near_protection_point':2}})

    def test_ya_ji_refills_once_and_extends_skill_duration_and_recharge_cycle(self):
        args={'operator':'kaltsit','skill':2}
        base=calculate_damage(args)
        r=calculate_damage({**args,'relic_ids':['rogue_6_relic_legacy_140']})
        self.assertEqual(r['hits'],15)
        self.assertAlmostEqual(r['estimate']['skill']['total_damage'],base['estimate']['skill']['total_damage']*1.5)
        self.assertGreater(r['estimate']['skill']['duration_seconds'],base['estimate']['skill']['duration_seconds'])
        self.assertEqual(r['estimate']['skill']['recharge_seconds'],base['estimate']['skill']['recharge_seconds'])
        self.assertTrue(r['relic_resolution']['complete'])
        fractional=calculate_damage({'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_140']})
        self.assertTrue(fractional['relic_resolution']['complete'])
        # Three shots have a floor(30%)=0 threshold. Positive-ammo checks
        # cannot refill after exhaustion, even though the quota rounds to two.
        base=calculate_damage({'operator':'mechanist','skill':1})
        self.assertEqual(fractional['total_damage'],base['total_damage'])
        self.assertEqual(fractional['estimate']['skill'],base['estimate']['skill'])

    @historical_combat_test
    def test_crown_boosts_one_damage_event_and_does_not_repeat_during_recharge(self):
        args={'operator':'char_133_mm','skill':2,'base_attack':1000,'enemy_defense':100}
        base=calculate_damage(args)
        selected={**args,'relic_ids':['rogue_6_relic_fight_1']}
        missing=calculate_damage(selected)
        self.assertIn('enemy_first_damage_unused',missing['relic_resolution']['records'][0]['missing_conditions'])
        boosted=calculate_damage({**selected,'relic_context':{'enemy_first_damage_unused':1}})
        # S2 +120%, E2 talent +7%; (1000*2.27-100)*2 extra first-hit damage.
        self.assertEqual(boosted['total_damage']-base['total_damage'],4340)
        self.assertEqual(boosted['estimate']['skill']['total_damage']-base['estimate']['skill']['total_damage'],4340)
        self.assertEqual(boosted['estimate']['skill']['cycle_damage']-base['estimate']['skill']['cycle_damage'],4340)
        used=calculate_damage({**selected,'relic_context':{'enemy_first_damage_unused':0}})
        self.assertEqual(used['total_damage'],base['total_damage'])

    def test_grudge_layers_are_battle_multiplier_after_two_percent_rune(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_artifact_7'],
              'effects':[{'kind':'attack_pct','value':.2}]}
        missing=calculate_damage(args)
        self.assertIn('grudge_stacks',missing['relic_resolution']['records'][0]['missing_conditions'])
        # Static rune round-even(573*1.02)=584. The confirmed layer buff
        # is ATK MULTIPLIER, added to manual +20%, not a final scaler.
        for stacks,attack in ((0,700.8),(100,817.6),(999,1867.632),(2000,1867.632)):
            r=calculate_damage({**args,'relic_context':{'grudge_stacks':stacks}})
            self.assertAlmostEqual(r['estimate']['base_stats']['attack'],attack)
            self.assertTrue(r['relic_resolution']['complete'])
        summoner=calculate_damage({'operator':'char_110_deepcl','skill':1,
            'relic_ids':['rogue_6_relic_artifact_7'],'relic_context':{'grudge_stacks':100}})
        self.assertFalse(summoner['relic_token_stats'])

    @historical_combat_test
    def test_castle_resident_waits_eighty_deployed_seconds_and_adds_flat_defense(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_63']}
        missing=calculate_damage(args)
        self.assertIn('deployed_seconds',missing['relic_resolution']['records'][0]['missing_conditions'])
        for time,defense,res in ((79.9,765,0),(80,1165,30),(100,1165,30)):
            r=calculate_damage({**args,'relic_context':{'deployed_seconds':time}})
            self.assertEqual(r['estimate']['base_stats']['defense'],defense)
            self.assertEqual(r['estimate']['base_stats']['resistance'],res)

    def test_empty_bed_uses_empty_capacity_not_owned_count_and_requires_evidence(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_cargo_3']}
        missing=calculate_damage(args)
        self.assertIn('empty_slots',missing['relic_resolution']['records'][0]['missing_conditions'])
        # The native condition needs actual capacity minus inventory count.
        # Without it, the unmodified cost is not the predicted current cost.
        self.assertIsNone(missing['deployment_cost'])
        self.assertIn('empty_slots',missing['deployment_reference']['cost']['missing_conditions'])
        for empty,cost in ((3,23),(4,17),(12,17)):
            r=calculate_damage({**args,'relic_context':{'empty_slots':empty}})
            self.assertEqual(r['deployment_cost'],cost)
            self.assertTrue(r['relic_resolution']['complete'])

    def test_altar_uses_confirmed_layers_not_battle_count_probability_or_compounding(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_103']}
        missing=calculate_damage(args)
        self.assertIn('altar_stacks',missing['relic_resolution']['records'][0]['missing_conditions'])
        self.assertEqual(missing['estimate']['base_stats']['attack'],573)
        # CAttributeMulByLayer accumulates rune multipliers; integer fields
        # round to even at AttributesData write before any battle buff.
        for stacks,atk,defense in [(0,573,765),(3,659,880),(10,860,1148),(100,860,1148)]:
            with self.subTest(stacks=stacks):
                result=calculate_damage({**args,'relic_context':{'altar_stacks':stacks}})
                self.assertAlmostEqual(result['estimate']['base_stats']['attack'],atk)
                self.assertAlmostEqual(result['estimate']['base_stats']['defense'],defense)
                self.assertTrue(result['relic_resolution']['complete'])
                self.assertEqual(result['estimate']['skill']['cycle_seconds'],75)  #40s skill +35s natural recharge
        mixed=calculate_damage({**args,'effects':[{'kind':'attack_pct','value':.2}],
            'relic_context':{'altar_stacks':3}})
        self.assertAlmostEqual(mixed['estimate']['base_stats']['attack'],659*1.2)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids'],
            'relic_context':{'altar_stacks':3}})
        self.assertAlmostEqual(summon['estimate']['base_stats']['attack'],463)
        self.assertAlmostEqual(summon['relic_token_stats'][0]['attack'],531)

    def test_chitin_random_recipient_is_explicit_and_does_not_buff_the_team_or_tokens(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_52']}
        missing=calculate_damage(args)
        self.assertIn('chitin_recipient',missing['relic_resolution']['records'][0]['missing_conditions'])
        for recipient,atk,hp in [(0,573,3631),(1,1146,7262)]:
            result=calculate_damage({**args,'relic_context':{'chitin_recipient':recipient}})
            self.assertEqual(result['estimate']['base_stats']['attack'],atk)
            self.assertEqual(result['estimate']['base_stats']['hp'],hp)
            self.assertEqual(result['estimate']['skill']['cycle_seconds'],75)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids'],
            'relic_context':{'chitin_recipient':1}})
        self.assertEqual(summon['estimate']['base_stats']['attack'],806)
        self.assertFalse(summon['relic_token_stats'])
        with self.assertRaises(ValueError):calculate_damage({**args,'relic_context':{'chitin_recipient':2}})

    def test_lake_shield_uses_battle_start_run_shields_and_reaches_independent_tokens(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_57']}
        missing=calculate_damage(args)
        self.assertIn('battle_start_shields',missing['relic_resolution']['records'][0]['missing_conditions'])
        for count,hp in [(0,3631),(1,5809.6),(5,5809.6)]:
            result=calculate_damage({**args,'relic_context':{'battle_start_shields':count}})
            self.assertAlmostEqual(result['estimate']['base_stats']['hp'],hp)
            self.assertEqual(result['estimate']['base_stats']['attack'],573)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids'],
            'relic_context':{'battle_start_shields':2}})
        self.assertEqual(summon['estimate']['base_stats']['hp'],2160)
        self.assertAlmostEqual(summon['relic_token_stats'][0]['hp'],3225.6)
        self.assertEqual(summon['relic_token_stats'][0]['attack'],462)

    @historical_combat_test
    def test_glory_uses_actual_blocked_count_and_independent_summon_conditions(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_100']}
        missing=calculate_damage(args)
        self.assertIn('blocked_enemies',missing['relic_resolution']['records'][0]['missing_conditions'])
        for count,atk in [(0,573),(1,1146),(2,573)]:
            result=calculate_damage({**args,'relic_context':{'blocked_enemies':count}})
            self.assertEqual(result['estimate']['base_stats']['attack'],atk)
        summon_args={'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids']}
        missing_token=calculate_damage({**summon_args,'relic_context':{'blocked_enemies':1}})
        self.assertEqual(missing_token['estimate']['base_stats']['attack'],806)
        self.assertFalse(missing_token['relic_token_stats'])
        self.assertTrue(any('token_conditions' in field for field in missing_token['relic_resolution']['records'][0]['missing_conditions']))
        independent=calculate_damage({**summon_args,'relic_context':{'blocked_enemies':0,
            'token_conditions':{'token_10001_deepcl_tentac':{'blocked_enemies':1}}}})
        self.assertEqual(independent['estimate']['base_stats']['attack'],403)
        self.assertEqual(independent['relic_token_stats'][0]['attack'],924)

    def test_perfume_scales_with_supported_hp_and_regeneration_but_is_not_direct_hps(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_91']}
        result=calculate_damage(args)
        self.assertAlmostEqual(result['relic_regeneration_rate'],36.31)
        self.assertEqual(result['estimate']['skill']['total_healing'],0)
        self.assertEqual(result['estimate']['skill']['cycle_hps'],0)
        mixed=calculate_damage({**args,'relic_ids':args['relic_ids']+['rogue_6_relic_legacy_57',
            'rogue_6_relic_legacy_22','rogue_6_relic_legacy_81'],
            'relic_context':{'battle_start_shields':1}})
        self.assertAlmostEqual(mixed['relic_regeneration_rate'],73.3152)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,
            'relic_ids':['rogue_6_relic_legacy_91','rogue_6_relic_legacy_81']})
        self.assertAlmostEqual(summon['relic_regeneration_rate'],16.2)
        self.assertAlmostEqual(summon['relic_token_stats'][0]['regeneration_rate'],24.192)

    def test_probe_only_changes_chosen_proto_enemy_and_composes_with_difficulty_and_relic(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_fight_30'],
            'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_2137_shsdgo','level':0},
            'run_config':{'difficulty':{'value':15},'zone':{'id':'zone_1'}}}
        missing=calculate_damage(args)
        self.assertIn('probe_stacks',missing['relic_resolution']['records'][0]['missing_conditions'])
        result=calculate_damage({**args,'relic_context':{'probe_stacks':2}})
        self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['maxHp'],58968)
        self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['atk'],540.96)
        mixed=calculate_damage({**args,'relic_context':{'probe_stacks':2},
            'relic_ids':args['relic_ids']+['rogue_6_relic_legacy_84']})
        self.assertAlmostEqual(mixed['run_resolution']['enemy']['stats']['maxHp'],56019.6)
        other=calculate_damage({**args,'target_enemy':{**args['target_enemy'],'enemy_id':'enemy_1093_ccsbr'},
            'relic_context':{'probe_stacks':2}})
        self.assertAlmostEqual(other['run_resolution']['enemy']['stats']['maxHp'],4056)
        self.assertIn('rogue_6_relic_fight_30',other['inapplicable_relics'])
        self.assertEqual(result['estimate']['skill']['cycle_seconds'],75)
        self.assertEqual(result['estimate']['base_stats']['attack'],573)

    def test_flat_and_ratio_regeneration_are_both_counted_for_independent_summons(self):
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,
            'relic_ids':['rogue_6_relic_legacy_91','rogue_6_relic_legacy_22','rogue_6_relic_legacy_81']})
        self.assertAlmostEqual(result['relic_regeneration_rate'],19.8)
        self.assertAlmostEqual(result['relic_token_stats'][0]['regeneration_rate'],27.792)
        plain=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_22']})
        self.assertEqual(plain['relic_token_stats'][0]['regeneration_rate'],3)
