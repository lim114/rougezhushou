"""Cultivation and rune classification are each resolved at one input boundary."""
from copy import deepcopy
from importlib import import_module
import unittest
from unittest.mock import patch
from rouge import calibration, relic_attributes


class CultivationInputReviewTests(unittest.TestCase):
    def test_panel_layers_reads_cultivation_once_without_rune_writeback(self):
        catalog = import_module('rouge.catalog')
        source = {'operator': 'mechanist', 'skill': 3,
                  'relic_ids': ['rogue_6_relic_legacy_16']}
        before = deepcopy(source)
        with patch.object(catalog, 'operator_attributes', wraps=catalog.operator_attributes) as attributes, \
                patch.object(calibration, 'operator_attributes', attributes):
            result = calibration.panel_layers(source)
        self.assertEqual(attributes.call_count, 1)
        self.assertEqual(source, before)
        self.assertEqual(result['panels']['培养与模组']['attack'], 573)
        self.assertEqual(result['panels']['藏品与分队符文写回']['attack'], 716)

    def test_each_rune_is_classified_once_for_all_attribute_fields(self):
        attributes = {'attack': 100, 'hp': 1000, 'defense': 50,
                      'attack_speed': 100, 'resistance': 0, 'redeploy_seconds': 70}
        effects = [{'kind': kind, 'value': value, 'attribute_layer': 'relic_rune',
                    'formula_item': 'MULTIPLIER'}
                   for kind, value in (('attack_pct', .2), ('hp_pct', .5))]
        before = deepcopy((attributes, effects))
        with patch.object(relic_attributes, 'is_attribute_rune',
                          wraps=relic_attributes.is_attribute_rune) as classify:
            result = relic_attributes.apply_attribute_runes(attributes, effects)
        self.assertEqual(classify.call_count, len(effects))
        self.assertEqual((attributes, effects), before)
        self.assertEqual(result['attack'], 120)
        self.assertEqual(result['hp'], 1500)


if __name__ == '__main__':
    unittest.main()
