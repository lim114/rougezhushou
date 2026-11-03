"""AMB-Y retains original talent references without claiming attachment or healing."""
from copy import deepcopy
import unittest

from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.operator_engine import Combat, selected_talents


OPERATOR = 'char_437_mizuki'
MODULE = 'uniequip_003_mizuki'
PARAMETER = 'attack@mizuki_t_1.atk_scale'


def scenario(skill=2, **extra):
    return {'operator': OPERATOR, 'skill': skill, 'base_attack': 1000,
            'elite': 2, 'level': 60, 'potential': 1, 'skill_rank': 10,
            'module_id': MODULE, 'module_level': 2, **extra}


def evaluate(skill=2, **extra):
    return calculate_damage(scenario(skill, **extra))


class MizukiAmbYReferenceTests(unittest.TestCase):
    def test_public_eighteen_case_boundary_preserves_skill_reference(self):
        for skill, expected in ((1, 1500), (2, 650), (3, 1250)):
            for stage in (1, 2, 3):
                for level in (59, 60):
                    with self.subTest(skill=skill, stage=stage, level=level):
                        result = evaluate(skill, module_level=stage, level=level)
                        arts = next(c for c in result['components']
                                    if c['name'] == ('唤醒额外法术' if skill == 1 else '创伤性癔症'))
                        self.assertEqual(arts['per_hit'], expected)
                        affected = level == 60 and stage in (2, 3)
                        self.assertEqual('mizuki_amb_y_reference' in result, affected)
                        if affected or skill == 1:
                            self.assertIsNone(result['total_damage'])
                        else:
                            self.assertIsNotNone(result['total_damage'])

    def test_hidden_fields_are_separate_from_visible_original_identity(self):
        for stage, ratio in ((2, .05), (3, .1)):
            with self.subTest(stage=stage):
                talents, _ = selected_talents(catalog()['operators'][OPERATOR], scenario(module_level=stage))
                first = talents[0]
                self.assertEqual(first['name'], '创伤性癔症')
                self.assertEqual(first['values'][PARAMETER], .5)
                self.assertNotIn('hp_ratio', first['values'])
                self.assertTrue(first['reference_only'])
                result = evaluate(module_level=stage)
                ref = result['mizuki_amb_y_reference']
                self.assertEqual(ref['original_first_talent']['prefab_key'], '1')
                self.assertEqual(ref['hidden_module_ability']['prefab_key'], '10')
                self.assertEqual(ref['hidden_module_ability']['blackboard'], {'hp_ratio': ratio})
                self.assertFalse(ref['hidden_module_ability']['attachment_verified'])
                self.assertFalse(ref['original_first_talent']['attachment_verified'])

    def test_s2_s3_mask_arts_across_cast_window_and_cycle(self):
        for skill in (2, 3):
            with self.subTest(skill=skill):
                result = evaluate(skill)
                arts = next(c for c in result['components'] if c['name'] == '创伤性癔症')
                physical = next(c for c in result['components'] if c['damage_type'] == 'physical')
                self.assertIsNone(arts['actual_total'])
                self.assertNotIn('times_seconds', arts)
                self.assertIsNone(result['total_damage'])
                estimate = result['estimate']['skill']
                for key in ('total_damage', 'phase_damage', 'window_damage', 'window_dps',
                            'cycle_damage', 'cycle_dps'):
                    self.assertIsNone(estimate[key], key)
                self.assertIsNone(estimate['hit_counts']['创伤性癔症'])
                self.assertEqual(result['known_damage_subtotals']['window_damage'], physical['total'])
                self.assertGreater(result['known_damage_subtotals']['cycle_damage'], physical['total'])
                self.assertFalse(result['complete'])

    def test_normal_recharge_keeps_five_hundred_conditional_reference(self):
        for skill in (2, 3):
            with self.subTest(skill=skill):
                args = scenario(skill)
                attrs = operator_attributes(OPERATOR, elite=2, level=60,
                                            module_id=MODULE, module_level=2)
                normal = Combat(args, attrs).plan(normal=True, window=10)
                arts = next(c for c in normal['components'] if c['name'] == '创伤性癔症')
                self.assertEqual(arts['per_hit'], 500)
                self.assertIsNone(arts['actual_total'])
                self.assertNotIn('times_seconds', arts)

    def test_visible_second_talent_upgrade_and_potential_gates_remain_applied(self):
        for stage, low, high in ((2, .15, .17), (3, .2, .22)):
            for potential, expected in ((1, low), (5, high)):
                with self.subTest(stage=stage, potential=potential):
                    args = scenario(module_level=stage, potential=potential, enemy_below_half=True)
                    talents, _ = selected_talents(catalog()['operators'][OPERATOR], args)
                    second = next(t for t in talents if t['name'] == '反移情')
                    self.assertEqual(second['values']['atk'], expected)
                    result = calculate_damage(args)
                    self.assertAlmostEqual(result['attack'], 1000 * (1.3 + expected))
                    arts = next(c for c in result['components'] if c['name'] == '创伤性癔症')
                    self.assertAlmostEqual(arts['per_hit'], 500 * (1.3 + expected))

    def test_zero_observation_keeps_zero_damage_and_healing(self):
        for skill in (1, 2, 3):
            with self.subTest(skill=skill):
                result = evaluate(skill, window_seconds=0)
                self.assertEqual(result['total_damage'], 0)
                self.assertEqual(result['total_healing'], 0)
                self.assertEqual(result['estimate']['skill']['window_healing'], 0)
                self.assertFalse(result['mizuki_amb_y_reference']['recovery_source_possible']['window'])
                self.assertFalse(any(c['hits'] or 'actual_total' in c for c in result['components']))

    def test_current_target_exclusion_does_not_establish_no_module_recovery(self):
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0},
                       {'interrupt_windows': [[0, 3600]]}):
            with self.subTest(timing=timing):
                result = evaluate(window_seconds=10, timing=timing)
                self.assertEqual(result['total_damage'], 0)
                self.assertIsNone(result['total_healing'])
                self.assertIsNone(result['mizuki_amb_y_reference']['actual_extra_healing'])
                self.assertEqual(result['known_healing_subtotals']['window_healing'], 0)

    def test_recovery_has_no_scheduled_component_or_numerical_actual_total(self):
        for skill in (1, 2, 3):
            with self.subTest(skill=skill):
                result = evaluate(skill)
                self.assertIsNone(result['total_healing'])
                ref = result['mizuki_amb_y_reference']
                self.assertIsNone(ref['actual_extra_healing'])
                self.assertFalse(ref['kill_recovery_clock_verified'])
                self.assertEqual(result['known_healing_subtotals']['window_healing'], 0)
                self.assertFalse(any(c['damage_type'] in ('healing', 'regeneration')
                                     for c in result['components']))
                for key in ('total_healing', 'phase_healing', 'window_healing', 'window_hps'):
                    self.assertIsNone(result['estimate']['skill'][key], key)

    def test_s1_actual_end_and_cycle_guards_are_preserved(self):
        result = evaluate(1)
        self.assertEqual(result['mizuki_s1_reference']['arts_per_hit_reference'], 1500)
        self.assertFalse(result['mizuki_s1_reference']['skill_binding_verified'])
        for key in ('duration_seconds', 'initial_seconds', 'recharge_seconds',
                    'cycle_seconds', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(result['estimate']['skill'][key], key)

    def test_healing_relic_multipliers_preserve_unknown_and_observed_zero(self):
        for relic in ('rogue_6_relic_legacy_81', 'rogue_6_relic_legacy_82',
                      'rogue_6_relic_legacy_83'):
            for skill in (1, 2, 3):
                with self.subTest(relic=relic, skill=skill):
                    result = evaluate(skill, relic_ids=[relic])
                    self.assertIsNone(result['total_healing'])
                    self.assertIsNone(result['estimate']['skill']['window_healing'])
                    self.assertEqual(result['known_healing_subtotals']['window_healing'], 0)
                    zero = evaluate(skill, relic_ids=[relic], window_seconds=0)
                    self.assertEqual(zero['total_healing'], 0)
                    self.assertEqual(zero['estimate']['skill']['window_healing'], 0)

    def test_other_modules_and_below_elite_unlock_have_no_new_boundary(self):
        for module, stage, expected in ((None, 0, 1500), ('uniequip_002_mizuki', 2, 1650),
                                        ('uniequip_004_mizuki', 3, 1500)):
            with self.subTest(module=module):
                result = evaluate(1, module_id=module, module_level=stage)
                self.assertEqual(result['mizuki_s1_reference']['arts_per_hit_reference'], expected)
                self.assertNotIn('mizuki_amb_y_reference', result)
                self.assertEqual(result['total_healing'], 0)
        result = evaluate(1, elite=1, skill_rank=7)
        self.assertNotIn('mizuki_amb_y_reference', result)
        self.assertAlmostEqual(result['mizuki_s1_reference']['arts_per_hit_reference'], 690)

    def test_unreviewed_hidden_prefab_is_not_merged(self):
        profile = deepcopy(catalog()['operators'][OPERATOR])
        module = next(m for m in profile['modules'] if m['id'] == MODULE)
        part = next(p for p in module['levels'][1]['parts'] if p['target'] == 'TALENT')
        part['addOrOverrideTalentDataBundle']['candidates'][0]['prefabKey'] = 'unreviewed'
        talents, _ = selected_talents(profile, scenario())
        self.assertIsNone(talents[0]['name'])
        self.assertNotIn('reference_only', talents[0])

    def test_public_selection_and_calculation_do_not_mutate_input_or_catalog(self):
        profile = catalog()['operators'][OPERATOR]
        original_profile = deepcopy(profile)
        args = scenario()
        original_args = deepcopy(args)
        selected_talents(profile, args)
        calculate_damage(args)
        self.assertEqual(profile, original_profile)
        self.assertEqual(args, original_args)

    def test_report_names_the_reference_and_unknown_recovery(self):
        text = format_estimate(evaluate())
        self.assertIn('原版第一天赋单次法术条件参考：650', text)
        self.assertIn('模组实际额外回复：未知', text)
        self.assertIn('完整伤害未知', text)
        self.assertIn('单次技能总伤：未知', text)
        self.assertIn('观察窗口已计治疗小计：0', text)
        self.assertNotIn('河谷祭祈', text)


if __name__ == '__main__':
    unittest.main()
