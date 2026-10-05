"""Public fee estimates from independently frozen native instruction oracles."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.deployment import native_deployment_cost

BIND='rogue_6_relic_fight_11'
IRON='rogue_6_relic_book_3'
EMPTY='rogue_6_relic_cargo_3'
COIN='rogue_6_relic_legacy_141'


class NativeDeployment054Tests(unittest.TestCase):
    def test_rune_odd_cost_uses_ties_to_even_after_cultivation(self):
        # Installed native WriteAttributesField rounds its ObscuredInt branch
        # before card multiplication; these are independent literal oracles.
        for potential,expected in ((1,12),(6,10)):
            with self.subTest(potential=potential):
                scenario={'operator':'mechanist','skill':3,'potential':potential,'relic_ids':[BIND]}
                before=copy.deepcopy(scenario)
                result=calculate_damage(scenario)
                self.assertEqual(result['deployment_cost'],expected)
                self.assertEqual(result['deployment_reference']['cost']['estimated_cost'],expected)
                self.assertIsNone(result['deployment_reference']['cost']['actual_cost'])
                self.assertFalse(result['deployment_reference']['live_state_verified'])
                self.assertEqual(scenario,before)

    def test_first_card_discount_combines_after_rune_rounding(self):
        for relic_ids,expected in (([IRON],5),([BIND,IRON],3),([BIND,COIN,IRON],2)):
            with self.subTest(relic_ids=relic_ids):
                result=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':relic_ids})
                self.assertEqual(result['deployment_cost'],expected)
                first=result['deployment_reference']['first_deployment_cost']
                self.assertEqual(first['estimated_cost'],expected)
                self.assertTrue(first['rounding_verified'])
                self.assertFalse(first['live_first_deployment_verified'])

    def test_first_card_does_not_discount_other_professions_or_summons(self):
        for operator,skill in (('silverash',3),('char_110_deepcl',1)):
            with self.subTest(operator=operator):
                plain=calculate_damage({'operator':operator,'skill':skill})
                result=calculate_damage({'operator':operator,'skill':skill,'relic_ids':[IRON]})
                self.assertEqual(result['deployment_cost'],plain['deployment_cost'])
                self.assertNotIn('deployment_reference',result)
                self.assertEqual(result['relic_token_stats'],plain['relic_token_stats'])

    def test_missing_condition_blocks_combined_cost_but_proved_card_delta_combines(self):
        # 057 proves empty-bed runtime delta: round23*.5=12, floor12*.25=3,
        # then subtract6 and clamp to0. Missing inventory still remains unknown.
        for context,expected in (({},None),({'empty_slots':4},0),({'empty_slots':3},3)):
            with self.subTest(context=context):
                result=calculate_damage({'operator':'mechanist','skill':3,
                    'relic_ids':[BIND,IRON,EMPTY],'relic_context':context})
                self.assertEqual(result['deployment_cost'],expected)
                self.assertEqual(result['deployment_reference']['first_deployment_cost']['estimated_cost'],expected)

    def test_duplicate_items_cannot_multiply_the_first_discount_twice(self):
        args={'operator':'mechanist','skill':3,'relic_ids':[BIND,IRON]}
        one=calculate_damage(args)
        duplicate=calculate_damage({**args,'relic_ids':[BIND,IRON,IRON,BIND]})
        self.assertEqual(one['deployment_reference'],duplicate['deployment_reference'])

    def test_layered_native_oracles_keep_each_integer_boundary(self):
        # Literal rows in p1-native-cost-054/cost-oracle.json; not calculated
        # from the implementation under test or a synthetic game screenshot.
        examples=[
            (dict(cultivation_cost=7,rune_multipliers=(-.5,)),4),
            (dict(cultivation_cost=11,rune_multipliers=(-.5,)),6),
            (dict(cultivation_cost=13,rune_multipliers=(-.5,)),6),
            (dict(cultivation_cost=7,rune_multipliers=(-.5,),card_factors=(.25,)),1),
            (dict(cultivation_cost=13,rune_multipliers=(-.5,),redeploy_factor=1.5),9),
            (dict(cultivation_cost=13,redeploy_factor=1.5),19),
            (dict(cultivation_cost=20,card_factors=(.5,.25)),2),
            (dict(cultivation_cost=7,card_factors=(.25,),runtime_deltas=(-1,)),0),
            (dict(cultivation_cost=99,runtime_deltas=(20,)),99),
        ]
        for args,expected in examples:
            with self.subTest(args=args):
                result=native_deployment_cost(**args)
                self.assertEqual(result['estimated_cost'],expected)
                self.assertFalse(result['native_reference']['current_hotfix_equivalence_proven'])

    def test_non_finite_or_non_integer_cost_inputs_are_rejected(self):
        for value in (True,-1,.5,float('nan'),float('inf'),'7',None):
            with self.subTest(value=value),self.assertRaises(ValueError):
                native_deployment_cost(value)
        with self.assertRaises(ValueError):
            native_deployment_cost(7,runtime_deltas=(.5,))
