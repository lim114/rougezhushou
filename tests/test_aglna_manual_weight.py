from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge.catalog import stage_previews
from rouge.damage import calculate_damage

OP = 'char_1015_aglna2'
TARGET = {'stage_id': 'ro6_n_1_1', 'enemy_id': 'enemy_2133_shdopl', 'level': 0}


def evaluate(**extra):
    return calculate_damage({'operator': OP, 'skill': 1, 'base_attack': 1000,
                             'window_seconds': 3, **extra})


def extra_hit(result):
    return next(c['per_hit'] for c in result['components'] if c['name'] == '飘浮大地之上')


class AglnaManualWeightTests(unittest.TestCase):
    def test_visible_manual_control_selects_light_and_heavy_talent(self):
        light, heavy = evaluate(enemy_weight=3), evaluate(enemy_weight=4)
        self.assertEqual(extra_hit(light), 868)
        self.assertEqual(extra_hit(heavy), 620)
        self.assertEqual(light['total_damage'], 3348)
        self.assertEqual(heavy['total_damage'], 3100)

    def test_threshold_and_control_endpoints_across_three_skills(self):
        for skill in (1, 2, 3):
            light = evaluate(skill=skill, enemy_weight=3)
            heavy = evaluate(skill=skill, enemy_weight=4)
            self.assertEqual(extra_hit(evaluate(skill=skill, enemy_weight=0)), extra_hit(light))
            self.assertEqual(extra_hit(evaluate(skill=skill, enemy_weight=100)), extra_hit(heavy))
            self.assertGreater(extra_hit(light), extra_hit(heavy))

    def test_source_cultivation_scales_are_preserved(self):
        for elite, potential, hi, lo in ((1, 1, .20, .13), (1, 3, .30, .18),
                                      (2, 1, .35, .25), (2, 3, .45, .30)):
            options = {'elite': elite, 'potential': potential, 'skill_rank': 7 if elite == 1 else 10}
            light = evaluate(enemy_weight=3, **options)
            heavy = evaluate(enemy_weight=4, **options)
            self.assertAlmostEqual(extra_hit(light)/extra_hit(heavy), hi/lo)

    def test_selected_identity_overrides_manual_weight(self):
        light = evaluate(target_enemy=TARGET, enemy_weight=0)
        heavy = evaluate(target_enemy=TARGET, enemy_weight=100)
        self.assertEqual(light['estimate']['skill'], heavy['estimate']['skill'])
        self.assertEqual(light['run_resolution']['enemy']['reference_stats']['massLevel'], 0)

    def test_missing_pinned_weight_cannot_silently_select_light_branch(self):
        data = deepcopy(stage_previews())
        for record in data[TARGET['stage_id']]['possible_enemies']:
            if record['id'] == TARGET['enemy_id']:
                record['reference_stats']['massLevel'] = None
        with patch('rouge.enemy_environment.stage_previews', return_value=data):
            with self.assertRaisesRegex(ValueError, '固定敌人重量档案缺失'):
                evaluate(target_enemy=TARGET, enemy_weight=4)

    def test_manual_weight_does_not_supply_gravity_identity(self):
        r = evaluate(enemy_weight=4, relic_ids=['rogue_6_relic_legacy_56'])
        record = r['relic_resolution']['records'][0]
        self.assertFalse(record['applied'])
        self.assertIn('target_enemy', record['missing_conditions'])
        self.assertEqual(extra_hit(r), 620)

    def test_manual_control_rejects_invalid_declaration(self):
        for value in (True, '4', None, float('nan'), float('inf'), -.1, 101, 3.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate(enemy_weight=value)

    def test_input_and_catalog_are_not_mutated(self):
        args = {'operator': OP, 'skill': 1, 'base_attack': 1000, 'enemy_weight': 4}
        original, catalog = deepcopy(args), deepcopy(stage_previews())
        calculate_damage(args)
        self.assertEqual(args, original)
        self.assertEqual(stage_previews(), catalog)


if __name__ == '__main__':
    unittest.main()
