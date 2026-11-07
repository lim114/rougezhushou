from unittest.mock import patch
import unittest

from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationStageBoundaryReviewTests(unittest.TestCase):
    def test_supplemental_skill_uses_the_computed_proposal_attributes(self):
        from rouge import supplemental_skills as skills
        profiles = comparison.operator_profiles()
        for identity in skills.supplemental_profiles()['operators']:
            with self.subTest(identity=identity):
                self.assertEqual(profiles[identity]['modules'], [])
                scenario = skills.defaults(identity)
                choices = {'proposals': [proposal('基准', level=50), proposal('升级', level=55)]}
                with patch.object(skills, '_attribute_values', wraps=skills._attribute_values) as duplicate:
                    rows = comparison.compare_cultivation(scenario, choices)['rows']
                duplicate.assert_not_called()
                for row in rows:
                    standalone = {**scenario, 'level': row['proposal']['level'], 'count': 1, 'missing_hp': 0}
                    self.assertEqual(row['skill_reference'], skills.skill_reference(standalone))

    def test_supplemental_skill_still_requires_an_explicit_integer_level(self):
        from rouge import supplemental_skills as skills
        scenario = skills.defaults()
        choices = {'proposals': [proposal('默认满级', level=None)]}
        row = comparison.compare_cultivation(scenario, choices)['rows'][0]
        self.assertIsNotNone(row['attributes'])
        self.assertIsNone(row['skill_reference'])
        self.assertIn('level需要整数', row['error'])

    def test_trust_parser_internal_error_propagates(self):
        with patch.object(comparison, '_amount', side_effect=ValueError('internal amount error')):
            with self.assertRaisesRegex(ValueError, 'internal amount error'):
                comparison.compare_cultivation({'operator': 'mechanist'}, {'proposals': [proposal('基准')]})

    def test_equipped_stage_errors_are_owned_by_attribute_entry(self):
        for stage in (True, False, 1.0, '1', None, [], {}, 0, 4):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('模组方案', elite=2, level=70,
                             module_id='uniequip_002_nights', module_level=stage)]}
                with patch.object(comparison, '_attribute_values',
                                  wraps=comparison._attribute_values) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 2)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
                self.assertIsNone(result['rows'][1]['attributes'])

    def test_no_module_pair_is_validated_before_attribute_entry(self):
        for stage in (True, 1, 0.0, None):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('无模组', elite=2, level=70, module_level=stage)]}
                with patch.object(comparison, '_attribute_values',
                                  wraps=comparison._attribute_values) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 1)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
