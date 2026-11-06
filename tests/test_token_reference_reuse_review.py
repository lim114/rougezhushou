from collections import Counter
from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import summons,token_counts,token_module_comparison as comparison
from rouge.damage import calculate_damage


class TokenReferenceReuseReviewTests(unittest.TestCase):
    def test_duration_finisher_reuses_existing_panel_reference_and_keeps_copies_independent(self):
        original=summons.finish_duration_references;calls=[]

        def finish(*args):
            with patch.object(summons,'duration_reference',wraps=summons.duration_reference) as read:
                original(*args)
            calls.extend(read.call_args_list)

        with patch.object(summons,'finish_duration_references',side_effect=finish):
            result=calculate_damage({'operator':'mechanist','skill':1,'elite':2,'level':60,
                'module_id':'uniequip_002_mcnist','module_level':2,'relic_ids':['rogue_6_relic_legacy_134']})
        self.assertTrue(result['relic_token_stats'])
        self.assertEqual(len(calls),0)
        panel=next(t for t in result['relic_token_stats'] if 'duration_reference' in t)
        reference=next(r for r in result['token_duration_references'] if r['token_id']==panel['id'])
        original_panel=deepcopy(panel)
        reference['sources'].clear()
        self.assertEqual(panel,original_panel)

    def test_comparison_reads_base_count_reference_once(self):
        with patch.object(token_counts,'token_count_reference',wraps=token_counts.token_count_reference) as counts:
            with patch.object(comparison,'token_count_reference',counts):
                result=comparison.compare_token_module('char_2027_wang',{'elite':2,'level':80},'uniequip_002_wang')
        by_stage=Counter(call.args[1]['module_level'] for call in counts.call_args_list)
        self.assertEqual(by_stage,Counter({0:1,1:1,2:1,3:1}))
        self.assertTrue(result['tokens'])

    def test_missing_panel_is_read_but_known_absent_duration_is_not_retried(self):
        original=summons.finish_duration_references
        for identity,relics,expected in (('mechanist',[],1),
                                         ('char_110_deepcl',['rogue_6_relic_legacy_134'],0)):
            with self.subTest(operator=identity):
                calls=[]

                def finish(*args):
                    with patch.object(summons,'duration_reference',wraps=summons.duration_reference) as read:
                        original(*args)
                    calls.extend(read.call_args_list)

                with patch.object(summons,'finish_duration_references',side_effect=finish):
                    result=calculate_damage({'operator':identity,'skill':1,'module_id':None,'module_level':0,
                                             'relic_ids':relics})
                self.assertEqual(len(calls),expected)
                self.assertEqual('token_duration_references' in result,identity=='mechanist')
