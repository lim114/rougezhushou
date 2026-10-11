import unittest
from rouge.supplemental_skills import defaults,skill_reference,format_reference
from rouge.catalog import operator_attributes


class Supplemental136Tests(unittest.TestCase):
    def test_melantha_talent_and_skill_additive(self):
        p=defaults();p['count']=3;p['enemy_defense']=200
        r=skill_reference(p);base=operator_attributes(p['operator'],1,55,100)['attack']
        self.assertAlmostEqual(r['rows'][1]['value'],base*1.58)
        self.assertAlmostEqual(r['rows'][2]['declared_total'],3*(base*1.58-200))
        self.assertEqual(p['count'],3);self.assertIsNone(r['cycle_output'])

    def test_talent_boundary_and_physical_floor(self):
        p=defaults();p['level']=54;p['enemy_defense']=100000
        r=skill_reference(p);self.assertEqual(r['talents'][0]['blackboard'][0]['value'],.04)
        self.assertAlmostEqual(r['rows'][2]['value'],r['rows'][1]['value']*.05)
        p['elite']=0;p['level']=40;p['count']=0
        r=skill_reference(p);self.assertEqual(r['talents'],[]);self.assertEqual(r['rows'][2]['declared_total'],0)
        self.assertIsNone(r['actual_activation_verified'])

    def test_fang_cost_and_count(self):
        p=defaults('char_123_fang');p['potential']=6;p['count']=4
        r=skill_reference(p);self.assertEqual([row['value'] for row in r['rows']],[6,8]);self.assertEqual(r['rows'][0]['declared_total'],24)
        p['elite']=0;p['level']=40
        self.assertEqual(skill_reference(p)['rows'][1]['value'],7)
        self.assertIn('原表',format_reference(r))

    def test_strict_inputs(self):
        for key,value in [('operator','bad'),('elite',2),('level',56),('potential',0),('skill_rank',8),('skill_rank',True),('count',1.5),('count',1001),('trust',True),('trust',float('nan')),('enemy_resistance',101),('enemy_defense',-1)]:
            p=defaults();p[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):skill_reference(p)
        p=defaults();p['unknown']=1
        with self.assertRaises(ValueError):skill_reference(p)
