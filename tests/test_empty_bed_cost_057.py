"""Independent pinned-data/native-contract oracles for empty-slot card costs."""
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge import deployment
from rouge.relics import mechanics

BED = 'rogue_6_relic_cargo_3'
TIED = 'rogue_6_relic_fight_11'
LIGHT = 'rogue_6_relic_book_3'
COIN = 'rogue_6_relic_legacy_141'


def scenario(items, empty_slots=4, **extra):
    return {'operator': 'mechanist', 'skill': 3, 'relic_ids': items,
            'relic_context': {'empty_slots': empty_slots}, **extra}


class EmptyBedCost057Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        receipt = json.loads(Path('.cache/game-data/receipt.json').read_text('utf-8'))
        assert receipt['commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
        originals = {}
        for name in ('character_table', 'roguelike_topic_table'):
            data = Path('.cache/game-data', name + '.json').read_bytes()
            assert hashlib.sha256(data).hexdigest() == receipt['files'][name]['sha256']
            originals[name] = json.loads(data)
        cls.character = originals['character_table']['char_4230_mcnist']
        cls.relics = originals['roguelike_topic_table']['details']['rogue_6']['relics']

    def test_original_parameters_and_cultivation_cost(self):
        c = self.character
        self.assertEqual(c['profession'], 'TANK')
        self.assertEqual([p['attributesKeyFrames'][0]['data']['cost'] for p in c['phases']], [19, 21, 23])
        b = self.relics[BED]['buffs'][0]
        self.assertEqual(b['key'], 'global_buff_normal')
        board = {p['key']: p['valueStr'] if p.get('valueStr') is not None else p['value'] for p in b['blackboard']}
        self.assertEqual((board['key'], board['cnt'], board['value']), ('rogue_6_relic_inventory_cost', 4, -6))
        self.assertEqual(set(board['selector.profession'].lower().split('|')),
                         {'warrior', 'sniper', 'tank', 'medic', 'support', 'caster', 'special', 'pioneer'})

    def test_source_oracle_places_delta_after_rune_rounding_and_card_floor(self):
        # Exact dyadic original inputs. Fraction arithmetic is independent of
        # rouge.deployment FP helpers; literals preserve each observed boundary.
        rows = [
            ([BED], 1, 0, Fraction(0), Fraction(1), 23, 23, 17),
            ([TIED, BED], 1, 0, Fraction(-1, 2), Fraction(1), 12, 12, 6),
            ([LIGHT, BED], 1, 0, Fraction(0), Fraction(1, 4), 23, 5, 0),
            ([TIED, LIGHT, BED], 1, 0, Fraction(-1, 2), Fraction(1, 4), 12, 3, 0),
            ([TIED, COIN, BED], 1, -1, Fraction(-1, 2), Fraction(1), 11, 11, 5),
            ([TIED, COIN, LIGHT, BED], 1, -1, Fraction(-1, 2), Fraction(1, 4), 11, 2, 0),
            ([TIED, BED], 6, 0, Fraction(-1, 2), Fraction(1), 10, 10, 4),
        ]
        for items, potential, additive, mul, scale, attr, scaled, expected in rows:
            with self.subTest(items=items, potential=potential):
                base = 23 if potential == 1 else 21
                self.assertEqual(round(Fraction(base + additive) * (1 + mul)), attr)
                self.assertEqual((Fraction(attr) * scale).__floor__(), scaled)
                self.assertEqual(min(99, max(0, scaled - 6)), expected)
                result = calculate_damage(scenario(items, potential=potential))
                self.assertEqual(result['deployment_cost'], expected)
                key = 'first_deployment_cost' if LIGHT in items else 'cost'
                ref = result['deployment_reference'][key]
                self.assertEqual(ref['estimated_cost'], expected)
                self.assertEqual(ref['native_trace']['attributes_cost'], attr)
                self.assertEqual(ref['native_trace']['scaled_card_cost'], scaled)
                self.assertEqual(ref['native_trace']['runtime_delta'], -6)
                self.assertIsNone(ref['actual_cost'])
                self.assertFalse(result['deployment_reference']['live_state_verified'])
                self.assertFalse(ref['native_trace']['native_reference']['current_hotfix_equivalence_proven'])

    def test_threshold_is_actual_empty_slots_not_part_count(self):
        for empty, expected in ((0, 12), (3, 12), (4, 6), (12, 6)):
            with self.subTest(empty=empty):
                result = calculate_damage(scenario([TIED, BED], empty_slots=empty))
                self.assertEqual(result['deployment_cost'], expected)
                self.assertEqual(result['deployment_reference']['cost']['missing_conditions'], [])
        result = calculate_damage({'operator': 'mechanist', 'skill': 3, 'relic_ids': [TIED, BED],
                                  'relic_context': {'parts_count': 4}})
        self.assertIsNone(result['deployment_cost'])
        self.assertEqual(result['deployment_reference']['cost']['missing_conditions'], ['empty_slots'])

    def test_missing_empty_slots_never_becomes_zero_or_a_live_cost(self):
        for items, key in (([BED], 'cost'), ([TIED, BED], 'cost'),
                           ([LIGHT, BED], 'first_deployment_cost'), ([TIED, LIGHT, BED], 'first_deployment_cost')):
            with self.subTest(items=items):
                result = calculate_damage(scenario(items, relic_context={}))
                self.assertIsNone(result['deployment_cost'])
                self.assertIsNone(result['deployment_reference'][key]['estimated_cost'])
                self.assertIn('empty_slots', result['deployment_reference'][key]['missing_conditions'])

    def test_duplicate_items_and_reordering_do_not_repeat_delta(self):
        one = calculate_damage(scenario([TIED, BED]))
        duplicate = calculate_damage(scenario([BED, TIED, BED, TIED]))
        self.assertEqual(one['deployment_cost'], duplicate['deployment_cost'])
        self.assertEqual(duplicate['deployment_reference']['cost']['native_trace']['runtime_delta'], -6)

    def test_cost_modification_leaves_damage_stats_skills_and_tokens_unchanged(self):
        for operator, skill in (('mechanist', 3), ('kaltsit', 1), ('silverash', 3), ('char_110_deepcl', 1)):
            with self.subTest(operator=operator):
                args = {'operator': operator, 'skill': skill}
                plain = calculate_damage(args)
                supplied = {**args, 'relic_ids': [BED], 'relic_context': {'empty_slots': 4}}
                before = copy.deepcopy(supplied)
                result = calculate_damage(supplied)
                self.assertEqual(supplied, before)
                self.assertEqual(result['deployment_cost'], max(0, plain['deployment_cost'] - 6))
                self.assertEqual(result['relic_token_stats'], plain['relic_token_stats'])
                self.assertEqual(result['total_damage'], plain['total_damage'])
                self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
                for stat in ('hp', 'attack', 'defense', 'resistance', 'attack_speed'):
                    self.assertEqual(result['estimate']['base_stats'][stat], plain['estimate']['base_stats'][stat])

    def test_runtime_classifier_rejects_wrong_source_and_scaled_or_unrelated_rules(self):
        rule = {**mechanics()['relics'][BED]['effects'][0], 'relic_id': BED}
        self.assertTrue(deployment._runtime_cost_delta(rule))
        self.assertTrue(deployment._runtime_cost_delta({**rule, 'value': 0}))
        for changes in ({'relic_id': TIED}, {'source_buff_index': 1}, {'source_buff_key': 'char_attribute_add'},
                        {'condition': 'parts_count'}, {'threshold': 3}, {'value': -12}, {'token_only': True}):
            with self.subTest(changes=changes):
                self.assertFalse(deployment._runtime_cost_delta({**rule, **changes}))
        changed = copy.deepcopy(mechanics())
        changed['relics'][BED]['raw_buffs'][0]['key'] = 'char_attribute_add'
        with patch('rouge.deployment.mechanics', return_value=changed):
            self.assertFalse(deployment._runtime_cost_delta(rule))

    def test_unknown_conditional_additive_source_is_not_laundered_into_runtime_delta(self):
        changed = copy.deepcopy(mechanics())
        changed['relics'][BED]['raw_buffs'][0]['key'] = 'unproved_script'
        # Only the cost classifier sees this mismatched evidence. Resolver's
        # valid known effect cannot grant proof to the mismatched source.
        with patch('rouge.deployment.mechanics', return_value=changed):
            result = calculate_damage(scenario([TIED, BED]))
        self.assertIsNone(result['deployment_cost'])
        self.assertIn(BED, result['deployment_reference']['cost']['excluded_script_discounts'])


if __name__ == '__main__':
    unittest.main()
