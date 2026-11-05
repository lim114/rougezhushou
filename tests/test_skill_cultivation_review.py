"""Skill rows retain owner isolation while sharing each owner's cultivation."""
from copy import deepcopy
from importlib import import_module
from unittest.mock import patch
import unittest
from rouge import calibration as c


class SkillCultivationReviewTests(unittest.TestCase):
    def test_first_three_read_each_owner_once_and_keep_module_on_its_owner(self):
        catalog = import_module('rouge.catalog')
        source = {'operator': 'mechanist', 'skill': 3, 'module_id': 'uniequip_002_mcnist', 'module_level': 3}
        before = deepcopy(source)
        with patch.object(catalog, 'operator_attributes', wraps=catalog.operator_attributes) as attributes, \
                patch.object(c, 'operator_attributes', attributes):
            result = c.skill_matrix(source)
        self.assertEqual(attributes.call_count, 3)
        calls = {call.args[0]: call.args for call in attributes.call_args_list}
        self.assertEqual(calls['mechanist'][-2:], ('uniequip_002_mcnist', 3))
        self.assertEqual(calls['kaltsit'][-2:], (None, 0))
        self.assertEqual(calls['silverash'][-2:], (None, 0))
        self.assertEqual(len(result['rows']), 9)
        self.assertEqual(source, before)

    def test_extended_owner_uses_one_cultivation_read_for_all_skills(self):
        catalog = import_module('rouge.catalog')
        with patch.object(catalog, 'operator_attributes', wraps=catalog.operator_attributes) as attributes, \
                patch.object(c, 'operator_attributes', attributes):
            result = c.skill_matrix({'operator': 'char_151_myrtle'})
        self.assertEqual(attributes.call_count, 1)
        self.assertEqual([row['skill'] for row in result['rows']], [1, 2])
        self.assertTrue(all(row['operator_key'] == 'char_151_myrtle' for row in result['rows']))


if __name__ == '__main__':
    unittest.main()
