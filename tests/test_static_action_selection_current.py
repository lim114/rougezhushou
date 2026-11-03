import copy
import unittest
from unittest.mock import patch
from rouge.animation_reference import choices, descriptor, references, static_bindings
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.timing import AttackTimeline


class StaticActionSelectionTests(unittest.TestCase):
    def test_mechanist_modes_filter_unselected_ordinary_variants(self):
        self.assertEqual([(r['animation'],r['orientation']) for r in choices('mechanist',normal=True)],
            [('Attack_A','Front'),('Attack_Down','Front'),('Attack_A','Back')])
        expected={1:['Skill_1','Skill_Down_1','Skill_1'],
                  2:['Skill_2_Loop','Skill_Down_2_Loop','Skill_2_Loop'],
                  3:['Skill_3_Loop','Skill_3_Loop']}
        for skill,names in expected.items():
            self.assertEqual([r['animation'] for r in choices('mechanist',skill)],names)
        self.assertFalse(any(r['animation']=='Attack_B' for r in choices('mechanist',normal=True)))

    def test_loop_name_does_not_override_native_nonloop_play_config(self):
        for skill in (2,3):
            for r in choices('mechanist',skill):
                self.assertIn('Loop',r['animation'])
                self.assertFalse(r['selectable_as_conventional_reference'])
                self.assertTrue(r['selectable_as_static_bound_segment_reference'])
                self.assertFalse(r['static_action_binding']['native_animation_loop'])
                self.assertIsNone(r['actual_callback_frames'])
                d=descriptor('mechanist',skill,{'animation_reference':r['id']})
                self.assertEqual(d['windup_frames'],13)
                self.assertTrue(d['frame_numbers_are_animation_segment_reference'])
                self.assertFalse(d['runtime_binding_verified'])
                self.assertIsNone(d['actual_activation_phase_seconds'])
                self.assertIsNone(d['actual_end_seconds'])

    def test_mode_hook_selects_silverash_combat_and_retains_other_events(self):
        selected=choices('silverash',3)
        self.assertEqual([(r['animation'],r['orientation']) for r in selected],
                         [('Skill_3_Combat','Front'),('Skill_3_Combat','Back')])
        for r in selected:
            b=r['static_action_binding']
            self.assertEqual(b['ability_sources'][0]['key_before_hook'],'Attack')
            self.assertEqual(b['ability_sources'][0]['key_after_hook'],'Skill_3_Combat')
            self.assertEqual(len([e for e in r['events'] if e['name']=='OnAttack']),1)
            self.assertTrue(any(e['name']=='OnActivateEffect' for e in r['events']))
            self.assertFalse(r['runtime_binding_verified'])

    def test_kaltsit_orientation_and_down_variants_use_their_own_skeletons(self):
        rows=choices('kaltsit',3)
        self.assertEqual({(r['animation'],r['orientation']):r['preview']['windup_frames'] for r in rows},
            {('Skill_3_Attack','Front'):12,('Skill_Down_3_Attack','Front'):13,('Skill_3_Attack','Back'):13})
        self.assertTrue(all(r['mode_indices']==[1] for r in rows))
        self.assertFalse(any(r['orientation']=='Back' and 'Down' in r['animation'] for r in rows))
        self.assertEqual(len(choices('kaltsit',2)),3)

    def test_source_float_and_normalized_reference_do_not_become_callback_frames(self):
        r=choices('mechanist',3)[0]
        event=next(e for e in r['events'] if e['name']=='OnAttack')
        self.assertGreater(event['raw_frames_30hz'],13)
        self.assertEqual(event['strict_ceil_frames_30hz'],14)
        self.assertEqual(r['preview']['windup_frames'],13)
        self.assertEqual(r['static_action_binding']['source_on_attack_seconds'],event['seconds'])
        self.assertIsNone(r['static_action_binding']['actual_callback_frames'])

    def test_default_without_explicit_choice_is_unchanged(self):
        # A source selection proof does not fill the missing controller clock.
        s={'operator':'kaltsit','skill':3}
        baseline=calculate_damage(s)
        empty=copy.deepcopy(static_bindings());empty['operators']={}
        with patch('rouge.animation_reference.static_bindings',return_value=empty):
            self.assertEqual(calculate_damage(s),baseline)
        self.assertFalse(baseline['timing']['streams'][0]['known_animation'])
        self.assertNotIn('original_animation_reference',baseline['timing']['streams'][0])

    def test_wrong_skill_and_unselected_normal_action_cannot_leak(self):
        normal=choices('mechanist',normal=True)[0]['id']
        for op,skill in [('mechanist',2),('mechanist',3),('kaltsit',2)]:
            with self.assertRaises(ValueError):descriptor(op,skill,{'animation_reference':normal})
        self.assertIsNotNone(descriptor('mechanist',2,{'normal_animation_reference':normal},normal=True))

    def test_three_part_static_proofs_do_not_fill_runtime_lifecycle_or_other_operator_scope(self):
        for op,skill,normal in [('kaltsit',1,False),('silverash',3,True)]:
            for r in choices(op,skill,normal=normal):
                self.assertTrue(r['static_action_binding']['static_selection_verified'])
                self.assertFalse(r['runtime_binding_verified'])
                self.assertIsNone(r['static_action_binding']['three_part_reference']['first_attack_gate_actual'])
        self.assertTrue(all('static_action_binding' not in r for r in choices('char_196_sunbr',3)))

    def test_modified_skeleton_hash_or_play_config_cannot_inherit_proof(self):
        r=choices('mechanist',3)[0]
        changed=copy.deepcopy(references())
        next(x for x in changed['operators']['mechanist']['records'] if x['id']==r['id'])['source']['sha256']='changed'
        with patch('rouge.animation_reference.references',return_value=changed):
            self.assertNotIn(r['id'],[x['id'] for x in choices('mechanist',3)])
            with self.assertRaises(ValueError):descriptor('mechanist',3,{'animation_reference':r['id']})
        changed=copy.deepcopy(references())
        record=next(x for x in changed['operators']['mechanist']['records'] if x['id']==r['id'])
        next(e for e in record['events'] if e['name']=='OnAttack')['seconds']=.5
        with patch('rouge.animation_reference.references',return_value=changed):
            self.assertNotIn(r['id'],[x['id'] for x in choices('mechanist',3)])
        changed=copy.deepcopy(static_bindings())
        changed['operators']['mechanist']['3']['records'][0]['native_animation_loop']=True
        with patch('rouge.animation_reference.static_bindings',return_value=changed):
            self.assertNotIn(r['id'],[x['id'] for x in choices('mechanist',3)])

    def test_repeated_calls_do_not_share_mutable_binding_or_original_event_rows(self):
        expected=choices('mechanist',2)
        altered=choices('mechanist',2)
        altered[0]['events'].clear()
        altered[0]['static_action_binding']['ability_sources'][0]['mode_index']=999
        self.assertEqual(choices('mechanist',2),expected)
        d=descriptor('mechanist',2,{'animation_reference':expected[0]['id']})
        d['static_action_binding']['ability_sources'].clear()
        self.assertTrue(descriptor('mechanist',2,{'animation_reference':expected[0]['id']})['static_action_binding']['ability_sources'])

    def test_explicit_preview_stream_and_report_separate_static_binding_from_actual(self):
        ref=choices('mechanist',3)[0]['id']
        r=calculate_damage({'operator':'mechanist','skill':3,'timing':{'animation_reference':ref}})
        stream=r['timing']['streams'][0];original=stream['original_animation_reference']
        self.assertTrue(original['static_selection_verified'])
        self.assertFalse(original['runtime_binding_verified'])
        self.assertFalse(stream['exact_binding'])
        for key in ('actual_callback_frames','actual_activation_phase_seconds','actual_end_seconds'):
            self.assertIsNone(original[key])
        text=format_estimate(r)
        self.assertIn('静态绑定动作参考',text)
        self.assertIn('帧数仅为动画内条件参考',text)
        self.assertIn('实际首击回调和结束相位未核验',text)

    def test_explicit_s2_body_reference_drives_only_manual_duration_ordinary_subtotal(self):
        ref=choices('mechanist',2)[0]['id']
        s={'operator':'mechanist','skill':2,'base_attack':1000,
           'skill_duration_seconds':20,'shield_break_count':2,
           'timing':{'animation_reference':ref,'windup_frames':6,'recovery_frames':9}}
        before=copy.deepcopy(s);r=calculate_damage(s)
        stream=r['timing']['streams'][0];original=stream['original_animation_reference']
        self.assertTrue(original['static_selection_verified'])
        self.assertTrue(original['overridden_by_preview'])
        self.assertEqual(stream['release_frames'][0],6)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['shield_break_reference']['actual_break_times_seconds'])
        self.assertIsNone(r['shield_break_reference']['actual_end_seconds'])
        self.assertGreater(r['known_damage_subtotals']['total_damage'],0)
        self.assertEqual(s,before)


if __name__=='__main__':unittest.main()
