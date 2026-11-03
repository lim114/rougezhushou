import unittest
from rouge.supplemental_skills import defaults,skill_reference
from rouge.catalog import operator_attributes


class Supplemental138Tests(unittest.TestCase):
    def test_cardigan_max_hp_and_clipped_budget(self):
        p=defaults('char_209_ardign');p.update(count=3,missing_hp=500)
        r=skill_reference(p);base=operator_attributes(p['operator'],1,55,100)['hp']
        self.assertAlmostEqual(r['rows'][0]['value'],base*1.12)
        self.assertAlmostEqual(r['rows'][1]['value'],base*1.12*.4)
        self.assertEqual(r['rows'][2]['value'],500)
        self.assertAlmostEqual(r['rows'][3]['value'],base*1.12*.4*3-500)
        p['missing_hp']=100000
        with self.assertRaises(ValueError):skill_reference(p)

    def test_cardigan_unlock_and_zero_count(self):
        p=defaults('char_209_ardign');p.update(elite=0,level=40,count=0)
        r=skill_reference(p);self.assertEqual(r['talents'],[])
        self.assertEqual(r['rows'][2]['value'],0);self.assertEqual(r['rows'][3]['value'],0)
        p.update(elite=1,level=54)
        self.assertEqual(skill_reference(p)['talents'][0]['blackboard'][0]['value'],.06)

    def test_beagle_defense_talent_skill_additive(self):
        p=defaults('char_122_beagle');p['potential']=6
        r=skill_reference(p);base=operator_attributes(p['operator'],1,55,100,6)['defense']
        self.assertAlmostEqual(r['rows'][1]['value'],base*1.6)
        p['level']=54;r=skill_reference(p)
        self.assertEqual(r['talents'][0]['blackboard'][0]['value'],.05)

    def test_hibiscus_attack_heal_and_one_gap_for_all_counts(self):
        p=defaults('char_120_hibisc');p.update(count=2,missing_hp=100)
        r=skill_reference(p);a=operator_attributes(p['operator'],1,55,100)['attack']
        self.assertAlmostEqual(r['rows'][1]['value'],a*1.58)
        self.assertEqual(r['rows'][2]['value'],100)
        self.assertAlmostEqual(r['rows'][3]['value'],2*a*1.58-100)
        p['missing_hp']=0;self.assertEqual(skill_reference(p)['rows'][2]['value'],0)
        p['missing_hp']=True
        with self.assertRaises(ValueError):skill_reference(p)
