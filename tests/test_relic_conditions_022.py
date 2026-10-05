from tests.offline_scope_retirement import historical_combat_test
"""Public calculation scenarios for researched conditional relics."""
import unittest
from rouge.damage import calculate_damage

class RelicConditionsTests(unittest.TestCase):
    @historical_combat_test
    def test_medicine_seeds_are_two_shield_layers_not_hp_barrier_or_healing(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_53']})
        self.assertEqual([(p['kind'],p['value']) for p in r['relic_protection']],[('shield_layers',2)])
        self.assertEqual(r['estimate']['skill']['total_healing'],0)
        block=next(s for s in r['report']['sections'] if s['id']=='relic_protection')
        self.assertEqual([(m['value'],m['unit']) for m in block['metrics']],[(2,'层')])
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_53']})
        self.assertEqual(summon['relic_token_stats'][0]['protection'][0]['value'],2)

    @historical_combat_test
    def test_dodge_relics_report_per_source_and_type_without_adding_probabilities_or_dps(self):
        args={'operator':'mechanist','skill':3}
        base=calculate_damage(args)
        result=calculate_damage({**args,'relic_ids':['rogue_6_relic_legacy_128',
            'rogue_6_relic_legacy_129','rogue_6_relic_legacy_130']})
        entries=result['relic_protection']
        self.assertEqual([(p['damage_type'],p['value']) for p in entries],
            [('physical',.15),('magic',.15),('physical',.1),('magic',.1)])
        self.assertEqual(result['total_damage'],base['total_damage'])
        self.assertEqual(result['estimate']['skill']['cycle_seconds'],base['estimate']['skill']['cycle_seconds'])
        block=next(s for s in result['report']['sections'] if s['id']=='relic_protection')
        self.assertEqual([m['value'] for m in block['metrics']],[15,15,10,10])
        self.assertNotIn('true',[p['damage_type'] for p in entries])
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_128']})
        self.assertEqual(summon['relic_token_stats'][0]['protection'][0]['value'],.15)

    @historical_combat_test
    def test_deployment_barriers_use_own_hp_and_keep_tokens_separate_from_high_tile_operators(self):
        args={'operator':'mechanist','skill':3}
        baseline=calculate_damage(args)
        barrier=calculate_damage({**args,'relic_ids':['rogue_6_relic_legacy_101']})
        self.assertEqual(barrier['relic_protection'][0]['value'],1815.5)
        self.assertEqual(barrier['total_damage'],baseline['total_damage'])
        self.assertEqual(barrier['estimate']['skill']['total_healing'],0)
        self.assertIn('relic_protection',[s['id'] for s in barrier['report']['sections']])
        self.assertNotIn('relic_protection',[s['id'] for s in baseline['report']['sections']])
        ranged=calculate_damage({'operator':'char_110_deepcl','skill':1,
            'relic_ids':['rogue_6_relic_legacy_101','rogue_6_relic_fight_7']})
        self.assertEqual([(p['relic_id'],p['value']) for p in ranged['relic_protection']],
            [('rogue_6_relic_fight_7',1350)])
        self.assertEqual(ranged['relic_token_stats'][0]['protection'][0]['value'],1008)
        self.assertEqual(ranged['relic_token_stats'][0]['protection'][0]['relic_id'],'rogue_6_relic_legacy_101')

    def test_mercenary_ornament_requires_recipient_and_count_already_includes_initial_layer(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_136']}
        missing=calculate_damage({**args,'relic_context':{'mercenary_stacks':10}})
        self.assertIn('mercenary_recipient',missing['relic_resolution']['records'][0]['missing_conditions'])
        not_recipient=calculate_damage({**args,'relic_context':{'mercenary_recipient':0}})
        self.assertEqual(not_recipient['estimate']['base_stats']['attack'],573)
        # Rune writer rounds HP/ATK before ordinary skill multipliers.
        for count,attack,hp in ((1,602,3813),(10,860,5446),(11,860,5446)):
            result=calculate_damage({**args,'relic_context':{'mercenary_recipient':1,'mercenary_stacks':count}})
            self.assertAlmostEqual(result['estimate']['base_stats']['attack'],attack)
            self.assertAlmostEqual(result['estimate']['base_stats']['hp'],hp)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids'],
            'relic_context':{'mercenary_recipient':1,'mercenary_stacks':10}})
        self.assertFalse(summon['relic_token_stats'])

    @historical_combat_test
    def test_dog_aura_needs_active_other_sources_and_never_inherits_to_tokens(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_artifact_4']}
        unknown=calculate_damage(args)
        self.assertIn('active_other_aura_sources',unknown['relic_resolution']['records'][0]['missing_conditions'])
        for count,attack in ((0,573),(1,630.3),(3,744.9)):
            result=calculate_damage({**args,'relic_context':{'active_other_aura_sources':count}})
            self.assertAlmostEqual(result['estimate']['base_stats']['attack'],attack)
        summon=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':args['relic_ids'],
            'relic_context':{'active_other_aura_sources':2}})
        self.assertFalse(summon['relic_token_stats'])

    def test_swaddled_dragon_uses_entered_area_counter_not_current_floor(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_start_3'],
            'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_2137_shsdgo','level':0},
            'run_config':{'zone':{'id':'zone_1'}}}
        unknown=calculate_damage(args)
        self.assertIn('entered_zone_count',unknown['relic_resolution']['records'][0]['missing_conditions'])
        for entered,hp in ((1,9000),(2,9000),(3,18000),(6,18000)):
            result=calculate_damage({**args,'relic_context':{'entered_zone_count':entered}})
            self.assertEqual(result['run_resolution']['enemy']['stats']['maxHp'],hp)
            self.assertTrue(result['relic_resolution']['complete'])

    def test_hunting_seal_uses_confirmed_probe_layers_and_only_proto_enemy(self):
        args={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_cargo_12'],
            'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_2137_shsdgo','level':0}}
        unknown=calculate_damage(args)
        self.assertIn('probe_stacks',unknown['relic_resolution']['records'][0]['missing_conditions'])
        result=calculate_damage({**args,'relic_context':{'probe_stacks':2}})
        self.assertEqual(result['estimate']['base_stats']['resistance'],20)
        # The fixed stage reference has 280 ATK; Hunting Seal halves this enemy only.
        self.assertEqual(result['run_resolution']['enemy']['stats']['atk'],140)
        self.assertTrue(result['relic_resolution']['complete'])
        high=calculate_damage({**args,'relic_context':{'probe_stacks':99}})
        self.assertEqual(high['estimate']['base_stats']['resistance'],100)
        other=calculate_damage({**args,'target_enemy':{**args['target_enemy'],'enemy_id':'enemy_1093_ccsbr'},
            'relic_context':{'probe_stacks':2}})
        self.assertEqual(other['estimate']['base_stats']['resistance'],20)
        control=calculate_damage({**args,'relic_ids':[],
            'target_enemy':{**args['target_enemy'],'enemy_id':'enemy_1093_ccsbr'}})
        self.assertEqual(other['run_resolution']['enemy']['stats'],control['run_resolution']['enemy']['stats'])
