from unittest import TestCase
from unittest.mock import patch
from rouge import relic_damage_factors as factors
from tests.test_relic_damage_composition import rule, EP


class RelicFactorValidationTests(TestCase):
    def test_each_public_entry_validates_each_source_once(self):
        rules = [rule(identity, 'elemental') for identity in EP]
        for calculate in (factors.source_factor, factors.parameter_factor):
            with self.subTest(entry=calculate.__name__), patch.object(factors, 'verified_rule', wraps=factors.verified_rule) as verify:
                self.assertEqual(calculate(rules, 'elemental'), 3.5)
                self.assertEqual(verify.call_args_list, [((item, 'elemental'),) for item in rules])

    def test_independent_source_entry_still_rejects_unverified_mixture(self):
        rules = [rule(identity, 'elemental') for identity in EP]
        rules[1]['composition_evidence'] = 'unverified'
        self.assertIsNone(factors.source_factor(rules, 'elemental'))
