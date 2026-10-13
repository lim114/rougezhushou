"""Current source-qualified behavior of the three approved047 guard extensions.

Original16-function AST checks remain in test_readable_battle_047_current_guard.
These controls add behavior protection; they do not recreate missing pre047 files.
"""
from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge.battle_preview import battle_data, enemy_preview, enemy_text
from rouge.enemy_skills import enemy_skill_reference, enemy_skill_text
from rouge.spawn_reference import movement_reference
from tests.test_enemy_skills_042 import fixture


class ReadableBattle047CurrentSuccessorTests(unittest.TestCase):
    def test_enemy_preview_preserves_raw_and_qualified_sources_through_both_renderings(self):
        cases = [('ro6_n_1_2', 'enemy_1093_ccsbr'),
                 ('ro6_n_2_3', 'enemy_2133_shdopl_lancer'),
                 ('ro6_n_3_2', 'enemy_1303_mhshep_2b')]
        for stage_id, enemy_id in cases:
            with self.subTest(stage=stage_id, enemy=enemy_id):
                stage_before = deepcopy(battle_data()['stages'][stage_id])
                config = {'difficulty': {'value': 0}}
                config_before = deepcopy(config)
                raw = next(r for r in stage_before['enemies'] if r['id'] == enemy_id and r['level'] == 0)
                result = enemy_preview(stage_id, enemy_id, 0, config)
                self.assertEqual(result['raw_reference_stats'], raw['reference_stats'])
                self.assertEqual(result['reference_stats'], result['fixed_panel_reference']['attributes'])
                self.assertIsNone(result['skill_reference']['first_activation_seconds'])
                self.assertIsNone(result['skill_reference']['effective_skill_damage'])
                self.assertFalse(result['movement_reference']['complete_effective_speed_verified'])
                saved = deepcopy(result)
                for technical in (False, True):
                    text = enemy_text(result, technical)
                    self.assertIn('未知', text)
                    self.assertEqual(result, saved)
                self.assertEqual(config, config_before)
                self.assertEqual(battle_data()['stages'][stage_id], stage_before)
                result['raw_reference_stats']['atk'] = -99
                self.assertEqual(enemy_preview(stage_id, enemy_id, 0, config)['raw_reference_stats'], raw['reference_stats'])

    def test_skill_extension_keeps_zero_null_empty_and_future_level_boundaries(self):
        data = fixture()
        original = deepcopy(data)
        with patch('rouge.enemy_skills.skill_data', return_value=data):
            result = enemy_skill_reference('stage', 'enemy', 1)
            self.assertEqual([r['level'] for r in result['definitions']], [0, 1])
            self.assertIsNone(result['definitions'][1]['skills'])
            self.assertIsNone(result['definitions'][1]['spData'])
            self.assertEqual(result['definitions'][1]['talentBlackboard'], [])
            self.assertEqual(result['definitions'][0]['skills'][0]['initCooldown'], 0)
            self.assertEqual(result['definitions'][0]['spData']['initSp'], 0)
            self.assertIsNone(result['first_activation_seconds'])
            self.assertIsNone(result['effective_skill_damage'])
            self.assertFalse(result['inheritance_resolved'])
            saved = deepcopy(result)
            for technical in (False, True):
                text = enemy_skill_text(result, technical)
                self.assertNotIn('future', text)
                self.assertIn('实际首次发动时刻：未知', text)
                self.assertEqual(result, saved)
            self.assertEqual(data, original)
            result['definitions'][0]['skills'][0]['cooldown'] = -99
            self.assertEqual(enemy_skill_reference('stage', 'enemy', 1)['definitions'][0]['skills'][0]['cooldown'], 10)
            for wrong_level in (True, -1, 2, 1.0, '1'):
                with self.assertRaises(ValueError):
                    enemy_skill_reference('stage', 'enemy', wrong_level)
            with self.assertRaises(ValueError):
                enemy_skill_reference('stage', 'enemy', 1, resource_plan={}, prefab_gate_plan={})

    def test_movement_extension_separates_nominal_source_conditional_write_and_actual_clock(self):
        stage = deepcopy(battle_data()['stages']['ro6_e_3_6'])
        saved = deepcopy(stage)
        reference = movement_reference(stage, .4)
        self.assertEqual(reference['base_times_stage_speed'], .2)
        conditional = reference['conditional_native_movement']
        self.assertEqual(conditional['written_move_speed_attribute'], .6000000238418579)
        self.assertEqual(conditional['conditional_speed_tiles_per_second'], .30000001192092896)
        self.assertNotEqual(conditional['conditional_speed_tiles_per_second'], .4 * 1.5 * .5)
        self.assertIsNone(conditional['complete_effective_speed'])
        self.assertIsNone(conditional['actual_position_or_arrival_time'])
        self.assertFalse(conditional['rune_execution_verified'])
        self.assertFalse(reference['complete_effective_speed_verified'])
        self.assertIsNone(reference['stage_move_speed_rune_reference']['combined_with_stage_multiplier_speed'])
        unknown = movement_reference(stage, None)
        self.assertIsNone(unknown['base_times_stage_speed'])
        self.assertEqual(unknown['conditional_native_movement']['state'], 'unavailable_parameters')
        self.assertIsNone(unknown['conditional_native_movement']['conditional_speed_tiles_per_second'])
        changed = deepcopy(stage)
        changed['level_source']['sha256'] = 'changed'
        self.assertNotIn('conditional_native_movement', movement_reference(changed, .4))
        self.assertEqual(stage, saved)


if __name__ == '__main__':
    unittest.main()
