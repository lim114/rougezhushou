import copy
import unittest

from rouge.token_module_comparison import compare_token_module
from rouge.catalog import catalog

D='char_110_deepcl';DM='uniequip_002_deepcl';W='char_2027_wang';WM='uniequip_002_wang'


class TokenModuleComparison126Tests(unittest.TestCase):
    def test_deepcolor_upgrade_has_separate_hp_cost_stock_and_concurrent_references(self):
        r=compare_token_module(D,{'elite':2,'level':70},DM)
        stages=r['tokens'][0]['stages']
        self.assertEqual(stages[0]['values']['hp'],2016)
        self.assertEqual(stages[0]['values']['deployment_cost'],5)
        self.assertEqual(stages[0]['values']['held_limit'],4)
        self.assertEqual(stages[0]['values']['concurrent_limit'],4)
        for stage,factor in zip(stages[1:],(1,1.1,1.15)):
            self.assertEqual(stage['state'],'partial_reference')
            self.assertAlmostEqual(stage['values']['hp'],2016*factor)
            self.assertEqual(stage['values']['deployment_cost'],3)
            self.assertEqual(stage['values']['held_limit'],7)
            self.assertEqual(stage['values']['concurrent_limit'],7)
            self.assertIsNone(stage['values']['attack'])
        self.assertAlmostEqual(stages[3]['differences']['hp'],302.4)
        self.assertIsNone(r['tokens'][0]['actual_presence'])

    def test_wang_known_cost_and_count_limits_leave_unknown_module_hp_separate(self):
        stages=compare_token_module(W,{'elite':2,'level':80},WM)['tokens'][0]['stages']
        self.assertEqual(stages[0]['values']['deployment_cost'],3)
        for stage in stages[1:]:
            self.assertEqual(stage['verified_fields'],['concurrent_limit','deployment_cost','held_limit'])
            self.assertEqual(stage['values']['deployment_cost'],2)
            self.assertEqual(stage['differences'],{'deployment_cost':-1,'held_limit':0,'concurrent_limit':1})
            self.assertIsNone(stage['values']['hp'])
            self.assertEqual(stage['values']['held_limit'],7)
            self.assertEqual(stage['values']['concurrent_limit'],7)

    def test_unlock_boundary_keeps_locked_upgrades_unknown(self):
        for level,state in ((59,'locked'),(60,'partial_reference')):
            result=compare_token_module(W,{'elite':2,'level':level},WM)
            self.assertEqual(result['tokens'][0]['stages'][1]['state'],state)
        result=compare_token_module(D,{'elite':1,'level':60},DM)
        self.assertTrue(all(s['state']=='locked' for s in result['tokens'][0]['stages'][1:]))

    def test_missing_module_rule_is_unknown_not_a_zero_effect_upgrade(self):
        r=compare_token_module('mechanist',{'elite':2,'level':90},'uniequip_002_mcnist')
        for stage in r['tokens'][0]['stages'][1:]:
            self.assertEqual(stage['state'],'unverified')
            self.assertFalse(stage['differences'])
            self.assertTrue(all(v is None for v in stage['values'].values()))

    def test_all_token_profiles_have_base_parameters_without_requiring_relics(self):
        count=0
        for op,p in catalog()['operators'].items():
            if not p.get('tokens'):continue
            r=compare_token_module(op,{'elite':2})
            self.assertEqual(len(r['tokens']),len(p['tokens']))
            for token in r['tokens']:
                self.assertEqual(len(token['stages']),1)
                self.assertIsInstance(token['stages'][0]['values']['hp'],(int,float))
                count+=1
        self.assertEqual(count,13)

    def test_preview_is_independent_from_run_effects_and_preserves_caller_and_catalog(self):
        cultivation={'elite':2,'level':70,'trust':100,'potential':6,
            'relic_ids':['unused'],'effects':[{'kind':'hp_pct','value':99,'target_scope':'all_units'}]}
        before=copy.deepcopy(cultivation);before_catalog=copy.deepcopy(catalog())
        r=compare_token_module(D,cultivation,DM)
        self.assertEqual(r['tokens'][0]['stages'][0]['values']['hp'],2016)
        r['tokens'][0]['stages'][1]['source']['hp_pct']=99
        self.assertEqual(cultivation,before);self.assertEqual(catalog(),before_catalog)
        self.assertEqual(compare_token_module(D,cultivation,DM)['tokens'][0]['stages'][1]['source']['hp_pct'],0)

    def test_wrong_module_or_invalid_cultivation_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'不属于'):compare_token_module(D,{'elite':2},WM)
        for cultivation in ({'elite':True},{'elite':2,'level':0}):
            with self.assertRaises(ValueError):compare_token_module(D,cultivation,DM)


if __name__=='__main__':unittest.main()
