import unittest
from unittest.mock import patch
from rouge.catalog import catalog
from rouge import summons
from rouge.token_counts import token_count_reference


class TokenLevelContractTests(unittest.TestCase):
    def cases(self):
        for function, operator, module in (
            (summons.duration_reference, 'mechanist', 'uniequip_002_mcnist'),
            (summons.module_reference, 'char_110_deepcl', 'uniequip_002_deepcl'),
            (summons.token_cost_reference, 'char_2027_wang', 'uniequip_002_wang'),
            (summons.token_attributes, 'mechanist', 'uniequip_002_mcnist'),
            (token_count_reference, 'char_2027_wang', 'uniequip_002_wang')):
            profile = catalog()['operators'][operator]
            yield function, profile, {'operator': operator, 'elite': 2, 'module_id': module, 'module_level': 2}, next(iter(profile['tokens']))

    def test_only_missing_and_none_default_to_maximum(self):
        for function, profile, scenario, token in self.cases():
            with self.subTest(function=function.__name__):
                expected = function(profile, {**scenario, 'level': profile['phases'][2]['max_level']}, token)
                self.assertIsNotNone(expected)
                self.assertEqual(function(profile, scenario, token), expected)
                self.assertEqual(function(profile, {**scenario, 'level': None}, token), expected)

    def test_invalid_explicit_levels_are_not_full_level(self):
        for function, profile, scenario, token in self.cases():
            for level in (0, False, '', -1, 1.5, '60', profile['phases'][2]['max_level'] + 1):
                with self.subTest(function=function.__name__, level=level), self.assertRaises(ValueError):
                    function(profile, {**scenario, 'level': level}, token)

    def test_prepared_cultivation_does_not_revalidate(self):
        for function, profile, scenario, token in self.cases():
            with self.subTest(function=function.__name__):
                expected = function(profile, {**scenario, 'level': 60}, token)
                with patch.object(summons, 'resolve_cultivation', side_effect=AssertionError('duplicate validation')):
                    self.assertEqual(function(profile, scenario, token, cultivation=(2, 60)), expected)
