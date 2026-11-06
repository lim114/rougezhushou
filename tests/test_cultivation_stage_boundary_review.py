from unittest.mock import patch
import unittest

from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationStageBoundaryReviewTests(unittest.TestCase):
    def test_equipped_stage_errors_are_owned_by_attribute_entry(self):
        for stage in (True, False, 1.0, '1', None, [], {}, 0, 4):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('模组方案', elite=2, level=70,
                             module_id='uniequip_002_nights', module_level=stage)]}
                with patch.object(comparison, '_operator_attribute_reference',
                                  wraps=comparison._operator_attribute_reference) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 2)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
                self.assertIsNone(result['rows'][1]['attributes'])

    def test_no_module_pair_is_validated_before_attribute_entry(self):
        for stage in (True, 1, 0.0, None):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('无模组', elite=2, level=70, module_level=stage)]}
                with patch.object(comparison, '_operator_attribute_reference',
                                  wraps=comparison._operator_attribute_reference) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 1)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
