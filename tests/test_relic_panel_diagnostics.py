from copy import deepcopy
import unittest
from rouge.calibration import panel_layers,relic_panel_diagnostics

def field(rows,panel,key):
    return next(row for row in rows if row['panel']==panel and row['field']==key)

class RelicPanelDiagnosticsTests(unittest.TestCase):
    def test_life_rune_writeback_and_talent_difference_are_separate(self):
        r=relic_panel_diagnostics({'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_legacy_90']})
        rows=r['source_rows'][0]['fields']
        a=field(rows,'藏品与分队符文写回','hp');b=field(rows,'已覆盖常态天赋与效果','hp')
        self.assertEqual((a['combined_model_reference'],a['background_model_reference'],a['marginal_model_difference']),(3180,2120,1060))
        self.assertEqual((b['combined_model_reference'],b['background_model_reference'],b['marginal_model_difference']),(3975,2650,1325))
        self.assertIsNone(b['actual_source_effect']);self.assertIsNone(r['actual_cause_of_observed_error'])
    def test_attack_rune_and_skill_model_differences_not_white_value_override(self):
        r=relic_panel_diagnostics({'operator':'mechanist','skill':3,'charge_count':0,'relic_ids':['rogue_6_relic_legacy_16']})
        rows=r['source_rows'][0]['fields'];a=field(rows,'藏品与分队符文写回','attack');b=field(rows,'技能期间参考','attack')
        self.assertEqual(a['marginal_model_difference'],143)
        self.assertAlmostEqual(b['marginal_model_difference'],543.4)
        self.assertEqual(field(rows,'培养与模组','attack')['marginal_model_difference'],0)
    def test_subset_retains_other_sources_as_background_and_recomposition_is_labelled_model(self):
        ids=['rogue_6_relic_legacy_27','rogue_6_relic_legacy_29','rogue_6_relic_legacy_12']
        for op in ('kaltsit','silverash','mechanist'):
            s={'operator':op,'skill':1,'relic_ids':ids};r=relic_panel_diagnostics(s,ids[:2])
            self.assertEqual(r['background_relic_ids'],ids[2:]);self.assertEqual(len(r['source_rows']),2)
            for row in r['combination_rows']:
                d=row['combined_model_difference'];summed=row['sum_single_background_model_differences'];res=row['nonadditive_model_residual']
                if d is not None and summed is not None:self.assertAlmostEqual(d,summed+res)
                self.assertIsNone(row['actual_combination_effect'])
            self.assertFalse(r['native_verified']);self.assertIsNone(r['actual_panel_difference'])
    def test_acquired_targeted_buff_is_not_deleted_with_relic_source_declaration(self):
        s={'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_assign_13'],
           'char_buff_ids':['rogue_6_from_relic_13'],'char_buffs_complete':True}
        r=relic_panel_diagnostics(s);self.assertEqual(r['preserved_targeted_buff_ids'],s['char_buff_ids'])
        background=deepcopy(s);background['relic_ids']=[]
        self.assertEqual(r['background_context_token'],panel_layers(background)['context_token'])
        self.assertTrue(all(row['marginal_model_difference'] in (0,None) for row in r['source_rows'][0]['fields']))
    def test_unknown_source_zero_model_delta_does_not_become_actual_no_effect(self):
        r=relic_panel_diagnostics({'operator':'mechanist','skill':3,'charge_count':0,'relic_ids':['unknown-public-id']})
        source=r['source_rows'][0];self.assertFalse(source['fixed_mechanic_record_available'])
        self.assertTrue(r['full_warnings']);self.assertIsNone(source['actual_causal_attribution'])
        self.assertTrue(all(row['actual_source_effect'] is None for row in source['fields']))
        self.assertTrue(any('零差值' in note for note in r['notes']))
    def test_caller_contexts_and_returns_are_isolated_and_source_identity_kept(self):
        s={'operator':'mechanist','skill':3,'charge_count':0,'relic_ids':['rogue_6_relic_legacy_16']};before=deepcopy(s)
        a=relic_panel_diagnostics(s);b=relic_panel_diagnostics(s);self.assertEqual(a,b);self.assertEqual(s,before)
        self.assertEqual(a['source']['commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
        a['source_rows'][0]['fields'].clear();self.assertTrue(b['source_rows'][0]['fields'])
    def test_strict_relic_subset_internal_inputs_and_limits(self):
        s={'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_16']}
        for ids in ([],['not-selected'],['rogue_6_relic_legacy_16']*2,'rogue_6_relic_legacy_16',[True]):
            with self.assertRaises(ValueError):relic_panel_diagnostics(s,ids)
        for ids in (None,True,[True],['x','x']):
            bad={**s,'relic_ids':ids}
            with self.assertRaises(ValueError):relic_panel_diagnostics(bad)
        with self.assertRaises(ValueError):relic_panel_diagnostics({**s,'_attribute_runes':[]})
        with self.assertRaises(ValueError):relic_panel_diagnostics({**s,'relic_ids':[str(i) for i in range(13)]})

if __name__=='__main__':unittest.main()
