"""Preview and cultivated rune paths share work without sharing mutable results."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from rouge import relic_attributes as runes


class RunePreviewReviewTests(unittest.TestCase):
    def test_preparation_classifies_each_input_once(self):
        effects = [
            {'kind': 'attack_pct', 'value': .25, 'attribute_layer': 'relic_rune', 'formula_item': 'MULTIPLIER'},
            {'kind': 'hp_pct', 'value': .5, 'attribute_layer': 'relic_rune', 'formula_item': 'MULTIPLIER'},
            {'kind': 'defense_pct', 'value': .1},
        ]
        attributes = {'hp': 1000, 'attack': 100, 'defense': 50, 'attack_speed': 100, 'resistance': 0}
        for preview, expected in ((100, 125), (200, 250), (0, 0)):
            with self.subTest(preview=preview):
                scenario = {'base_attack': preview, 'effects': effects}
                before = deepcopy((scenario, attributes))
                with patch.object(runes, 'is_attribute_rune', wraps=runes.is_attribute_rune) as classify:
                    resolved, actual = runes.prepare_attribute_runes(scenario, attributes)
                self.assertEqual(classify.call_count, len(effects))
                self.assertEqual(resolved['base_attack'], expected)
                self.assertEqual(actual['attack'], 125)
                self.assertEqual(actual['hp'], 1500)
                self.assertEqual((scenario, attributes), before)
                self.assertIs(resolved['_attribute_runes'][0], effects[0])
                self.assertIs(resolved['effects'][0], effects[2])

    def test_token_rune_exclusion_keeps_order_and_identity(self):
        attack = {'kind': 'attack_pct', 'value': .25, 'attribute_layer': 'relic_rune', 'formula_item': 'MULTIPLIER'}
        token = dict(attack, token_only=True, value=10)
        scenario = {'base_attack': 100, 'effects': [token, attack], '_relic_rules': [token, attack]}
        attributes = {'hp': 1000, 'attack': 100, 'defense': 50, 'attack_speed': 100, 'resistance': 0}
        resolved, actual = runes.prepare_attribute_runes(scenario, attributes)
        self.assertEqual(actual['attack'], 150)
        self.assertEqual(resolved['effects'], [])
        self.assertEqual(len(resolved['_attribute_runes']), 2)
        self.assertTrue(all(e is attack for e in resolved['_attribute_runes']))


if __name__ == '__main__':
    unittest.main()
