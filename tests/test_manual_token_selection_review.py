from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import relics
from rouge.damage import calculate_damage


class ScopeProbe(dict):
    def __init__(self, values):
        super().__init__(values)
        self.scope_reads=0

    def get(self,key,default=None):
        if key=='target_scope':self.scope_reads+=1
        return super().get(key,default)


class ManualTokenSelectionReviewTests(unittest.TestCase):
    def test_two_token_panel_qualifies_manual_scope_once(self):
        original=relics.finish;reads=[]
        def finish(result,resolution,attributes,scenario):
            probe=ScopeProbe(scenario['effects'][0])
            original(result,resolution,attributes,{**scenario,'effects':[probe]})
            reads.append(probe.scope_reads)
        args={'operator':'char_1042_phatm2','skill':1,'elite':2,'level':90,
              'effects':[{'kind':'attack_pct','value':.5,'target_scope':'all_units'}]}
        before=deepcopy(args)
        with patch.object(relics,'finish',side_effect=finish):result=calculate_damage(args)
        self.assertEqual(len(result['relic_token_stats']),2)
        self.assertEqual(reads,[1])
        self.assertEqual(args,before)
