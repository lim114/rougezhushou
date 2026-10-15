"""Bound shared-SP components, never actual cast clocks or private state."""
from copy import deepcopy
import importlib.util,json,time,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from rouge.deployment import _Q32,_fp
from rouge.enemy_skill_resources import initial_skill_resource_reference,skill_resource_text,SCOPE
from rouge.enemy_skills import enemy_skill_reference,enemy_skill_text,skill_data
from rouge.battle_preview import enemy_preview,enemy_text
from rouge.battle_planning import mechanism_provenance
from rouge.offline_tools_view import OfflineToolsPanel,run_offline_query,render_offline_result
from rouge.battle_view import BattlePreviewPanel

def fixture(init=4,maximum=4,skills=None):
    return {'compiled_configuration':{'state':'compiled_configuration_available',
        'configuration':{'skills':skills if skills is not None else [skill('A',2),skill('B',3)]}},
        'compiled_sp_reference':{'initialization_reference':{'state':'conditional_baseline_available',
            'path':'declared_test_baseline','scalar_assignment_reference':{'initSp':init,'maxSp':maximum}}}}
def skill(key,cost,cd=0):return {'prefabKey':key,'spCost':cost,'initCooldown':cd}
def plan(requests,**values):return {'scope':SCOPE,'requests':requests,**values}

