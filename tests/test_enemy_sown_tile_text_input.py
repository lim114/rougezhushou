"""Only the queried Shu S3 condition rejects textual checkbox inputs."""
import copy
import json
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.relics import mechanics
from rouge.reporting import format_report


OP = 'char_2025_shu'
ERROR = 'enemy_on_sown_tile 不接受文本条件；请使用布尔值。'


def calculate(value=False, mode='frames', skill=3, **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 10, 'timing_mode': mode,
                             'enemy_on_sown_tile': value, **extra})


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


class EnemySownTileTextInputTests(unittest.TestCase):
    def test_active_s3_text_is_rejected_at_all_ten_ranks(self):
        for mode in ('frames', 'continuous'):
            for rank in range(1, 11):
                for value in ('false', 'true', '', '0', '1', 'False', ' off ', '  true  '):
                    with self.subTest(mode=mode, rank=rank, value=value):
                        with self.assertRaises(ValueError) as caught:
                            calculate(value, mode, skill_rank=rank)
                        self.assertEqual(str(caught.exception), ERROR)

    def test_actual_query_still_rejects_text_at_empty_observation_boundaries(self):
        for mode in ('frames', 'continuous'):
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}, {'healing_targets': 0}):
                with self.subTest(mode=mode, extra=extra):
                    with self.assertRaises(ValueError) as caught:
                        calculate('false', mode, **extra)
                    self.assertEqual(str(caught.exception), ERROR)

    def test_nontext_contract_keeps_complete_bool_numeric_null_and_container_results(self):
        for mode in ('frames', 'continuous'):
            for value in (False, True, 0, 1, 0.0, 1.0, None, [], {}, ['manual'], {'manual': 1}):
                with self.subTest(mode=mode, value=value):
                    actual = calculate(value, mode)
                    expected = calculate(bool(value), mode)
                    self.assertEqual(strict(actual), strict(expected))
                    self.assertEqual(format_report(actual), format_report(expected))
            plain = {'operator': OP, 'skill': 3, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode}
            self.assertEqual(strict(calculate_damage(plain)), strict(calculate(False, mode)))

    def test_unqueried_shu_skills_and_other_owners_ignore_text(self):
        for mode in ('frames', 'continuous'):
            for operator, skill in ((OP, 1), (OP, 2), ('silverash', 3), ('mechanist', 3)):
                plain = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                         'window_seconds': 10, 'timing_mode': mode}
                for value in ('false', 'true', ''):
                    with self.subTest(mode=mode, operator=operator, skill=skill, value=value):
                        self.assertEqual(strict(calculate_damage({**plain, 'enemy_on_sown_tile': value})),
                                         strict(calculate_damage(plain)))

    def test_existing_skill_training_and_four_sui_errors_keep_priority(self):
        for mode in ('frames', 'continuous'):
            for elite in (0, 1):
                with self.assertRaisesRegex(ValueError, '当前精英阶段尚未开放所选技能或专精'):
                    calculate('false', mode, elite=elite, skill_rank=1)
            with self.assertRaisesRegex(ValueError, '技能等级需要为1–10的整数'):
                calculate('false', mode, skill_rank=True)
            with self.assertRaisesRegex(ValueError, 'four_sui 不接受文本条件'):
                calculate('false', mode, four_sui='false')

    def test_periodic_reference_stays_unknown_for_valid_conditions(self):
        for mode in ('frames', 'continuous'):
            for value in (False, True, 0, 1, None):
                result = calculate(value, mode, four_sui=True)
                reference = result['shu_periodic_sp_reference']
                self.assertIsNone(reference['first_tick_seconds'])
                self.assertIsNone(reference['actual_tick_times_seconds'])
                self.assertIsNone(reference['clock_origin'])
                self.assertFalse(reference['events_scheduled'])
                self.assertFalse(reference['clock_verified'])

    def test_control_label_has_original_ground_condition_without_new_target_filter(self):
        row = next(row for row in OPTIONS[OP] if row[0] == 'enemy_on_sown_tile')
        self.assertEqual(row, ('enemy_on_sown_tile', '存在地面敌人处于播种地块', False, 1, (3,)))

    def test_public_callers_and_shared_sources_are_preserved_on_acceptance_and_error(self):
        before_catalog = strict(catalog())
        before_mechanics = strict(mechanics())
        for value in ('false', '', True, None):
            args = {'operator': OP, 'skill': 3, 'enemy_on_sown_tile': value}
            before = copy.deepcopy(args)
            try:
                calculate_damage(args)
            except ValueError:
                pass
            self.assertEqual(strict(args), strict(before))
        self.assertEqual(strict(catalog()), before_catalog)
        self.assertEqual(strict(mechanics()), before_mechanics)


if __name__ == '__main__':
    unittest.main()
