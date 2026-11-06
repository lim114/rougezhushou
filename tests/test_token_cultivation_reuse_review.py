from collections import Counter
from copy import deepcopy
import unittest

from rouge.catalog import catalog
from rouge.summons import token_attributes
from rouge.token_counts import token_count_reference
from tests.test_token_budget_module_identity_review import CountingModules


class CountedScenario(dict):
    def __init__(self, **values):
        super().__init__(values)
        self.reads=Counter()

    def get(self, key, default=None):
        self.reads[key]+=1
        return super().get(key,default)


class TokenCultivationReuseReviewTests(unittest.TestCase):
    def test_attributes_and_references_read_cultivation_once(self):
        for operator in ('char_110_deepcl','char_2027_wang','mechanist'):
            profile=catalog()['operators'][operator];token=next(iter(profile['tokens']))
            args=CountedScenario(operator=operator,elite=2,level=60,
                                 module_id=profile['modules'][0]['id'],module_level=2)
            with self.subTest(operator=operator):
                token_attributes(profile,args,token)
                self.assertEqual((args.reads['elite'],args.reads['level']),(1,1))

    def test_duration_uses_operator_level_not_capped_token_level(self):
        profile=deepcopy(catalog()['operators']['mechanist']);token=next(iter(profile['tokens']))
        profile['tokens'][token]['phases'][2]['max_level']=1
        result=token_attributes(profile,{'operator':'mechanist','elite':2,'level':60,
            'module_id':'uniequip_002_mcnist','module_level':2},token)
        self.assertEqual(result['duration_reference']['state'],'unlimited')

    def test_counts_do_not_resolve_equipment_that_cannot_apply(self):
        profile=dict(catalog()['operators']['char_2027_wang']);token=next(iter(profile['tokens']))
        for module_id,elite,level in ((None,2,90),('wrong',2,90),('uniequip_002_wang',1,80),('uniequip_002_wang',2,59)):
            modules=CountingModules(profile['modules']);current={**profile,'modules':modules}
            result=token_count_reference(current,{'operator':profile['id'],'module_id':module_id,
                'module_level':3,'elite':elite,'level':level},token)
            self.assertFalse(result['module_applied'])
            self.assertEqual(modules.reads,0)
