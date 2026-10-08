"""Unavailable medical Amiya regeneration is not an unplaced active source."""
import copy
import json
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report

OP = 'char_1037_amiya3'
NAME = '诚挚期许本体生命回复'
MODULE = 'uniequip_002_amiya3'


def scenario(**extra):
    return {'operator': OP, 'skill': 1, 'skill_rank': 7, 'elite': 0,
            'level': 1, 'base_attack': 1000, 'window_seconds': 10, **extra}


def regeneration(result):
    return next(c for c in result['components'] if c['name'] == NAME)


class AmiyaRegenerationTalentQualificationTests(unittest.TestCase):
    def test_medical_profile_selected_talent_starts_at_e1(self):
        profile = catalog()['operators'][OP]
        self.assertEqual(profile['profession'], 'medic')
        self.assertEqual(profile['subprofession_id'], 'incantationmedic')
        for elite in (0, 1, 2):
            for potential in range(1, 7):
                chosen, _ = selected_talents(profile, scenario(elite=elite, potential=potential))
                self.assertEqual(any(t['name'] == '诚挚期许' for t in chosen), elite >= 1)

    def test_e0_s1_excludes_regeneration_without_changing_skill_duration_or_body(self):
        for mode in ('frames', 'continuous'):
            result = calculate_damage(scenario(timing_mode=mode))
            component = regeneration(result)
            self.assertEqual(component['hits'], 0.0)
            self.assertIs(type(component['hits']), float)
            self.assertEqual(component['total'], 0.0)
            self.assertIs(type(component['total']), float)
            self.assertNotIn('actual_total', component)
            self.assertEqual(result['estimate']['skill']['hit_counts'][NAME], 0.0)
            self.assertEqual(result['estimate']['skill']['duration_seconds'], 50.0)
            self.assertEqual((result['total_damage'], result['total_healing']), (10000.0, 7000.0))
            self.assertNotIn(NAME, result['timing'].get('unplaced_components', []))
            self.assertNotIn('尚未统一排入时间轴的输出分项：' + NAME, format_report(result))

    def test_zero_observation_still_excludes_full_skill_regeneration_reference(self):
        for mode in ('frames', 'continuous'):
            result = calculate_damage(scenario(window_seconds=0, timing_mode=mode))
            self.assertIs(type(regeneration(result)['hits']), float)
            self.assertEqual(regeneration(result)['hits'], 0.0)
            self.assertEqual(result['estimate']['skill']['hit_counts'][NAME], 0.0)
            self.assertEqual(result['estimate']['skill']['duration_seconds'], 50.0)
            self.assertEqual((result['total_damage'], result['total_healing']), (0.0, 0.0))

    def test_e1_e2_zero_attack_does_not_suppress_selected_regeneration(self):
        for elite in (1, 2):
            for mode in ('frames', 'continuous'):
                result = calculate_damage(scenario(elite=elite, base_attack=0, timing_mode=mode))
                component = regeneration(result)
                self.assertGreater(component['per_hit'], 0)
                self.assertEqual(component['hits'], 10.0)
                self.assertGreater(component['total'], 0)
                self.assertEqual(result['estimate']['skill']['hit_counts'][NAME], 50.0)

    def test_selected_s2_regeneration_end_clock_remains_unknown_at_empty_enemy(self):
        for elite in (1, 2):
            for mode in ('frames', 'continuous'):
                for extra in ({}, {'base_attack': 0}, {'healing_targets': 0},
                              {'timing': {'target_disappears_seconds': 0}}):
                    result = calculate_damage(scenario(elite=elite, skill=2, timing_mode=mode, **extra))
                    component = regeneration(result)
                    self.assertEqual(component['hits'], 10.0)
                    self.assertEqual(component['nominal_duration_reference_seconds'], 10.0)
                    self.assertIsNone(component['actual_total'])
                    self.assertIsNone(result['amiya_phase_reference']['actual_skill_end_seconds'])

    def test_module_does_not_unlock_talent_early_and_preserves_eligible_stages(self):
        for mode in ('frames', 'continuous'):
            for elite, level in ((0, 50), (1, 70), (2, 49), (2, 50)):
                for stage in (1, 2, 3):
                    result = calculate_damage(scenario(elite=elite, level=level, timing_mode=mode,
                        module_id=MODULE, module_level=stage))
                    self.assertEqual(regeneration(result)['hits'], 0.0 if elite == 0 else 10.0)
                    if elite:
                        self.assertGreater(regeneration(result)['per_hit'], 0)

    def test_older_skill_and_option_errors_are_not_bypassed(self):
        for extra in ({'skill': 2}, {'skill_rank': 8}, {'skill': 2, 'amiya_hit_targets': True}):
            with self.assertRaisesRegex(ValueError, '^当前精英阶段尚未开放所选技能或专精。$'):
                calculate_damage(scenario(**extra))
        with self.assertRaisesRegex(ValueError, '^精英阶段需要为 0、1 或 2。$'):
            calculate_damage(scenario(elite=True))
        with self.assertRaisesRegex(ValueError, '^amiya_hit_targets需要1到100之间的整数。$'):
            calculate_damage(scenario(elite=1, skill=2, amiya_hit_targets=True))

    def test_inputs_catalog_and_other_amiya_forms_are_unchanged(self):
        args = scenario()
        original = copy.deepcopy(args)
        cached = json.dumps(catalog(), sort_keys=True, ensure_ascii=False)
        self.assertEqual(calculate_damage(args), calculate_damage(args))
        self.assertEqual(args, original)
        self.assertEqual(json.dumps(catalog(), sort_keys=True, ensure_ascii=False), cached)
        for owner in ('char_002_amiya', 'char_1001_amiya2'):
            result = calculate_damage(scenario(operator=owner))
            self.assertNotIn(NAME, [c['name'] for c in result['components']])


if __name__ == '__main__':
    unittest.main()
