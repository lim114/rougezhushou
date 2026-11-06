from copy import deepcopy
import unittest
from unittest.mock import patch
from rouge import catalog as data
from rouge.summons import token_attributes


class SingleLevelCultivationTests(unittest.TestCase):
    def test_operator_single_point_and_default_level(self):
        profile=deepcopy(data.catalog()['operators']['mechanist'])
        frame={**profile['phases'][2]['frames'][0], 'level':1, 'hp':123, 'attack':45, 'defense':6}
        profile['phases'][2]={'max_level':1,'frames':[frame]}
        with patch.object(data,'operator_profiles',return_value={'mechanist':profile}):
            for level in (None,1):
                with self.subTest(level=level):
                    result=data.operator_attributes('mechanist',elite=2,level=level,trust=0,potential=1)
                    self.assertEqual((result['hp'],result['attack'],result['defense']),(123,45,6))
            for level in (0,False,2):
                with self.assertRaises(ValueError):
                    data.operator_attributes('mechanist',elite=2,level=level,trust=0)

    def test_token_single_point_keeps_operator_level_for_unlocks(self):
        profile=deepcopy(data.catalog()['operators']['mechanist'])
        token=next(iter(profile['tokens']))
        frame={**profile['tokens'][token]['phases'][2]['frames'][0], 'level':1, 'hp':123, 'attack':45, 'defense':6}
        profile['tokens'][token]['phases'][2]={'max_level':1,'frames':[frame]}
        scenario={'operator':'mechanist','elite':2,'level':60,'module_id':'uniequip_002_mcnist','module_level':2}
        result=token_attributes(profile,scenario,token)
        self.assertEqual((result['hp'],result['attack'],result['defense']),(123,45,6))
        self.assertEqual(result['duration_reference']['state'],'unlimited')

    def test_two_point_operator_interpolation_still_works(self):
        profile=deepcopy(data.catalog()['operators']['mechanist'])
        first={**profile['phases'][2]['frames'][0], 'level':1, 'hp':100, 'attack':20, 'defense':4}
        last={**first,'level':3,'hp':200,'attack':40,'defense':8}
        profile['phases'][2]={'max_level':3,'frames':[first,last]}
        with patch.object(data,'operator_profiles',return_value={'mechanist':profile}):
            result=data.operator_attributes('mechanist',elite=2,level=2,trust=0,potential=1)
        self.assertEqual((result['hp'],result['attack'],result['defense']),(150,30,6))
