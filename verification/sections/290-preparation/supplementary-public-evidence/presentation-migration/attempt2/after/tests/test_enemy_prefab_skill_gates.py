"""Actual public APIs/temporary Qt with bound prefab primitives; no game/chat."""
from copy import deepcopy
import importlib.util,json,time,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.enemy_prefab_skill_gates import prefab_data,prefab_key_reference,prefab_skill_reference,prefab_skill_text,SCOPE
from rouge.enemy_skills import enemy_skill_reference,enemy_skill_text,skill_data
from rouge.enemy_skill_resources import initial_skill_resource_reference,SCOPE as SP_SCOPE
from rouge.battle_view import BattlePreviewPanel
from rouge.offline_tools_view import OfflineToolsPanel,run_offline_query
from rouge.deployment import _Q32,_fp

def plan(requests,**values):return {'scope':SCOPE,'requests':requests,**values}
def fixed(plan_value=None):return enemy_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,prefab_gate_plan=plan_value)

class EnemyPrefabSkillGateTests(unittest.TestCase):
    def test_current_source_artifacts_keep_abstract_ability_and_unexecuted_boundaries(self):
        root=Path(__file__).resolve().parents[1];directory=root/'research/p3-enemy-prefab-skill-gates-current'
        spec=importlib.util.spec_from_file_location('native_prefab_skill_gate_check',directory/'verify_native.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);r=module.verify(directory)
        self.assertTrue(r['artifact_consistency']);self.assertEqual(r['native_file_comparison'],'unavailable')
        self.assertEqual(r['bundle_file_comparison'],'unavailable');self.assertFalse(r['current_runtime_attachment_verified'])
        self.assertFalse(r['current_hotfix_equivalence_proven']);self.assertFalse(r['native_get_name_icall_execution_verified'])
        receipt=json.loads((directory/'receipt.json').read_text())
        self.assertEqual((receipt['native_methods'],receipt['unique_instruction_checks'],receipt['metadata_binding_spans']),(19,2173,235))
        self.assertEqual((receipt['selected_bundle_count'],receipt['selected_prefab_count'],receipt['exact_enemy_skill_components']),(10,23,26))
        self.assertEqual((receipt['bound_positive_cost_skills'],receipt['unbound_positive_cost_skills']),(22,0))

    def test_real_finite_gate_can_deny_while_shared_sp_gate_passes(self):
        result=fixed(plan(['AOEAttack'],starting_counts={'AOEAttack':1}))['prefab_skill_gates']
        s=result['skills'][0];self.assertEqual(s['maximum_trigger_time_reference'],1)
        self.assertEqual(s['initial_trigger_count_reference'],0);self.assertTrue(s['initial_count_gate_pass'])
        event=result['declared_start_budget']['events'][0]
        self.assertFalse(event['count_gate_pass']);self.assertTrue(event['sp_numeric_gate_pass'])
        self.assertFalse(event['conditional_start_accepted']);self.assertEqual(event['after_sp_raw'],_Q32)
        self.assertEqual(event['after_count'],1);self.assertIsNone(event['actual_cast_succeeded'])

    def test_start_success_increments_after_fee_and_failure_retains_request_without_increment(self):
        for success,left_count in ((True,1),(False,0)):
            r=fixed(plan([{'skill':'AOEAttack','ability_start_success':success}]))['prefab_skill_gates']
            event=r['declared_start_budget']['events'][0]
            self.assertTrue(event['conditional_positive_sp_request_before_ability_result'])
            self.assertEqual(event['conditional_start_accepted'],success)
            self.assertEqual(event['after_sp_raw'],0);self.assertEqual(event['after_count'],left_count)
            self.assertFalse(event['immediate_refund_in_baseline_failure_branch'])
        text=prefab_skill_text(fixed(plan([{'skill':'AOEAttack','ability_start_success':False}]))['prefab_skill_gates'])
        self.assertIn('启动计数不增加',text);self.assertIn('不立即返还',text)

    def test_default_is_initial_counter_not_actual_count_or_cast_clock(self):
        r=fixed()['prefab_skill_gates'];self.assertIsNone(r['declared_start_budget'])
        for obj in [r,*r['skills']]:
            self.assertIsNone(obj['full_availability']);self.assertIsNone(obj['actual_cast_count'])
            self.assertIsNone(obj['first_activation_seconds']);self.assertIsNone(obj['complete_cycle_seconds'])
        self.assertFalse(r['actual_attachment_verified']);self.assertFalse(r['actual_current_controller_verified'])
        self.assertFalse(r['current_hotfix_equivalence_proven']);self.assertIsNone(r['skills'][0]['current_trigger_count'])

    def test_never_trigger_is_not_a_claim_that_scripted_cast_is_impossible(self):
        r=enemy_skill_reference('ro6_n_5_4','enemy_10087_hlchgr_2',0)['prefab_skill_gates']
        self.assertFalse(r['skills'][0]['autonomous_target_reference'])
        self.assertIsNone(r['skills'][0]['actual_manual_or_scripted_trigger'])
        text=prefab_skill_text(r);self.assertIn('不等于不能施放',text)
        r=enemy_skill_reference('ro6_n_5_4','enemy_10087_hlchgr_2',0,
            prefab_gate_plan=plan(['ForeverEnhance']*8))['prefab_skill_gates']
        budget=r['declared_start_budget'];self.assertEqual(sum(e['conditional_start_accepted'] for e in budget['events']),7)
        self.assertFalse(budget['events'][-1]['sp_numeric_gate_pass']);self.assertIsNone(budget['actual_cast_count'])

    def test_case_normalization_binds_cuttree_without_generic_unicode_or_culture_guess(self):
        r=enemy_skill_reference('ro6_n_2_2','enemy_1097_cclmbjk',0)['prefab_skill_gates']
        self.assertEqual(r['skills'][0]['key'],'cuttree');self.assertEqual(r['skills'][0]['component']['key'],'CutTree')
        base=fixed();source=deepcopy(base);source['compiled_configuration']['configuration']['skills'][0]['prefabKey']='I'
        result=prefab_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,source)
        self.assertEqual(result['skills'][0]['state'],'unbound_component_or_name_culture')
        self.assertIsNone(result['skills'][0]['full_availability'])

    def test_normalized_source_collision_never_allocates_independent_component_counters(self):
        source=deepcopy(fixed());row=source['compiled_configuration']['configuration']['skills'][0]
        source['compiled_configuration']['configuration']['skills'].append({**row,'prefabKey':'aoeattack'})
        r=prefab_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,source,
            plan(['AOEAttack','aoeattack']))
        self.assertEqual(r['state'],'ambiguous_assignment_source_keys')
        self.assertEqual(r['skills'],[]);self.assertIsNone(r['declared_start_budget'])
        self.assertIsNone(r['full_availability'])

    def test_actual_prefab_override_data_branch_and_int_float_conversion(self):
        base=fixed();source=deepcopy(base)
        table=deepcopy(prefab_data());component=table['prefabs']['enemy_1320_wdrrl_2']['skills'][0]
        for override,source_cd,expected,branch in ((0,8,0,'prefab_nonnegative_override'),
            (-1,8,8,'source_data_negative_override'),(16777217,8,16777216,'prefab_nonnegative_override')):
            component['initial_cooldown_override']=override
            source['compiled_configuration']['configuration']['skills'][0]['initCooldown']=source_cd
            with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=table):
                result=prefab_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,source)
            row=result['skills'][0]
            self.assertEqual(row['initial_cooldown_branch'],branch)
            self.assertEqual(row['initial_cooldown_period_fp_raw'],expected*_Q32)
            self.assertIsNone(row['first_activation_seconds'])

    def test_counter_zero_unlimited_and_finite_boundaries_use_signed_gate(self):
        base=fixed();table=deepcopy(prefab_data());component=table['prefabs']['enemy_1320_wdrrl_2']['skills'][0]
        for limit,passes in ((-1,True),(0,False),(1,True)):
            component['max_trigger_time']=limit
            with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=table):
                r=prefab_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,base)
            self.assertEqual(r['skills'][0]['initial_count_gate_pass'],passes)
            self.assertEqual(r['skills'][0]['unlimited_by_this_counter'],limit<0)

    def test_start_fee_gate_remains_exact_fp_boundary(self):
        for raw,passed in ((_Q32-1,False),(_Q32,True)):
            event=fixed(plan(['AOEAttack'],starting_sp_raw=raw))['prefab_skill_gates']['declared_start_budget']['events'][0]
            self.assertEqual(event['sp_numeric_gate_pass'],passed);self.assertEqual(event['conditional_start_accepted'],passed)
            self.assertEqual(event['after_sp_raw'],raw-_Q32 if passed else raw)

    def test_invalid_scope_counts_or_sequence_fail_without_sp_clock_guess(self):
        invalid=[{},[],plan('AOEAttack'),plan(['']),plan([True]),plan(['AOEAttack']*257),
            plan(['AOEAttack'],scope='actual_casts'),plan([{'skill':'AOEAttack','ability_start_success':1}]),
            plan([{'skill':'AOEAttack','ability_start_success':True,'time':1}]),plan(['unknown']),
            plan(['AOEAttack'],starting_counts={'AOEAttack':-1}),plan(['AOEAttack'],starting_counts={'AOEAttack':True}),
            plan(['AOEAttack'],starting_counts={'AOEAttack':1<<31}),plan(['AOEAttack'],starting_counts={'unknown':0}),
            plan(['AOEAttack'],starting_sp=True),plan(['AOEAttack'],starting_sp=float('inf')),
            plan(['AOEAttack'],starting_sp=10**1000),plan(['AOEAttack'],starting_sp=2),
            plan(['AOEAttack'],starting_sp_raw=True),plan(['AOEAttack'],starting_sp_raw=1<<63),
            plan(['AOEAttack'],starting_sp=1,starting_sp_raw=_Q32),plan(['AOEAttack'],regeneration=1)]
        for value in invalid:
            with self.subTest(value=str(value)[:80]),self.assertRaises(ValueError):fixed(value)
        with self.assertRaises(ValueError):enemy_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,
            resource_plan={'scope':SP_SCOPE,'requests':['AOEAttack']},prefab_gate_plan=plan(['AOEAttack']))

    def test_counter_overflow_is_not_silently_wrapped(self):
        with self.assertRaisesRegex(ValueError,'溢出'):
            enemy_skill_reference('ro6_n_5_4','enemy_10087_hlchgr_2',0,
                prefab_gate_plan=plan(['ForeverEnhance'],starting_counts={'ForeverEnhance':(1<<31)-1}))

    def test_mutations_do_not_change_cached_asset_data_or_other_calls(self):
        p=plan(['AOEAttack']);r=fixed(p)['prefab_skill_gates'];p['requests'].append('AOEAttack')
        self.assertEqual(r['declaration']['requests'],['AOEAttack'])
        r['skills'][0]['component']['max_trigger_time']=9
        self.assertEqual(fixed()['prefab_skill_gates']['skills'][0]['maximum_trigger_time_reference'],1)

    def test_prefab_identity_uses_defined_data_not_db_id_or_stage_alias(self):
        from rouge.enemy_panel import panel_data
        r=enemy_skill_reference('ro6_n_2_3','enemy_2133_shdopl_lancer',0)['prefab_skill_gates']
        self.assertEqual(r['prefab_key_reference']['key'],'enemy_2133_shdopl')
        self.assertFalse(r['prefab_key_reference']['alias_used_as_prefab_key'])
        self.assertEqual(r['state'],'unavailable_fixed_prefab')
        data=deepcopy(prefab_data());records=data['database_prefab_keys']['enemy_1320_wdrrl_2']
        records['0']={'defined':False,'value':'enemy_1320_wdrrl_2'}
        with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=data):
            reference=prefab_key_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,fixed())
        self.assertFalse(reference['known']);self.assertIsNone(reference['key'])
        records['0']={'defined':True,'value':None}
        with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=data):
            result=prefab_skill_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,fixed())
        self.assertTrue(result['prefab_key_reference']['known']);self.assertIsNone(result['prefab_key_reference']['key'])
        self.assertEqual(result['state'],'unavailable_fixed_prefab')

    def test_prefab_key_null_defined_and_higher_level_boundaries_do_not_borrow_future(self):
        base=fixed();data=deepcopy(prefab_data());records=data['database_prefab_keys']['enemy_1320_wdrrl_2']
        records['1']={'defined':True,'value':'higher_level_resource'}
        with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=data):
            r=prefab_key_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,base)
        self.assertEqual(r['key'],'enemy_1320_wdrrl_2')
        records['0']={'defined':False,'value':None}
        with patch('rouge.enemy_prefab_skill_gates.prefab_data',return_value=data):
            r=prefab_key_reference('ro6_duel_1','enemy_1320_wdrrl_2',0,base)
        self.assertFalse(r['known'])

    def test_all_1087_refs_cover_every_22_positive_fee_source_but_not_all_controllers(self):
        states={};rows=positive=0
        for stage,bindings in skill_data()['bindings'].items():
            for key in bindings:
                enemy,level=key.rsplit('@',1);ref=enemy_skill_reference(stage,enemy,int(level));r=ref['prefab_skill_gates']
                states[r['state']]=states.get(r['state'],0)+1
                self.assertIsNone(r['full_availability']);self.assertIsNone(r['actual_cast_count'])
                self.assertIsNone(r['first_activation_seconds']);self.assertIsNone(r['complete_cycle_seconds'])
                self.assertFalse(r['current_hotfix_equivalence_proven']);self.assertIsNone(r['declared_start_budget'])
                for item in r['skills']:
                    if item['state']=='conditional_prefab_gates_available':
                        rows+=1;positive+=item['sp_numeric_reference']['source_sp_cost']>0
                for item in ref['initial_skill_resources']['skills']:
                    if item['source_sp_cost']>0:
                        self.assertTrue(any(s['key']==item['prefab_key'] and s['state']=='conditional_prefab_gates_available' for s in r['skills']))
        self.assertEqual(states,{'unavailable_fixed_prefab':1065,'conditional_prefab_gates_available':22})
        self.assertEqual((rows,positive),(26,22))

class EnemyPrefabSkillGateViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def test_fixed_preview_shows_finite_limit_without_english_ids_or_actual_count(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.show();panel.set_stage('ro6_duel_1');self.qt.processEvents()
        i=next(i for i in range(panel.enemy_combo.count()) if (panel.enemy_combo.itemData(i) or (None,))[0]=='enemy_1320_wdrrl_2')
        panel.enemy_combo.setCurrentIndex(i);self.qt.processEvents();text=panel.enemy_detail.toPlainText()
        self.assertIn('启动次数上限 1',text);self.assertIn('发动时间仍未知',text);self.assertNotIn('AOEAttack',text)
        panel.technical.setChecked(True);self.qt.processEvents()
        self.assertIn('AOEAttack',panel.enemy_detail.toPlainText());self.assertIn('prefab_key_defined',panel.enemy_detail.toPlainText())

    def test_offline_failure_sequence_returns_and_refresh_preserves_declaration(self):
        panel=OfflineToolsPanel();self.addCleanup(panel.close);panel.show();panel.select_query('battle','mechanism')
        payload={'stage_id':'ro6_duel_1','enemy_id':'enemy_1320_wdrrl_2','level':0,
            'prefab_gate_plan':plan([{'skill':'AOEAttack','ability_start_success':False}])}
        panel.editor.setPlainText(json.dumps(payload));panel.run_button.click();end=time.monotonic()+8
        while panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(panel._workers);self.assertIsNotNone(panel.result_snapshot(),panel.status.text())
        self.assertEqual(panel.result_snapshot()['prefab_skill_gates']['declared_start_budget']['remaining_sp_raw'],0)
        self.assertIn('启动计数不增加',panel.result_view.toPlainText())
        before=(panel.editor.toPlainText(),panel.current_query(),panel.result_view.toHtml(),panel.result_snapshot())
        panel.set_stage('ro6_n_1_2');self.qt.processEvents()
        self.assertEqual(before,(panel.editor.toPlainText(),panel.current_query(),panel.result_view.toHtml(),panel.result_snapshot()))

if __name__=='__main__':unittest.main()
