from collections import Counter
from unittest.mock import patch
import unittest

from rouge import supplemental_run as run
from rouge import supplemental_cost as cost, supplemental_sp as sp
from rouge import supplemental_healing as healing, supplemental_damage as damage
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalClassificationBoundaryReviewTests(unittest.TestCase):
    def test_run_classifies_each_effect_once_across_public_and_calculation_boundaries(self):
        ids=['rogue_6_relic_legacy_2','rogue_6_relic_legacy_81',
             'rogue_6_relic_fight_11','rogue_6_relic_book_1']
        for module,name in ((cost,'supported_cost'),(sp,'supported_sp'),
                            (healing,'supported_healing'),(damage,'supported_damage')):
            with self.subTest(predicate=name):
                with patch.object(run,name,wraps=getattr(module,name)) as qualify:
                    with patch.object(module,name,qualify):
                        result=run.run_skill_reference(defaults('char_123_fang'),environment(ids))
                calls=Counter(id(call.args[0]) for call in qualify.call_args_list)
                self.assertTrue(calls)
                self.assertTrue(all(n==1 for n in calls.values()),dict(calls))
                self.assertEqual(result['deployment_reference']['estimated_cost'],5)
                self.assertAlmostEqual(result['sp_reference']['natural_recovery_rate_parameter'],1.2)

    def test_natural_sp_source_restrictions_survive_predicate_inline(self):
        rule={'kind':'sp_recovery','relic_id':'rogue_6_relic_legacy_2',
              '_verified_rule':True,'source_buff_key':'global_buff_stack',
              'source_buff_index':0,'group':'modify_sp_recover[normal]','value':.2}
        self.assertTrue(sp.supported_sp(rule))
        for change in ({'_verified_rule':False},{'token_only':True},
                       {'source_buff_index':1},{'value':.3},{'relic_id':'unknown'}):
            with self.subTest(change=change):
                self.assertFalse(sp.supported_sp({**rule,**change}))
