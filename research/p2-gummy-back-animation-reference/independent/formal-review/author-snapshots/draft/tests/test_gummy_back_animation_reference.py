import unittest

from rouge.animation_reference import choices, descriptor, references
from rouge.damage import calculate_damage


OP = 'char_196_sunbr'
BACK = OP + ':Back:Attack'
FRONT = OP + ':Front:Attack'
BACK_SHA = '09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2'
REFERENCE_ERROR = '原版动画参考与当前干员/技能不符，或该动作不适合常规逐击参考。'


def evaluate(skill=2, **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 11, **extra})


class GummyBackAnimationReferenceTests(unittest.TestCase):
    def test_only_attack_is_exposed_without_inventing_a_skill_number(self):
        expected = [FRONT, BACK]
        for skill in (1, 2):
            self.assertEqual([r['id'] for r in choices(OP, skill)], expected)
            self.assertEqual([r['id'] for r in choices(OP, skill, normal=True)], expected)
            data = descriptor(OP, skill, {'animation_reference': BACK})
            self.assertEqual(data['original_orientation'], 'Back')
            self.assertEqual(data['source_sha256'], BACK_SHA)
            self.assertFalse(data['runtime_binding_verified'])
        self.assertTrue(next(r for r in references()['operators'][OP]['records']
                             if r['id'] == OP + ':Back:Skill')['selectable_as_conventional_reference'])
        with self.assertRaisesRegex(ValueError, REFERENCE_ERROR):
            descriptor(OP, 1, {'animation_reference': OP + ':Back:Skill'})

    def test_explicit_back_attack_retains_cooking_and_friendly_scope_unknowns(self):
        result = evaluate(timing={'animation_reference': BACK, 'target_windows': []})
        self.assertEqual(result['total_healing'], 1800)
        stream = result['timing']['streams'][0]
        self.assertEqual(stream['target_scope'], 'friendly')
        self.assertEqual(stream['start_frames'], [300])
        self.assertEqual(stream['release_frames'], [316])
        self.assertEqual(stream['original_animation_reference']['source_sha256'], BACK_SHA)
        self.assertTrue(stream['reference_binding'])
        self.assertFalse(stream['exact_binding'])
        self.assertFalse(result['timing']['complete'])

    def test_zero_window_and_zero_recipients_do_not_create_healing(self):
        for extra in ({'window_seconds': 0}, {'healing_targets': 0}):
            with self.subTest(extra=extra):
                result = evaluate(timing={'animation_reference': BACK}, **extra)
                self.assertEqual(result['total_healing'], 0)
                self.assertFalse(result['timing']['complete'])

    def test_s1_next_heal_clock_stays_unknown_with_both_explicit_references(self):
        result = evaluate(1, timing={'animation_reference': BACK, 'normal_animation_reference': BACK})
        self.assertIsNone(result['total_healing'])
        for key in ('recharge_seconds', 'cycle_seconds', 'cycle_healing', 'cycle_hps'):
            self.assertIsNone(result['estimate']['skill'][key])
        self.assertFalse(result['timing']['complete'])
        self.assertEqual(result['timing']['streams'], [])

    def test_manual_preview_and_subsequent_default_requests_stay_separate(self):
        result = evaluate(timing={'animation_reference': BACK, 'windup_frames': 6, 'recovery_frames': 9})
        stream = result['timing']['streams'][0]
        self.assertEqual(stream['release_frames'], [306])
        self.assertTrue(stream['original_animation_reference']['overridden_by_preview'])
        original = descriptor(OP, 2, {'animation_reference': BACK})
        self.assertEqual((original['windup_frames'], original['recovery_frames']), (16, 24))
        default = evaluate()
        self.assertEqual(default['timing']['streams'][0]['release_frames'], [316])
        self.assertNotIn('original_animation_reference', default['timing']['streams'][0])
        front = evaluate(timing={'animation_reference': FRONT})['timing']['streams'][0]
        self.assertEqual(front['original_animation_reference']['original_orientation'], 'Front')
        self.assertFalse(front['original_animation_reference']['runtime_binding_verified'])

    def test_generic_missing_and_cross_owner_ids_keep_the_public_error(self):
        cases = [
            {'operator': OP, 'skill': 2, 'timing': {'animation_reference': OP + ':Back:Skill'}},
            {'operator': OP, 'skill': 2, 'timing': {'animation_reference': OP + ':Back:Start'}},
            {'operator': OP, 'skill': 2, 'timing': {'animation_reference': OP + ':Back:Die'}},
            {'operator': 'kaltsit', 'skill': 3, 'timing': {'animation_reference': BACK}},
        ]
        for scenario in cases:
            with self.subTest(scenario=scenario):
                with self.assertRaisesRegex(ValueError, REFERENCE_ERROR):
                    calculate_damage(scenario)

    def test_float_representation_does_not_add_a_frame_or_fill_absent_motions(self):
        records = [r for r in references()['operators'][OP]['records'] if r['orientation'] == 'Back']
        attack = next(r for r in records if r['id'] == BACK)
        self.assertEqual(attack['duration']['strict_ceil_frames_30hz'], 41)
        self.assertEqual(attack['duration']['ceil_frames_30hz'], 40)
        self.assertEqual(attack['events'][0]['strict_ceil_frames_30hz'], 17)
        self.assertEqual(attack['events'][0]['ceil_frames_30hz'], 16)
        self.assertEqual(attack['preview'], {'windup_frames': 16, 'recovery_frames': 24, 'animation_frames': 40})
        self.assertEqual([r['animation'] for r in records], ['Attack', 'Default', 'Idle', 'Skill', 'Start'])
        for record in records:
            self.assertFalse(record['runtime_binding_verified'])


if __name__ == '__main__':
    unittest.main()
