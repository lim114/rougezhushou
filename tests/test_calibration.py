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


    def test_154_full_curve_rounding_and_contributions(self):
        r=c.cultivation_curve({'operator':'kaltsit','potential':4})
        self.assertEqual(len(r['rows']),90)
        end=r['rows'][-1]['contributions']
        self.assertEqual(end['attack'],{'level_base':510,'trust_increment':0,'potential_increment':25.0,'module_increment':0.0})
        self.assertEqual(end['hp']['trust_increment'],500)
        self.assertEqual(r['rows'][0]['cultivated']['attack'],433)
    def test_154_module_gate_inside_level_curve(self):
        r=c.cultivation_curve({'operator':'mechanist','module_id':'uniequip_002_mcnist','module_level':3},levels=[59,60])
        self.assertEqual(r['rows'][0]['contributions']['attack']['module_increment'],0)
        self.assertEqual(r['rows'][1]['contributions']['attack']['module_increment'],100)


    def test_155_three_module_stages_and_exact_gate(self):
        r=c.module_stages({'operator':'mechanist','level':90})
        self.assertEqual([x['attribute_delta']['attack'] for x in r['rows']],[60,80,100])
        self.assertEqual([x['attribute_delta']['defense'] for x in r['rows']],[40,60,80])
        self.assertTrue(all(x['qualified'] for x in r['rows']))
        self.assertEqual(r['rows'][2]['cultivated_attributes']['attack'],673)
        self.assertEqual(r['rows'][2]['cultivated_attributes']['defense'],845)
        low=c.module_stages({'operator':'mechanist','level':59})
        self.assertTrue(all(x['attribute_delta']['attack']==0 and not x['qualified'] for x in low['rows']))
    def test_155_empty_module_identity_and_parts_not_certified(self):
        self.assertEqual(c.module_stages({'operator':'kaltsit'})['rows'],[])
        r=c.module_stages({'operator':'mechanist'})
        self.assertFalse(r['rows'][0]['parts'][1]['runtime_attachment_verified'])
        self.assertEqual(r['rows'][0]['parts'][1]['map_tag'],'rogue_6')


    def test_156_silver_time_and_potential_variants(self):
        r=c.talent_states({'operator':'silverash'},elapsed_seconds=[14.9,15])
        self.assertEqual(r['rows'][0]['base_stats']['defense'],497)
        self.assertEqual(r['rows'][1]['base_stats']['defense'],557)
        refs=[x['talent_references'][0] for x in r['rows']]
        self.assertAlmostEqual(refs[0]['regeneration_per_second_reference'],34.77)
        self.assertAlmostEqual(refs[1]['regeneration_per_second_reference'],69.54)
        p=c.talent_states({'operator':'silverash','potential':5},elapsed_seconds=[15])
        self.assertEqual(p['rows'][0]['talent_references'][0]['defense_addition_reference'],160)
    def test_156_kaltsit_recipient_unknown_not_skill_healing(self):
        r=c.talent_states({'operator':'kaltsit','potential':6},elapsed_seconds=[0])
        t=r['rows'][0]['talent_references'][0]
        self.assertEqual(t['recipient_regeneration_rate_reference'],60)
        self.assertEqual(t['rhodes_rate_reference'],120)
        self.assertIsNone(t['actual_healing_total'])
        self.assertEqual(c.talent_states({'operator':'mechanist'},elapsed_seconds=[0])['rows'][0]['talent_references'],[])


    def test_157_kaltsit_directional_s3_events(self):
        f=c.animation_events({'operator':'kaltsit'},orientation='Front',animation_contains='Skill_3_Attack')
        b=c.animation_events({'operator':'kaltsit'},orientation='Back',animation_contains='Skill_3_Attack')
        self.assertTrue(f['records']);self.assertTrue(b['records'])
        self.assertEqual(f['records'][0]['events'][0]['ceil_frames_30hz'],12)
        self.assertEqual(b['records'][0]['events'][0]['ceil_frames_30hz'],13)
        self.assertFalse(f['records'][0]['runtime_binding_verified'])
    def test_157_transition_preserved_not_selected(self):
        r=c.animation_events({'operator':'kaltsit'},orientation='Front',animation_contains='Attack_Begin')
        self.assertTrue(r['records'])
        self.assertFalse(r['records'][0]['selectable_as_conventional_reference'])
        self.assertEqual(r['records'][0]['events'],[])


    def test_158_recipient_independent_clocks_and_attack_snapshots(self):
        r=c.recipient_events({'operator':'silverash','skill':2},recipients=[
            {'id':'A','deployment_seconds':8,'stacks':2,'attack_at_triggers':[500,600]},
            {'id':'B','deployment_seconds':9,'stacks':1,'attack_at_triggers':[400]}],enemy_defense=200)
        self.assertEqual([round(x['time_seconds_reference'],1) for x in r['events']],[9.1,9.6,10.1])
        self.assertEqual([x['post_defense_damage_reference'] for x in r['events']],[1700,2080,1320])
        self.assertEqual(r['declared_recipient_damage_reference'],5100)
        self.assertIsNone(r['full_skill_damage']);self.assertFalse(r['native_clock_verified'])
    def test_158_unknown_snapshot_window_and_token_exclusion(self):
        s={'operator':'silverash','skill':2}
        r=c.recipient_events(s,recipients=[{'id':'A','stacks':2,'attack_at_triggers':[500,None]}],window_seconds=1.6)
        self.assertEqual(r['declared_recipient_damage_reference'],1900)
        r=c.recipient_events(s,recipients=[{'id':'A','stacks':2,'attack_at_triggers':[500,None]}])
        self.assertEqual(r['known_packet_subtotal_reference'],1900)
        self.assertIsNone(r['declared_recipient_damage_reference'])
        with self.assertRaises(ValueError):c.recipient_events(s,recipients=[{'id':'T','is_token':True,'stacks':1}])


    def test_159_kaltsit_true_damage_and_single_healing(self):
        r=c.packet_worksheet({'operator':'kaltsit','skill':2,'enemy_defense':9999,'enemy_resistance':100})
        self.assertEqual(r['rows'][0]['single_packet_reference'],4845)
        self.assertEqual(r['rows'][1]['single_packet_reference'],2550)
        self.assertTrue(all(x['complete_cast_total'] is None for x in r['rows']))
    def test_159_mechanist_separate_physical_magic_packets(self):
        r=c.packet_worksheet({'operator':'mechanist','skill':3,'enemy_defense':100,'enemy_resistance':20})
        self.assertAlmostEqual(r['rows'][0]['single_packet_reference'],2177.4*2.6*.8)
        self.assertAlmostEqual(r['rows'][1]['single_packet_reference'],2177.4*3-100)
        self.assertEqual(c.packet_worksheet({'operator':'silverash','skill':1})['rows'],[])

if __name__=='__main__':unittest.main()
