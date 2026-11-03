import unittest
from copy import deepcopy
from rouge.cultivation_comparison import compare_cultivation,format_cultivation
from rouge.catalog import operator_attributes,operator_profiles
from rouge.damage import calculate_damage


def proposal(name,elite=1,level=54,trust=100,potential=1,module_id=None,module_level=0):
    return dict(name=name,elite=elite,level=level,trust=trust,potential=potential,module_id=module_id,module_level=module_level)


class Cultivation140Tests(unittest.TestCase):
    def test_talent_breakpoint_and_potential(self):
        s={'operator':'char_124_kroos','skill':1,'skill_rank':7}
        p={'proposals':[proposal('54级'),proposal('55级',level=55,potential=5)]};before=deepcopy(p)
        r=compare_cultivation(s,p);base,upgrade=r['rows']
        self.assertEqual(base['delta_attack'],0);self.assertGreater(upgrade['delta_attack'],0)
        self.assertGreater(upgrade['skill_differences']['普通单次边际期望'],0)
        self.assertIsNone(upgrade['skill_differences']['二连射含天赋组合']);self.assertEqual(p,before)
        self.assertIn('未知差值',format_cultivation(r))

    def test_core_replaces_base_attack_and_keeps_other_conditions(self):
        s={'operator':'mechanist','skill':3,'skill_rank':7,'base_attack':99999,'window_seconds':10,'enemy_resistance':50}
        p={'proposals':[proposal('低培养',elite=2,level=1,trust=0),proposal('满培养',elite=2,level=90)]}
        r=compare_cultivation(s,p);row=r['rows'][1]
        expected=calculate_damage({k:v for k,v in {**s,**p['proposals'][1]}.items() if k not in ('base_attack','name')})
        self.assertEqual(row['window_damage'],expected['estimate']['skill']['window_damage'])
        self.assertGreater(row['delta_window_damage'],0);self.assertEqual(s['base_attack'],99999)

    def test_unopened_skill_keeps_attribute_comparison(self):
        s={'operator':'mechanist','skill':3,'skill_rank':10}
        r=compare_cultivation(s,{'proposals':[proposal('精一'),proposal('精二',elite=2,level=90)]})
        self.assertIsNotNone(r['rows'][0]['attack']);self.assertIsNone(r['rows'][0]['window_damage'])
        self.assertIsNone(r['rows'][1]['delta_window_damage']);self.assertIn('未开放',r['rows'][0]['error'])

    def test_general_archive_without_skill_and_invalid_row(self):
        identity=next(k for k in operator_profiles() if k not in ('char_124_kroos',) and len(operator_profiles()[k]['phases'])==1)
        r=compare_cultivation({'operator':identity}, {'proposals':[proposal('基准',elite=0,level=1),proposal('错误',elite=2)]})
        self.assertEqual(r['rows'][0]['status'],'基础属性参考');self.assertIsNone(r['rows'][0]['window_damage'])
        self.assertEqual(r['rows'][1]['status'],'不可测算');self.assertIsNone(r['rows'][1]['delta_attack'])

    def test_strict_proposals_and_module_gate(self):
        s={'operator':'char_124_kroos','skill':1,'skill_rank':7}
        for p in [[],[proposal('a'),proposal('a')],[proposal('a',trust=True)],[proposal('a',module_level=1)],[proposal('a',elite=True)]]:
            with self.assertRaises(ValueError):compare_cultivation(s,{'proposals':p})
        identity='char_110_deepcl';module=operator_profiles()[identity]['modules'][0]
        p={'proposals':[proposal('未解锁',module_id=module['id'],module_level=1)]}
        row=compare_cultivation({'operator':identity,'skill':1,'skill_rank':7},p)['rows'][0]
        self.assertFalse(row['module_applied']);self.assertIn('未满足',row['notes'][0])
        self.assertEqual(row['attack'],operator_attributes(identity,1,54,100)['attack'])
