"""Mei MAR-X source parameters stay distinct from unverified combat behavior."""
import copy
import json
import re
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.mei_module_reference import reference
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report


def scenario(**extra):
    return {'operator': 'char_133_mm', 'skill': 1, 'skill_rank': 10,
            'elite': 2, 'level': 40, 'base_attack': 1000,
            'module_id': 'uniequip_002_mm', 'module_level': 1, **extra}


class MeiAirborneModuleReferenceTests(unittest.TestCase):
    def test_all_three_levels_expose_exact_trait_source_and_unknown_actual_condition(self):
        for stage in (1, 2, 3):
            for skill in (1, 2):
                for mode in ('frames', 'continuous'):
                    with self.subTest(stage=stage, skill=skill, mode=mode):
                        result = calculate_damage(scenario(module_level=stage, skill=skill,
                                                           timing_mode=mode))
                        ref = result['mei_airborne_module_reference']
                        self.assertEqual(ref['attack_scale_parameter'], 1.1)
                        self.assertEqual((ref['unlock_elite'], ref['unlock_level']), (2, 40))
                        self.assertEqual(ref['candidate_unlock_condition'], {'phase': 'PHASE_2', 'level': 40})
                        self.assertEqual(ref['required_potential_rank'], 0)
                        self.assertIn('phases[' + str(stage - 1) + '].parts[0]', ref['source_selectors'][-1])
                        self.assertIsNone(ref['actual_target_is_airborne'])
                        self.assertIsNone(ref['actual_conditional_damage'])
                        self.assertFalse(ref['applied_to_numeric_estimate'])
                        self.assertFalse(ref['native_attachment_verified'])
                        self.assertFalse(ref['damage_composition_verified'])
                        self.assertFalse(ref['live_state_verified'])

    def test_real_module_unlock_and_skill_rank_qualification_stay_separate(self):
        for elite, level in ((1, 60), (2, 39)):
            for stage in (1, 2, 3):
                result = calculate_damage(scenario(elite=elite, level=level,
                                                  skill_rank=7, module_level=stage))
                self.assertNotIn('mei_airborne_module_reference', result)
                self.assertNotIn('mei_airborne_module', [s['id'] for s in result['report']['sections']])
        for rank in (1, 7, 10):
            result = calculate_damage(scenario(skill_rank=rank))
            self.assertIn('mei_airborne_module_reference', result)

    def test_trait_parameter_does_not_multiply_existing_skill_damage_or_attack(self):
        # Current module talent overrides are already modeled. Their old S1
        # raw values are 2140/2200/2240 for the explicit base=1000, potential1.
        for stage, raw in ((1, 2140), (2, 2200), (3, 2240)):
            for mode in ('frames', 'continuous'):
                result = calculate_damage(scenario(module_level=stage, enemy_defense=200,
                                                   timing_mode=mode))
                self.assertAlmostEqual(result['components'][0]['per_hit'], raw - 200)
                self.assertAlmostEqual(result['attack'], raw / 2)
                self.assertIsNone(result['total_damage'])
                self.assertIsNone(result['components'][0]['actual_total'])
                self.assertFalse(result['estimate']['complete'])
                self.assertEqual(result['complete_definition'],
                                 'complete 仅指当前局外计算范围内的已支持部分；资料栏的战斗触发效果未计入，也不表示完整实战模拟。')

    def test_report_discloses_unused_parameter_and_unknown_composition(self):
        result = calculate_damage(scenario(skill=2, module_level=3))
        section = next(s for s in result['report']['sections'] if s['id'] == 'mei_airborne_module')
        metrics = {m['key']: m['value'] for m in section['metrics']}
        self.assertAlmostEqual(metrics['attack_scale'], 110)
        self.assertIsNone(metrics['target_airborne'])
        self.assertIsNone(metrics['conditional_damage'])
        text = format_report(result)
        self.assertIn('本次未确认目标是否为空中单位', text)
        self.assertIn('110%参数未计入当前伤害数值', text)
        self.assertIn('组合层尚未核验', text)
        self.assertIn(result['complete_definition'], text)
        self.assertFalse(result['timing']['complete'])

    def test_no_target_motion_inference_from_weight_name_or_unrecognized_condition(self):
        plain = calculate_damage(scenario())
        for fields in ({'enemy_weight': 0}, {'enemy_name': '飞行目标'},
                       {'enemy_is_airborne': True}, {'enemy_is_airborne': 'false'}):
            with self.subTest(fields=fields):
                self.assertEqual(calculate_damage(scenario(**fields)), plain)

    def test_no_module_other_owner_and_foreign_parts_cannot_gain_this_reference(self):
        plain = calculate_damage(scenario(module_id=None, module_level=0))
        self.assertNotIn('mei_airborne_module_reference', plain)
        other = calculate_damage({'operator': 'char_328_cammou', 'skill': 1,
                                  'module_id': 'uniequip_002_cammou', 'module_level': 1})
        self.assertNotIn('mei_airborne_module_reference', other)
        profile = catalog()['operators']['char_133_mm']
        args = scenario()
        foreign = catalog()['operators']['char_328_cammou']['modules'][0]['levels'][0]['parts']
        self.assertIsNone(reference(profile, args, foreign))
        self.assertIsNone(reference(profile, args, []))

    def test_empty_window_and_known_empty_enemy_scope_do_not_become_airborne_claims(self):
        for skill in (1, 2):
            for mode in ('frames', 'continuous'):
                for extra in ({'window_seconds': 0},
                              {'timing': {'target_disappears_seconds': 0}},
                              {'timing': {'target_windows': []}}):
                    with self.subTest(skill=skill, mode=mode, extra=extra):
                        result = calculate_damage(scenario(skill=skill, timing_mode=mode, **extra))
                        ref = result['mei_airborne_module_reference']
                        self.assertIsNone(ref['actual_target_is_airborne'])
                        self.assertIsNone(ref['actual_conditional_damage'])
                        self.assertFalse(ref['applied_to_numeric_estimate'])
                        self.assertFalse(ref['native_attachment_verified'])

    def test_public_training_errors_and_input_catalog_immutability_are_preserved(self):
        for fields, message in (({'elite': 1, 'level': 60}, '当前精英阶段尚未开放所选技能或专精。'),
                                ({'module_level': True}, '模组身份或等级尚无可用规则。'),
                                ({'potential': True}, '潜能需要为 1–6。')):
            with self.assertRaisesRegex(ValueError, '^' + re.escape(message) + '$'):
                calculate_damage(scenario(**fields))
        args = scenario(module_level=3, potential=6, skill=2, window_seconds=10)
        original = copy.deepcopy(args)
        snapshot = json.dumps(catalog(), sort_keys=True, ensure_ascii=False)
        first = calculate_damage(args)
        second = calculate_damage(args)
        self.assertEqual(first, second)
        self.assertEqual(args, original)
        self.assertEqual(json.dumps(catalog(), sort_keys=True, ensure_ascii=False), snapshot)
        profile = catalog()['operators']['char_133_mm']
        _, parts = selected_talents(profile, args)
        ref = reference(profile, args, parts)
        ref['candidate_unlock_condition']['level'] = 999
        self.assertEqual(reference(profile, args, parts)['candidate_unlock_condition']['level'], 40)


if __name__ == '__main__':
    unittest.main()
