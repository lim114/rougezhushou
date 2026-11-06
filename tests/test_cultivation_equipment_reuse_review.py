from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import catalog as data
from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationEquipmentReuseReviewTests(unittest.TestCase):
    def test_attribute_only_proposals_resolve_equipment_once(self):
        class Modules(list):
            scans = 0

            def __iter__(self):
                self.scans += 1
                return super().__iter__()

        profiles = deepcopy(data.operator_profiles())
        profile = profiles['char_141_nights']
        profile['modules'] = Modules(profile['modules'])
        identity = profile['modules'][0]['id']
        preview = {'proposals': [proposal('未解锁', elite=1, level=1, module_id=identity, module_level=1),
                                  proposal('已解锁', elite=2, level=70, module_id=identity, module_level=3)]}
        with patch.object(data, 'operator_profiles', return_value=profiles), \
                patch.object(comparison, 'operator_profiles', return_value=profiles):
            result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
        self.assertEqual([r['module_applied'] for r in result['rows']], [False, True])
        self.assertEqual(profile['modules'].scans, 2)

    def test_omitted_level_uses_same_resolved_level_as_attributes(self):
        identity = 'uniequip_002_nights'
        implicit = proposal('默认等级', elite=2, level=None, module_id=identity, module_level=3)
        explicit = {**implicit, 'name': '指定满级', 'level': 70}
        result = comparison.compare_cultivation({'operator': 'char_141_nights'}, {'proposals': [implicit, explicit]})
        first, second = result['rows']
        self.assertTrue(first['module_applied'])
        self.assertEqual(first['attributes'], second['attributes'])
        self.assertIsNone(first['error'])
