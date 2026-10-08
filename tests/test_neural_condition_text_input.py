"""Reject text only at the two actual neural consumers, after old errors."""
from copy import deepcopy
import re
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage


OWNERS = ('char_1042_phatm2', 'char_4204_mantra')
FIELDS = ('enemy_is_boss', 'enemy_in_neural_break')
RIVER = 'rogue_6_relic_fight_22'


def scenario(owner, skill, mode='frames', **extra):
    return {'operator': owner, 'skill': skill, 'timing_mode': mode,
            'base_attack': 1000, 'window_seconds': 10, **extra}


def error(args):
    try:
        calculate_damage(args)
    except Exception as exc:
        return type(exc).__name__, str(exc)
    raise AssertionError('This legacy-invalid scenario must still raise.')


class NeuralConditionTextInputTests(unittest.TestCase):
    def assert_text_error(self, args, field):
        before = deepcopy(args)
        with self.assertRaisesRegex(ValueError, '^' + re.escape(
                field + ' 不接受文本条件；请使用布尔值。') + '$'):
            calculate_damage(args)
        self.assertEqual(args, before)

    def test_all_actual_owner_skills_reject_text_without_decoding_it(self):
        # S3 still consumes neural state even when its Qt options are hidden.
        for owner in OWNERS:
            for skill in (1, 2, 3):
                for mode in ('frames', 'continuous'):
                    for field in FIELDS:
                        for text in ('false', 'true', '0', '', 'unknown'):
                            with self.subTest(owner=owner, skill=skill, mode=mode,
                                              field=field, text=text):
                                self.assert_text_error(scenario(owner, skill, mode,
                                                                **{field: text}), field)

    def test_environment_fields_do_not_require_an_unrelated_talent_upgrade(self):
        for owner in OWNERS:
            for elite, skill in ((0, 1), (1, 2), (2, 3)):
                for field in FIELDS:
                    self.assert_text_error(scenario(owner, skill, elite=elite,
                        level=1, skill_rank=7, **{field: 'false'}), field)

    def test_nontext_legacy_truthiness_and_default_keep_whole_results(self):
        for owner in OWNERS:
            for field in FIELDS:
                args = scenario(owner, 2, initial_neural_buildup=999, relic_ids=[RIVER])
                false = calculate_damage({**args, field: False})
                true = calculate_damage({**args, field: True})
                self.assertEqual(calculate_damage(args), false)
                for value in (None, 0, 0.0, [], {}):
                    self.assertEqual(calculate_damage({**args, field: value}), false)
                for value in (1, 1.0, [False], {'assumed': False}):
                    self.assertEqual(calculate_damage({**args, field: value}), true)

    def test_selected_enemy_identity_overrides_stale_manual_boss_text(self):
        for owner in OWNERS:
            for target in (
                {'stage_id': 'ro6_e_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0},
                {'stage_id': 'ro6_b_3', 'enemy_id': 'enemy_2143_shwksc', 'level': 0},
            ):
                args = scenario(owner, 3, target_enemy=target,
                                run_config={'difficulty': {'value': 10}})
                expected = calculate_damage(args)
                for value in (False, True, 'false', '', 'unknown'):
                    self.assertEqual(calculate_damage({**args, 'enemy_is_boss': value}), expected)
                self.assert_text_error({**args, 'enemy_in_neural_break': 'false'},
                                       'enemy_in_neural_break')

    def test_existing_errors_win_before_either_new_text_error(self):
        for owner in OWNERS:
            extras = ({'skill': False}, {'skill_rank': False}, {'elite': 1},
                      {'level': 999}, {'module_id': 'unknown', 'module_level': 1},
                      {'initial_neural_buildup': 2500}, {'enemy_buildup_resistance': 101},
                      {'enemy_elemental_resistance': 101}, {'window_seconds': -1},
                      {'timing': {'windup_frames': -1}},
                      {'timing': {'sp_lockout_extra_seconds': -1}},
                      {'target_enemy': {'stage_id': 'unknown', 'enemy_id': 'unknown', 'level': 0}},
                      {'run_config': {'difficulty': {'value': 16}}})
            for extra in extras:
                args = {**scenario(owner, 3), **extra}
                expected = error({**args, 'enemy_is_boss': True,
                                  'enemy_in_neural_break': True})
                self.assertEqual(error({**args, 'enemy_is_boss': 'false',
                                        'enemy_in_neural_break': 'false'}), expected)
        for owner, skill, field in (('char_1042_phatm2', 2, 'bait_triggers'),
                                   ('char_1042_phatm2', 3, 'enemy_attack_count'),
                                   ('char_4204_mantra', 3, 'palsy_triggers')):
            args = scenario(owner, skill, **{field: True})
            expected = error(args)
            self.assertEqual(error({**args, 'enemy_is_boss': 'false',
                                    'enemy_in_neural_break': 'false'}), expected)

    def test_unrelated_owners_ignore_both_text_fields(self):
        for owner, skill in (('silverash', 3), ('mechanist', 1),
                             ('char_1037_amiya3', 2), ('char_1048_orchd2', 3)):
            args = scenario(owner, skill)
            self.assertEqual(calculate_damage({**args, 'enemy_is_boss': 'false',
                'enemy_in_neural_break': 'unknown'}), calculate_damage(args))

    def test_empty_observation_or_enemy_does_not_change_consumer_scope(self):
        for owner in OWNERS:
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for field in FIELDS:
                    self.assert_text_error(scenario(owner, 3, **extra, **{field: 'false'}), field)

    def test_mantra_S3_typed_river_state_keeps_unknown_periodic_clock(self):
        args = scenario('char_4204_mantra', 3, relic_ids=[RIVER])
        false = calculate_damage({**args, 'enemy_in_neural_break': False})
        true = calculate_damage({**args, 'enemy_in_neural_break': True})
        self.assertFalse(false['neural_relic_reference']['preexisting_break_assumed'])
        self.assertFalse(false['neural_relic_reference']['periodic_damage_possible'])
        self.assertTrue(true['neural_relic_reference']['preexisting_break_assumed'])
        self.assertIsNone(true['total_damage'])
        self.assertFalse(true['neural_relic_reference']['periodic_damage_scheduled'])
        self.assert_text_error({**args, 'enemy_in_neural_break': 'false'}, 'enemy_in_neural_break')
        self.assert_text_error({**args, 'enemy_is_boss': 'false',
                               'initial_neural_buildup': 1500}, 'enemy_is_boss')

    def test_both_text_fields_use_declared_order_and_preserve_shared_sources(self):
        original = deepcopy(catalog())
        args = scenario('char_4204_mantra', 3, enemy_is_boss='unknown',
                        enemy_in_neural_break='false', relic_ids=[RIVER])
        self.assert_text_error(args, 'enemy_is_boss')
        self.assertEqual(catalog(), original)
        valid = {**args, 'enemy_is_boss': False, 'enemy_in_neural_break': False}
        self.assertEqual(calculate_damage(valid), calculate_damage(valid))


if __name__ == '__main__':
    unittest.main()
