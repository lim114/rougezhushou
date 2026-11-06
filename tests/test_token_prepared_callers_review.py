from collections import Counter
from unittest.mock import patch
import unittest

from rouge import token_module_comparison as comparison, summons
from rouge.damage import calculate_damage
from tests.test_token_cultivation_reuse_review import CountedScenario


class TokenPreparedCallersReviewTests(unittest.TestCase):
    def test_module_comparison_does_not_reparse_prepared_cultivation(self):
        reads=Counter()
        def observe(fn):
            def call(profile,scenario,token,*args,**kwargs):
                counted=CountedScenario(**scenario)
                result=fn(profile,counted,token,*args,**kwargs)
                reads.update(counted.reads)
                return result
            return call
        with patch.object(comparison,'token_attributes',side_effect=observe(comparison.token_attributes)), \
             patch.object(comparison,'module_reference',side_effect=observe(comparison.module_reference)), \
             patch.object(comparison,'token_cost_reference',side_effect=observe(comparison.token_cost_reference)), \
             patch.object(comparison,'token_count_reference',side_effect=observe(comparison.token_count_reference)):
            result=comparison.compare_token_module('char_2027_wang',{'elite':2,'level':80},'uniequip_002_wang')
        self.assertEqual((reads['elite'],reads['level']),(0,0))
        self.assertEqual(result['tokens'][0]['stages'][3]['values']['concurrent_limit'],7)

    def test_relic_panel_reuses_prepared_cultivation(self):
        with patch.object(summons,'token_attributes',wraps=summons.token_attributes) as attributes:
            result=calculate_damage({'operator':'mechanist','skill':1,'elite':2,'level':60,
                'module_id':'uniequip_002_mcnist','module_level':2,'relic_ids':['rogue_6_relic_legacy_134']})
        panel_calls=[call for call in attributes.call_args_list if 'module_references' in call.kwargs]
        self.assertTrue(panel_calls)
        self.assertTrue(all(call.kwargs.get('cultivation')==(2,60) for call in panel_calls))
        self.assertEqual(result['token_duration_references'][0]['state'],'unlimited')
