import unittest
from unittest.mock import patch

from rouge.catalog import catalog, operator_profiles, operator_attributes
from rouge.token_budget import token_budget


class CountingModules(list):
    def __init__(self, values):
        super().__init__(values)
        self.reads=0

    def __iter__(self):
        self.reads+=1
        return super().__iter__()


class TokenBudgetModuleIdentityReviewTests(unittest.TestCase):
    def test_budget_reuses_the_module_resolved_by_equipment_validation(self):
        operator,profile=next((k,p) for k,p in catalog()['operators'].items()
                              if p['modules'] and not p.get('tokens'))
        modules=CountingModules(profile['modules'])
        training={'module_id':modules[0]['id'],'module_level':1}
        with patch.dict(profile,modules=modules), patch.dict(operator_profiles()[operator],modules=modules):
            result=token_budget(operator,training,{},10)
        self.assertEqual(modules.reads,1)
        self.assertEqual(result['rows'],[])

    def test_false_module_ids_keep_the_two_public_entry_contracts(self):
        for module_id in ('',False,0,[],{}):
            with self.subTest(module_id=module_id):
                self.assertEqual(operator_attributes('char_110_deepcl',module_id=module_id),
                                 operator_attributes('char_110_deepcl'))
                with self.assertRaisesRegex(ValueError,'模组不属于'):
                    token_budget('char_110_deepcl',{'module_id':module_id},{},10)
