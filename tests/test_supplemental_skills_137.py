import unittest
from rouge.supplemental_skills import defaults,skill_reference,format_reference
from rouge.catalog import operator_attributes


class Supplemental137Tests(unittest.TestCase):
    def test_critical_branch_floor_before_expectation(self):
        p=defaults('char_124_kroos');p['potential']=5;p['enemy_defense']=600
        r=skill_reference(p);a=operator_attributes(p['operator'],1,55,100,5)['attack']
        normal=max(a-600,a*.05);crit=max(a*1.6-600,a*1.6*.05)
        self.assertAlmostEqual(r['rows'][2]['value'],normal*.8+crit*.2)
        self.assertIsNone(r['rows'][-1]['value']);self.assertIn('独立抽样未知',format_reference(r))

    def test_double_hit_and_talent_unlock(self):
        p=defaults('char_124_kroos');p.update(elite=0,level=40,count=3)
        r=skill_reference(p);a=r['attributes']['attack']
        self.assertEqual(r['talents'],[]);self.assertIsNone(r['rows'][1]['value'])
        self.assertAlmostEqual(r['rows'][4]['declared_total'],a*1.4*2*3)
        self.assertEqual(r['rows'][4]['value'],r['rows'][5]['value'])
        p.update(elite=1,level=54);r=skill_reference(p)
        self.assertEqual(r['talents'][0]['blackboard'][0]['value'],.1)

    def test_steward_talent_magic_and_resistance_cap(self):
        p=defaults('char_210_stward');p['enemy_resistance']=100;p['enemy_defense']=100000
        r=skill_reference(p);a=operator_attributes(p['operator'],1,55,100)['attack']
        self.assertAlmostEqual(r['rows'][1]['value'],a*1.06*1.9*.05)
        p['level']=54;r=skill_reference(p)
        self.assertEqual(r['talents'][0]['blackboard'][0]['value'],.03)

    def test_potential_upgrade_selects_one_candidate(self):
        p=defaults('char_124_kroos');p['potential']=4
        r=skill_reference(p);self.assertEqual(len(r['talents']),1)
        self.assertEqual(r['talents'][0]['blackboard'][1]['value'],1.5)
        p['potential']=5
        self.assertEqual(skill_reference(p)['talents'][0]['blackboard'][1]['value'],1.6)
