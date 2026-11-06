import unittest
from copy import deepcopy
from unittest.mock import patch

from rouge import supplemental_sp as sp
from rouge import supplemental_healing as healing


class SupplementalPendingReviewTests(unittest.TestCase):
    def test_child_effects_only_block_recovery_and_only_when_recipient_missing(self):
        data={'relics':{'parent':{'effects':[{'kind':'initial_sp'}],
                               'bound_char_buffs':[{'id':'child'}]}},
              'char_buffs':{'child':{'effects':[{'kind':'sp_recovery'},{'kind':'sp_cost_factor'}]}}}
        skill={'spData':{'spCost':10,'initSp':2,'spType':'INCREASE_WITH_TIME','increment':1}}
        for pending,missing in (([],[]),(['pending'],[]),([],['recipient'])):
            with self.subTest(pending=pending,missing=missing):
                record={'id':'parent','name':'parent','pending':pending,'missing_conditions':missing}
                original=deepcopy(data)
                with patch.object(sp,'mechanics',return_value=data):
                    result=sp.sp_reference(skill,[],[record])
                self.assertEqual(result['unresolved_initial_sources'],['parent'] if pending or missing else [])
                self.assertEqual(result['unresolved_cost_sources'],[])
                self.assertEqual(result['unresolved_recovery_sources'],['parent'] if missing else [])
                self.assertEqual(result['natural_recovery_rate_parameter'],None if missing else 1)
                self.assertEqual(data,original)

    def test_healing_pending_sources_do_not_add_healing_to_damage_operator(self):
        data={'relics':{},'char_buffs':{'child':{'effects':[{'kind':'healing_factor'},
                                                          {'kind':'regeneration_factor'}]}}}
        record={'id':'child','name':'child','pending':['pending'],'missing_conditions':[]}
        result={'attributes':{'hp':100},'rows':[]}
        with patch.object(healing,'mechanics',return_value=data):
            reference=healing.apply_healing_reference(result,[],[record],'damage')
        self.assertEqual(reference['pending_healing'],[])
        self.assertEqual(reference['pending_regeneration'],['child'])
        self.assertEqual(result['rows'][0]['name'],'藏品常态生命回复')
        self.assertIsNone(result['rows'][0]['value'])