class EnemySkillResourceTests(unittest.TestCase):
    def test_source_binding_identity_and_scope_are_reproducible_without_game(self):
        root=Path(__file__).resolve().parents[1]
        directory=root/'research/p3-enemy-skill-resource-gates-current'
        spec=importlib.util.spec_from_file_location('native_skill_resources',directory/'verify_native.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=module.verify(directory)
        self.assertTrue(result['artifact_consistency']);self.assertEqual(result['native_file_comparison'],'unavailable')
        self.assertFalse(result['actual_current_controller_verified'])
        self.assertFalse(result['actual_modifier_acceptance_verified'])
        self.assertFalse(result['game_dll_executed']);self.assertFalse(result['current_hotfix_equivalence_proven'])
        receipt=json.loads((directory/'receipt.json').read_text())
        self.assertEqual((receipt['native_methods'],receipt['metadata_binding_spans']),(35,311))
        self.assertFalse(receipt['actual_visible_original_window_verified'])

    def test_initial_pool_integer_upper_cap_and_no_lower_zero_clamp(self):
        for initial,expected in ((5,3),(-2,-2),(0,0)):
            r=initial_skill_resource_reference(fixture(initial,3,[]));p=r['initial_pool']
            self.assertEqual(p['initial_integer_after_upper_cap'],expected)
            self.assertEqual(p['initial_sp_raw'],expected*_Q32)
            self.assertFalse(p['initial_lower_zero_clamp_applied'])
            self.assertIsNone(p['actual_current_sp']);self.assertIsNone(p['actual_current_max_sp'])

    def test_source_integer_float_conversion_is_not_exact_integer_fp_conversion(self):
        r=initial_skill_resource_reference(fixture(16777217,20000000,[]))
        self.assertEqual(r['initial_pool']['initial_sp_raw'],16777216*_Q32)
        r=initial_skill_resource_reference(fixture(16777219,16777219,[]))
        self.assertEqual(r['state'],'unsupported_initial_rounding_at_capacity')
        self.assertIsNone(r['initial_pool'])

    def test_exact_signed_fp_ge_has_no_hp_epsilon(self):
        source=fixture(1,2,[skill('A',1)])
        for raw,passed in ((_Q32-1,False),(_Q32,True),(_Q32+1,True)):
            r=initial_skill_resource_reference(source,plan(['A'],starting_sp_raw=raw))
            event=r['declared_request_budget']['events'][0]
            self.assertEqual(event['sp_numeric_gate_pass'],passed)
            self.assertEqual(event['after_sp_raw'],raw-_Q32 if passed else raw)
        self.assertFalse(initial_skill_resource_reference(source,plan(['A'],starting_sp=.9999999))[
            'declared_request_budget']['events'][0]['sp_numeric_gate_pass'])

    def test_zero_and_negative_cost_never_request_sp_gain_or_loss(self):
        source=fixture(-2,3,[skill('zero',0),skill('negative',-3),skill('positive',1)])
        r=initial_skill_resource_reference(source,plan(['zero','negative','positive']))
        events=r['declared_request_budget']['events']
        self.assertEqual([e['sp_numeric_gate_pass'] for e in events],[False,True,False])
        self.assertEqual([e['requested_delta'] for e in events],[0,0,0])
        self.assertEqual([e['after_sp_raw'] for e in events],[-2*_Q32]*3)
        self.assertTrue(r['skills'][1]['nonpositive_cost_request_is_no_op'])

    def test_declared_sequence_consumes_one_shared_pool_and_order_matters(self):
        for requests,gate,remaining in ((['A','B'],[True,False],2),(['B','A'],[True,False],1)):
            r=initial_skill_resource_reference(fixture(),plan(requests))
            b=r['declared_request_budget']
            self.assertEqual([e['sp_numeric_gate_pass'] for e in b['events']],gate)
            self.assertEqual(b['remaining_sp_raw'],remaining*_Q32)
            self.assertTrue(b['shared_pool']);self.assertTrue(b['no_regeneration_or_other_effects_added'])
            self.assertIsNone(b['actual_accepted_requests']);self.assertIsNone(b['actual_cast_count'])
            self.assertIsNone(b['actual_time_seconds'])
            self.assertTrue(all(e['actual_cast_succeeded'] is None for e in b['events']))

    def test_no_request_budget_or_actual_availability_is_inferred_by_default(self):
        r=initial_skill_resource_reference(fixture());self.assertIsNone(r['declared_request_budget'])
        self.assertIsNone(r['full_availability']);self.assertIsNone(r['first_activation_seconds'])
        self.assertIsNone(r['complete_cycle_seconds']);self.assertFalse(r['actual_controller_or_attachment_verified'])
        self.assertFalse(r['current_hotfix_equivalence_proven'])
        for item in r['skills']:
            self.assertIsNone(item['full_availability']);self.assertIsNone(item['actual_cast_count'])
            self.assertFalse(item['actual_attachment_verified'])

    def test_data_cooldown_component_preserves_prefab_override_unknown(self):
        r=initial_skill_resource_reference(fixture(skills=[skill('A',1,-4),skill('B',1,.1),skill('C',1,0)]))
        for row,expected in zip(r['skills'],(0,.1,0)):
            self.assertEqual(row['source_init_cooldown_period_fp_raw'],max(0,_fp(expected)))
            self.assertEqual(row['default_constructor_init_cooldown_override'],-1)
            self.assertIsNone(row['actual_prefab_init_cooldown_override'])
            self.assertIn('including0',row['override_rule']);self.assertTrue(row['cooldown_wait_first_period'])
        text=skill_resource_text(r,True);self.assertIn('不由初始冷却0推出生即施放',text)

    def test_unsupported_cooldown_does_not_destroy_independent_sp_gate(self):
        for cd in (None,float('nan'),float('inf'),1e100):
            r=initial_skill_resource_reference(fixture(skills=[skill('A',1,cd)]))
            self.assertEqual(r['state'],'conditional_initial_numeric_gates_available')
            row=r['skills'][0];self.assertTrue(row['initial_sp_numeric_gate_pass'])
            self.assertIsNone(row['source_init_cooldown_period_reference'])
            self.assertEqual(row['source_init_cooldown_reference_state'],'unsupported_native_cooldown_conversion')

    def test_invalid_source_pool_and_skill_shape_are_unknown_not_zero(self):
        for init,maximum in ((True,2),(1.0,2),(0,-1),(2,True),(1,1<<31)):
            r=initial_skill_resource_reference(fixture(init,maximum));self.assertEqual(r['state'],'unsupported_source_pool')
            self.assertIsNone(r['initial_pool'])
        for rows in ([skill('A',True)],[skill('A',1.0)],[skill('A',1<<31)],[skill('',1)],[skill('A',1),skill('A',2)]):
            r=initial_skill_resource_reference(fixture(skills=rows));self.assertEqual(r['state'],'unsupported_source_skill')
            self.assertEqual(r['skills'],[]);self.assertIsNone(r['declared_request_budget'])

    def test_no_skill_db_borrow_when_pool_only_baseline_known(self):
        source=fixture();source['compiled_configuration']['state']='constructor_mechanism_baseline_unknown'
        r=initial_skill_resource_reference(source,plan(['A']))
        self.assertEqual(r['state'],'conditional_initial_pool_only_skill_baseline_unknown')
        self.assertEqual(r['initial_pool']['initial_sp_reference'],4)
        self.assertEqual(r['skills'],[]);self.assertIsNone(r['declared_request_budget'])
        self.assertIn('不借用数据库费用',skill_resource_text(r))

    def test_invalid_or_undeclared_plans_are_rejected_without_hidden_effect_inputs(self):
        bad=[{},[],{'requests':['A']},plan(['A'],scope='actual_casts'),plan('A'),plan(['']),plan([True]),
            plan(['A']*257),plan(['A'],starting_sp=True),plan(['A'],starting_sp=float('nan')),
            plan(['A'],starting_sp=float('inf')),plan(['A'],starting_sp=10**1000),
            plan(['A'],starting_sp_raw=True),plan(['A'],starting_sp_raw=1<<63),
            plan(['A'],starting_sp_raw=-(1<<63)-1),plan(['A'],starting_sp=1,starting_sp_raw=_Q32),
            plan(['A'],regeneration=1),plan(['A'],starting_sp=5),plan(['unknown'])]
        for value in bad:
            with self.subTest(value=str(value)[:100]),self.assertRaises(ValueError):
                initial_skill_resource_reference(fixture(),value)

    def test_plan_output_is_independent_of_source_and_caller_mutations(self):
        source=fixture();p=plan(['A'],starting_sp=4);before=deepcopy(source)
        r=initial_skill_resource_reference(source,p);self.assertEqual(source,before)
        p['requests'].append('B');source['compiled_configuration']['configuration']['skills'][0]['spCost']=4
        self.assertEqual(r['declaration']['requests'],['A']);self.assertEqual(r['skills'][0]['source_sp_cost'],2)
        r['skills'][0]['source_sp_cost']=9
        self.assertEqual(initial_skill_resource_reference(fixture())['skills'][0]['source_sp_cost'],2)

    def test_fixed_real_skill_pool_and_budget_enter_public_mechanism_and_preview(self):
        r=enemy_skill_reference('ro6_n_5_4','enemy_10087_hlchgr_2',0,
            resource_plan=plan(['ForeverEnhance']*8))
        resource=r['initial_skill_resources'];self.assertEqual(resource['initial_pool']['source_init_sp'],7)
        b=resource['declared_request_budget'];self.assertEqual(sum(e['sp_numeric_gate_pass'] for e in b['events']),7)
        self.assertFalse(b['events'][-1]['sp_numeric_gate_pass']);self.assertIsNone(b['actual_cast_count'])
        payload={'stage_id':'ro6_n_5_4','enemy_id':'enemy_10087_hlchgr_2','level':0,
            'resource_plan':plan(['ForeverEnhance']*8)}
        data=run_offline_query('battle','mechanism',payload)
        self.assertEqual(data['initial_skill_resources'],resource)
        text=render_offline_result('battle','mechanism',data)
        self.assertIn('共享技力数值门与声明预算',text);self.assertIn('实际施放未知',text)
        entry=enemy_preview('ro6_n_5_4','enemy_10087_hlchgr_2',0)
        self.assertIn('技能技力条件分项',enemy_text(entry))
        self.assertIn('实际首次发动时刻：未知',enemy_skill_text(r))

    def test_all_fixed_bindings_keep_conditional_scope_and_false_constructors_unknown(self):
        states={};skills=positive=0
        for stage,binding in skill_data()['bindings'].items():
            for key in binding:
                enemy,level=key.rsplit('@',1);r=enemy_skill_reference(stage,enemy,int(level));x=r['initial_skill_resources']
                states[x['state']]=states.get(x['state'],0)+1;skills+=len(x['skills'])
                positive+=sum(s['source_sp_cost']>0 for s in x['skills'])
                self.assertIsNone(x['full_availability']);self.assertIsNone(x['first_activation_seconds'])
                self.assertIsNone(x['complete_cycle_seconds']);self.assertIsNone(x['declared_request_budget'])
                self.assertFalse(x['current_hotfix_equivalence_proven'])
                for row in x['skills']:self.assertIsNone(row['actual_cast_count'])
        self.assertEqual(sum(states.values()),1087)
        self.assertEqual(states,{'conditional_initial_numeric_gates_available':1028,
            'conditional_initial_pool_only_skill_baseline_unknown':43,'unavailable_source':16})
        self.assertEqual((skills,positive),(450,22))

class EnemySkillResourceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_fixed_preview_displays_chinese_gate_and_never_claims_actual_cast(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.show()
        panel.set_stage('ro6_n_5_4');self.qt.processEvents()
        index=next(i for i in range(panel.enemy_combo.count()) if (panel.enemy_combo.itemData(i) or (None,))[0]=='enemy_10087_hlchgr_2')
        panel.enemy_combo.setCurrentIndex(index);self.qt.processEvents();text=panel.enemy_detail.toPlainText()
        self.assertIn('技能技力条件分项',text);self.assertIn('初始时达到费用',text)
        self.assertIn('完整可施放未知',text);self.assertNotIn('ForeverEnhance',text)
        panel.technical.setChecked(True);self.qt.processEvents()
        self.assertIn('ForeverEnhance',panel.enemy_detail.toPlainText())
        self.assertIn('实际覆盖未知',panel.enemy_detail.toPlainText())

    def test_offline_query_runs_declared_budget_and_refresh_keeps_selected_result(self):
        panel=OfflineToolsPanel();self.addCleanup(panel.close);panel.show()
        panel.select_query('battle','mechanism')
        payload={'stage_id':'ro6_n_5_4','enemy_id':'enemy_10087_hlchgr_2','level':0,
            'resource_plan':plan(['ForeverEnhance']*8)}
        panel.editor.setPlainText(json.dumps(payload));panel.run_button.click()
        end=time.monotonic()+8
        while panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(panel._workers);self.assertIsNotNone(panel.result_snapshot(),panel.status.text())
        self.assertEqual(panel.result_snapshot()['initial_skill_resources']['declared_request_budget']['remaining_sp_raw'],0)
        self.assertIn('第8项：技力数值门不通过',panel.result_view.toPlainText())
        before=(panel.editor.toPlainText(),panel.current_query(),panel.result_view.toHtml(),panel.result_snapshot())
        panel.set_stage('ro6_n_2_3');self.qt.processEvents()
        self.assertEqual(before,(panel.editor.toPlainText(),panel.current_query(),panel.result_view.toHtml(),panel.result_snapshot()))

if __name__=='__main__':unittest.main()
