import copy,unittest
from unittest.mock import patch
from rouge.enemy_sp_reference import compiled_sp_reference
from rouge.enemy_skills import enemy_skill_reference,enemy_skill_text,skill_data
from rouge.enemy_panel import enemy_panel_reference
from rouge.battle_preview import enemy_preview,enemy_text,battle_data
from rouge.battle_planning import mechanism_provenance

BASE={'spType':'INCREASE_WHEN_ATTACK','maxSp':3,'initSp':0,'increment':1.}
def reference(**extra):
    return {'requested_level':1,'exact_requested_level_present':True,
        'definitions':[{'level':0,'spData':copy.deepcopy(BASE)},{'level':1,'spData':None}],
        'stage_overrides':{},**extra}

class EnemySpInheritanceReferenceTests(unittest.TestCase):
    def test_null_higher_level_does_not_clear_previous_whole_sp_object(self):
        r=compiled_sp_reference(reference())
        self.assertEqual(r['configuration'],BASE)
        self.assertEqual(r['applied_source'],{'origin':'database_level','level':0})
        self.assertEqual(r['source_chain'][1]['state'],'null')
        self.assertIsNone(r['first_activation_seconds']);self.assertIsNone(r['complete_cycle_seconds'])

    def test_nonnull_stage_sp_record_wholly_replaces_with_explicit_zero(self):
        override={'spType':'INCREASE_WITH_TIME','maxSp':0,'initSp':0,'increment':0.}
        r=compiled_sp_reference(reference(stage_overrides={'spData':override}))
        self.assertEqual(r['configuration'],override)
        self.assertEqual(r['applied_source'],{'origin':'stage_override','level':1})

    def test_partial_sp_record_is_unknown_and_never_patched_with_previous_fields(self):
        r=compiled_sp_reference(reference(stage_overrides={'spData':{'maxSp':8}}))
        self.assertEqual(r['state'],'unsupported_source_shape')
        self.assertIsNone(r['configuration']);self.assertIsNone(r['applied_source'])

    def test_absent_or_null_stage_does_not_apply_a_record(self):
        for override in ({},{'spData':None}):
            r=compiled_sp_reference(reference(stage_overrides=override))
            self.assertEqual(r['configuration'],BASE)
            self.assertIsNone(r['current_runtime_controller'])

    def test_unavailable_exact_level_does_not_borrow_lower_or_apply_unverified_alias(self):
        r=compiled_sp_reference(reference(exact_requested_level_present=False,
            stage_overrides={'spData':BASE}))
        self.assertEqual(r['state'],'unavailable_exact_database_level')
        self.assertIsNone(r['configuration']);self.assertEqual(r['source_chain'],[])

    def test_future_level_records_are_not_used(self):
        rows=reference()['definitions']+[{'level':2,'spData':{**BASE,'maxSp':999}}]
        r=compiled_sp_reference(reference(definitions=rows))
        self.assertEqual(r['configuration']['maxSp'],3)
        self.assertTrue(all(row['level']<=1 for row in r['source_chain']))

    def test_no_explicit_sp_is_not_a_claim_of_no_default_controller(self):
        r=compiled_sp_reference(reference(definitions=[{'level':1,'spData':None}]))
        self.assertEqual(r['state'],'no_explicit_sp_configuration')
        self.assertIsNone(r['configuration']);self.assertIsNone(r['current_runtime_controller'])
        self.assertTrue(any('默认控制器' in note for note in r['limits']))

    def test_default_initialization_reference_is_conditional_and_not_runtime_values(self):
        r=compiled_sp_reference(reference(definitions=[{'level':1,'spData':None}]))
        init=r['initialization_reference']
        self.assertEqual(init['path'],'shared_default')
        self.assertEqual(init['scalar_assignment_reference'],{'spType':'NONE','maxChargeTime':1,
            'spCost':0,'initSp':0,'increment':1.,'maxSp':0})
        self.assertFalse(init['current_hooks_bound']);self.assertIsNone(r['current_runtime_controller'])

    def test_explicit_source_maxsp_maps_to_cost_with_single_charge_and_preserves_zero(self):
        r=compiled_sp_reference(reference(stage_overrides={'spData':{**BASE,'maxSp':0,'initSp':0,'increment':0.}}))
        init=r['initialization_reference']
        self.assertEqual(init['path'],'explicit_record_conversion')
        self.assertEqual(init['scalar_assignment_reference'],{'spType':'INCREASE_WHEN_ATTACK',
            'spCost':0,'maxChargeTime':1,'initSp':0,'increment':0.,'maxSp':0})
        self.assertIsNone(r['complete_cycle_seconds'])

    def test_unknown_sp_type_or_invalid_level_has_no_baseline_numeric_projection(self):
        r=compiled_sp_reference(reference(stage_overrides={'spData':{**BASE,'spType':'UNVERIFIED_NEW_TYPE'}}))
        self.assertEqual(r['state'],'compiled_configuration_available')
        self.assertEqual(r['initialization_reference']['state'],'unsupported_sp_type')
        self.assertIsNone(r['initialization_reference']['scalar_assignment_reference'])
        unavailable=compiled_sp_reference(reference(exact_requested_level_present=False))
        self.assertIsNone(unavailable['initialization_reference']['scalar_assignment_reference'])

    def test_nonfinite_bool_and_malformed_records_keep_source_unknown(self):
        for record in ([],False,{**BASE,'maxSp':True},{**BASE,'increment':float('nan')},
            {**BASE,'increment':False}):
            r=compiled_sp_reference(reference(stage_overrides={'spData':record}))
            self.assertEqual(r['state'],'unsupported_source_shape');self.assertIsNone(r['configuration'])

    def test_results_do_not_mutate_inputs_or_native_evidence(self):
        data=reference();before=copy.deepcopy(data)
        r=compiled_sp_reference(data);r['configuration']['maxSp']=99;r['native_evidence'].clear()
        self.assertEqual(data,before)
        self.assertEqual(compiled_sp_reference(data)['configuration']['maxSp'],3)
        self.assertTrue(compiled_sp_reference(data)['native_evidence'])

    def test_public_skill_reference_contains_compiled_sp_without_merging_skills(self):
        d=skill_data()
        sid,key=next((sid,key) for sid,rows in d['bindings'].items() for key in rows
            if key.startswith('enemy_1047_sagent@'))
        eid,level=key.split('@');r=enemy_skill_reference(sid,eid,int(level))
        self.assertEqual(r['compiled_sp_reference']['configuration']['maxSp'],2)
        self.assertFalse(r['inheritance_resolved']);self.assertIsNone(r['effective_skill_damage'])
        ordinary=enemy_skill_text(r);technical=enemy_skill_text(r,technical=True)
        self.assertIn('完整回转仍未知',ordinary)
        self.assertNotIn('maxSp',ordinary)
        self.assertIn('基包技力配置继承参考',technical)
        self.assertIn('"maxSp":2',technical)
        self.assertNotIn('maxChargeTime',ordinary)
        self.assertNotIn('spCost',ordinary)
        self.assertIn('"spCost":2',technical)

    def test_invalid_source_level_reaches_preview_text_and_mechanism_source_query(self):
        sid='ro6_n_2_3';eid='enemy_2133_shdopl_lancer'
        ref=enemy_panel_reference(sid,eid,0)
        self.assertTrue(ref['compiled_database_result_available']);self.assertFalse(ref['exact_level_present'])
        self.assertEqual(ref['attributes']['maxHp'],6000)
        self.assertFalse(ref['construction_reference']['database_records_used'])
        self.assertIsNotNone(ref['source_projection']['attributes']['maxHp'])
        entry=enemy_preview(sid,eid,0,{'difficulty':{'value':0},'zone':{'id':'zone_2'}})
        text=enemy_text(entry)
        self.assertIn('预计生命值：未知',text)
        self.assertIn('独立构造',text)
        self.assertIn('原字段投影',enemy_text(entry,technical=True))
        query=mechanism_provenance(sid,eid,0)
        self.assertEqual(query['compiled_sp_reference']['state'],'constructor_sp_baseline_unknown')
        self.assertIsNone(query['effective_merged_mechanism'])

    def test_all_stage_references_keep_clock_and_current_hotfix_unknown(self):
        total=0;available=0
        for sid,stage in battle_data()['stages'].items():
            for enemy in stage['enemies']:
                ref=enemy_skill_reference(sid,enemy['id'],enemy['level'])['compiled_sp_reference']
                self.assertFalse(ref['native_evidence']['current_hotfix_verified'])
                self.assertIsNone(ref['complete_cycle_seconds']);self.assertIsNone(ref['first_activation_seconds'])
                if ref['state']=='compiled_configuration_available':available+=1
                if not ref['database_exact_level_available']:
                    self.assertEqual(ref['construction_reference']['mode'],'stage_constructor')
                    if ref['state']=='compiled_configuration_available':self.assertEqual(ref['applied_source']['origin'],'stage_override')
                    else:self.assertIsNone(ref['configuration'])
                total+=1
        self.assertEqual(total,1087);self.assertGreater(available,0)

if __name__=='__main__':unittest.main()
