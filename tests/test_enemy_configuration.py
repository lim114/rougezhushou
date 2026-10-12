from copy import deepcopy
import importlib.util,json,unittest
from pathlib import Path
from rouge.enemy_configuration import compiled_configuration,construction_text
from rouge.enemy_skills import enemy_skill_reference,enemy_skill_text,skill_data
from rouge.enemy_panel import enemy_panel_reference
from rouge.catalog import stage_previews
from rouge.damage import calculate_damage
from rouge.battle_preview import enemy_preview,enemy_text
from rouge.battle_planning import mechanism_provenance

def pair(key,value=1,text=None):return {'key':key,'value':value,'valueStr':text}
def skill(key='s',board=None,**changes):
    return {'prefabKey':key,'priority':2,'cooldown':10,'initCooldown':5,'spCost':3,'blackboard':board,**changes}
def reference(*records,override=None,exact=True):
    return {'definitions':[{'level':i,**r} for i,r in enumerate(records)],
        'requested_level':max(0,len(records)-1),'stage_overrides':override or {},
        'exact_requested_level_present':exact}

class EnemyConfigurationTests(unittest.TestCase):
    def test_talents_null_empty_do_not_clear_existing_and_same_key_reorders(self):
        source=reference({'talentBlackboard':[pair('a'),pair('b',2)]},
            {'talentBlackboard':None},{'talentBlackboard':[]},
            override={'talentBlackboard':[pair('a',0),pair('c',4)]})
        before=deepcopy(source);r=compiled_configuration(source)
        self.assertEqual(r['configuration']['talentBlackboard'],[pair('b',2),pair('a',0),pair('c',4)])
        self.assertEqual(source,before)
        self.assertIsNone(compiled_configuration(reference({'talentBlackboard':[]}))['configuration']['talentBlackboard'])

    def test_pair_constructor_only_applies_on_executed_helper_path(self):
        dirty=pair('name',91,'hello');empty=pair('n',6,'')
        a=compiled_configuration(reference({'skills':[skill(board=[dirty,empty])],'talentBlackboard':[dirty,empty]}))['configuration']
        self.assertEqual(a['skills'][0]['blackboard'],[dirty,empty])
        self.assertEqual(a['talentBlackboard'],[pair('name',0,'hello'),pair('n',6)])
        b=compiled_configuration(reference({'skills':[skill(board=[pair('old',8)])]},
            {'skills':[skill(board=[dirty,empty])]}))['configuration']['skills'][0]['blackboard']
        self.assertEqual(b,[pair('old',8),pair('name',0,'hello'),pair('n',6)])

    def test_matching_skill_keeps_old_board_but_all_scalars_come_from_delta_including_zero(self):
        r=compiled_configuration(reference({'skills':[skill(board=[pair('x'),pair('keep',7)])]},
            {'skills':[skill(board=[pair('x',0)],priority=0,cooldown=0,initCooldown=0,spCost=0)]}))
        self.assertEqual(r['configuration']['skills'],[skill(board=[pair('keep',7),pair('x',0)],priority=0,cooldown=0,initCooldown=0,spCost=0)])
        self.assertEqual(r['source_chain'][1]['skill_writes'][0]['path'],'clone_delta_merge_previous_board')
        self.assertIsNone(r['effective_skill_damage']);self.assertIsNone(r['first_activation_seconds'])

    def test_whole_record_empty_board_replaces_matching_skill_without_old_parameters(self):
        for board in (None,[]):
            new=skill(board=board,cooldown=0)
            r=compiled_configuration(reference({'skills':[skill(board=[pair('old',9)])]},override={'skills':[new]}))
            self.assertEqual(r['configuration']['skills'],[new])
            self.assertEqual(r['source_chain'][-1]['skill_writes'][0]['path'],'whole_delta_record')

    def test_null_and_empty_skill_lists_do_not_clear_but_no_skills_writes_none(self):
        for delta in (None,[]):
            r=compiled_configuration(reference({'skills':[skill()]},{'skills':delta}))
            self.assertEqual(r['configuration']['skills'],[skill()])
        self.assertIsNone(compiled_configuration(reference({'skills':[]}))['configuration']['skills'])

    def test_ordinal_keys_duplicates_and_distinct_skills_keep_actual_list_order(self):
        r=compiled_configuration(reference({'skills':[skill('A'),skill('B')]},
            override={'skills':[skill('a'),skill('A',cooldown=0),skill('A',cooldown=3)]}))
        self.assertEqual([s['prefabKey'] for s in r['configuration']['skills']],['B','a','A'])
        self.assertEqual(r['configuration']['skills'][-1]['cooldown'],3)
        t=compiled_configuration(reference({'talentBlackboard':[pair('a'),pair('A'),pair('a',3)]}))
        self.assertEqual(t['configuration']['talentBlackboard'],[pair('A'),pair('a',3)])

    def test_missing_exact_level_blocks_every_partial_source_and_override(self):
        r=compiled_configuration(reference({'skills':[skill()]},override={'skills':[skill('new')]},exact=False))
        self.assertEqual(r['state'],'unavailable_exact_database_level');self.assertIsNone(r['configuration'])
        self.assertFalse(r['compiled_inheritance_resolved']);self.assertEqual(r['source_chain'],[])

    def test_partial_or_malformed_source_is_unknown_instead_of_defaulting_fields(self):
        for row in ({'skills':[{'prefabKey':'s'}]},{'skills':{}},{'talentBlackboard':'x'},
            {'talentBlackboard':[pair('a',True)]},{'skills':[skill(cooldown=float('nan'))]}):
            r=compiled_configuration(reference(row));self.assertEqual(r['state'],'unsupported_source_shape')
            self.assertIsNone(r['configuration']);self.assertFalse(r['compiled_inheritance_resolved'])

    def test_public_native_receipt_matches_runtime_rule_and_preserves_review_correction(self):
        root=Path(__file__).resolve().parents[1];directory=root/'research/p3-enemy-configuration-current'
        spec=importlib.util.spec_from_file_location('native_configuration_check',directory/'verify_native.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        check=module.verify(directory);self.assertEqual(check['native_file_comparison'],'unavailable')
        self.assertTrue(check['artifact_consistency']);self.assertFalse(check['runtime_binding_verified'])
        from rouge.enemy_configuration import construction_rules
        rules=construction_rules();receipt=json.loads((directory/'receipt.json').read_text(encoding='utf8'))
        self.assertEqual(rules['native_evidence']['dll_sha256'],receipt['game_dll_sha256'])
        self.assertEqual(rules['native_evidence']['metadata_sha256'],receipt['metadata_sha256'])
        self.assertFalse(receipt['review_corrections'][0]['wrong_rule_used_for_contract'])
        self.assertTrue(rules['rules']['talents_allocate_only_when_destination_null_and_delta_nonempty'])

    def test_all_fixed_bindings_preserve_unknown_runtime_and_source_shapes(self):
        total=0;available=0;missing=0
        for sid,bindings in skill_data()['bindings'].items():
            for key in bindings:
                eid,level=key.rsplit('@',1);r=enemy_skill_reference(sid,eid,int(level))
                compiled=r['compiled_configuration'];total+=1
                self.assertFalse(r['inheritance_resolved']);self.assertIsNone(compiled['effective_skill_damage'])
                self.assertIsNone(compiled['complete_cycle_seconds']);self.assertIsNone(compiled['current_runtime_controller'])
                self.assertFalse(compiled['native_evidence']['current_hotfix_verified'])
                self.assertNotEqual(compiled['state'],'unsupported_source_shape')
                if compiled['database_exact_level_available']:available+=1
                else:missing+=1;self.assertIsNone(compiled['configuration'])
        self.assertEqual((total,available,missing),(1087,1029,58))

    def test_unavailable_target_is_rejected_in_calculation_but_raw_source_remains_viewable(self):
        sid='ro6_n_2_3';eid='enemy_2133_shdopl_lancer';target={'stage_id':sid,'enemy_id':eid,'level':0}
        calculated=calculate_damage({'operator':'mechanist','skill':1,'target_enemy':target})
        qualified=calculated['run_resolution']['enemy']['fixed_source_qualification']
        self.assertEqual(qualified['state'],'stage_constructor_overrides_available')
        self.assertFalse(qualified['construction_reference']['database_records_used'])
        with self.assertRaisesRegex(ValueError,'不能填零'):
            calculate_damage({'operator':'mechanist','skill':1,'target_enemy':{'stage_id':'ro6_n_3_2','enemy_id':'enemy_1303_mhshep_2b','level':0}})
        r=enemy_preview(sid,eid,0,{'difficulty':{'value':0}})
        self.assertIsNotNone(r['environment']);self.assertIn('预计生命值：未知',enemy_text(r))
        self.assertFalse(r['skill_reference']['compiled_configuration']['compiled_inheritance_resolved'])
        self.assertIsNotNone(r['fixed_panel_reference']['source_projection']['attributes']['maxHp'])
        self.assertIn('原字段投影',enemy_text(r,technical=True))

    def test_supported_target_uses_same_qualified_numbers_and_retains_manual_preview(self):
        target={'stage_id':'ro6_e_1_2','enemy_id':'enemy_1093_ccsbr','level':0}
        r=calculate_damage({'operator':'mechanist','skill':1,'target_enemy':target,
            'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_1'}}})
        enemy=r['run_resolution']['enemy'];self.assertAlmostEqual(enemy['stats']['maxHp'],5424.9)
        self.assertEqual(enemy['stats']['def'],72);self.assertEqual(enemy['fixed_source_qualification']['state'],'exact_database_level_available')
        direct=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':72,'enemy_resistance':10})
        self.assertAlmostEqual(r['total_damage'],direct['total_damage'])

    def test_query_and_copy_boundaries_expose_configuration_without_changing_raw_records(self):
        sid='ro6_e_1_2';eid='enemy_1093_ccsbr';r=enemy_skill_reference(sid,eid,0)
        before=deepcopy(r['definitions']);text=enemy_skill_text(r)
        self.assertIn('基包配置分项',text);self.assertNotIn('prefabKey',text)
        self.assertIn('基包招式与黑板构建参考',enemy_skill_text(r,technical=True))
        self.assertEqual(r['definitions'],before)
        query=mechanism_provenance(sid,eid,0);self.assertIsNone(query['effective_merged_mechanism'])
        self.assertEqual(query['compiled_configuration'],r['compiled_configuration'])
        r['compiled_configuration']['configuration']['talentBlackboard']=[pair('changed')]
        self.assertNotEqual(r['compiled_configuration'],enemy_skill_reference(sid,eid,0)['compiled_configuration'])

if __name__=='__main__':unittest.main()
