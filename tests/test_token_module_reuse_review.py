from collections import Counter
from unittest.mock import patch
import unittest

from rouge import relics,summons,token_module_comparison as comparison
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from copy import deepcopy


class TokenModuleReuseReviewTests(unittest.TestCase):
    def test_finish_resolves_each_module_reference_once_per_token(self):
        original=relics.finish
        for identity,module,level in (('char_110_deepcl','uniequip_002_deepcl',70),
                                      ('char_2027_wang','uniequip_002_wang',80)):
            with self.subTest(operator=identity):
                calls=[]

                def finish(*args,**kwargs):
                    with patch.object(summons,'module_reference',wraps=summons.module_reference) as hp, \
                         patch.object(summons,'token_cost_reference',wraps=summons.token_cost_reference) as cost:
                        result=original(*args,**kwargs)
                    calls.extend((hp.call_args_list,cost.call_args_list))
                    return result

                with patch.object(relics,'finish',side_effect=finish):
                    result=calculate_damage({'operator':identity,'skill':1,'elite':2,'level':level,
                        'module_id':module,'module_level':3,'relic_ids':['rogue_6_relic_legacy_91']})
                self.assertTrue(result['relic_token_stats'])
                for records in calls:
                    counts=Counter(call.args[2] for call in records)
                    self.assertTrue(counts)
                    self.assertTrue(all(n==1 for n in counts.values()),counts)

    def test_no_effect_or_module_still_omits_token_panel(self):
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,
                                 'module_id':None,'module_level':0})
        self.assertEqual(result['relic_token_stats'],[])

    def test_upgrade_comparison_resolves_cost_once_per_stage(self):
        with patch.object(summons,'token_cost_reference',wraps=summons.token_cost_reference) as cost:
            with patch.object(comparison,'token_cost_reference',cost):
                report=comparison.compare_token_module('char_2027_wang',{'elite':2,'level':80},'uniequip_002_wang')
        counts=Counter(call.args[1]['module_level'] for call in cost.call_args_list)
        self.assertEqual(counts,Counter({0:1,1:1,2:1,3:1}))
        self.assertTrue(report['tokens'])

    def test_prepared_module_pair_is_read_only_including_explicit_absence(self):
        profile=catalog()['operators']['char_110_deepcl'];token='token_10001_deepcl_tentac'
        for module,stage in ((None,0),('uniequip_002_deepcl',3)):
            scenario={'operator':profile['id'],'elite':2,'level':70,'module_id':module,'module_level':stage}
            pair=(summons.module_reference(profile,scenario,token),summons.token_cost_reference(profile,scenario,token))
            before=deepcopy(pair);expected=summons.token_attributes(profile,scenario,token)
            with patch.object(summons,'module_reference') as hp,patch.object(summons,'token_cost_reference') as cost:
                actual=summons.token_attributes(profile,scenario,token,module_references=pair)
            hp.assert_not_called();cost.assert_not_called()
            self.assertEqual(actual,expected);self.assertEqual(pair,before)
