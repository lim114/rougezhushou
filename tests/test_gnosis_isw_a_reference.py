"""ISW-A preserves distinct source identities and unknown actual DOT clocks."""
from copy import deepcopy
import unittest

from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.gnosis_module_reference import DOT_NAME
from rouge.operator_engine import Combat, selected_talents


OPERATOR = 'char_206_gnosis'
MODULE = 'uniequip_004_gnosis'


def scenario(skill=2, **extra):
    return {'operator': OPERATOR, 'skill': skill, 'base_attack': 1000,
            'elite': 2, 'level': 60, 'potential': 1, 'skill_rank': 10,
            'module_id': MODULE, 'module_level': 2, **extra}


def evaluate(skill=2, **extra):
    return calculate_damage(scenario(skill, **extra))


class GnosisIswAReferenceTests(unittest.TestCase):
    def test_original_ice_parameters_and_description_survive_all_module_stages(self):
        for stage in (1, 2, 3):
            for potential, cold, frozen in ((1, 1.25, 1.5), (5, 1.27, 1.54)):
                with self.subTest(stage=stage, potential=potential):
                    talents, _ = selected_talents(catalog()['operators'][OPERATOR],
                                                 scenario(module_level=stage, potential=potential))
                    ice = next(t for t in talents if t['name'] == '坚冰')
                    self.assertEqual(ice['values'], {'cold': 1, 'damage_scale_cold': cold,
                                                    'damage_scale_freeze': frozen})
                    self.assertIn('攻击造成1秒', ice['description'])
                    self.assertIn('范围内', ice['description'])
                    self.assertTrue(ice['reference_only'])
                    self.assertEqual(ice['reference_identity'], {'talent_index': 0, 'prefab_key': '1'})

    def test_same_talent_index_has_separate_prefab_records_and_raw_metadata(self):
        for stage in (2, 3):
            for potential in (1, 5):
                with self.subTest(stage=stage, potential=potential):
                    ref = evaluate(module_level=stage, potential=potential)['gnosis_isw_a_reference']
                    records = {r['prefab_key']: r for r in ref['module_records'] if r['kind'] == 'talent'}
                    self.assertEqual(set(records), {'#', '1', '10_root', '11_root'})
                    self.assertEqual(records['10_root']['blackboard'], {'cold': stage + 1, 'delay': .8})
                    self.assertEqual(records['11_root']['blackboard'], {'cold': 1})
                    self.assertEqual(records['10_root']['raw_candidate']['prefabKey'], '10_root')
                    self.assertEqual(records['11_root']['raw_candidate']['requiredPotentialRank'],
                                     4 if potential == 5 else 0)
                    self.assertTrue(records['10_root']['hidden'])
                    self.assertTrue(records['11_root']['hidden'])
                    self.assertNotIn('delay', ref['original_talent']['blackboard'])
                    self.assertNotIn('multi', ref['original_talent']['blackboard'])
                    self.assertFalse(ref['native_ability_attachment_verified'])
                    self.assertFalse(ref['original_talent']['module_coexistence_verified'])

    def test_stage_three_growth_fields_remain_source_parameters(self):
        ref = evaluate(module_level=3)['gnosis_isw_a_reference']
        first = next(r for r in ref['module_records'] if r['prefab_key'] == '1')
        self.assertEqual(first['blackboard'], {'damage_scale_cold': 1.3, 'multi': 2, 'add': .05, 'max': 1.8})
        self.assertEqual(ref['original_talent']['blackboard']['damage_scale_cold'], 1.25)
        self.assertFalse(ref['stack_phase_reset_interaction_verified'])

    def test_positive_observation_masks_all_qualified_skill_stage_state_modes(self):
        for skill in (1, 2, 3):
            for stage in (1, 2, 3):
                for status in (0, 1, 2):
                    for mode in ('frames', 'continuous'):
                        with self.subTest(skill=skill, stage=stage, status=status, mode=mode):
                            r = evaluate(skill, module_level=stage, cold_state=status,
                                         timing_mode=mode, window_seconds=3)
                            self.assertIsNone(r['total_damage'])
                            self.assertIsNone(r['estimate']['skill']['total_damage'])
                            self.assertIsNone(r['estimate']['skill']['window_damage'])
                            self.assertIsNone(r['estimate']['skill']['cycle_damage'])
                            self.assertTrue(r['timing']['phase_clock_unbound'])
                            self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
                            self.assertFalse(r['complete'])

    def test_per_tick_reference_has_parameters_without_tick_schedule_or_lifecycle(self):
        for skill in (1, 2, 3):
            r = evaluate(skill, cold_state=1, window_seconds=3)
            dot = next(c for c in r['components'] if c['name'] == DOT_NAME)
            self.assertEqual(dot['per_hit'], 625)
            self.assertEqual(dot['attack_scale_parameter'], .5)
            self.assertEqual(dot['tick_interval_parameter_seconds'], .5)
            self.assertEqual(dot['hits'], 0)
            self.assertIsNone(dot['actual_total'])
            self.assertNotIn('times_seconds', dot)
            ref = r['gnosis_isw_a_reference']
            self.assertIsNone(ref['actual_tick_count'])
            self.assertIsNone(ref['actual_tick_times_seconds'])
            self.assertIsNone(ref['actual_dot_damage'])
            self.assertFalse(ref['post_skill_dot_lifecycle_verified'])
            self.assertFalse(ref['attack_snapshot_binding_verified'])

    def test_initial_no_cold_does_not_prove_no_future_dot(self):
        r = evaluate(3, cold_state=0, window_seconds=.1, frozen_at_skill_end=False)
        self.assertIsNone(r['total_damage'])
        self.assertTrue(r['gnosis_isw_a_reference']['source_possible']['window'])
        self.assertEqual(r['gnosis_isw_a_reference']['per_tick_damage_reference'], 500)

    def test_no_owner_target_or_full_interrupt_does_not_exclude_existing_cold_dot(self):
        for timing in ({'target_windows': []}, {'interrupt_windows': [[0, 3600]]}):
            with self.subTest(timing=timing):
                r = evaluate(3, window_seconds=3, timing=timing)
                self.assertTrue(r['gnosis_isw_a_reference']['source_possible']['window'])
                self.assertIsNone(r['total_damage'])

    def test_zero_window_has_zero_observed_damage_without_actual_tick_claim(self):
        for skill in (1, 2, 3):
            for stage in (1, 2, 3):
                r = evaluate(skill, module_level=stage, window_seconds=0)
                self.assertEqual(r['total_damage'], 0)
                self.assertFalse(r['gnosis_isw_a_reference']['source_possible']['window'])
                self.assertFalse(any(c['hits'] or 'actual_total' in c for c in r['components']))
                self.assertIsNone(r['gnosis_isw_a_reference']['actual_tick_count'])

    def test_current_enemy_zero_lifetime_excludes_actual_damage_in_every_phase(self):
        for skill in (1, 2, 3):
            r = evaluate(skill, window_seconds=3, timing={'target_disappears_seconds': 0})
            self.assertEqual(r['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['total_damage'], 0)
            self.assertFalse(r['gnosis_isw_a_reference']['source_possible']['cast'])
            self.assertFalse(r['gnosis_isw_a_reference']['source_possible']['window'])

    def test_existing_sp_and_s1_end_guards_are_preserved(self):
        result = evaluate(1)
        self.assertTrue(result['timing']['phase_clock_unbound'])
        self.assertFalse(result['timing']['resource_and_damage_shared_clock'])
        s1 = result['estimate']['skill']
        for key in ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds'):
            self.assertIsNone(s1[key], key)
        s2 = evaluate(2)['estimate']['skill']
        self.assertEqual((s2['initial_seconds'], s2['recharge_seconds']), (6, 6))
        s3 = evaluate(3)['estimate']['skill']
        self.assertEqual((s3['initial_seconds'], s3['duration_seconds'], s3['recharge_seconds']), (15, 13, 40))
        for skill in (2, 3):
            result = evaluate(skill)
            self.assertTrue(result['timing']['phase_clock_unbound'])
            self.assertFalse(result['timing']['resource_and_damage_shared_clock'])

    def test_normal_attack_parameter_reference_and_dot_remain_separate(self):
        args = scenario(cold_state=2)
        attrs = operator_attributes(OPERATOR, elite=2, level=60, module_id=MODULE, module_level=2)
        normal = Combat(args, attrs).plan(normal=True, window=10)
        attack = next(c for c in normal['components'] if c['name'] == '普通攻击')
        dot = next(c for c in normal['components'] if c['name'] == DOT_NAME)
        self.assertEqual(attack['per_hit'], 1500)
        self.assertEqual(dot['per_hit'], 750)
        self.assertIsNone(attack['actual_total'])
        self.assertIsNone(dot['actual_total'])
        self.assertNotIn('times_seconds', dot)

    def test_locked_module_and_other_modules_keep_their_old_boundary(self):
        for extra in ({'module_id': None, 'module_level': 0},
                      {'module_id': 'uniequip_002_gnosis'},
                      {'module_id': 'uniequip_003_gnosis'}, {'level': 59},
                      {'elite': 1, 'level': 80, 'skill_rank': 7}):
            with self.subTest(extra=extra):
                r = evaluate(2, cold_state=1, **extra)
                self.assertNotIn('gnosis_isw_a_reference', r)
                self.assertIsNotNone(r['total_damage'])
                self.assertFalse(any(c['name'] == DOT_NAME for c in r['components']))

    def test_unrefereed_prefab_is_not_claimed_as_reviewed_identity(self):
        profile = deepcopy(catalog()['operators'][OPERATOR])
        module = next(m for m in profile['modules'] if m['id'] == MODULE)
        module['levels'][1]['parts'][4]['addOrOverrideTalentDataBundle']['candidates'][0]['prefabKey'] = 'unreviewed'
        talents, _ = selected_talents(profile, scenario())
        self.assertNotIn('gnosis_isw_a_reference', talents[0])

    def test_report_exposes_original_description_and_unknown_actual_dot(self):
        text = format_estimate(evaluate(2, cold_state=1, window_seconds=3))
        self.assertIn('攻击造成1秒寒冷', text)
        self.assertIn('灵知ISW-A · 天赋与持续法术待核验', text)
        self.assertIn('每跳法术伤害条件参考：625', text)
        self.assertIn('实际持续法术跳数：未知', text)
        self.assertIn('单次技能总伤：未知', text)

    def test_selection_and_calculation_preserve_input_and_catalog(self):
        profile = catalog()['operators'][OPERATOR]
        before = deepcopy(profile)
        args = scenario()
        original = deepcopy(args)
        selected_talents(profile, args)
        calculate_damage(args)
        self.assertEqual(args, original)
        self.assertEqual(profile, before)


if __name__ == '__main__':
    unittest.main()
