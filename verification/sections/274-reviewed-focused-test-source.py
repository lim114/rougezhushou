"""Literal/control-flow qualification of the source-bound natural SP timer.

Declared read points are independent. Expected fixed-point vectors are literal
source examples or integer boundary proofs, never production-math oracles.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import sp_recovery_clock as module

ROOT = Path(__file__).resolve().parents[1]
Q = 4294967296
EPS = 42950


def stop(value=False, *, exists=True, normal=True):
    return {'exists': exists, 'normal': normal, 'value': value}


def recovery(sp=5 * Q, *, force=False, paused=False, stop_exists=True, stop_normal=True,
             sp_exists=True, sp_normal=True, setter_normal=True, native=True):
    return {'ordinary_native_path': native, 'force': force,
            'stop_read': stop(paused, exists=stop_exists, normal=stop_normal),
            'sp_read': {'exists': sp_exists, 'normal': sp_normal, 'raw': sp},
            'setter_returns_normally': setter_normal}


def tick(identity='tick', *, delta=0, enabled=True, paused=False, stop_exists=True,
         stop_normal=True, full=False, full_normal=True, request=None, native=True):
    return {'id': identity, 'kind': 'tick', 'ordinary_native_path': native,
            'delta_raw': delta, 'enabled': enabled,
            'gate_stop': stop(paused, exists=stop_exists, normal=stop_normal),
            'full_read': {'normal': full_normal, 'value': full},
            'recovery': recovery() if request is None else request}


def recover(identity='recover', *, amount=Q, request=None, native=True):
    return {'id': identity, 'kind': 'recover', 'ordinary_native_path': native,
            'amount_raw': amount, 'recovery': recovery() if request is None else request}


def rate(flat=Q, ratio=Q, *, exists=True, normal=True, native=True):
    return {'ordinary_native_path': native, 'attributes_exist': exists,
            'reads_return_normally': normal, 'attr14_raw': flat, 'attr30_raw': ratio}


def reconfigure(identity='reconfigure', *, input_rate=2 * Q, drain=None, can_recover=None, native=True):
    return {'id': identity, 'kind': 'reconfigure', 'ordinary_native_path': native,
            'rate_input_raw': input_rate, 'drain': drain, 'can_recover_rate': can_recover}


def payload(*actions, period=Q, remaining=Q, controller=True, timer=True):
    return {'controller_exists': controller, 'precise_timer_identity': True,
            'no_intervening_timer_changes': True,
            'timer': {'exists': timer, 'period_raw': period, 'remaining_raw': remaining},
            'actions': list(actions) or [tick()]}


def tick_result(data):
    return module.sp_recovery_clock_reference(data)['rows'][0]['tick']


class SpRecoveryClockTests(unittest.TestCase):
    def test_public_three_actions_batch_once_pause_again_and_force_negative_independent_read(self):
        data = module.public_example(); before = deepcopy(data)
        result = module.sp_recovery_clock_reference(data)
        self.assertTrue(result['source_valid'])
        first, second, third = result['rows']
        self.assertEqual(first['tick']['updated_remaining_raw_reference'], -3221225472)
        self.assertEqual(first['tick']['quotient_raw_reference'], 12884901888)
        self.assertEqual(first['tick']['floor_count_reference'], 3)
        self.assertEqual(first['tick']['batch_count_reference'], 4)
        self.assertEqual(first['tick']['remaining_after_raw_reference'], 1073741824)
        self.assertEqual(first['tick']['recovery']['setter_value_argument_raw_reference'], 38654705664)
        self.assertEqual(second['tick']['batch_count_reference'], 1)
        self.assertEqual(second['tick']['remaining_after_raw_reference'], 1073741824)
        self.assertFalse(second['tick']['recovery']['getter_called_reference'])
        self.assertFalse(second['tick']['recovery']['setter_called_reference'])
        self.assertTrue(second['tick']['recovery']['normal_return_reference'])
        self.assertEqual(third['recovery']['setter_value_argument_raw_reference'], 30064771072)
        self.assertFalse(third['recovery']['stop_read_called_reference'])
        self.assertEqual(result['final_period_raw_reference'], 1073741824)
        self.assertEqual(result['final_remaining_raw_reference'], 1073741824)
        self.assertEqual(data, before)

    def test_bound_preparation_batch9_to13_is_a_distinct_independent_sp_input(self):
        data = payload(tick(delta=7 * Q // 8, request=recovery(9 * Q)), period=Q // 4, remaining=Q // 8)
        result = tick_result(data)
        self.assertEqual(result['batch_count_reference'], 4)
        self.assertEqual(result['recovery']['setter_value_argument_raw_reference'], 55834574848)

    def test_period_validity_and_ready_have_separate_strict_epsilon_boundaries(self):
        for period in (-Q, 0, EPS - 1, EPS):
            with self.subTest(period=period):
                row = tick_result(payload(tick(delta=Q), period=period, remaining=0))
                self.assertFalse(row['valid_reference']); self.assertFalse(row['delta_applied_reference'])
                self.assertFalse(row['next_multiple_called_reference']); self.assertIsNone(row['recovery'])
                self.assertEqual(row['remaining_after_raw_reference'], 0)
        row = tick_result(payload(tick(), period=EPS + 1, remaining=0))
        self.assertTrue(row['valid_reference']); self.assertEqual(row['batch_count_reference'], 1)
        self.assertEqual(row['remaining_after_raw_reference'], 42951)
        for remaining, count, after in ((EPS - 1, 1, Q + EPS - 1), (EPS, 0, EPS), (EPS + 1, 0, EPS + 1)):
            with self.subTest(remaining=remaining):
                row = tick_result(payload(tick(), remaining=remaining))
                self.assertEqual(row['batch_count_reference'], count)
                self.assertEqual(row['remaining_after_raw_reference'], after)

    def test_negative_delta_delays_without_sp_access_or_batch(self):
        row = tick_result(payload(tick(delta=-Q, request=recovery(sp_normal=False)), remaining=Q // 2))
        self.assertTrue(row['delta_applied_reference'])
        self.assertEqual(row['updated_remaining_raw_reference'], 3 * Q // 2)
        self.assertEqual(row['batch_count_reference'], 0)
        self.assertFalse(row['next_multiple_called_reference']); self.assertIsNone(row['recovery'])
        self.assertTrue(row['normal_return_reference'])

    def test_half_raw_rounding_can_cross_an_integer_floor_before_batch_count(self):
        vectors = [(Q, Q - 1, 4294967295, 0, 1, 1),
                   (2 * Q, 2 * Q - 1, 4294967296, 1, 2, 8589934593),
                   (4 * Q, 4 * Q - 1, 4294967296, 1, 2, 17179869185)]
        for period, delta, quotient, floor, count, after in vectors:
            with self.subTest(period=period):
                row = tick_result(payload(tick(delta=delta), period=period, remaining=0))
                self.assertEqual(row['quotient_raw_reference'], quotient)
                self.assertEqual(row['floor_count_reference'], floor)
                self.assertEqual(row['batch_count_reference'], count)
                self.assertEqual(row['remaining_after_raw_reference'], after)

    def test_small_positive_ready_remaining_uses_negative_floor_then_max_zero_plus_one(self):
        row = tick_result(payload(tick(), remaining=EPS - 1))
        self.assertEqual(row['division_numerator_raw_reference'], -42949)
        self.assertEqual(row['quotient_raw_reference'], -42949)
        self.assertEqual(row['floor_count_reference'], -1)
        self.assertEqual(row['batch_count_reference'], 1)

    def test_batch_counter_int_max_wraps_negative_and_skips_next_and_recovery(self):
        data = payload(tick(request=recovery(sp_normal=False)), remaining=-9223372032559808512)
        row = tick_result(data)
        self.assertEqual(row['quotient_raw_reference'], 9223372032559808512)
        self.assertEqual(row['floor_count_reference'], 2147483647)
        self.assertEqual(row['batch_count_reference'], -2147483648)
        self.assertFalse(row['next_multiple_called_reference']); self.assertIsNone(row['recovery'])
        self.assertEqual(row['remaining_after_raw_reference'], -9223372032559808512)
        self.assertTrue(row['normal_return_reference'])

    def test_unary_min64_maps_to_fp_max_before_the_signed32_counter_wrap(self):
        row = tick_result(payload(tick(), remaining=-9223372036854775808))
        self.assertEqual(row['division_numerator_raw_reference'], 9223372036854775806)
        self.assertEqual(row['quotient_raw_reference'], 9223372036854775806)
        self.assertEqual(row['floor_count_reference'], 2147483647)
        self.assertEqual(row['batch_count_reference'], -2147483648)
        self.assertEqual(row['remaining_after_raw_reference'], -9223372036854775808)

    def test_signed64_update_and_next_wrap_are_retained_as_literal_timer_prefixes(self):
        updated = tick_result(payload(tick(delta=-1), remaining=9223372036854775807))
        self.assertEqual(updated['updated_remaining_raw_reference'], -9223372036854775808)
        self.assertEqual(updated['batch_count_reference'], -2147483648)
        advanced = tick_result(payload(tick(), period=9223372036854775807, remaining=1))
        self.assertEqual(advanced['batch_count_reference'], 1)
        self.assertTrue(advanced['next_multiple_called_reference'])
        self.assertEqual(advanced['remaining_after_raw_reference'], -9223372036854775808)

    def test_division_outside_bound_keeps_written_update_but_never_invents_count_or_failure(self):
        row = tick_result(payload(tick(), period=EPS + 1, remaining=-9223372036854775808))
        self.assertTrue(row['delta_applied_reference'])
        self.assertEqual(row['updated_remaining_raw_reference'], -9223372036854775808)
        self.assertEqual(row['known_prefix_remaining_raw_reference'], -9223372036854775808)
        self.assertIsNone(row['quotient_raw_reference']); self.assertIsNone(row['batch_count_reference'])
        self.assertIsNot(row['normal_return_reference'], False)

    def test_disabled_invalid_first_stop_and_full_gates_do_not_apply_delta(self):
        variants = [payload(tick(enabled=False, delta=Q, stop_normal=False), remaining=Q // 2),
                    payload(tick(delta=Q, stop_normal=False), period=0, remaining=Q // 2),
                    payload(tick(delta=Q, paused=True, full_normal=False), remaining=Q // 2),
                    payload(tick(delta=Q, full=True), remaining=Q // 2)]
        for index, data in enumerate(variants):
            with self.subTest(index=index):
                row = tick_result(data)
                self.assertFalse(row['delta_applied_reference']); self.assertTrue(row['normal_return_reference'])
                self.assertFalse(row['next_multiple_called_reference']); self.assertIsNone(row['recovery'])
                self.assertEqual(row['remaining_after_raw_reference'], Q // 2)

    def test_early_gate_unknowns_close_only_when_all_normal_branches_skip(self):
        for index, data in enumerate((payload(tick(enabled=None), period=0, remaining=Q // 2),
                                      payload(tick(paused=None, full=True), remaining=Q // 2))):
            with self.subTest(index=index):
                row = tick_result(data)
                self.assertTrue(row['normal_return_reference']); self.assertFalse(row['delta_applied_reference'])
                self.assertEqual(row['remaining_after_raw_reference'], Q // 2)
        row = tick_result(payload(tick(enabled=None, delta=Q), remaining=Q // 2))
        self.assertIsNone(row['normal_return_reference']); self.assertIsNone(row['remaining_after_raw_reference'])

    def test_first_stop_and_full_read_failures_occur_before_any_timer_update(self):
        for stage in ('gate_stop', 'full_read'):
            for normal in (False, None):
                action = tick(delta=Q); action[stage]['normal'] = normal
                with self.subTest(stage=stage, normal=normal):
                    row = tick_result(payload(action, remaining=Q // 2))
                    self.assertIs(row['delta_applied_reference'], False if normal is False else None)
                    self.assertEqual(row['known_prefix_remaining_raw_reference'], Q // 2)
                    self.assertIs(row['normal_return_reference'], normal)
                    self.assertIs(row['next_multiple_called_reference'], False if normal is False else None)
                    self.assertIsNone(row['recovery'])

    def test_second_pause_is_a_distinct_read_after_next_multiple(self):
        row = tick_result(payload(tick(delta=Q, request=recovery(paused=True)), remaining=Q))
        self.assertEqual(row['batch_count_reference'], 1)
        self.assertTrue(row['next_advanced_reference'])
        self.assertEqual(row['remaining_after_raw_reference'], Q)
        self.assertTrue(row['recovery']['normal_return_reference'])
        self.assertFalse(row['recovery']['getter_called_reference'])
        self.assertFalse(row['recovery']['setter_called_reference'])

    def test_failed_or_unknown_second_pause_retains_next_and_stops_later_action(self):
        for normal in (False, None):
            data = payload(tick(delta=Q, request=recovery(stop_normal=normal)), tick('later'), remaining=Q)
            with self.subTest(normal=normal):
                result = module.sp_recovery_clock_reference(data); first = result['rows'][0]['tick']
                self.assertTrue(first['next_advanced_reference'])
                self.assertEqual(first['known_prefix_remaining_raw_reference'], Q)
                self.assertIs(first['normal_return_reference'], normal)
                self.assertIs(result['rows'][1]['called_reference'], False if normal is False else None)
                self.assertIs(first['recovery']['getter_called_reference'], False if normal is False else None)

    def test_one_batch_uses_one_independent_sp_read_and_no_per_tick_previous_setter_loop(self):
        data = payload(tick('four', delta=7 * Q // 8, request=recovery(5 * Q)),
                       tick('one', delta=Q // 4, request=recovery(20 * Q)),
                       period=Q // 4, remaining=Q // 8)
        result = module.sp_recovery_clock_reference(data)
        first = result['rows'][0]['tick']; second = result['rows'][1]['tick']
        self.assertEqual(first['batch_count_reference'], 4)
        self.assertEqual(first['recovery']['setter_value_argument_raw_reference'], 9 * Q)
        self.assertEqual(second['batch_count_reference'], 1)
        self.assertEqual(second['recovery']['setter_value_argument_raw_reference'], 21 * Q)
        self.assertTrue(first['recovery']['getter_called_reference'])
        self.assertTrue(second['recovery']['getter_called_reference'])

    def test_force_skips_second_stop_failure_but_never_bypasses_sp_or_setter(self):
        data = payload(recover(amount=-2 * Q, request=recovery(9 * Q, force=True, stop_exists=False,
                                                              stop_normal=False, paused=True)))
        result = module.sp_recovery_clock_reference(data); row = result['rows'][0]['recovery']
        self.assertFalse(row['stop_read_called_reference'])
        self.assertTrue(row['getter_called_reference']); self.assertTrue(row['setter_called_reference'])
        self.assertEqual(row['setter_value_argument_raw_reference'], 7 * Q)
        self.assertEqual(result['final_remaining_raw_reference'], Q)
        for exists, normal, overall, getter_called, setter_called in (
                (False, True, False, False, False), (True, False, False, True, False),
                (True, None, None, True, None), (None, False, False, None, False),
                (None, True, None, None, None)):
            request = recovery(force=True, stop_normal=False, sp_exists=exists, sp_normal=normal)
            with self.subTest(exists=exists, normal=normal):
                row = module.sp_recovery_clock_reference(payload(recover(request=request)))['rows'][0]['recovery']
                self.assertIs(row['getter_called_reference'], getter_called)
                self.assertIs(row['getter_normal_reference'], normal if exists is True else None)
                self.assertIs(row['setter_called_reference'], setter_called)
                self.assertIs(row['normal_return_reference'], overall)

    def test_recover_zero_negative_and_sp_addition_wrap_do_not_change_timer(self):
        vectors = [(0, 5 * Q, 5 * Q), (-2 * Q, 9 * Q, 7 * Q),
                   (1, 9223372036854775807, -9223372036854775808)]
        for amount, sp, expected in vectors:
            with self.subTest(amount=amount, sp=sp):
                result = module.sp_recovery_clock_reference(payload(recover(amount=amount, request=recovery(sp, force=True)),
                                                                    period=Q // 4, remaining=Q // 8))
                row = result['rows'][0]['recovery']
                self.assertTrue(row['getter_called_reference']); self.assertTrue(row['setter_called_reference'])
                self.assertEqual(row['setter_value_argument_raw_reference'], expected)
                self.assertEqual(result['final_period_raw_reference'], Q // 4)
                self.assertEqual(result['final_remaining_raw_reference'], Q // 8)

    def test_stopped_nonforce_recovery_skips_unknown_amount_sp_and_setter_normally(self):
        action = recover(amount=None, request=recovery(None, paused=True, sp_normal=False, setter_normal=False))
        row = module.sp_recovery_clock_reference(payload(action))['rows'][0]['recovery']
        self.assertTrue(row['normal_return_reference'])
        self.assertFalse(row['getter_called_reference']); self.assertFalse(row['setter_called_reference'])
        self.assertIsNone(row['setter_value_argument_raw_reference'])

    def test_unknown_force_closes_shared_successful_recovery_but_not_the_stop_read_call(self):
        action = recover(amount=2 * Q, request=recovery(5 * Q, force=None, paused=False))
        row = module.sp_recovery_clock_reference(payload(action))['rows'][0]['recovery']
        # false force reads a normal, false stop; true force skips that read.
        # Both branches then perform the same qualified getter/setter request.
        self.assertTrue(row['normal_return_reference'])
        self.assertIsNone(row['stop_read_called_reference'])
        self.assertTrue(row['getter_called_reference']); self.assertTrue(row['setter_called_reference'])
        self.assertEqual(row['setter_value_argument_raw_reference'], 7 * Q)
        self.assertEqual(row['declared_request_count_reference'], 1)
        action['recovery']['stop_read']['value'] = True
        result = module.sp_recovery_clock_reference(payload(action)); row = result['rows'][0]['recovery']
        self.assertTrue(row['normal_return_reference'])
        self.assertIsNone(row['getter_called_reference']); self.assertIsNone(row['setter_called_reference'])
        self.assertIsNone(row['setter_value_argument_raw_reference'])
        self.assertIsNone(row['declared_request_count_reference'])
        self.assertIsNone(result['declared_complete_setter_request_count'])
        action['recovery']['stop_read']['value'] = False
        action['recovery']['stop_read']['normal'] = False
        row = module.sp_recovery_clock_reference(payload(action))['rows'][0]['recovery']
        self.assertIsNone(row['normal_return_reference'])
        self.assertIsNone(row['getter_called_reference']); self.assertIsNone(row['setter_called_reference'])

    def test_sp_failure_does_not_undo_next_and_getter_parameter_is_never_actual_sp(self):
        for exists, normal in ((False, True), (True, False), (True, None)):
            data = payload(tick(delta=Q, request=recovery(sp_exists=exists, sp_normal=normal)), tick('later'))
            with self.subTest(exists=exists, normal=normal):
                result = module.sp_recovery_clock_reference(data); row = result['rows'][0]['tick']
                self.assertTrue(row['next_advanced_reference'])
                self.assertEqual(row['known_prefix_remaining_raw_reference'], Q)
                self.assertIs(row['recovery']['setter_called_reference'], None if exists is True and normal is None else False)
                self.assertIs(row['normal_return_reference'], False if exists is False else normal)
                self.assertIs(result['rows'][1]['called_reference'], None if exists is True and normal is None else False)

    def test_unknown_sp_value_has_normal_access_and_unknown_argument_not_a_fabricated_failure(self):
        row = module.sp_recovery_clock_reference(payload(recover(request=recovery(None, force=True))))['rows'][0]['recovery']
        self.assertTrue(row['getter_called_reference']); self.assertTrue(row['setter_called_reference'])
        self.assertTrue(row['normal_return_reference']); self.assertIsNone(row['setter_value_argument_raw_reference'])

    def test_setter_failure_keeps_attempted_parameter_and_next_prefix_but_stops_chain(self):
        for normal in (False, None):
            data = payload(tick(delta=Q, request=recovery(5 * Q, setter_normal=normal)), tick('later'))
            with self.subTest(normal=normal):
                result = module.sp_recovery_clock_reference(data); row = result['rows'][0]['tick']
                self.assertEqual(row['recovery']['setter_value_argument_raw_reference'], 6 * Q)
                self.assertTrue(row['recovery']['setter_called_reference'])
                self.assertIs(row['normal_return_reference'], normal)
                self.assertEqual(row['known_prefix_remaining_raw_reference'], Q)
                self.assertIs(result['rows'][1]['called_reference'], False if normal is False else None)

    def test_valid_timer_drain_zero_then_keep_elapsed_time_not_ratio_scale(self):
        data = payload(reconfigure(drain=tick('drain'), can_recover=rate()), remaining=3 * Q // 4)
        result = module.sp_recovery_clock_reference(data); row = result['rows'][0]
        self.assertIsNotNone(row['drain'])
        self.assertEqual(result['final_period_raw_reference'], Q // 2)
        self.assertEqual(result['final_remaining_raw_reference'], Q // 4)
        self.assertNotEqual(result['final_remaining_raw_reference'], 3 * Q // 8)

    def test_valid_timer_drain_ready_request_occurs_before_reset(self):
        data = payload(reconfigure(input_rate=4 * Q, drain=tick('drain', request=recovery(5 * Q)), can_recover=rate()), remaining=0)
        result = module.sp_recovery_clock_reference(data); row = result['rows'][0]
        self.assertEqual(row['drain']['batch_count_reference'], 1)
        self.assertEqual(row['drain']['recovery']['setter_value_argument_raw_reference'], 6 * Q)
        self.assertEqual(row['drain']['remaining_after_raw_reference'], Q)
        self.assertEqual(result['final_period_raw_reference'], Q // 4)
        self.assertEqual(result['final_remaining_raw_reference'], Q // 4)

    def test_valid_timer_canrecover_false_marks_both_invalid_despite_positive_input_rate(self):
        for can_rate in (rate(0), rate(-Q), rate(EPS), rate(Q, 0)):
            data = payload(reconfigure(input_rate=4 * Q, drain=tick('drain'), can_recover=can_rate))
            with self.subTest(can_rate=can_rate):
                result = module.sp_recovery_clock_reference(data)
                self.assertEqual(result['final_period_raw_reference'], -Q)
                self.assertEqual(result['final_remaining_raw_reference'], -Q)
                self.assertTrue(result['rows'][0]['normal_return_reference'])

    def test_invalid_timer_resets_directly_without_drain_or_canrecover_reads(self):
        for period in (0, EPS, -Q):
            action = reconfigure(input_rate=2 * Q, drain=tick('unused', stop_normal=False),
                                 can_recover=rate(exists=False, normal=False))
            with self.subTest(period=period):
                result = module.sp_recovery_clock_reference(payload(action, period=period, remaining=-9 * Q))
                self.assertIsNone(result['rows'][0]['drain']); self.assertIsNone(result['rows'][0]['can_recover'])
                self.assertTrue(result['rows'][0]['normal_return_reference'])
                self.assertEqual(result['final_period_raw_reference'], Q // 2)
                self.assertEqual(result['final_remaining_raw_reference'], Q // 2)

    def test_input_rate_and_attribute_rate_are_independent_and_negative_rate_is_not_auto_rejected(self):
        data = payload(reconfigure(input_rate=4 * Q, drain=tick('drain'), can_recover=rate(2 * Q, 3 * Q)),
                       remaining=3 * Q // 4)
        result = module.sp_recovery_clock_reference(data)
        self.assertEqual(result['rows'][0]['can_recover']['rate_raw_reference'], 6 * Q)
        self.assertEqual(result['final_period_raw_reference'], Q // 4)
        self.assertEqual(result['final_remaining_raw_reference'], 0)
        for input_rate, period in ((0, -Q), (-2 * Q, -Q // 2)):
            with self.subTest(input_rate=input_rate):
                result = module.sp_recovery_clock_reference(payload(
                    reconfigure(input_rate=input_rate, drain=tick('drain'), can_recover=rate()), remaining=Q // 2))
                self.assertEqual(result['final_period_raw_reference'], period)
                self.assertEqual(result['final_remaining_raw_reference'], 0)
                direct = module.sp_recovery_clock_reference(payload(reconfigure(input_rate=input_rate), period=0))
                self.assertEqual(direct['final_period_raw_reference'], period)
                self.assertEqual(direct['final_remaining_raw_reference'], period)

    def test_canrecover_rate_strict_epsilon_and_typed_zero_product_closure(self):
        for flat, ratio, active in ((EPS, Q, False), (EPS + 1, Q, True),
                                    (None, 0, False), (0, None, False)):
            action = reconfigure(input_rate=2 * Q, drain=tick('drain'), can_recover=rate(flat, ratio))
            with self.subTest(flat=flat, ratio=ratio):
                result = module.sp_recovery_clock_reference(payload(action))
                if active:
                    self.assertEqual(result['final_period_raw_reference'], Q // 2)
                else:
                    self.assertEqual(result['final_period_raw_reference'], -Q)
                    self.assertEqual(result['final_remaining_raw_reference'], -Q)
                self.assertTrue(result['rows'][0]['normal_return_reference'])

    def test_valid_drain_failure_stops_before_canrecover_and_reset_keeps_next_prefix(self):
        action = reconfigure(input_rate=4 * Q,
                             drain=tick('drain', request=recovery(setter_normal=False)), can_recover=rate())
        result = module.sp_recovery_clock_reference(payload(action, tick('later'), remaining=0)); row = result['rows'][0]
        self.assertIs(row['normal_return_reference'], False)
        self.assertIsNone(row['can_recover']); self.assertIsNone(row['period_reset'])
        self.assertEqual(row['period_after_raw_reference'], Q)
        self.assertEqual(row['remaining_after_raw_reference'], Q)
        self.assertFalse(result['rows'][1]['called_reference'])

    def test_canrecover_getter_failure_preserves_drained_timer_and_does_not_reset(self):
        for exists, normal in ((False, True), (True, False), (True, None)):
            action = reconfigure(drain=tick('drain'), can_recover=rate(exists=exists, normal=normal))
            with self.subTest(exists=exists, normal=normal):
                result = module.sp_recovery_clock_reference(payload(action, tick('later'))); row = result['rows'][0]
                self.assertIs(row['normal_return_reference'], False if exists is False else normal)
                self.assertIsNone(row['period_reset'])
                self.assertIs(result['rows'][1]['called_reference'], None if exists is True and normal is None else False)

    def test_tiny_unknown_or_unsafe_rate_does_not_invent_a_period_or_definite_arithmetic_failure(self):
        for input_rate in (1, -1, 2, -2, None):
            with self.subTest(input_rate=input_rate):
                result = module.sp_recovery_clock_reference(payload(reconfigure(input_rate=input_rate), period=0))
                self.assertIsNone(result['final_period_raw_reference'])
                self.assertIsNot(result['rows'][0]['normal_return_reference'], False)

    def test_general_safe_division_includes_small_rate_literals_below_epsilon(self):
        # The denominator-domain proof is broader than the prior ONE-only
        # epsilon domain. These integer quotients are inside signed64 FP.Max.
        for input_rate, period in ((3, 6148914691236517205),
                                   (42949, 429503459305445), (-42949, -429503459305445)):
            with self.subTest(input_rate=input_rate):
                result = module.sp_recovery_clock_reference(payload(reconfigure(input_rate=input_rate), period=0))
                self.assertEqual(result['final_period_raw_reference'], period)
                self.assertEqual(result['final_remaining_raw_reference'], period)
                self.assertTrue(result['rows'][0]['normal_return_reference'])

    def test_controller_and_timer_absence_are_separate_from_disabled_and_explicit_recovery(self):
        result = module.sp_recovery_clock_reference(payload(tick(enabled=False), controller=False))
        self.assertIs(result['rows'][0]['normal_return_reference'], False)
        result = module.sp_recovery_clock_reference(payload(tick(enabled=False), timer=False))
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        self.assertFalse(result['rows'][0]['tick']['delta_applied_reference'])
        for action in (tick(), reconfigure(input_rate=2 * Q)):
            result = module.sp_recovery_clock_reference(payload(action, timer=False))
            self.assertIs(result['rows'][0]['normal_return_reference'], False)
        data = payload(recover(request=recovery(5 * Q, force=True)), timer=False)
        data['precise_timer_identity'] = False; data['no_intervening_timer_changes'] = False
        result = module.sp_recovery_clock_reference(data)
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        self.assertEqual(result['rows'][0]['recovery']['setter_value_argument_raw_reference'], 6 * Q)
        self.assertIsNone(result['final_period_raw_reference'])

    def test_context_and_action_native_qualification_guard_actual_values(self):
        for key in ('precise_timer_identity', 'no_intervening_timer_changes'):
            for value in (False, None):
                data = payload(tick(delta=Q)); data[key] = value
                with self.subTest(key=key, value=value):
                    result = module.sp_recovery_clock_reference(data)
                    self.assertIsNone(result['rows'][0]['normal_return_reference'])
                    self.assertIsNone(result['final_remaining_raw_reference'])
        for native in (False, None):
            result = module.sp_recovery_clock_reference(payload(tick(native=native)))
            self.assertIsNone(result['rows'][0]['normal_return_reference'])

    def test_schema_rejects_unsupported_fields_raws_ids_triangles_and_force_natural_tick(self):
        mutations = [lambda p: p.update(extra=1), lambda p: p.update(controller_exists=1),
            lambda p: p.update(actions=[]), lambda p: p['timer'].update(period_raw=True),
            lambda p: p['timer'].update(remaining_raw=1 << 63),
            lambda p: p['actions'][0].update(delta_raw=.5), lambda p: p['actions'][0].update(id='\n'),
            lambda p: p['actions'][0].update(id='\ud800'), lambda p: p['actions'][0].update(enabled=1),
            lambda p: p['actions'][0].update(kind='attack'), lambda p: p['actions'][0].update(amount_raw=Q),
            lambda p: p['actions'][0]['full_read'].update(value=1),
            lambda p: p['actions'][0]['recovery'].update(force=True),
            lambda p: p['actions'][0]['recovery']['sp_read'].update(raw='1'),
            lambda p: p['actions'].append(deepcopy(p['actions'][0]))]
        for index, mutation in enumerate(mutations):
            data = payload(); mutation(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.sp_recovery_clock_reference(data)
            self.assertEqual(data, before)
        for drain in (recover('wrong'), tick('wrong', delta=Q)):
            with self.subTest(drain=drain), self.assertRaises(ValueError):
                module.sp_recovery_clock_reference(payload(reconfigure(drain=drain)))

    def test_bound_source50_methods2252_unique_and3518_spans_copy_and_invalid_guard(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(hashlib.sha256((ROOT / module.SOURCE).read_bytes()).hexdigest(), module.SOURCE_SHA256)
        for name, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        proof_path = next(name for name in source['source_artifacts_sha256'] if '274' in name and name.endswith('/source-proof.json'))
        proof = json.loads((ROOT / proof_path).read_text(encoding='utf8'))
        self.assertEqual(len(proof['methods']), 50); unique = {}
        for record in proof['methods']:
            self.assertTrue(record['cfg_bounded_traversal_finished']); self.assertFalse(record['limits'])
            raw = b''.join(bytes.fromhex(row['bytes']) for row in record['instructions'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['reachable_bytes_sha256'])
            unique.update({row['address']: row for row in record['instructions']})
        self.assertEqual(len(unique), 2252); self.assertEqual(len(proof['byte_spans']), 3518)
        self.assertFalse(proof['game_dll_executed']); self.assertFalse(proof['process_memory_read'])
        source['source_artifacts_sha256'].clear(); self.assertTrue(module.source_data()['source_artifacts_sha256'])
        with patch.object(module, '_source_data', return_value=None):
            result = module.sp_recovery_clock_reference(module.public_example())
        self.assertFalse(result['source_valid']); self.assertIsNone(result['rows'][0]['normal_return_reference'])
        self.assertIsNone(result['final_remaining_raw_reference'])

    def test_no_declared_request_is_actual_sp_recovery_skill_cycle_or_clock(self):
        result = module.sp_recovery_clock_reference(module.public_example())
        for field in ('actual_sp_after', 'actual_complete_recovery', 'actual_skill_cycle', 'actual_clock', 'actual_attribute_values'):
            self.assertIsNone(result[field])
        self.assertFalse(result['events_scheduled']); self.assertFalse(result['hotfix_equivalence_proven'])


if __name__ == '__main__':
    unittest.main()
