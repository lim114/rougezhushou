import copy,json,unittest
from pathlib import Path
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.damage_budget import damage_sources
from rouge.mei_module_static_reference import FLAG,MOTION,qualification,rule
from rouge.reporting import format_report

def scenario(skill=1,stage=1,**extra):
    return {'operator':'char_133_mm','skill':skill,'skill_rank':10,'elite':2,'level':40,
            'base_attack':1000,'module_id':'uniequip_002_mm','module_level':stage,
            FLAG:True,'relic_context':{MOTION:'fly'},**extra}
def packets(r):return {p['key']:p for p in r['mei_module_static_reference']['packets']}

class MeiModuleStaticReferenceTests(unittest.TestCase):
    def test_default_off_and_inactive_input_unchanged(self):
        for skill in (1,2):
            s=scenario(skill);s.pop(FLAG)
            self.assertEqual(calculate_damage(s),calculate_damage({**s,FLAG:False}))
            self.assertNotIn('mei_module_static_reference',calculate_damage(s))
        for extra in ({'level':39},{'module_id':None,'module_level':0}):
            self.assertNotIn('mei_module_static_reference',calculate_damage(scenario(relic_context={MOTION:9},**extra)))
        self.assertNotIn('mei_module_static_reference',calculate_damage({'operator':'silverash','skill':1,FLAG:9}))

    def test_three_stages_both_skills_and_timing_previews(self):
        for stage in (1,2,3):
            for skill in (1,2):
                for mode in ('frames','continuous'):
                    with self.subTest(stage=stage,skill=skill,mode=mode):
                        s=scenario(skill,stage,timing_mode=mode)
                        r=calculate_damage(s);ref=r['mei_module_static_reference']
                        self.assertTrue(qualification(s)['qualified'])
                        self.assertEqual(qualification(s)['native_skill_index'],skill-1)
                        self.assertEqual(len(ref['packets']),2)
                        self.assertEqual(ref['packets'][1]['module_attack_scale'],1.1)
                        self.assertEqual(ref['native_multiplier_parameter'],1.1)
                        self.assertIsNone(r['total_damage'])
                        self.assertIsNone(r['estimate']['skill']['cycle_damage'])

    def test_qualification_unlock_and_map_not_invented(self):
        for extra in ({'elite':1,'level':60,'skill_rank':7},{'level':39},{'module_level':0},{'module_id':None}):
            self.assertFalse(qualification(scenario(**extra))['qualified'])
        for stage in (1,2,3):
            self.assertTrue(qualification(scenario(2,stage,map_tag='rogue_5'))['qualified'])
            self.assertEqual(qualification(scenario(1,stage))['native_skill_gate'],'none_in_current_trait_prefabs')

    def test_before_armor_order_and_existing_talent_gear_are_not_repeated(self):
        for stage,raw in ((1,2140),(2,2200),(3,2240)):
            r=calculate_damage(scenario(stage=stage,enemy_defense=200))
            off=calculate_damage(scenario(stage=stage,enemy_defense=200,**{FLAG:False}))
            self.assertAlmostEqual(r['per_hit'],raw*1.1-200)
            self.assertNotEqual(r['per_hit'],(raw-200)*1.1)
            self.assertEqual(r['attack'],off['attack'])
            self.assertEqual(r['estimate']['base_stats'],off['estimate']['base_stats'])
            self.assertEqual(r['estimate']['skill']['skill_attack'],off['estimate']['skill']['skill_attack'])
            self.assertAlmostEqual(packets(r)['normal']['per_hit_reference'],(raw/2)*1.1-200)

    def test_skill2_additive_attack_and_final_damage_taken_once(self):
        s=scenario(2,3,enemy_defense=300,effects=[{'kind':'attack_pct','value':.25},
                   {'kind':'damage_taken','damage_type':'physical','value':.2}])
        r=calculate_damage(s);p=packets(r)
        self.assertAlmostEqual(p['skill']['per_hit_reference'],(r['attack']*1.1-300)*1.2)
        self.assertAlmostEqual(p['normal']['per_hit_reference'],(r['estimate']['base_stats']['attack']*1.1-300)*1.2)
        self.assertEqual(p['skill']['skill_attack_scale'],1)
        self.assertGreater(p['skill']['source_attack_reference'],p['normal']['source_attack_reference'])

    def test_physical_floor_is_based_on_scaled_raw(self):
        for skill in (1,2):
            r=calculate_damage(scenario(skill,enemy_defense=100000))
            for p in packets(r).values():
                self.assertAlmostEqual(p['per_hit_reference'],p['selected_raw_packet']*.05)

    def test_false_condition_keeps_unmodified_packet_but_actual_totals_unknown(self):
        for skill in (1,2):
            r=calculate_damage(scenario(skill,relic_context={MOTION:'not_fly'}))
            off=calculate_damage(scenario(skill,**{FLAG:False}))
            self.assertEqual(r['per_hit'],off['components'][0]['per_hit'])
            self.assertTrue(all(p['module_attack_scale']==1 for p in packets(r).values()))
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['mei_airborne_module_reference']['actual_target_is_airborne'])

    def test_missing_condition_retains_both_candidates_and_no_damage_source(self):
        for context in ({},{MOTION:'unknown'},{'enemy_is_airborne':True,'levitate_triggers':999}):
            for skill in (1,2):
                r=calculate_damage(scenario(skill,relic_context=context))
                for p in packets(r).values():
                    self.assertIsNone(p['per_hit_reference'])
                    self.assertEqual(len(p['motion_unknown_candidates']),2)
                self.assertIsNone(r['per_hit']);self.assertEqual(damage_sources(r),[])
                self.assertIsNone(r['total_damage'])

    def test_enemy_name_weight_base_class_and_top_level_condition_do_not_infer(self):
        base=scenario(relic_context={});reference=calculate_damage(base)
        for extra in ({'enemy_weight':0},{'enemy_name':'飞行目标'},{'enemy_is_airborne':True},
                      {MOTION:'fly'},{'levitate_triggers':100}):
            self.assertEqual(calculate_damage({**base,**extra}),reference)

    def test_declarations_reject_bool_count_text_case_and_objects(self):
        for value in (True,False,0,1,1.1,'FLY','false',[],{}):
            with self.assertRaisesRegex(ValueError,MOTION):
                calculate_damage(scenario(relic_context={MOTION:value}))
        for flag in (1,'true',None):
            with self.assertRaisesRegex(ValueError,FLAG):calculate_damage(scenario(**{FLAG:flag}))

    def test_zero_observation_and_empty_target_keep_zero_conditional_count(self):
        for skill in (1,2):
            for mode in ('frames','continuous'):
                for extra in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
                              {'timing':{'target_windows':[]}}):
                    r=calculate_damage(scenario(skill,timing_mode=mode,relic_context={},**extra))
                    p=packets(r)['skill']
                    self.assertEqual(p['modeled_or_declared_count'],0)
                    self.assertEqual(p['conditional_count_damage_reference'],0)
                    self.assertIsNone(r['total_damage'])
                    self.assertIsNone(p['per_hit_reference'])

    def test_actual_report_budget_sources_receive_selected_owner_packet(self):
        for skill in (1,2):
            r=calculate_damage(scenario(skill,enemy_defense=111))
            selected=packets(r)['skill']
            self.assertEqual(damage_sources(r)[0]['per_hit'],selected['per_hit_reference'])
            self.assertEqual(r['components'][0]['total'],selected['conditional_count_damage_reference'])
            self.assertIsNone(r['components'][0]['actual_total'])
            if skill==1:self.assertEqual(r['mei_s1_reference']['per_hit_damage_reference'],selected['per_hit_reference'])
            text=format_report(r)
            self.assertIn('明确选择的静态单包条件',text)
            self.assertIn('110%乘入本体伤害包的atkScale',text)
            self.assertNotIn('110%参数未计入当前伤害数值',text)
            self.assertIn('完整实际技能伤害',text)
            source=r['report']['selected_module_source_reference']['existing_coverage']
            self.assertIn('/mei_module_static_reference',source['native_paths'])
            self.assertTrue(any(s['section_id']=='mei_module_static_reference' for s in source['report_sections']))

    def test_unknown_report_candidates_and_static_versus_runtime_flags(self):
        r=calculate_damage(scenario(relic_context={}));ref=r['mei_module_static_reference']
        self.assertTrue(ref['native_static_binding_verified']);self.assertTrue(ref['native_static_composition_verified'])
        for key in ('runtime_binding_verified','current_hotfix_equivalence_verified'):self.assertFalse(ref[key])
        for key in ('actual_target_motion_mode','actual_attachment','actual_source_valid','actual_window_damage','full_cast_damage','cycle_damage'):
            self.assertIsNone(ref[key])
        self.assertIn('条件不成立候选',format_report(r));self.assertIn('条件成立候选',format_report(r))

    def test_input_catalog_and_reference_repeat_are_immutable(self):
        s=scenario(2,3,potential=6,window_seconds=10);before=copy.deepcopy(s)
        source=json.dumps(catalog(),ensure_ascii=False,sort_keys=True)
        r=calculate_damage(s)
        self.assertEqual(r,calculate_damage(s));self.assertEqual(s,before)
        self.assertEqual(source,json.dumps(catalog(),ensure_ascii=False,sort_keys=True))
        r['mei_module_static_reference']['source']['catalog_commit']='changed'
        self.assertNotEqual(calculate_damage(s)['mei_module_static_reference']['source']['catalog_commit'],'changed')

    def test_current_proof_matches_consumed_rule_asset_stages_and_melee_vtable(self):
        folder=Path(__file__).resolve().parents[1]/'research/p2-mei-module-current'
        receipt=json.loads((folder/'receipt.json').read_text(encoding='utf-8'))
        proof=json.loads((folder/'native-proof.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['physical_validation']['methods'],52)
        self.assertTrue(receipt['physical_validation']['all_instruction_bytes_match'])
        self.assertEqual(receipt['physical_validation']['limits'],[])
        self.assertEqual(rule()['source']['game_dll_sha256'],receipt['physical_validation']['game_dll_sha256'])
        self.assertEqual(rule()['stages'],receipt['stages'])
        self.assertFalse(receipt['game_dll_executed']);self.assertFalse(receipt['process_memory_read'])
        fields=json.loads((folder/'selected-metadata.json').read_text(encoding='utf-8'))
        melee=next(t for t in fields['selected'] if t['name']=='Torappu.Battle.Abilities.MeleeAttack')
        self.assertEqual(melee['vtable'][107]['decoded_index'],91792)
        self.assertEqual(melee['vtable'][106]['decoded_index'],91791)
        self.assertEqual(melee['vtable'][112]['decoded_index'],90348)
        self.assertTrue(any(w['method']['metadata_method_index']==99327 for w in proof['methods']))
        self.assertTrue(any(w['method']['metadata_method_index']==76027 for w in proof['methods']))

if __name__=='__main__':unittest.main()
