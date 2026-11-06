from copy import deepcopy
from unittest.mock import Mock, patch
import unittest

from rouge import token_budget as budget
from rouge import token_module_comparison as comparison
from rouge import catalog as catalog_module
from rouge.catalog import catalog


class TokenBudgetValidationReviewTests(unittest.TestCase):
    def test_budget_validates_cultivation_and_equipment_once(self):
        training={'elite':2,'level':70,'potential':6,
                  'module_id':'uniequip_002_deepcl','module_level':3}
        requests={key:{'additional':2,'present':None,'available_stock':None}
                  for key in catalog()['operators']['char_110_deepcl']['tokens']}
        saved=deepcopy((training,requests))
        validate=Mock(wraps=catalog_module._operator_attribute_reference)
        with patch.object(budget,'_operator_attribute_reference',validate), patch.object(catalog_module,'_operator_attribute_reference',validate):
            result=budget.token_budget('char_110_deepcl',training,requests,20)
        self.assertEqual(validate.call_count,1)
        self.assertEqual(validate.call_args.kwargs,training)
        self.assertEqual(result['total_cost_reference'],6)
        self.assertEqual((training,requests),saved)

    def test_equipment_error_precedes_request_error(self):
        with self.assertRaisesRegex(ValueError,'模组身份或等级'):
            budget.token_budget('char_110_deepcl',{'module_id':'wrong','module_level':1},{},10)
        with self.assertRaisesRegex(ValueError,'费用预算'):
            budget.token_budget('char_110_deepcl',{'module_id':'wrong','module_level':1},{},-1)

    def test_direct_comparison_keeps_its_entry_validation(self):
        with self.assertRaisesRegex(ValueError,'等级或信赖'):
            comparison.compare_token_module('char_110_deepcl',{'level':0},'wrong')
