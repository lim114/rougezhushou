"""Actual continuous-attack consumers defer text errors and isolate private scope."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import unittest

from rouge.condition_inputs import read_continuous_attacks, validate_continuous_attacks
from rouge.damage import calculate_damage
from rouge.sp_events import charge

ERROR = '^continuous_attacks 不接受文本条件；请使用布尔值。$'


def scenario(op='mechanist', skill=1, **extra):
    return {'operator': op, 'skill': skill, 'elite': 2, 'level': 60,
            'base_attack': 1379, 'window_seconds': 9.75, **extra}


class ContinuousAttacksTextInputTests(unittest.TestCase):
    def test_actual_attack_consumer_rejects_both_nonempty_and_empty_text(self):
        for value in ('false', ''):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, ERROR):
                calculate_damage(scenario(continuous_attacks=value))

    def test_inactive_natural_skill_keeps_ignored_text(self):
        expected = calculate_damage(scenario('silverash', 3))
        for value in ('false', ''):
            self.assertEqual(calculate_damage(scenario('silverash', 3, continuous_attacks=value)), expected)

    def test_nonstring_truthiness_aliases_preserve_the_old_results(self):
        yes = calculate_damage(scenario(continuous_attacks=True))
        no = calculate_damage(scenario(continuous_attacks=False))
        for value in (1, 0, None, [1], []):
            with self.subTest(value=value):
                self.assertEqual(calculate_damage(scenario(continuous_attacks=value)), yes if value else no)

    def test_hidden_restricted_amiya_reference_keeps_native_clock_unknown(self):
        for elite, level, rank in ((0, 30, 4), (1, 40, 7)):
            with self.subTest(elite=elite), self.assertRaisesRegex(ValueError, ERROR):
                calculate_damage(scenario('char_002_amiya', 1, elite=elite, level=level,
                    skill_rank=rank, timing_mode='continuous', timing={'target_disappears_seconds': .75},
                    continuous_attacks='false'))
        accepted = calculate_damage(scenario('char_002_amiya', 1, elite=0, level=30,
            skill_rank=4, timing_mode='continuous', timing={'target_disappears_seconds': .75},
            continuous_attacks=True))
        self.assertFalse(accepted['amiya_continuous_reference']['native_clock_binding_verified'])
        self.assertIsNone(accepted['estimate']['skill']['cycle_seconds'])

    def test_older_numeric_and_processed_neural_errors_stay_first(self):
        with self.assertRaisesRegex(ValueError, '^base_attack 需要有限非负数；法抗范围为 0–100。$'):
            calculate_damage(scenario(base_attack=-1, continuous_attacks='false'))
        with self.assertRaisesRegex(ValueError, '^enemy_is_boss 不接受文本条件；请使用布尔值。$'):
            calculate_damage(scenario('char_1042_phatm2', 1,
                enemy_is_boss='false', continuous_attacks='false'))

    def test_user_markers_cannot_control_scope_and_caller_is_unchanged(self):
        args = scenario(continuous_attacks='false', _continuous_attacks_text_pending=False,
                        continuous_attacks_text_pending=False)
        saved = deepcopy(args)
        with self.assertRaisesRegex(ValueError, ERROR):
            calculate_damage(args)
        self.assertEqual(args, saved)
        inactive = scenario('silverash', 3, continuous_attacks='false',
                            _continuous_attacks_text_pending=True)
        saved = deepcopy(inactive)
        calculate_damage(inactive)
        self.assertEqual(inactive, saved)
        self.assertEqual(read_continuous_attacks({'continuous_attacks': 'false'}), 'false')

    def test_nested_failure_and_threads_reset_each_private_context(self):
        @validate_continuous_attacks
        def inner(value):
            return read_continuous_attacks({'continuous_attacks': value})

        @validate_continuous_attacks
        def outer():
            with self.assertRaisesRegex(ValueError, ERROR):
                inner('false')
            return read_continuous_attacks({'continuous_attacks': True})

        @validate_continuous_attacks
        def old_error():
            read_continuous_attacks({'continuous_attacks': 'false'})
            raise ValueError('older error')

        self.assertIs(outer(), True)
        with self.assertRaisesRegex(ValueError, '^older error$'):
            old_error()
        self.assertEqual(read_continuous_attacks({'continuous_attacks': ''}), '')

        def thread_case(value):
            try:
                return inner(value)
            except ValueError as exc:
                return str(exc)
        with ThreadPoolExecutor(max_workers=2) as pool:
            values = list(pool.map(thread_case, ('false', True)))
        self.assertEqual(values, ['continuous_attacks 不接受文本条件；请使用布尔值。', True])
        self.assertIs(read_continuous_attacks({'continuous_attacks': False}), False)

    def test_standalone_event_helper_and_actual_tail_qualification(self):
        args = {'operator': 'mechanist', 'skill': 3, 'continuous_attacks': 'false',
                'timing': {'sp_events': {'initial': []}}, '_relic_rules': []}
        skill = {'sp_type': 'INCREASE_WITH_TIME', 'sp_increment': 1}
        def event(value, wait=False, rate=1):
            return charge({**args, 'continuous_attacks': value}, skill, 3, rate, 1, 100,
                          initial=True, wait_next_attack=wait)
        self.assertEqual(event('false'), event(True))
        scoped = validate_continuous_attacks(event)
        self.assertIsNotNone(scoped('false')['seconds'])
        with self.assertRaisesRegex(ValueError, ERROR):
            scoped('false', True)
        # Waiting alone does not consume the condition if readiness stays unknown.
        self.assertIsNone(scoped('false', True, 0)['seconds'])


if __name__ == '__main__':
    unittest.main()
