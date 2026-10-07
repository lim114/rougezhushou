from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge.catalog import stage_previews
from rouge.damage import calculate_damage


def evaluate(stage, enemy, **extra):
    return calculate_damage({'operator': 'mechanist', 'skill': 1,
        'run_config': {'difficulty': {'value': 4}},
        'target_enemy': {'stage_id': stage, 'enemy_id': enemy, 'level': 0}, **extra})


def stats(stage, enemy, **extra):
    return evaluate(stage, enemy, **extra)['run_resolution']['enemy']['stats']


class EnemyRuneSelectorTests(unittest.TestCase):
    def test_explosion_specialist_scoped_attack_preserves_matching_target(self):
        self.assertEqual(stats('ro6_e_3_3', 'enemy_1076_bsthmr')['atk'], 3600)

    def test_unrelated_beast_receives_only_global_emergency_multiplier(self):
        r = stats('ro6_e_3_3', 'enemy_1108_uterer')
        self.assertEqual(r['atk'], 456)
        self.assertEqual(r['maxHp'], 5250)

    def test_scoped_health_preserves_matching_specialist(self):
        self.assertEqual(stats('ro6_e_4_1', 'enemy_10151_nspace_2')['maxHp'], 32400)

    def test_unrelated_proto_hound_does_not_get_specialist_health(self):
        self.assertEqual(stats('ro6_e_4_1', 'enemy_2137_shsdgo')['maxHp'], 21600)

    def test_normal_variants_keep_original_values(self):
        self.assertEqual(stats('ro6_n_3_3', 'enemy_1108_uterer')['atk'], 380)
        self.assertEqual(stats('ro6_n_4_1', 'enemy_2137_shsdgo')['maxHp'], 18000)

    def test_existing_difficulty_health_factor_still_composes_once(self):
        r = stats('ro6_e_4_1', 'enemy_2137_shsdgo', run_config={'difficulty': {'value': 5}})
        self.assertAlmostEqual(r['maxHp'], 21600*1.3)

    def test_unsupported_selector_does_not_apply_known_numbers_broadly(self):
        for value in (None, '', 'enemy_1076_bsthmr|enemy_1108_uterer', 'enemy_unknown'):
            data = deepcopy(stage_previews())
            rune = data['ro6_e_3_3']['runes'][1]
            selector = next(b for b in rune['blackboard'] if b['key'] == 'enemy')
            selector['valueStr'] = value
            with patch('rouge.enemy_environment.stage_previews', return_value=data):
                r = evaluate('ro6_e_3_3', 'enemy_1108_uterer')['run_resolution']['enemy']
            self.assertEqual(r['stats']['atk'], 456)
            self.assertTrue(any('敌人选择器尚未覆盖' in text for text in r['pending']))

    def test_selector_metadata_is_not_reported_as_unknown_numeric_attribute(self):
        r = evaluate('ro6_e_3_3', 'enemy_1076_bsthmr')['run_resolution']['enemy']
        self.assertFalse(any('未覆盖的属性修正字段' in text for text in r['pending']))

    def test_public_input_and_pinned_preview_are_not_mutated(self):
        before = deepcopy(stage_previews())
        args = {'run_config': {'difficulty': {'value': 4}}}
        original = deepcopy(args)
        evaluate('ro6_e_3_3', 'enemy_1108_uterer', **args)
        self.assertEqual(args, original)
        self.assertEqual(stage_previews(), before)


if __name__ == '__main__':
    unittest.main()
