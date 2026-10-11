import unittest
from copy import deepcopy
from rouge.token_budget import token_budget, format_token_budget
from rouge.catalog import catalog

def requests(op, additional=1, present=None, stock=None):
    return {key:{'additional':additional,'present':present,'available_stock':stock}
            for key in catalog()['operators'][op].get('tokens',{})}

class TokenBudgetTests(unittest.TestCase):
    def test_deepcolor_cost_cap_and_stock_independent(self):
        op='char_110_deepcl'; training={'elite':2,'level':70,'module_id':'uniequip_002_deepcl','module_level':3}
        result=token_budget(op,training,requests(op,3,5,2),10); row=result['rows'][0]
        self.assertEqual(row['cost_reference'],3); self.assertEqual(result['total_cost_reference'],9)
        self.assertEqual(row['held_limit_reference'],7); self.assertEqual(row['concurrent_limit_reference'],7)
        self.assertFalse(row['stock_sufficient_declared']); self.assertFalse(row['concurrent_within_reference'])
        self.assertEqual(result['remaining_budget_reference'],1); self.assertIsNone(row['actual_deployable'])

    def test_wang_cost_only_unknown_limits(self):
        op='char_2027_wang'; result=token_budget(op,{'elite':2,'level':80,'module_id':'uniequip_002_wang','module_level':2},requests(op,2,0,5),3)
        row=result['rows'][0]; self.assertEqual(row['cost_reference'],2); self.assertEqual(result['total_cost_reference'],4)
        self.assertFalse(result['budget_sufficient_reference']); self.assertIsNone(row['concurrent_limit_reference'])
        self.assertIsNone(row['concurrent_within_reference']); self.assertIsNone(row['held_limit_reference'])

    def test_unknown_module_cost_not_zero_or_approved(self):
        op='mechanist'; profile=catalog()['operators'][op]; module=profile['modules'][0]['id']
        result=token_budget(op,{'elite':2,'level':90,'module_id':module,'module_level':1},requests(op),99)
        self.assertIsNone(result['total_cost_reference']); self.assertIsNone(result['budget_sufficient_reference'])
        zero=token_budget(op,{'elite':2,'level':90,'module_id':module,'module_level':1},requests(op,0),0)
        self.assertEqual(zero['total_cost_reference'],0)

    def test_all_supported_entities_and_no_mutations(self):
        before=deepcopy(catalog()); total=0
        for op,p in catalog()['operators'].items():
            if not p.get('tokens'):continue
            req=requests(op); saved=deepcopy(req)
            result=token_budget(op,{},req,999); total+=len(result['rows'])
            self.assertEqual(req,saved); self.assertIn('实际',format_token_budget(result))
        self.assertEqual(total,13); self.assertEqual(catalog(),before)

    def test_invalid_conditions(self):
        op='char_110_deepcl'
        for value in (True,1.0,-1,10000,None):
            with self.assertRaises(ValueError):token_budget(op,{},requests(op),value)
        for value in (True,1.0,-1,101):
            with self.assertRaises(ValueError):token_budget(op,{},requests(op,value),10)
        with self.assertRaises(ValueError):token_budget(op,{}, {},10)
        with self.assertRaises(ValueError):token_budget(op,{'module_id':'wrong','module_level':1},requests(op),10)
