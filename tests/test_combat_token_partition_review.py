from collections import Counter
from unittest.mock import patch
import unittest

from rouge import relic_attributes
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat


class CombatTokenPartitionReviewTests(unittest.TestCase):
    def test_each_plan_classifies_each_token_effect_once(self):
        original=Combat.plan
        for identity,token in (('char_110_deepcl','token_10001_deepcl_tentac'),
                               ('char_1035_wisdel','token_10035_wisdel_wward')):
            with self.subTest(operator=identity):
                counts=[]

                def plan(combat,*args,**kwargs):
                    with patch.object(relic_attributes,'is_attribute_rune',
                                      wraps=relic_attributes.is_attribute_rune) as qualify:
                        result=original(combat,*args,**kwargs)
                    counts.append(Counter(id(c.args[0]) for c in qualify.call_args_list))
                    return result

                with patch.object(Combat,'plan',plan):
                    report=calculate_damage({'operator':identity,'skill':1,'ghost_count':1,'ghost_casts':2,
                        'relic_ids':['rogue_6_relic_legacy_134'],
                        'effects':[{'kind':'hp_pct','value':.2,'target_scope':'all_units','token_ids':[token]},
                                   {'kind':'attack_pct','value':.3,'target_scope':'all_units','token_ids':['other']}]})
                self.assertTrue(counts)
                for row in counts:
                    self.assertTrue(row)
                    self.assertTrue(all(n==1 for n in row.values()),row)
                self.assertTrue(report['components'])
