from collections import Counter
from unittest.mock import patch
import unittest

from rouge import supplemental_cost as cost
from rouge.supplemental_run import run_skill_reference
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalCostLayersReviewTests(unittest.TestCase):
    def test_cost_source_queries_are_not_repeated_during_calculation(self):
        env=environment(['rogue_6_relic_legacy_141','rogue_6_relic_fight_11',
                         'rogue_6_relic_cargo_3'])
        env['relic_context']['empty_slots']=4
        for name in ('_rune_cost_add','_rune_cost_mul','_runtime_cost_delta'):
            with self.subTest(query=name):
                with patch.object(cost,name,wraps=getattr(cost,name)) as query:
                    result=run_skill_reference(defaults('char_123_fang'),env)
                counts=Counter(id(call.args[0]) for call in query.call_args_list)
                self.assertTrue(counts)
                self.assertTrue(all(n==1 for n in counts.values()),dict(counts))
                self.assertEqual(result['deployment_reference']['estimated_cost'],0)
                trace=result['deployment_reference']['native_with_talent']
                self.assertEqual((trace['attributes_cost'],trace['deck_base_delta'],trace['runtime_delta']),(5,-1,-6))
