import unittest
from copy import deepcopy
from rouge import calibration as c

class CalibrationTests(unittest.TestCase):
    def test_151_layers_independent_oracles_and_no_mutation(self):
        s={'operator':'mechanist','skill':3,'charge_count':0,'relic_ids':['rogue_6_relic_legacy_16']}
        before=deepcopy(s);r=c.panel_layers(s)
        self.assertEqual(s,before)
        self.assertEqual(r['panels']['培养与模组']['attack'],573)
        self.assertEqual(r['panels']['藏品与分队符文写回']['attack'],716)
        self.assertAlmostEqual(r['panels']['技能期间参考']['attack'],2720.8)
        self.assertFalse(r['native_verified'])
        self.assertEqual(r['source']['commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
    def test_151_kaltsit_rune_before_talent(self):
        r=c.panel_layers({'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_legacy_90']})
        self.assertEqual(r['panels']['培养与模组']['hp'],2120)
        self.assertEqual(r['panels']['藏品与分队符文写回']['hp'],3180)
        self.assertEqual(r['panels']['已覆盖常态天赋与效果']['hp'],3975)


    def test_152_paired_context_and_stage_diagnostic(self):
        s={'operator':'mechanist','skill':3};p=c.panel_layers(s)
        obs={'context_token':p['context_token'],'panel':'已覆盖常态天赋与效果',
             'evidence_kind':'formula_reference','source':'固定培养表独立对照','values':{'attack':573,'defense':765}}
        r=c.compare_panel(s,obs)
        self.assertTrue(r['all_compared_values_match']);self.assertFalse(r['native_verified'])
        obs['values']['attack']=2177.4;r=c.compare_panel(s,obs)
        self.assertFalse(r['all_compared_values_match'])
        self.assertIn('技能期间参考',r['rows'][0]['other_stage_matches'])
        with self.assertRaises(ValueError):c.compare_panel({**s,'potential':4},obs)
    def test_152_public_case_not_promoted_to_native(self):
        s={'operator':'kaltsit','skill':2};p=c.panel_layers(s)
        r=c.compare_panel(s,{'context_token':p['context_token'],'panel':'技能期间参考',
            'evidence_kind':'public_case','source':'https://prts.wiki/w/凯尔希·思衡托',
            'values':{'attack':1275}})
        self.assertTrue(r['all_compared_values_match'])
        self.assertEqual(r['evidence_kind'],'public_case');self.assertFalse(r['native_verified'])


    def test_153_nine_skills_and_partial_unknown(self):
        r=c.skill_matrix({'operator':'mechanist','skill':3,'charge_count':1})
        self.assertEqual(len(r['rows']),9)
        m=next(x for x in r['rows'] if x['operator_id']=='char_4230_mcnist' and x['skill']==3)
        self.assertFalse(m['model_complete']);self.assertIsNone(m['full_skill_damage'])
        self.assertTrue(m['declared_components'])
        silver=next(x for x in r['rows'] if x['operator_id']=='char_1045_svash2' and x['skill']==2)
        self.assertEqual(len(silver['declared_components']),1)
    def test_153_locked_skills_and_module_ownership(self):
        r=c.skill_matrix({'operator':'mechanist','elite':0,'skill_rank':7,'module_id':'uniequip_002_mcnist','module_level':3})
        self.assertEqual(sum(x['status']=='培养条件未开放' for x in r['rows']),6)

if __name__=='__main__':unittest.main()
