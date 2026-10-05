"""Public offline behavior for parts caps, enemy scaling and first-deploy costs."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

RED='rogue_6_relic_cargo_2'
HYDRA='rogue_6_start_4'
LIGHT='rogue_6_relic_book_3'


class OfflineRelics031Tests(unittest.TestCase):
    def test_red_zero_count_is_confirmed_zero_and_complete(self):
        s={'operator':'mechanist','skill':3}
        r=calculate_damage({**s,'relic_ids':[RED],'relic_context':{'parts_count':0}})
        self.assertEqual(r['estimate']['base_stats'],calculate_damage(s)['estimate']['base_stats'])
        self.assertTrue(r['relic_resolution']['complete'])

    def test_red_count_uses_parts_not_capacity_or_estimated_value(self):
        s={'operator':'mechanist','skill':3,'base_attack':1000}
        base=calculate_damage(s)['estimate']['base_stats']
        r=calculate_damage({**s,'relic_ids':[RED],'relic_context':{'parts_count':3,'capacity':12,'valuation':99}})
        self.assertEqual(r['estimate']['base_stats']['attack'],1240)
        self.assertAlmostEqual(r['estimate']['base_stats']['hp'],base['hp']*1.24)
        self.assertTrue(r['relic_resolution']['complete'])

    def test_red_counter_stops_at_ninety_nine(self):
        s={'operator':'mechanist','skill':3,'base_attack':1000,'relic_ids':[RED]}
        for count in (99,100,10000):
            r=calculate_damage({**s,'relic_context':{'parts_count':count}})
            self.assertAlmostEqual(r['estimate']['base_stats']['attack'],8920)
            self.assertEqual(r['relic_resolution']['records'][0]['pending'],[])
        self.assertIn('99',format_estimate(r))

    def test_red_missing_count_stays_unknown_and_invalid_count_is_rejected(self):
        s={'operator':'mechanist','skill':3,'relic_ids':[RED]}
        missing=calculate_damage(s)
        self.assertEqual(missing['relic_resolution']['records'][0]['missing_conditions'],['parts_count'])
        self.assertFalse(missing['relic_resolution']['complete'])
        for count in (-1,1.5,True,float('inf'),'3'):
            with self.subTest(count=count),self.assertRaises(ValueError):
                calculate_damage({**s,'relic_context':{'parts_count':count}})

    def test_red_does_not_duplicate_or_inherit_profession_to_tokens(self):
        s={'operator':'char_110_deepcl','skill':1,'relic_context':{'parts_count':4}}
        one=calculate_damage({**s,'relic_ids':[RED]})
        duplicate=calculate_damage({**s,'relic_ids':[RED,RED]})
        self.assertEqual(one['estimate']['base_stats'],duplicate['estimate']['base_stats'])
        self.assertFalse(one['relic_token_stats'])

    def test_red_attribute_bonus_is_additive_with_existing_stat_percent(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'base_attack':1000,
            'effects':[{'kind':'attack_pct','value':.2}], 'relic_ids':[RED],'relic_context':{'parts_count':4}})
        self.assertAlmostEqual(r['estimate']['base_stats']['attack'],1520)

    def target(self,enemy='enemy_1093_ccsbr'):
        return {'stage_id':'ro6_n_1_2','enemy_id':enemy,'level':0}

    def test_hydra_scales_enemy_attack_and_hp_after_environment(self):
        s={'operator':'mechanist','skill':3,'target_enemy':self.target(),
           'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_2'}}}
        base=calculate_damage(s)
        r=calculate_damage({**s,'relic_ids':[HYDRA]})
        before=base['run_resolution']['enemy']['stats'];after=r['run_resolution']['enemy']['stats']
        for key in ('atk','maxHp'):self.assertAlmostEqual(after[key],before[key]*1.3)
        for key in ('def','magicResistance'):self.assertEqual(after[key],before[key])
        self.assertEqual(r['estimate']['base_stats'],base['estimate']['base_stats'])
        self.assertEqual(r['estimate']['skill'],base['estimate']['skill'])

    def test_hydra_missing_target_does_not_invent_an_enemy(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':[HYDRA]})
        self.assertEqual(r['relic_resolution']['enemy_effects']['atk_factors'],[1.3])
        self.assertNotIn('enemy',r['run_resolution'])

    def test_hydra_zone_growth_and_lifetime_are_not_inferred_from_depth(self):
        s={'operator':'mechanist','skill':3}
        base=calculate_damage(s)['estimate']['base_stats']
        r=calculate_damage({**s,'relic_ids':[HYDRA],'relic_context':{'entered_zone_count':5},
                           'run_config':{'zone':{'id':'zone_5'}}})
        self.assertEqual(r['estimate']['base_stats'],base)
        self.assertFalse(r['relic_resolution']['complete'])
        self.assertTrue(any('zone_into_buff' in p for p in r['relic_resolution']['records'][0]['pending']))
        self.assertFalse(any('enemy_atk_down' in p for p in r['relic_resolution']['records'][0]['pending']))

    def test_hydra_and_hunt_mark_use_independent_enemy_final_scalers_for_the_hound(self):
        s={'operator':'mechanist','skill':3,'target_enemy':self.target('enemy_2137_shsdgo')}
        base=calculate_damage(s)
        r=calculate_damage({**s,'relic_ids':[HYDRA,'rogue_6_relic_cargo_12'], 'relic_context':{'probe_stacks':1}})
        # Both are FINAL_SCALER channels: 1.3 from Hydra, .5 for the selected hound.
        self.assertAlmostEqual(r['run_resolution']['enemy']['stats']['atk'],
                               base['run_resolution']['enemy']['stats']['atk']*.65)
        self.assertFalse(any('enemy_atk_down' in w and '尚未核验' in w for w in r['warnings']))
        self.assertFalse(r['relic_resolution']['complete'])  # Hydra region history is still unknown.
        self.assertTrue(any('zone_into_buff' in p for row in r['relic_resolution']['records'] for p in row['pending']))
        other=calculate_damage({**s,'target_enemy':self.target(),'relic_ids':[HYDRA,'rogue_6_relic_cargo_12'],
                               'relic_context':{'probe_stacks':1}})
        clean=calculate_damage({**s,'target_enemy':self.target(),'relic_ids':[HYDRA]})
        self.assertEqual(other['run_resolution']['enemy']['stats'],clean['run_resolution']['enemy']['stats'])

    def test_first_card_fee_keeps_unrounded_diagnostic_and_floored_native_estimate(self):
        s={'operator':'mechanist','skill':3}
        base=calculate_damage(s)
        r=calculate_damage({**s,'relic_ids':[LIGHT]})
        fee=r['deployment_reference']['first_deployment_cost']
        self.assertEqual(fee['unrounded_single_item_reference'],5.75)
        self.assertEqual(fee['card_factor'],.25)
        self.assertEqual(fee['combined_reference'],5)
        self.assertEqual(fee['estimated_cost'],5)
        self.assertIsNone(fee['actual_cost'])
        self.assertEqual(r['deployment_cost'],5)
        self.assertFalse(fee['live_first_deployment_verified'])
        self.assertTrue(fee['first_deployment_only'])
        self.assertEqual(r['estimate']['base_stats'],base['estimate']['base_stats'])
        self.assertEqual(r['estimate']['skill'],base['estimate']['skill'])

    def test_first_card_fee_uses_potential_and_is_not_reapplied_by_recalculation(self):
        s={'operator':'mechanist','skill':3,'potential':6,'relic_ids':[LIGHT,LIGHT]}
        before=copy.deepcopy(s);r=calculate_damage(s)
        self.assertEqual(r['deployment_reference']['first_deployment_cost']['unrounded_single_item_reference'],5.25)
        self.assertEqual(r['deployment_reference'],calculate_damage(s)['deployment_reference'])
        self.assertEqual(s,before)

    def test_first_card_fee_is_hidden_and_inapplicable_for_non_tanks_and_tokens(self):
        for op in ('kaltsit','char_110_deepcl','silverash'):
            s={'operator':op,'skill':1};base=calculate_damage(s)
            r=calculate_damage({**s,'relic_ids':[LIGHT]})
            self.assertNotIn('deployment_reference',r)
            self.assertEqual(r['deployment_cost'],base['deployment_cost'])
            self.assertEqual(r['warnings'],base['warnings'])
            self.assertEqual(r['relic_resolution']['records'][0]['status'],'inapplicable')
            self.assertFalse(r['relic_token_stats'])

    def test_first_card_and_proved_rune_modifiers_follow_integer_then_card_order(self):
        # Fixed source costs: * .5, -1 and +2. Rune integers precede card floor.
        for rid,expected in (('rogue_6_relic_fight_11',3),('rogue_6_relic_legacy_141',5),('rogue_6_relic_final_1',6)):
            r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':[LIGHT,rid]})
            fee=r['deployment_reference']['first_deployment_cost']
            self.assertEqual(fee['unrounded_single_item_reference'],5.75)
            self.assertEqual(fee['combined_reference'],expected)
            self.assertEqual(r['deployment_cost'],expected)
            self.assertEqual(fee['excluded_discount_sources'],[])
            self.assertIsNone(fee['actual_cost'])
            if rid=='rogue_6_relic_fight_11':
                self.assertEqual(r['deployment_reference']['cost']['combined_reference'],3)
                self.assertEqual(r['deployment_reference']['cost']['native_trace']['attributes_cost'],12)
                self.assertEqual(r['deployment_reference']['cost']['excluded_script_discounts'],[])

    def test_first_card_and_missing_script_fee_condition_keep_combination_unknown(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':[LIGHT,'rogue_6_relic_cargo_3']})
        fee=r['deployment_reference']['first_deployment_cost']
        self.assertIsNone(fee['combined_reference'])
        self.assertIn('rogue_6_relic_cargo_3',fee['excluded_discount_sources'])

    def test_first_card_report_distinguishes_assumed_first_deploy_and_actual_deduction(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':[LIGHT]})
        text=format_estimate(r)
        self.assertIn('首次部署费用参考',text)
        self.assertIn('首次部署预计费用：5 费',text)
        self.assertIn('未观测本局是否已经消耗',text)
        self.assertIsNone(r['deployment_reference']['first_deployment_cost']['actual_cost'])
        self.assertNotIn('本次事件前当前生命参考',text)
