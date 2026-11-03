"""Opt-in Chen motion inspection must not create native combat clocks."""
import copy
import unittest
from rouge.animation_reference import choices, descriptor, references
from rouge.chen_motion_reference import chen_motion_reference
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

OP = 'char_1050_chen3'


def scenario(skill, **extra):
    return {'operator': OP, 'skill': skill, 'base_attack': 1000, **extra}


def without_motion_blocks(result):
    result = copy.deepcopy(result)
    result['report']['sections'] = [s for s in result['report']['sections']
                                   if not s['id'].startswith('chen_motion_')]
    return result


class ChenMotionReferenceTests(unittest.TestCase):
    def assert_numeric_unchanged(self, skill, face, **extra):
        original = calculate_damage(scenario(skill, **extra))
        inspected = calculate_damage(scenario(skill, chen_motion_orientation=face, **extra))
        self.assertEqual(without_motion_blocks(inspected), original)
        return inspected

    def test_default_off_and_none_preserve_the_complete_public_result(self):
        for skill in (1, 2, 3):
            original = calculate_damage(scenario(skill))
            self.assertEqual(calculate_damage(scenario(skill, chen_motion_orientation=None)), original)
            self.assertIsNone(chen_motion_reference(scenario(skill)))
            self.assertFalse(any(s['id'].startswith('chen_motion_') for s in original['report']['sections']))

    def test_frames_inspection_changes_only_motion_report_blocks(self):
        for skill in (1, 2, 3):
            for face in ('Front', 'Back', 'both'):
                with self.subTest(skill=skill, face=face):
                    self.assert_numeric_unchanged(skill, face, timing_mode='frames', window_seconds=2,
                                                  timing={'projectile_travel_seconds': .5})

    def test_continuous_inspection_does_not_schedule_animation_events(self):
        for skill in (1, 2, 3):
            self.assert_numeric_unchanged(skill, 'both', timing_mode='continuous', window_seconds=.1)

    def test_empty_observation_retains_resource_events_without_new_damage(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for empty in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}):
                    with self.subTest(skill=skill, mode=mode, empty=empty):
                        self.assert_numeric_unchanged(skill, 'Front', timing_mode=mode, **empty)
                        ref = chen_motion_reference(scenario(skill, chen_motion_orientation='Front'))
                        self.assertTrue(any(r['events'] for r in ref['motions']))

    def test_selected_orientation_never_fills_from_the_other_side(self):
        for skill in (1, 2, 3):
            for face in ('Front', 'Back'):
                ref = chen_motion_reference(scenario(skill, chen_motion_orientation=face))
                self.assertEqual(len(ref['motions']), 3)
                self.assertEqual({r['orientation'] for r in ref['motions']}, {face})
                self.assertTrue(all('/' + face + '/' in r['source']['url'] for r in ref['motions']))
                result = calculate_damage(scenario(skill, chen_motion_orientation=face))
                self.assertEqual([s['id'] for s in result['report']['sections']
                                  if s['id'].startswith('chen_motion_')], ['chen_motion_' + face.lower()])

    def test_both_faces_and_all_source_fields_are_preserved_without_aliases(self):
        before = copy.deepcopy(references())
        ref = chen_motion_reference(scenario(3, chen_motion_orientation='both'))
        self.assertEqual([r['orientation'] for r in ref['motions']], ['Front'] * 3 + ['Back'] * 3)
        for motion in ref['motions']:
            source = next(r for r in before['operators'][OP]['records'] if r['id'] == motion['id'])
            self.assertEqual({k: v for k, v in motion.items() if k != 'label'}, source)
        ref['motions'][1]['events'][0]['seconds'] = -1
        ref['motions'][0]['source']['sha256'] = 'changed'
        self.assertEqual(references(), before)
        self.assertGreater(chen_motion_reference(scenario(3, chen_motion_orientation='both'))
                           ['motions'][1]['events'][0]['seconds'], 0)

    def test_s1_multi_events_preserve_representation_error_and_order(self):
        for face in ('Front', 'Back'):
            ref = chen_motion_reference(scenario(1, chen_motion_orientation=face))
            loop = next(r for r in ref['motions'] if r['animation'] == 'Skill_1_Loop')
            self.assertEqual([e['name'] for e in loop['events']], ['OnAttack', 'OnAttack'])
            self.assertEqual([e['ceil_frames_30hz'] for e in loop['events']], [13, 20])
            self.assertEqual([e['strict_ceil_frames_30hz'] for e in loop['events']], [14, 21])
            self.assertEqual(loop['duration']['strict_ceil_frames_30hz'], 38)
            self.assertEqual([r['duration']['ceil_frames_30hz'] for r in ref['motions']], [6, 37, 6])

    def test_s2_resource_entries_do_not_invent_slash_or_phase_clocks(self):
        ref = chen_motion_reference(scenario(2, chen_motion_orientation='Front'))
        self.assertEqual([r['animation'] for r in ref['motions']],
                         ['Skill_2_Begin', 'Skill_2_Disappear', 'Attack'])
        self.assertEqual([r['duration']['ceil_frames_30hz'] for r in ref['motions']], [17, 5, 37])
        self.assertEqual([len(r['events']) for r in ref['motions']], [0, 0, 1])
        result = calculate_damage(scenario(2, chen_motion_orientation='Front'))
        phase = result['chen_phase_reference']
        self.assertEqual(phase['strengthening_duration_parameter_seconds'], 6)
        for key in ('actual_slash_end_seconds', 'actual_strengthening_start_seconds', 'actual_skill_end_seconds'):
            self.assertIsNone(phase[key])
        self.assertEqual(result['timing']['streams'], [])
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])

    def test_s3_three_events_leave_wave_collision_and_body_subtotals_unchanged(self):
        ref = chen_motion_reference(scenario(3, chen_motion_orientation='Back'))
        loop = next(r for r in ref['motions'] if r['animation'] == 'Skill_3_Loop')
        self.assertEqual([e['ceil_frames_30hz'] for e in loop['events']], [16, 18, 20])
        self.assertEqual([e['strict_ceil_frames_30hz'] for e in loop['events']], [17, 19, 21])
        self.assertEqual([r['duration']['ceil_frames_30hz'] for r in ref['motions']], [13, 37, 8])
        result = calculate_damage(scenario(3, chen_motion_orientation='Back'))
        self.assertIsNone(result['chen_phase_reference']['actual_collision_times_seconds'])
        self.assertFalse(result['chen_phase_reference']['collision_clock_verified'])
        self.assertIsNone(result['total_damage'])
        self.assertEqual(result['known_damage_subtotals']['total_damage'], 128142)

    def test_inspection_never_opens_forbidden_numeric_selectors(self):
        for skill in (1, 2, 3):
            before = choices(OP, skill)
            chen_motion_reference(scenario(skill, chen_motion_orientation='both'))
            self.assertEqual(choices(OP, skill), before)
            self.assertEqual({r['animation'] for r in before}, {'Attack'})
        for skill in (1, 3):
            for face in ('Front', 'Back'):
                with self.assertRaises(ValueError):
                    descriptor(OP, skill, {'animation_reference': f'{OP}:{face}:Skill_{skill}_Loop'})

    def test_unknown_actual_clocks_and_prohibited_duration_sum_are_explicit(self):
        for skill in (1, 2, 3):
            ref = chen_motion_reference(scenario(skill, chen_motion_orientation='both'))
            for key in ('numeric_schedule_changed', 'runtime_motion_selection_verified',
                        'damage_event_binding_verified', 'phase_duration_sum_permitted'):
                self.assertFalse(ref[key])
            for key in ('actual_damage_times_seconds', 'actual_skill_end_seconds',
                        'actual_slash_end_seconds', 'actual_wave_collision_seconds'):
                self.assertIsNone(ref[key])

    def test_all_formatters_show_reference_and_preserve_caller_and_result(self):
        for skill in (1, 2, 3):
            caller = scenario(skill, chen_motion_orientation='both',
                              timing={'target_windows': [[5, 10]]}, window_seconds=10)
            before = copy.deepcopy(caller)
            result = calculate_damage(caller)
            original = copy.deepcopy(result)
            texts = [format_estimate(result), format_report(result), format_report(result, technical=True)]
            for text in texts:
                for value in ('陈 · 原版阶段资料 · 正面', '陈 · 原版阶段资料 · 背面', '原始浮点帧',
                              '归一化参考帧', '实际技能结束时刻：未知', '不排程多事件伤害'):
                    self.assertIn(value, text)
            self.assertIn('https://raw.githubusercontent.com/fexli/ArknightsResource/', texts[-1])
            self.assertEqual(result, original)
            self.assertEqual(caller, before)

    def test_rank_and_attack_speed_do_not_rewrite_resource_offsets_or_numeric_result(self):
        for skill in (1, 2, 3):
            base = chen_motion_reference(scenario(skill, chen_motion_orientation='Front'))
            altered = chen_motion_reference(scenario(skill, chen_motion_orientation='Front', skill_rank=7,
                                                       effects=[{'kind': 'attack_speed', 'value': 500}]))
            self.assertEqual(altered, base)
            self.assert_numeric_unchanged(skill, 'Front', skill_rank=7, window_seconds=1,
                                          effects=[{'kind': 'attack_speed', 'value': 500}])

    def test_invalid_orientation_is_rejected_without_coercion(self):
        for value in ('front', '', 'left', True, 1, [], {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'Front、Back或both'):
                    chen_motion_reference(scenario(2, chen_motion_orientation=value))
                with self.assertRaisesRegex(ValueError, 'Front、Back或both'):
                    calculate_damage(scenario(2, chen_motion_orientation=value))

    def test_reference_is_scoped_to_chen_and_its_three_skills(self):
        self.assertIsNone(chen_motion_reference({'operator': 'char_002_amiya', 'skill': 1,
                                               'chen_motion_orientation': 'not-consumed'}))
        for value in (0, 4, True, '1'):
            with self.assertRaisesRegex(ValueError, '一、二、三技能'):
                chen_motion_reference(scenario(value, chen_motion_orientation='Front'))


if __name__ == '__main__':
    unittest.main()
