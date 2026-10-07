"""Reviewed IS data overlay retains the existing talent identity only."""
from copy import deepcopy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents


OPERATOR = 'char_437_mizuki'
MODULE = 'uniequip_004_mizuki'
PARAMETER = 'attack@mizuki_t_1.atk_scale'


def selected(**extra):
    scenario = {'elite': 2, 'level': 60, 'potential': 1,
                'module_id': MODULE, 'module_level': 3, **extra}
    return selected_talents(catalog()['operators'][OPERATOR], scenario)


class MizukiTalentIdentityTests(unittest.TestCase):
    def test_each_module_stage_preserves_named_half_attack_talent(self):
        for stage in (1, 2, 3):
            with self.subTest(stage=stage):
                talents, _ = selected(module_level=stage)
                self.assertEqual(talents[0]['name'], '创伤性癔症')
                self.assertEqual(talents[0]['values'][PARAMETER], .5)

    def test_public_s1_condition_retains_fifteen_hundred_arts_damage(self):
        for stage in (1, 2, 3):
            with self.subTest(stage=stage):
                result = calculate_damage({'operator': OPERATOR, 'skill': 1,
                    'base_attack': 1000, 'elite': 2, 'level': 60, 'skill_rank': 10,
                    'module_id': MODULE, 'module_level': stage})
                extra = next(c for c in result['components'] if c['name'] == '唤醒额外法术')
                self.assertEqual(extra['per_hit'], 1500)

    def test_other_existing_module_and_no_module_values_are_unchanged(self):
        for module, stage, expected in ((None, 0, 1500), ('uniequip_002_mizuki', 2, 1650),
                                        ('uniequip_002_mizuki', 3, 1800)):
            with self.subTest(module=module, stage=stage):
                result = calculate_damage({'operator': OPERATOR, 'skill': 1,
                    'base_attack': 1000, 'elite': 2, 'level': 60, 'skill_rank': 10,
                    'module_id': module, 'module_level': stage})
                extra = next(c for c in result['components'] if c['name'] == '唤醒额外法术')
                self.assertAlmostEqual(extra['per_hit'], expected)

    def test_below_level_unlock_does_not_read_module_parts(self):
        talents, parts = selected(level=59)
        self.assertEqual(parts, [])
        self.assertEqual(talents[0]['name'], '创伤性癔症')
        self.assertEqual(talents[0]['values'][PARAMETER], .5)
        _, unlocked = selected(level=60)
        self.assertTrue(unlocked)

    def test_below_elite_unlock_keeps_original_talent(self):
        talents, parts = selected(elite=1)
        self.assertEqual(parts, [])
        self.assertEqual(talents[0]['name'], '创伤性癔症')
        self.assertEqual(talents[0]['values'][PARAMETER], .3)

    def test_potential_gates_of_unrelated_talent_are_preserved(self):
        for potential in range(1, 7):
            with self.subTest(potential=potential):
                talents, _ = selected(potential=potential)
                self.assertEqual(talents[0]['name'], '创伤性癔症')
                self.assertEqual(talents[0]['values'][PARAMETER], .5)
                other = next(t for t in talents if t['name'] == '反移情')
                self.assertEqual(other['values']['atk'], .1 if potential < 5 else .12)

    def test_only_reviewed_null_data_overlay_recovers_the_previous_identity(self):
        profile = deepcopy(catalog()['operators'][OPERATOR])
        module = next(m for m in profile['modules'] if m['id'] == MODULE)
        part = next(p for p in module['levels'][2]['parts'] if p['target'] == 'TALENT_DATA_ONLY'
                    and p.get('validInGameTag') == 'roguelike')
        part['target'] = 'TALENT'
        talents, _ = selected_talents(profile, {'elite': 2, 'level': 60, 'potential': 1,
                                               'module_id': MODULE, 'module_level': 3})
        self.assertIsNone(talents[0]['name'])

    def test_negative_index_script_fields_are_not_imported_as_known_talents(self):
        talents, parts = selected()
        values = {key for talent in talents for key in talent['values']}
        self.assertFalse(values.intersection({'attack_speed', 'hp_recovery_per_sec_by_max_hp_ratio',
                                              'force_base', 'force_in_skill', 'sp_recovery_per_sec'}))
        self.assertTrue(any(part['target'] == 'TALENT' for part in parts))

    def test_selection_and_calculation_leave_pinned_catalog_and_input_unchanged(self):
        profile = catalog()['operators'][OPERATOR]
        before = deepcopy(profile)
        scenario = {'operator': OPERATOR, 'skill': 1, 'elite': 2, 'level': 60,
                    'potential': 1, 'base_attack': 1000,
                    'module_id': MODULE, 'module_level': 3}
        original = deepcopy(scenario)
        selected_talents(profile, scenario)
        calculate_damage(scenario)
        self.assertEqual(profile, before)
        self.assertEqual(scenario, original)

    def test_fix_does_not_apply_unverified_aspeed_or_life_recovery_scripts(self):
        for stage in (1, 2, 3):
            with self.subTest(stage=stage):
                result = calculate_damage({'operator': OPERATOR, 'skill': 2,
                    'base_attack': 1000, 'elite': 2, 'level': 60,
                    'module_id': MODULE, 'module_level': stage})
                self.assertEqual(result['estimate']['base_stats']['attack_speed'], 100)
                self.assertFalse(any(c['damage_type'] in ('healing', 'regeneration')
                                     for c in result['components']))
                self.assertFalse(result['estimate']['complete'])


if __name__ == '__main__':
    unittest.main()
