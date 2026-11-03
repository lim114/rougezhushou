"""Source/qualification boundaries for the existing nine condition controls."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge.catalog import catalog
from rouge.condition_cultivation import explanations, format_explanation, TARGET_FIELDS, TARGET_OPERATORS
from rouge.operator_options import OPTIONS


class ConditionCultivationTests(unittest.TestCase):
    def scenario(self, owner, elite=2, level=1, potential=1, module=None, stage=0):
        return {'operator':owner,'skill':1,'elite':elite,'level':level,'potential':potential,
                'module_id':module,'module_level':stage}

    def rows(self, scenario, **kwargs):
        return explanations(catalog()['operators'][scenario['operator']],scenario,**kwargs)

    def field(self, scenario, field, **kwargs):
        return next(r for r in self.rows(scenario,**kwargs) if r['field']==field)

    def test_nine_fields_keep_existing_owner_skill_and_named_consumer_surface(self):
        fields=[]
        for owner in TARGET_OPERATORS:
            profile=catalog()['operators'][owner]
            for skill in range(1,len(profile['skills'])+1):
                scenario={**self.scenario(owner),'skill':skill}
                rows=self.rows(scenario)
                expected=[key for key,_,_,_,skills in OPTIONS[owner] if key in TARGET_FIELDS and skill in skills]
                self.assertEqual([r['field'] for r in rows],expected)
                if skill==1:fields.extend(expected)
        self.assertEqual(len(fields),9)
        self.assertEqual(set(fields),set(TARGET_FIELDS))
        self.assertEqual(len(TARGET_OPERATORS),6)

    def test_placeholders_and_unrelated_owner_never_call_selector(self):
        with patch('rouge.operator_engine.selected_talents',side_effect=AssertionError('unexpected selector')):
            self.assertEqual(explanations(None,{'operator':None,'skill':None}),[])
            self.assertEqual(explanations(None,{'operator':'unimplemented','skill':1}),[])
            self.assertEqual(explanations(catalog()['operators']['char_2025_shu'],{'operator':'char_2025_shu','skill':None}),[])
            self.assertEqual(explanations(catalog()['operators']['char_110_deepcl'],{'operator':'char_110_deepcl','skill':1}),[])

    def test_orchid_E0_power_and_E1_nearby_have_distinct_qualification(self):
        owner='char_1048_orchd2'
        power=self.field(self.scenario(owner,0),'power_coating',values={'power_coating':True})
        nearby=self.field(self.scenario(owner,0),'near_previous_deployment',values={'near_previous_deployment':True})
        self.assertEqual(power['eligibility_status'],'met')
        self.assertEqual(power['original_source']['path'],owner+'.talents[0].candidates[0]')
        self.assertEqual(nearby['eligibility_status'],'unmet')
        self.assertEqual(self.field(self.scenario(owner,1),'near_previous_deployment')['original_source']['path'],owner+'.talents[1].candidates[0]')
        self.assertIn('普通与蓄力攻击不使用',format_explanation(power))
        self.assertIs(power['condition_value'],True)
        self.assertIs(nearby['condition_value'],True)

    def test_base_potential_transition_uses_last_actual_candidate_coordinates(self):
        owner='char_298_susuro'
        for elite,potential,index in ((1,4,0),(1,5,1),(2,4,2),(2,5,3)):
            with self.subTest(elite=elite,potential=potential):
                row=self.field(self.scenario(owner,elite,potential=potential),'low_cost_healing_target')
                self.assertEqual(row['original_source']['path'],f'{owner}.talents[0].candidates[{index}]')
                self.assertEqual(row['original_source']['raw_candidate']['requiredPotentialRank'],4 if potential==5 else 0)
        self.assertEqual(self.field(self.scenario(owner,0),'low_cost_healing_target')['eligibility_status'],'unmet')

    def test_all_eight_modules_three_stages_before_gate_preserve_base_source(self):
        modules=(('char_2025_shu','uniequip_002_shu','four_sui',60),
                 ('char_298_susuro','uniequip_002_susuro','low_cost_healing_target',40),
                 ('char_1048_orchd2','uniequip_002_orchd2','near_previous_deployment',60),
                 ('char_4087_ines','uniequip_002_ines','stolen_enemy_count',60),
                 ('char_437_mizuki','uniequip_002_mizuki','enemy_below_half',60),
                 ('char_437_mizuki','uniequip_003_mizuki','enemy_below_half',60),
                 ('char_437_mizuki','uniequip_004_mizuki','enemy_below_half',60),
                 ('char_1044_hsgma2','uniequip_002_hsgma2','current_hp_ratio',60))
        for owner,module,field,gate in modules:
            for stage in (1,2,3):
                for potential in (4,5):
                    with self.subTest(module=module,stage=stage,potential=potential):
                        row=self.field(self.scenario(owner,level=gate-1,potential=potential,module=module,stage=stage),field)
                        self.assertEqual(row['eligibility_status'],'met')
                        self.assertEqual(row['original_source']['table'],'character_table')
                        self.assertFalse(row['new_arithmetic_applied'])

    def test_named_module_overlay_exact_part_stage_and_potential_not_neighbor(self):
        modules=(('char_298_susuro','uniequip_002_susuro','low_cost_healing_target',40,0),
                 ('char_1048_orchd2','uniequip_002_orchd2','near_previous_deployment',60,1),
                 ('char_4087_ines','uniequip_002_ines','stolen_enemy_count',60,0),
                 ('char_437_mizuki','uniequip_003_mizuki','enemy_below_half',60,1),
                 ('char_1044_hsgma2','uniequip_002_hsgma2','current_hp_ratio',60,1))
        for owner,module,field,gate,index in modules:
            for stage in (2,3):
                for potential in (4,5):
                    with self.subTest(module=module,stage=stage,potential=potential):
                        row=self.field(self.scenario(owner,level=gate,potential=potential,module=module,stage=stage),field)
                        source=row['original_source']
                        self.assertEqual(source['table'],'battle_equip_table')
                        self.assertEqual(source['module_stage'],stage)
                        self.assertEqual(source['talent_index'],index)
                        self.assertEqual(source['part_index'],1)
                        self.assertEqual(source['candidate_index'],int(potential==5 and owner not in ('char_1048_orchd2','char_1044_hsgma2')))
                        self.assertEqual(source['raw_candidate']['name'],row['talent_name'])
                        self.assertEqual(source['raw_candidate']['upgradeDescription'],row['selected_talent']['description'])
                        self.assertIs(row['native_attachment'],None)

    def test_mizuki_other_modules_never_become_second_talent_hidden_source(self):
        owner='char_437_mizuki'
        for module in ('uniequip_002_mizuki','uniequip_004_mizuki'):
            for stage in (1,2,3):
                row=self.field(self.scenario(owner,level=60,module=module,stage=stage),'enemy_below_half')
                self.assertEqual(row['original_source']['table'],'character_table')
                self.assertEqual(row['original_source']['talent_index'],1)
                self.assertEqual(row['talent_name'],'反移情')
                self.assertIn('隐藏能力附着边界仍未核验',format_explanation(row))

    def test_zero_selected_value_remains_eligible_without_inventing_raw_identity(self):
        owner='char_1044_hsgma2';profile=deepcopy(catalog()['operators'][owner])
        for candidate in profile['talents'][1]:
            candidate['values']={key:0 for key in candidate['values']}
        row=explanations(profile,self.scenario(owner),values={'current_hp_ratio':1})[0]
        self.assertEqual(row['eligibility_status'],'met')
        self.assertEqual(row['source_status'],'missing')
        self.assertTrue(all(value==0 for value in row['selected_talent']['values'].values()))
        self.assertIn('原件坐标来源缺失',format_explanation(row))

    def test_type_only_or_signed_zero_mutation_cannot_claim_exact_original_source(self):
        owner='char_1044_hsgma2';scenario=self.scenario(owner)
        for value in (False,0,-0.0):
            with self.subTest(base_value=value,type=type(value)):
                profile=deepcopy(catalog()['operators'][owner])
                profile['talents'][1][0]['values']['max_atk']=value
                row=explanations(profile,scenario)[0]
                self.assertEqual(row['eligibility_status'],'met')
                self.assertEqual(row['source_status'],'missing')
        scenario=self.scenario(owner,level=60,module='uniequip_002_hsgma2',stage=3)
        for value in (False,0,-0.0):
            with self.subTest(module_value=value,type=type(value)):
                profile=deepcopy(catalog()['operators'][owner])
                module=next(m for m in profile['modules'] if m['id']==scenario['module_id'])
                candidate=module['levels'][2]['parts'][1]['addOrOverrideTalentDataBundle']['candidates'][0]
                entry=next(b for b in candidate['blackboard'] if b['key']=='max_atk')
                entry['value']=value
                row=explanations(profile,scenario)[0]
                self.assertEqual(row['eligibility_status'],'met')
                self.assertEqual(row['source_status'],'missing')

    def test_ines_count_and_hsgma_ratio_keep_independent_input_semantics(self):
        for owner,field,values in (('char_4087_ines','stolen_enemy_count',(0,1,100)),
                                   ('char_1044_hsgma2','current_hp_ratio',(0,.3,1))):
            for value in values:
                for elite in (0,1,2):
                    row=self.field(self.scenario(owner,elite),field,values={field:value})
                    self.assertEqual(row['condition_value'],value)
                    self.assertEqual(type(row['condition_value']),type(value))
                    self.assertIn('仍按原规则解析',format_explanation(row))
                    self.assertFalse(row['new_arithmetic_applied'])
        row=self.field(self.scenario('char_1044_hsgma2',level=60,module='uniequip_002_hsgma2',stage=3),'current_hp_ratio')
        self.assertEqual(row['modeled_parameter_keys'],['min_hp_ratio','min_atk','min_magic_resistance'])
        self.assertIn('atk',row['selected_talent']['values'])
        self.assertNotIn('atk',row['modeled_parameter_keys'])

    def test_effective_preview_missing_fields_and_simulated_level_are_labelled(self):
        scenario=self.scenario('char_2025_shu',level=90)
        row=self.field(scenario,'four_sui',state={'scope':'operator_profile','fields':{}})
        self.assertEqual(row['eligibility_status'],'met')
        self.assertTrue(row['uses_unconfirmed_preview'])
        self.assertEqual(row['training_provenance']['elite'],'preview_unconfirmed')
        self.assertIn('来源缺失，采用预览',format_explanation(row))
        state={'scope':'run','fields':{k:v for k,v in scenario.items() if k not in ('operator','skill')},'run_confirmed_fields':['elite','level','potential']}
        row=self.field(scenario,'four_sui',state=state,level_override=True)
        self.assertEqual(row['training_provenance']['level'],'simulated_override')
        self.assertIn('手动等级预览',format_explanation(row))

    def test_merged_run_and_account_view_retains_per_field_reference_provenance(self):
        scenario=self.scenario('char_298_susuro',level=40,potential=5,module='uniequip_002_susuro',stage=3)
        state={'scope':'run','fields':{k:v for k,v in scenario.items() if k not in ('operator','skill')},'run_confirmed_fields':['elite','level'],'skill_ranks':{'1':10}}
        row=self.field(scenario,'low_cost_healing_target',state=state)
        self.assertEqual(row['training_provenance']['elite'],'run_confirmed')
        self.assertEqual(row['training_provenance']['potential'],'account_reference')
        self.assertEqual(row['training_provenance']['module_id'],'account_reference')
        self.assertTrue(row['uses_account_reference'])
        self.assertIn('账号参考（本局未确认）',format_explanation(row))
        self.assertIs(row['account_unlock_verified'],None)

    def test_rows_detached_from_caller_catalog_raw_source_and_one_another(self):
        scenario=self.scenario('char_298_susuro',level=40,potential=5,module='uniequip_002_susuro',stage=3)
        before=deepcopy(scenario);profile=catalog()['operators'][scenario['operator']];profile_before=deepcopy(profile)
        rows=self.rows(scenario);fresh=self.rows(scenario)
        rows[0]['selected_talent']['values'].clear()
        rows[0]['original_source']['raw_candidate']['blackboard'][0]['value']=-999
        rows[0]['first_original_gate']['elite']=99
        self.assertEqual(scenario,before)
        self.assertEqual(profile,profile_before)
        self.assertEqual(self.rows(scenario),fresh)

    def test_opaque_state_and_unrelated_caller_values_are_never_copied(self):
        class Opaque:
            def __deepcopy__(self,memo):raise AssertionError('opaque state copied')
        opaque=Opaque();scenario={**self.scenario('char_2025_shu'),'unrelated':opaque}
        state={'scope':'operator_profile','fields':{},'private':opaque,'history':opaque}
        rows=self.rows(scenario,state=state,values={'four_sui':False,'unrelated':opaque})
        self.assertEqual(len(rows),3)
        self.assertIs(scenario['unrelated'],opaque)
        self.assertIs(state['private'],opaque)

    def test_unavailable_presentation_source_does_not_rewrite_original_error(self):
        scenario=self.scenario('char_298_susuro');before=deepcopy(scenario)
        with patch('rouge.operator_engine.selected_talents',side_effect=IndexError('original selector boundary')):
            row=self.field(scenario,'low_cost_healing_target')
        self.assertEqual(row['eligibility_status'],'unavailable')
        self.assertEqual(row['source_status'],'missing')
        self.assertEqual(row['selection_error'],{'type':'IndexError','message':'original selector boundary'})
        self.assertEqual(scenario,before)
        self.assertIn('原计算流程继续处理输入与错误',format_explanation(row))

    def test_plain_UI_text_keeps_clock_attachment_and_account_unlock_unknown(self):
        row=self.field(self.scenario('char_2025_shu'),'four_sui',values={'four_sui':True})
        text=format_explanation(row)
        self.assertIn('首跳、重置和锁技得点仍未核验',text)
        self.assertIn('当前局外条件声明：是',text)
        self.assertIn('账号任务解锁或原生附着',text)
        self.assertNotIn('https://',text)
        self.assertIs(row['actual_activation'],None)
        self.assertIs(row['native_attachment'],None)
        self.assertFalse(row['new_arithmetic_applied'])


if __name__=='__main__':unittest.main()
