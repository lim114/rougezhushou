import copy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.animation_reference import choices, descriptor, references, static_bindings, three_part_profile
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.timing import AttackTimeline


class ThreePartStaticCurrentTests(unittest.TestCase):
    def selected(self,op='kaltsit',skill=1,normal=False,face='Front',animation='Attack_Loop'):
        record=next(r for r in choices(op,skill,normal=normal) if r['orientation']==face and r['animation']==animation)
        key='normal_animation_reference' if normal else 'animation_reference'
        return record,descriptor(op,skill,{key:record['id']},normal=normal)

    def test_kaltsit_normal_and_s1_exact_mode_scopes_and_three_variants(self):
        for normal,mode in [(True,0),(False,3)]:
            rows=choices('kaltsit',1,normal=normal)
            self.assertEqual({(r['animation'],r['orientation']) for r in rows},
                {('Attack_Loop','Front'),('Attack_Down_Loop','Front'),('Attack_Loop','Back')})
            for r in rows:
                self.assertEqual(r['mode_indices'],[mode])
                b=r['static_action_binding']
                self.assertEqual(b['ability_sources'][0]['ability_type'],'RangedHeal')
                self.assertFalse(b['native_animation_loop'])
                self.assertTrue(b['three_part_reference']['only_begin_when_first_attack'])
                self.assertEqual(b['three_part_reference']['max_animation_scale'],-1)
                self.assertEqual(r['preview']['windup_frames'],18)
                self.assertFalse(r['runtime_binding_verified'])

    def test_silverash_candidates_preserve_face_events_and_do_not_assign_order_or_probability(self):
        rows=choices('silverash',3,normal=True)
        self.assertEqual(len(rows),6)
        self.assertEqual({(r['animation'],r['orientation']) for r in rows},
            {(a,f) for a in ('Attack_A','Attack_B','Attack_C') for f in ('Front','Back')})
        self.assertEqual({(r['animation'],r['orientation']):r['preview']['windup_frames'] for r in rows},
            {('Attack_A','Front'):15,('Attack_B','Front'):17,('Attack_C','Front'):16,
             ('Attack_A','Back'):17,('Attack_B','Back'):16,('Attack_C','Back'):16})
        for r in rows:
            choice=r['static_action_binding']['three_part_reference']['selection']
            self.assertEqual(choice['method'],'Random')
            self.assertEqual(choice['source_enum_value'],0)
            self.assertEqual(choice['candidates'],3)
            for k in ('actual_branch','probabilities','sequence'):self.assertIsNone(choice[k])

    def test_first_attack_gate_changes_entire_chain_scaling_and_event_offset(self):
        _,data=self.selected()
        p=three_part_profile(data,2.5)
        first,again=p['conditional_profiles']
        self.assertTrue(first['first_attack_condition'])
        self.assertFalse(again['first_attack_condition'])
        self.assertEqual(first['scaled_segment_seconds'],{'begin':.25,'oneshot':2.25,'end':0})
        self.assertEqual(again['scaled_segment_seconds'],{'begin':0,'oneshot':2.5,'end':0})
        self.assertAlmostEqual(first['animation_only_on_attack_offset_seconds'],.7,places=6)
        self.assertAlmostEqual(again['animation_only_on_attack_offset_seconds'],.5,places=6)
        self.assertIsNone(p['first_attack_gate_actual'])
        for case in p['conditional_profiles']:
            for k in ('actual_chain_start_seconds','actual_callback_seconds','actual_end_seconds'):self.assertIsNone(case[k])
        self.assertIsNone(p['actual_callback_frames'])
        self.assertFalse(p['runtime_binding_verified'])

    def test_kaltsit_allows_slow_playback_while_silverash_clamps_duration_scale(self):
        _,k=self.selected()
        first,again=three_part_profile(k,5)['conditional_profiles']
        self.assertEqual(first['scaled_segment_seconds'],{'begin':.5,'oneshot':4.5,'end':0})
        self.assertAlmostEqual(again['scaled_segment_seconds']['oneshot'],5,places=5)
        self.assertLess(first['playback_speed'],1)
        _,s=self.selected('silverash',3,True,animation='Attack_A')
        first,again=three_part_profile(s,5)['conditional_profiles']
        self.assertEqual(first['playback_speed'],1)
        self.assertEqual(again['playback_speed'],1)
        self.assertAlmostEqual(first['animation_only_chain_seconds'],4/3,places=6)
        self.assertAlmostEqual(again['animation_only_chain_seconds'],1.2,places=6)
        fast=three_part_profile(s,.6)['conditional_profiles'][0]
        self.assertAlmostEqual(fast['scaled_segment_seconds']['begin'],.06,places=6)
        self.assertAlmostEqual(fast['scaled_segment_seconds']['oneshot'],.54,places=6)

    def test_invalid_cooldown_is_not_coerced_to_a_clock(self):
        _,d=self.selected()
        for value in (True,False,None,'bad',0,-1,math.inf,math.nan,3601,1e-320,1e-40):
            with self.subTest(value=value),self.assertRaises(ValueError):three_part_profile(d,value)

    def test_actual_calculation_suppresses_body_18_frame_first_release(self):
        ref,_=self.selected()
        scenario={'operator':'kaltsit','skill':1,'timing':{'animation_reference':ref['id']}}
        before=copy.deepcopy(scenario);result=calculate_damage(scenario)
        stream=result['timing']['streams'][0]
        self.assertFalse(stream['known_animation'])
        self.assertIsNone(stream['windup_frames'])
        self.assertIsNone(stream['actual_first_release_seconds'])
        self.assertNotEqual(stream['release_frames'][0],18)
        self.assertTrue(stream['original_animation_reference']['body_event_is_not_first_release'])
        self.assertFalse(stream['original_animation_reference']['runtime_binding_verified'])
        self.assertIsNone(stream['three_part_reference']['first_attack_gate_actual'])
        self.assertEqual(scenario,before)

    def test_explicit_windup_override_keeps_preview_separate_from_conditional_profile(self):
        ref,_=self.selected()
        result=calculate_damage({'operator':'kaltsit','skill':1,
            'timing':{'animation_reference':ref['id'],'windup_frames':6,'recovery_frames':9}})
        stream=result['timing']['streams'][0]
        self.assertTrue(stream['known_animation'])
        self.assertEqual(stream['release_frames'][0],6)
        self.assertTrue(stream['original_animation_reference']['overridden_by_preview'])
        self.assertIsNone(stream['actual_first_release_seconds'])
        self.assertEqual(stream['three_part_reference']['conditional_profiles'][0]['source_segment_seconds']['oneshot'],3)

    def test_continuous_mode_reports_profiles_without_changing_existing_counts(self):
        ref,_=self.selected()
        s={'operator':'kaltsit','skill':1,'timing_mode':'continuous','timing':{'animation_reference':ref['id']}}
        result=calculate_damage(s)
        plain=calculate_damage({**s,'timing':{}})
        for key in ('total_damage','total_healing','attack_count'):
            self.assertEqual(result.get(key),plain.get(key))
        stream=result['timing']['streams'][0]
        self.assertFalse(stream['known_animation'])
        self.assertIn('three_part_reference',stream)
        self.assertIn('三段动作条件参考',format_estimate(result))

    def test_report_contains_both_profiles_segments_and_actual_unknowns(self):
        ref,_=self.selected()
        result=calculate_damage({'operator':'kaltsit','skill':1,'timing':{'animation_reference':ref['id']}})
        report=result['report']
        section=next(s for s in report['sections'] if s['id'].startswith('three_part_animation_'))
        labels={r['label'] for r in section['metrics']}
        for condition in ('开始段门成立','开始段门不成立'):
            for part in ('开始段','主体段','结束段'):self.assertIn(condition+'：缩放后'+part,labels)
        for label in ('实际首次出手回调','实际动作结束'):
            self.assertIsNone(next(r['value'] for r in section['metrics'] if r['label']==label))
        text=format_estimate(result)
        self.assertIn('firstAttack门',text)
        self.assertIn('延迟首击情景出手',text)
        self.assertIn('调度恢复相位',text)
        self.assertIn('Attack_End',text)

    def test_normal_silverash_profile_reaches_recharge_report_and_keeps_random_unknown(self):
        ref,_=self.selected('silverash',3,True,animation='Attack_B')
        result=calculate_damage({'operator':'silverash','skill':3,'timing':{'normal_animation_reference':ref['id']}})
        streams=[*result['timing'].get('streams',[]),*result['timing'].get('recharge_streams',[])]
        stream=next(s for s in streams if 'three_part_reference' in s)
        self.assertIsNone(stream['three_part_reference']['selection']['sequence'])
        text=format_estimate(result)
        self.assertIn('随机候选',text)
        self.assertIn('未设概率',text)

    def test_default_without_explicit_choice_is_unchanged(self):
        empty=copy.deepcopy(static_bindings());empty['operators']={}
        for scenario in ({'operator':'kaltsit','skill':1},{'operator':'silverash','skill':3}):
            normal=calculate_damage(scenario)
            with patch('rouge.animation_reference.static_bindings',return_value=empty):
                self.assertEqual(normal,calculate_damage(scenario))
            self.assertTrue(all('three_part_reference' not in s for s in normal['timing'].get('streams',[])))

    def test_changed_begin_source_duration_or_loop_rejects_complete_plan(self):
        record,_=self.selected()
        for field,value in [('sha256','wrong'),('seconds',.4)]:
            changed=copy.deepcopy(references())
            begin=next(r for r in changed['operators']['kaltsit']['records'] if r['animation']=='Attack_Begin' and r['orientation']=='Front')
            (begin['source'] if field=='sha256' else begin['duration'])[field]=value
            with patch('rouge.animation_reference.references',return_value=changed):
                self.assertNotIn(record['id'],[r['id'] for r in choices('kaltsit',1)])
                with self.assertRaises(ValueError):descriptor('kaltsit',1,{'animation_reference':record['id']})
        changed=copy.deepcopy(static_bindings())
        next(r for r in changed['operators']['kaltsit']['1']['records'] if r['reference_id']==record['id'])['three_part_reference']['begin']['native_loop']=True
        with patch('rouge.animation_reference.static_bindings',return_value=changed):
            self.assertNotIn(record['id'],[r['id'] for r in choices('kaltsit',1)])

    def test_wrong_scope_cannot_reuse_a_three_part_proof(self):
        ref,_=self.selected()
        with self.assertRaises(ValueError):descriptor('kaltsit',2,{'animation_reference':ref['id']})
        with self.assertRaises(ValueError):descriptor('silverash',3,{'animation_reference':ref['id']})
        self.assertIsNone(three_part_profile(descriptor('mechanist',3,{'animation_reference':choices('mechanist',3)[0]['id']}),2))

    def test_choices_descriptor_and_profiles_are_independent_copies(self):
        record,d=self.selected();expected=copy.deepcopy(d)
        d['three_part_reference']['begin']['duration_seconds']=999
        self.assertEqual(self.selected()[1],expected)
        p=three_part_profile(expected,2.5);p['selection']['method']='Changed'
        self.assertEqual(three_part_profile(expected,2.5)['selection']['method'],'Single')

    def test_exact_native_iterator_and_enum_source_proofs(self):
        root=Path(__file__).resolve().parents[1]/'research/p2-three-part-static-current'
        native=json.loads((root/'native-proof.json').read_text(encoding='utf-8'))
        iterator=next(m for m in native['method_records'] if m['method'].get('metadata_method_index')==94090)
        self.assertEqual(iterator['method']['Address'],0x180f824e0)
        self.assertEqual(iterator['method']['declaring_type'],'Torappu.Battle.Abilities.ThreePartOneshotAnimation+<DoPlayAnimation>d__21')
        self.assertEqual(iterator['instruction_count'],122)
        self.assertTrue(all(not m['limits'] and m['cfg_bounded_traversal_finished'] for m in native['method_records']))
        metadata=json.loads((root/'selected-metadata.json').read_text(encoding='utf-8'))
        enum=next(t for t in metadata['selected'] if t['name'].endswith('AbilityRandomGroup+SelectMethod'))
        self.assertEqual({f['name']:f['default']['value'] for f in enum['fields'] if f['default']},{'Random':0,'Loop':1})
        generic=json.loads((root/'behaviour-generic-binding.json').read_text(encoding='utf-8'))
        self.assertEqual(generic['method'],'UnityEngine.Component$$GetComponents')
        self.assertEqual(generic['generic_argument'],'Torappu.Battle.AbilityStandard+Behaviour')
        self.assertEqual(generic['method_spec_bytes'],'63500400ffffffffb92d0000')
        receipt=json.loads((root/'receipt.json').read_text(encoding='utf-8'))
        self.assertFalse(receipt['first_misaddress_extract_preserved']['used_for_proof'])
        self.assertFalse(native['hotfix_equivalence_proven'])


if __name__=='__main__':unittest.main()
