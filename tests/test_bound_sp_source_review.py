import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from rouge.relics import mechanics
from rouge.supplemental_sp import sp_reference


class BoundSPSourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.data={'relics':{'parent':{'effects':[], 'bound_char_buffs':[{'id':'child'}]}},
                   'char_buffs':{'child':{'effects':[{'kind':'sp_recovery'}]}}}
        mechanics.cache_clear()
        self.addCleanup(mechanics.cache_clear)

    def test_missing_declared_recipient_and_effects_rejected_at_load(self):
        for missing in ('child','effects'):
            data=deepcopy(self.data)
            if missing=='child':del data['char_buffs']['child']
            else:del data['char_buffs']['child']['effects']
            with self.subTest(missing=missing),patch.object(Path,'read_text',return_value=json.dumps(data)):
                with self.assertRaisesRegex(ValueError,'关联强化资料缺失'):
                    mechanics()
            mechanics.cache_clear()

    def test_valid_source_cached_and_unknown_recipient_stays_unknown(self):
        with patch.object(Path,'read_text',return_value=json.dumps(self.data)) as read:
            data=mechanics();self.assertIs(mechanics(),data)
            self.assertEqual(read.call_count,1)
        skill={'spData':{'spCost':10,'initSp':0,'spType':'INCREASE_WITH_TIME','increment':1}}
        record={'id':'parent','name':'关联藏品','pending':[],'missing_conditions':['recipient']}
        with patch('rouge.supplemental_sp.mechanics',return_value=data) as source:
            result=sp_reference(skill,[],[record,dict(record)])
        self.assertEqual(source.call_count,1)
        self.assertIsNone(result['natural_recovery_rate_parameter'])

    def test_optional_binding_and_empty_effects_remain_legal(self):
        del self.data['relics']['parent']['bound_char_buffs']
        self.data['char_buffs']['child']['effects']=[]
        with patch.object(Path,'read_text',return_value=json.dumps(self.data)):
            self.assertEqual(mechanics(),self.data)
