"""Independent literal and source-prefix acceptance for section276.

No protected value is decoded, no game state is sampled, and no
implementation arithmetic helper is used to construct expected values.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import sp_initialization_reference as module
from rouge import sp_recovery_clock as clock_module

ROOT = Path(module.__file__).resolve().parents[1]
Q = 4294967296


def int_read(identity, value, normal=True):
    return {'id': identity, 'normal': normal, 'value': value}


def opaque_read(identity, value, normal=True):
    return {'id': identity, 'normal': normal, 'payload_id': value}


def capacity(identity, cost=10, charges=2, *, normal=True, exists=True, native=True):
    decoded = {(10, 2): 20, (7, 3): 21, (-10, 3): -30,
               (2147483647, 2): -2, (65536, 65536): 0,
               (-2147483648, 1): -2147483648}[(cost, charges)]
    return {'id': identity, 'ordinary_native_path': native, 'sp_data_exists': exists,
            'cost_decode': int_read(identity + '-cost', cost),
            'charges_decode': int_read(identity + '-charges', charges),
            'max_encode_normally': True,
            'max_decode_read': int_read(identity + '-independent-decoded', decoded),
            'getter_returns_normally': normal}


def data(identity='data', *, exists=True):
    return {'exists': exists, 'sp_type_read': int_read(identity + '-type', 3),
            'sp_type_store_normally': True, 'cost_read': opaque_read(identity + '-cost', 'new-cost'),
            'cost_copy_normally': True,
            'increments_read': opaque_read(identity + '-increments', 'new-increments'),
            'increments_destination_exists': True, 'increments_length_read_normally': True,
            'increments_destination_length': 4, 'increments_copy_normally': True}


def reset(identity='reset', *, eligible=True, rate=4 * Q, data_exists=True):
    return {'id': identity, 'kind': 'reset', 'ordinary_native_path': True,
            'owner_id': 'new-owner', 'owner_write_normally': True,
            'data': data(identity + '-data', exists=data_exists),
            'can_recover_read': {'id': identity + '-eligible', 'exists': True, 'normal': True, 'value': eligible},
            'second_rate_read': {'id': identity + '-rate', 'exists': True, 'normal': True, 'raw': rate},
            'timer_call_returns_normally': True}


def update(identity='update', *, only_cost=False, eligible=True, rate=2 * Q):
    action = reset(identity, eligible=eligible, rate=rate)
    action.pop('owner_id'); action.pop('owner_write_normally')
    action.update(kind='update_data', only_update_sp_cost=only_cost)
    return action


def construct(identity='construct'):
    return {'id': identity, 'kind': 'construct', 'ordinary_native_path': True,
            'increments_allocate_normally': True, 'increments_assign_normally': True,
            'timer_allocate_normally': True, 'timer_constructor_normally': True,
            'timer_assign_normally': True, 'base_constructor_normally': True,
            'post_ctor_hotfix': {'present': False, 'returns_normally': True}}


def reset_timer(identity='reset-timer'):
    return {'id': identity, 'kind': 'reset_timer', 'ordinary_native_path': True,
            'timer_call_returns_normally': True}


def entity_init(identity='init', *, first_cost=10, first_charges=2, init_sp=30,
                second_cost=7, second_charges=3):
    return {'id': identity, 'kind': 'entity_init', 'ordinary_native_path': True,
            'first_max_read': capacity(identity + '-first', first_cost, first_charges),
            'init_sp_read': int_read(identity + '-initial', init_sp),
            'single_encoder_normally': True, 'sp_payload_copy_normally': True,
            'second_max_read': capacity(identity + '-second', second_cost, second_charges),
            'max_sp_write_normally': True, 'controller_reset': reset(identity + '-reset')}


def entity_update(identity='entity-update', *, only_cost=True, cost=7, charges=3):
    return {'id': identity, 'kind': 'entity_update', 'ordinary_native_path': True,
            'max_read': capacity(identity + '-capacity', cost, charges), 'max_sp_write_normally': True,
            'controller_update': update(identity + '-controller', only_cost=only_cost)}


def payload(*actions, period=Q // 4, remaining=Q // 8, timer_exists=True):
    return {'entity_exists': True, 'controller_exists': True, 'precise_timer_identity': True,
            'no_intervening_state_changes': True,
            'state': {'owner_id': 'old-owner', 'sp_type': 1, 'cost_payload_id': 'old-cost',
                      'increments_payload_id': 'old-increments', 'max_sp': 10,
                      'timer': {'exists': timer_exists, 'period_raw': period, 'remaining_raw': remaining}},
            'actions': list(actions) or [reset()]}


def report(action, **state):
    return module.sp_initialization_reference(payload(action, **state))


def row(action, **state):
    return report(action, **state)['rows'][0]


def stage(actual, name):
    matches = [entry for entry in actual['stages'] if entry['name'] == name]
    # The contract lists only a completed/attempted prefix. No later stage
    # entry is needed after a definite return/failure; an unknown prefix does
    # not certify that a later native call never happens.
    if not matches:
        return {'name': name, 'called_reference': None if actual['normal_return_reference'] is None else False,
                'normal_return_reference': None}
    if len(matches) != 1:
        raise AssertionError((name, [entry['name'] for entry in actual['stages']]))
    return matches[0]


def link(identity, *, controller=True, precise=True, unchanged=True, actions=None):
    return {'after_action_id': identity, 'controller_exists': controller,
            'precise_timer_identity': precise, 'no_intervening_timer_changes': unchanged,
            'actions': deepcopy(clock_module.public_example()['actions']) if actions is None else actions}


class SpInitializationReferenceTests(unittest.TestCase):
    def test_signed32_capacity_wrap_literals_do_not_saturate_or_impose_positive_cost(self):
        for cost, charges, expected in ((10, 2, 20), (-10, 3, -30), (0, 2147483647, 0),
                                        (2147483647, 2, -2), (65536, 65536, 0),
                                        (-2147483648, -1, -2147483648),
                                        (2147483647, -1, -2147483647)):
            with self.subTest(cost=cost, charges=charges):
                actual = module.max_sp_reference(cost, charges)
                self.assertTrue(actual['source_valid'])
                self.assertEqual(actual['signed32_product_reference'], expected)

    def test_capacity_unknown_typed_zero_closes_but_unknown_nonzero_does_not(self):
        for cost, charges, expected in ((0, None, 0), (None, 0, 0),
                                        (None, 2, None), (10, None, None), (None, None, None)):
            with self.subTest(cost=cost, charges=charges):
                self.assertEqual(module.max_sp_reference(cost, charges)['signed32_product_reference'], expected)

    def test_exact_single_small_negative_and_large_power_literals_have_exact_constructor_arguments(self):
        for value, expected in ((0, 0), (1, 4294967296), (-1, -4294967296),
                                 (-30, -128849018880), (20, 85899345920),
                                 (16777216, 72057594037927936), (16777218, 72057602627862528),
                                 (1073741824, 4611686018427387904),
                                 (-2147483648, -9223372036854775808)):
            with self.subTest(value=value):
                actual = module.initial_single_reference(value, value)
                self.assertEqual(actual['signed_min_reference'], value)
                self.assertTrue(actual['single_exact_reference'])
                self.assertTrue(actual['scaled_signed64_eligible_reference'])
                self.assertEqual(actual['encoder_constructor_argument_raw_reference'], expected)
                self.assertIsNone(actual['actual_initial_sp'])

    def test_nonrepresentable_large_single_without_mxcsr_stays_unknown_not_nearest_even(self):
        for value in (16777217, -16777217, 2147483647):
            with self.subTest(value=value):
                actual = module.initial_single_reference(value, value)
                self.assertEqual(actual['signed_min_reference'], value)
                self.assertFalse(actual['single_exact_reference'])
                self.assertIsNone(actual['encoder_constructor_argument_raw_reference'])
                self.assertIsNone(actual['actual_initial_sp'])

    def test_signed_min_above_below_equal_and_negative_never_applies_zero_clamp(self):
        for first, initial, expected, raw in ((20, 30, 20, 85899345920), (20, 10, 10, 42949672960),
                                             (20, 20, 20, 85899345920), (20, -5, -5, -21474836480),
                                             (-10, 5, -10, -42949672960), (-10, -20, -20, -85899345920)):
            with self.subTest(first=first, initial=initial):
                actual = module.initial_single_reference(first, initial)
                self.assertEqual(actual['signed_min_reference'], expected)
                self.assertEqual(actual['encoder_constructor_argument_raw_reference'], raw)

    def test_signed_min_unknown_extreme_closure_never_bypasses_read_normality(self):
        for first, initial, expected in ((-2147483648, None, -2147483648),
                                         (None, -2147483648, -2147483648),
                                         (20, None, None), (None, 20, None), (None, None, None)):
            with self.subTest(first=first, initial=initial):
                self.assertEqual(module.initial_single_reference(first, initial)['signed_min_reference'], expected)
        action = entity_init(first_cost=-2147483648, first_charges=1, init_sp=None)
        action['init_sp_read']['normal'] = False
        actual = row(action)
        self.assertIs(actual['normal_return_reference'], False)
        self.assertEqual(actual['known_prefix_state_reference']['max_sp'], 10)
        self.assertFalse(stage(actual, 'single_encoder')['called_reference'])
        self.assertFalse(stage(actual, 'second_max.sp_data_access')['called_reference'])

    def test_constructor_zero_zero_differs_from_markinvalid_and_preserves_unwritten_owner_type_cost(self):
        result = report(construct()); actual = result['rows'][0]
        self.assertTrue(actual['normal_return_reference'])
        self.assertEqual(result['state_after_reference']['timer'],
                         {'exists': True, 'period_raw': 0, 'remaining_raw': 0})
        self.assertEqual(result['state_after_reference']['owner_id'], 'old-owner')
        self.assertEqual(result['state_after_reference']['sp_type'], 1)
        self.assertEqual(result['state_after_reference']['cost_payload_id'], 'old-cost')
        invalid = report(reset(eligible=False))['state_after_reference']['timer']
        self.assertEqual((invalid['period_raw'], invalid['remaining_raw']), (-Q, -Q))
        constructed = report(construct())['rows'][0]
        self.assertEqual(stage(constructed, 'construct.timer_constructor')['value_reference'],
                         {'period_raw': 0, 'remaining_raw': 0})

    def test_constructor_allocation_assignment_and_base_failures_preserve_completed_prefix(self):
        for field in ('increments_allocate_normally', 'increments_assign_normally',
                      'timer_allocate_normally', 'timer_constructor_normally',
                      'timer_assign_normally', 'base_constructor_normally'):
            for normal in (False, None):
                with self.subTest(field=field, normal=normal):
                    action = construct(); action[field] = normal
                    actual = row(action)
                    self.assertIs(actual['normal_return_reference'], normal)
                    self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'old-owner')
                    self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'old-cost')
                    if field == 'base_constructor_normally':
                        self.assertEqual(actual['known_prefix_state_reference']['timer']['period_raw'], 0)
                        self.assertEqual(actual['known_prefix_state_reference']['timer']['remaining_raw'], 0)

    def test_constructor_unknown_pointer_assignment_and_callback_effects_do_not_create_known_after_state(self):
        for normal in (False, None):
            action = construct(); action['timer_assign_normally'] = normal
            actual = row(action, timer_exists=False, period=None, remaining=None)
            self.assertIs(actual['normal_return_reference'], normal)
            self.assertIs(actual['known_prefix_state_reference']['timer']['exists'], False)
            self.assertIsNone(actual['state_after_reference']['timer']['exists'])
            self.assertIsNone(actual['state_after_reference']['timer']['period_raw'])
            self.assertIsNone(actual['state_after_reference']['timer']['remaining_raw'])
        for present in (True, None):
            action = construct(); action['post_ctor_hotfix'] = {'present': present, 'returns_normally': True}
            result = report(action)
            actual = result['rows'][0]
            self.assertIs(actual['normal_return_reference'], True)
            self.assertEqual(actual['known_prefix_state_reference']['timer'],
                             {'exists': True, 'period_raw': 0, 'remaining_raw': 0})
            self.assertIsNone(actual['state_after_reference']['timer']['exists'])
            self.assertIsNone(actual['state_after_reference']['owner_id'])
            self.assertIsNone(actual['state_after_reference']['cost_payload_id'])
            linked = module.natural_clock_link(result, link('construct'))
            self.assertFalse(linked['qualified_reference'])
            self.assertIsNone(linked['request'])

    def test_reset_timer_waitfirst_uses_current_period_even_zero_negative_and_no_rate_reads(self):
        for period in (Q // 4, 0, -Q, 42950):
            with self.subTest(period=period):
                result = report(reset_timer(), period=period, remaining=7 * Q)
                self.assertTrue(result['rows'][0]['normal_return_reference'])
                self.assertEqual(result['state_after_reference']['timer']['period_raw'], period)
                self.assertEqual(result['state_after_reference']['timer']['remaining_raw'], period)
                self.assertEqual(result['state_after_reference']['owner_id'], 'old-owner')
                self.assertEqual(result['state_after_reference']['cost_payload_id'], 'old-cost')
                self.assertEqual(result['rows'][0]['capacity_reads'], [])
                self.assertTrue(stage(result['rows'][0], 'periodic_reset_current')['called_reference'])

    def test_reset_timer_missing_timer_and_abnormal_call_cannot_claim_completion(self):
        for timer_exists in (False, None):
            actual = row(reset_timer(), timer_exists=timer_exists)
            self.assertIs(actual['normal_return_reference'], False if timer_exists is False else None)
        for normal in (False, None):
            action = reset_timer(); action['timer_call_returns_normally'] = normal
            self.assertIs(row(action)['normal_return_reference'], normal)

    def test_reset_owner_write_precedes_missing_data_check(self):
        actual = row(reset(data_exists=False))
        self.assertIs(actual['normal_return_reference'], False)
        self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'new-owner')
        self.assertEqual(actual['known_prefix_state_reference']['sp_type'], 1)
        self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'old-cost')
        self.assertEqual(actual['known_prefix_state_reference']['timer']['period_raw'], Q // 4)
        self.assertTrue(stage(actual, 'owner_write')['normal_return_reference'])
        self.assertFalse(stage(actual, 'cost_read')['called_reference'])

    def test_reset_type_and_cost_failures_keep_prior_completed_owner_type_prefix(self):
        for field in ('sp_type_store_normally', 'cost_copy_normally'):
            for normal in (False, None):
                action = reset(); action['data'][field] = normal
                with self.subTest(field=field, normal=normal):
                    actual = row(action)
                    self.assertIs(actual['normal_return_reference'], normal)
                    self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'new-owner')
                    if field == 'cost_copy_normally':
                        self.assertEqual(actual['known_prefix_state_reference']['sp_type'], 3)
                    self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'old-cost')

    def test_failed_or_unknown_array_copy_retains_cost_prefix_without_partial_elements(self):
        for normal in (False, None):
            action = reset(); action['data']['increments_copy_normally'] = normal
            actual = row(action)
            self.assertIs(actual['normal_return_reference'], normal)
            self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'new-owner')
            self.assertEqual(actual['known_prefix_state_reference']['sp_type'], 3)
            self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'new-cost')
            self.assertEqual(actual['known_prefix_state_reference']['timer']['remaining_raw'], Q // 8)
            self.assertIs(stage(actual, 'can_recover_read')['called_reference'], False if normal is False else None)

    def test_reset_eligibility_false_marks_invalid_without_borrowing_second_rate(self):
        action = reset(eligible=False, rate=4 * Q)
        action['second_rate_read']['normal'] = False
        result = report(action)
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        timer = result['state_after_reference']['timer']
        self.assertEqual((timer['period_raw'], timer['remaining_raw']), (-Q, -Q))
        self.assertFalse(stage(result['rows'][0], 'second_rate_read')['called_reference'])
        self.assertTrue(stage(result['rows'][0], 'timer_mark_invalid')['called_reference'])

    def test_reset_eligible_true_second_rate_changes_zero_negative_and_tiny_division_domain(self):
        for rate, expected in ((4 * Q, 1073741824), (2 * Q, 2147483648),
                                (0, 0), (-2 * Q, 0),
                                (3, 6148914691236517205), (42949, 429503459305445)):
            with self.subTest(rate=rate):
                result = report(reset(eligible=True, rate=rate))
                self.assertTrue(result['rows'][0]['normal_return_reference'])
                timer = result['state_after_reference']['timer']
                self.assertEqual((timer['period_raw'], timer['remaining_raw']), (expected, expected))
                self.assertTrue(stage(result['rows'][0], 'periodic_reset')['called_reference'])
                self.assertFalse(stage(result['rows'][0], 'timer_mark_invalid')['called_reference'])
        for rate in (1, -1, 2, -2, None):
            with self.subTest(unsafe_or_unknown_rate=rate):
                result = report(reset(rate=rate))
                self.assertIsNone(result['state_after_reference']['timer']['period_raw'])
                self.assertIsNone(result['state_after_reference']['timer']['remaining_raw'])
                self.assertIsNot(result['rows'][0]['normal_return_reference'], False)

    def test_eligibility_read_and_second_rate_failures_preserve_all_copied_data(self):
        for read_name in ('can_recover_read', 'second_rate_read'):
            for field in ('normal', 'exists'):
                for normal in (False, None):
                    action = reset(); action[read_name][field] = normal
                    with self.subTest(read_name=read_name, field=field, normal=normal):
                        actual = row(action)
                        self.assertIs(actual['normal_return_reference'], normal)
                        self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'new-cost')
                        self.assertEqual(actual['known_prefix_state_reference']['increments_payload_id'], 'new-increments')
                        self.assertEqual(actual['known_prefix_state_reference']['timer']['period_raw'], Q // 4)

    def test_reset_timer_call_failure_does_not_undo_data_prefix_or_assert_actual_timer(self):
        for normal in (False, None):
            action = reset(); action['timer_call_returns_normally'] = normal
            actual = row(action)
            self.assertIs(actual['normal_return_reference'], normal)
            self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'new-owner')
            self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'new-cost')
            self.assertEqual(actual['known_prefix_state_reference']['increments_payload_id'], 'new-increments')

    def test_only_cost_true_does_not_read_type_array_owner_rate_or_timer(self):
        action = update(only_cost=True)
        action['data']['sp_type_read']['normal'] = False
        action['data']['sp_type_store_normally'] = False
        action['data']['increments_read']['normal'] = False
        action['data']['increments_copy_normally'] = False
        action['can_recover_read']['exists'] = False
        action['second_rate_read']['normal'] = False
        action['timer_call_returns_normally'] = False
        result = report(action, timer_exists=False)
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        state = result['state_after_reference']
        self.assertEqual(state['cost_payload_id'], 'new-cost')
        self.assertEqual(state['owner_id'], 'old-owner'); self.assertEqual(state['sp_type'], 1)
        self.assertEqual(state['increments_payload_id'], 'old-increments')
        self.assertEqual(state['timer'], {'exists': False, 'period_raw': Q // 4, 'remaining_raw': Q // 8})
        for name in ('sp_type_read', 'increments_read', 'can_recover_read', 'second_rate_read', 'timer_access'):
            self.assertFalse(stage(result['rows'][0], name)['called_reference'])

    def test_only_cost_unknown_merges_native_paths_without_losing_completed_cost(self):
        result = report(update(only_cost=None))
        actual = result['rows'][0]
        self.assertTrue(actual['normal_return_reference'])
        self.assertEqual(result['state_after_reference']['cost_payload_id'], 'new-cost')
        self.assertEqual(result['state_after_reference']['owner_id'], 'old-owner')
        self.assertIsNone(result['state_after_reference']['sp_type'])
        self.assertIsNone(result['state_after_reference']['increments_payload_id'])
        self.assertIsNone(result['state_after_reference']['timer']['period_raw'])
        self.assertIsNone(result['state_after_reference']['timer']['remaining_raw'])
        self.assertEqual(len(actual['conditional_branches']), 2)

    def test_full_update_keeps_past_time_without_274_drain_or_sp_request(self):
        result = report(update(rate=2 * Q), period=Q // 4, remaining=Q // 8)
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        state = result['state_after_reference']
        self.assertEqual(state['timer']['period_raw'], 2147483648)
        self.assertEqual(state['timer']['remaining_raw'], 1610612736)
        self.assertEqual(state['owner_id'], 'old-owner')
        self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])
        self.assertNotIn('drain', result['rows'][0])

    def test_keep_past_direct_period_write_and_lower_clamp_do_not_borrow_274_invalid_restart(self):
        for old_period, old_remaining, rate, expected_period, expected_remaining in (
                (Q, Q // 4, 4 * Q, Q // 4, 0),
                (0, -9 * Q, 2 * Q, Q // 2, 0),
                (-Q, 4 * Q, 2 * Q, Q // 2, 11 * Q // 2),
                (Q // 4, Q // 8, 0, -Q, 0),
                (Q // 4, Q, 2 * Q, Q // 2, 5 * Q // 4)):
            with self.subTest(old_period=old_period, old_remaining=old_remaining, rate=rate):
                result = report(update(rate=rate), period=old_period, remaining=old_remaining)
                state = result['state_after_reference']['timer']
                self.assertEqual((state['period_raw'], state['remaining_raw']), (expected_period, expected_remaining))

    def test_entity_update_max_write_precedes_even_only_cost_or_missing_controller(self):
        result = report(entity_update(only_cost=True))
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        self.assertEqual(result['state_after_reference']['max_sp'], 21)
        self.assertEqual(result['state_after_reference']['cost_payload_id'], 'new-cost')
        self.assertEqual(result['state_after_reference']['sp_type'], 1)
        self.assertEqual(result['state_after_reference']['timer']['remaining_raw'], Q // 8)
        declaration = payload(entity_update()); declaration['controller_exists'] = False
        actual = module.sp_initialization_reference(declaration)['rows'][0]
        self.assertIs(actual['normal_return_reference'], False)
        self.assertEqual(actual['known_prefix_state_reference']['max_sp'], 21)
        self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'old-cost')
        for normal in (False, None):
            action = entity_update()
            action['controller_update']['data']['cost_read']['normal'] = normal
            actual = row(action)
            self.assertIs(actual['normal_return_reference'], normal)
            self.assertEqual(actual['known_prefix_state_reference']['max_sp'], 21)
            self.assertEqual(actual['known_prefix_state_reference']['cost_payload_id'], 'old-cost')
            self.assertEqual(actual['known_prefix_state_reference']['sp_type'], 1)

    def test_entity_init_uses_two_independent_capacities_and_direct_signed_initial_prefix(self):
        for init_sp, expected_raw in ((30, 85899345920), (10, 42949672960), (-5, -21474836480)):
            with self.subTest(init_sp=init_sp):
                result = report(entity_init(init_sp=init_sp))
                actual = result['rows'][0]
                self.assertTrue(actual['normal_return_reference'])
                self.assertEqual(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'], expected_raw)
                self.assertEqual(result['state_after_reference']['max_sp'], 21)
                self.assertEqual(result['state_after_reference']['timer']['remaining_raw'], Q // 4)
                reads = actual['capacity_reads']
                self.assertEqual([entry['read_id'] for entry in reads], ['init-first', 'init-second'])
                self.assertEqual([entry['returned_max_sp_reference'] for entry in reads], [20, 21])
                self.assertTrue(actual['initial_sp_prefix']['sp_payload_copy_normal_reference'])
                self.assertEqual(actual['initial_sp_prefix']['copied_byte_count_reference'], 40)
                self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])

    def test_negative_and_wrapped_first_capacity_can_cap_initial_sp_below_zero(self):
        for cost, charges, expected, raw in ((-10, 3, -30, -128849018880),
                                             (2147483647, 2, -2, -8589934592),
                                             (65536, 65536, 0, 0)):
            with self.subTest(cost=cost, charges=charges):
                actual = row(entity_init(first_cost=cost, first_charges=charges, init_sp=5))
                self.assertEqual(actual['initial_sp_prefix']['signed_min_reference'], expected)
                self.assertEqual(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'], raw)
                self.assertEqual(actual['state_after_reference']['max_sp'], 21)

    def test_first_capacity_and_initial_decode_failure_cannot_reach_encoder_or_second_capacity(self):
        for location, field in ((('first_max_read',), 'getter_returns_normally'),
                                (('first_max_read',), 'max_encode_normally'),
                                (('first_max_read', 'max_decode_read'), 'normal'),
                                (('first_max_read', 'cost_decode'), 'normal'),
                                (('first_max_read', 'charges_decode'), 'normal'),
                                (('init_sp_read',), 'normal')):
            for normal in (False, None):
                with self.subTest(location=location, field=field, normal=normal):
                    action = entity_init(); target = action
                    for key in location: target = target[key]
                    target[field] = normal
                    actual = row(action)
                    self.assertIs(actual['normal_return_reference'], normal)
                    self.assertEqual(actual['known_prefix_state_reference']['max_sp'], 10)
                    self.assertIs(stage(actual, 'single_encoder')['called_reference'], False if normal is False else None)
                    self.assertIs(stage(actual, 'second_max.sp_data_access')['called_reference'], False if normal is False else None)

    def test_initial_encoder_and_opaque_copy_failure_do_not_perform_second_max_write(self):
        for field in ('single_encoder_normally', 'sp_payload_copy_normally'):
            for normal in (False, None):
                with self.subTest(field=field, normal=normal):
                    action = entity_init(); action[field] = normal
                    actual = row(action)
                    self.assertIs(actual['normal_return_reference'], normal)
                    self.assertEqual(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'], 85899345920)
                    self.assertEqual(actual['known_prefix_state_reference']['max_sp'], 10)
                    self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'old-owner')
                    self.assertIs(stage(actual, 'second_max.sp_data_access')['called_reference'], False if normal is False else None)

    def test_second_capacity_or_max_write_failure_keeps_initial_prefix_but_no_controller_reset(self):
        for location, field in (('second_max_read', 'getter_returns_normally'),
                                ('second_max_read', 'max_encode_normally'),
                                ('second_max_read.max_decode_read', 'normal'),
                                (None, 'max_sp_write_normally')):
            for normal in (False, None):
                action = entity_init()
                if location is None: action[field] = normal
                else:
                    target=action
                    for key in location.split('.'):target=target[key]
                    target[field] = normal
                with self.subTest(location=location, field=field, normal=normal):
                    result = report(action); actual = result['rows'][0]
                    self.assertIs(actual['normal_return_reference'], normal)
                    self.assertEqual(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'], 85899345920)
                    self.assertEqual(actual['known_prefix_state_reference']['owner_id'], 'old-owner')
                    self.assertEqual(actual['initial_sp_prefix']['copied_byte_count_reference'], 40)
                    self.assertIs(stage(actual, 'controller_reset.owner_write')['called_reference'], False if normal is False else None)
                    self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])

    def test_normal_failure_stops_next_action_and_unknown_normality_does_not_complete_it(self):
        for normal in (False, None):
            first = reset(); first['data']['cost_copy_normally'] = normal
            result = module.sp_initialization_reference(payload(first, reset_timer('later')))
            self.assertIs(result['rows'][0]['normal_return_reference'], normal)
            self.assertIs(result['rows'][1]['called_reference'], False if normal is False else None)
            self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])

    def test_native_and_instance_qualification_remain_distinct_from_read_values(self):
        for flag in ('entity_exists', 'controller_exists'):
            declaration = payload(entity_init()); declaration[flag] = False
            result = module.sp_initialization_reference(declaration)
            self.assertIs(result['rows'][0]['normal_return_reference'], False)
            self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])
        for native in (False, None):
            action = entity_init(); action['ordinary_native_path'] = native
            actual = row(action)
            self.assertIsNone(actual['normal_return_reference'])
            self.assertIsNone(actual['initial_sp_prefix'])

    def test_source_inventory_primary_signatures_hashes_and_deepcopy_are_bound(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(source['method_count'], 47)
        self.assertEqual(source['unique_instruction_count'], 4866)
        self.assertEqual(source['byte_span_count'], 6351)
        self.assertEqual(len(source['methods']), 47)
        self.assertEqual(len(source['byte_spans']), 6351)
        self.assertTrue(source['all_spans_rechecked_against_fresh_primary_files'])
        indices = {entry['method']['metadata_method_index'] for entry in source['methods']}
        self.assertTrue({32849, 32862, 66624, 66442, 66606, 66745, 66746, 66747, 66753,
                         25983, 25984, 220443, 237419, 237420}.issubset(indices))
        for name, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        source['methods'].clear(); source['source_facts']['init_bypasses_public_setter'] = 'mutated'
        again = module.source_data(); self.assertEqual(len(again['methods']), 47)
        self.assertNotEqual(again['source_facts']['init_bypasses_public_setter'], 'mutated')

    def test_input_and_public_example_deepcopy_actual_state_and_cycle_always_unknown(self):
        declaration = module.public_example(); before = deepcopy(declaration)
        result = module.sp_initialization_reference(declaration)
        self.assertEqual(declaration, before)
        self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])
        self.assertTrue(result['source_valid'])
        result['declared_initial_state']['timer']['period_raw'] = -123
        self.assertEqual(declaration, before)
        declaration['actions'].clear()
        self.assertGreater(len(module.public_example()['actions']), 0)

    def test_missing_bound_source_cannot_produce_numeric_prefix_or_qualified_clock_request(self):
        declaration = payload(entity_init()); before = deepcopy(declaration)
        with patch.object(module, '_source_data', return_value=None):
            result = module.sp_initialization_reference(declaration)
            self.assertFalse(result['source_valid'])
            self.assertIsNone(result['rows'][0]['called_reference'])
            self.assertIsNone(result['rows'][0]['normal_return_reference'])
            self.assertIsNone(result['rows'][0]['initial_sp_prefix'])
            self.assertIsNone(result['state_after_reference']['max_sp'])
            self.assertIsNone(module.max_sp_reference(10, 2)['signed32_product_reference'])
            self.assertIsNone(module.initial_single_reference(20, 30)['encoder_constructor_argument_raw_reference'])
            linked = module.natural_clock_link(result, link('init'))
            self.assertFalse(linked['source_valid']); self.assertFalse(linked['qualified_reference'])
            self.assertIsNone(linked['request'])
            self.assertIsNone(result['actual_current_sp']); self.assertIsNone(result['complete_cycle'])
        self.assertEqual(declaration, before)

    def test_schema_rejects_misleading_fields_duplicate_reads_bad_numeric_types_and_cardinality(self):
        declarations = []
        extra = payload(); extra['alive'] = True; declarations.append(extra)
        extra = payload(); extra['state']['actual_sp'] = 5; declarations.append(extra)
        extra = payload(entity_init()); extra['actions'][0]['second_max_read']['id'] = 'init-first'; declarations.append(extra)
        extra = payload(reset()); extra['actions'][0]['second_rate_read']['id'] = 'reset-eligible'; declarations.append(extra)
        for bad in (True, 2147483648, -2147483649, 1.5):
            extra = payload(entity_init()); extra['actions'][0]['init_sp_read']['value'] = bad; declarations.append(extra)
        for bad in (True, 9223372036854775808, -9223372036854775809, 1.5):
            extra = payload(); extra['state']['timer']['period_raw'] = bad; declarations.append(extra)
        for bad in ('true', 1, [], {}):
            extra = payload(); extra['controller_exists'] = bad; declarations.append(extra)
        extra = payload(); extra['actions'] = []; declarations.append(extra)
        extra = payload(); extra['actions'] = [reset_timer('op' + str(i)) for i in range(51)]; declarations.append(extra)
        extra = payload(); extra['actions'][0]['id'] = 'bad\nlabel'; declarations.append(extra)
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                before = deepcopy(declaration)
                with self.assertRaises(ValueError): module.sp_initialization_reference(declaration)
                self.assertEqual(declaration, before)
        for bad in (True, 2147483648, -2147483649, 1.25):
            with self.subTest(helper_argument=bad):
                with self.assertRaises(ValueError): module.max_sp_reference(bad, 1)
                with self.assertRaises(ValueError): module.initial_single_reference(20, bad)

    def test_clock_link_selects_normal_row_snapshot_without_replacing_other_requests_or_running_engine(self):
        declaration = payload(construct(), reset()); before = deepcopy(declaration)
        result = module.sp_initialization_reference(declaration); old_report = deepcopy(result)
        clock = clock_module.public_example(); old_clock = deepcopy(clock)
        binding = link('construct', actions=clock['actions']); old_binding = deepcopy(binding)
        with patch.object(clock_module, 'sp_recovery_clock_reference', side_effect=AssertionError('link must not execute clock')):
            linked = module.natural_clock_link(result, binding)
        self.assertTrue(linked['qualified_reference']); self.assertTrue(linked['source_valid'])
        request = linked['request']
        self.assertEqual(request['timer'], {'exists': True, 'period_raw': 0, 'remaining_raw': 0})
        self.assertNotEqual(request['timer'], result['state_after_reference']['timer'])
        self.assertEqual(request['actions'], clock['actions'])
        self.assertIsNone(linked['actual_clock']); self.assertIsNone(linked['complete_cycle'])
        self.assertEqual(result, old_report); self.assertEqual(clock, old_clock)
        self.assertEqual(binding, old_binding); self.assertEqual(declaration, before)
        request['actions'][0]['enabled'] = False
        self.assertEqual(clock, old_clock); self.assertEqual(result, old_report)

    def test_clock_link_requires_independent_identity_and_normal_timer_snapshot_and_strict_schema(self):
        result = report(reset_timer())
        for flag in ('controller_exists', 'precise_timer_identity', 'no_intervening_timer_changes'):
            for qualification in (False, None):
                binding = link('reset-timer'); binding[flag] = qualification
                with self.subTest(flag=flag, qualification=qualification):
                    linked = module.natural_clock_link(result, binding)
                    self.assertFalse(linked['qualified_reference'])
                    self.assertIsNone(linked['request'])
                    self.assertIsNone(linked['actual_clock']); self.assertIsNone(linked['complete_cycle'])
        action = reset_timer(); action['timer_call_returns_normally'] = False
        linked = module.natural_clock_link(report(action), link('reset-timer'))
        self.assertFalse(linked['qualified_reference']); self.assertIsNone(linked['request'])
        bindings = [link('absent'), {**link('reset-timer'), 'actual_sp': 0}]
        invalid_clock = clock_module.public_example()['actions']; invalid_clock[0]['recovery']['force'] = True
        bindings.append(link('reset-timer', actions=invalid_clock))
        for binding in bindings:
            with self.subTest(binding=binding):
                with self.assertRaises(ValueError): module.natural_clock_link(result, binding)


class InitializationQualificationRegressionTests(unittest.TestCase):
    def test_unknown_initial_encoder_does_not_claim_next_copy_uncalled(self):
        for normal in (False,None,True):
            action=entity_init();action['single_encoder_normally']=normal
            actual=row(action)['initial_sp_prefix']
            self.assertIs(actual['sp_payload_copy_called_reference'],normal)
            self.assertIs(actual['copied_byte_count_reference'],40 if normal is True else None)

    def test_unknown_constructor_prefix_does_not_fix_final_timer_pointer(self):
        for field in ('increments_allocate_normally', 'increments_assign_normally',
                      'timer_allocate_normally', 'timer_constructor_normally'):
            action=construct(); action[field]=None
            actual=report(action,timer_exists=False)['rows'][0]
            with self.subTest(field=field):
                self.assertIsNone(actual['state_after_reference']['timer']['exists'])
                self.assertFalse(actual['known_prefix_state_reference']['timer']['exists'])
                self.assertIsNone(actual['normal_return_reference'])

    def test_later_unqualified_construct_cannot_keep_old_pointer_certainty(self):
        first=reset();first['data']['cost_copy_normally']=None
        actual=module.sp_initialization_reference(payload(first,construct('later')))
        self.assertIsNone(actual['rows'][1]['called_reference'])
        self.assertIsNone(actual['state_after_reference']['timer']['exists'])

    def test_capacity_future_calls_distinguish_failed_and_unknown_decode(self):
        future=('charges_decode_called_reference','max_encode_called_reference',
                'getter_return_called_reference','max_decode_called_reference')
        for normal in (False,None):
            action=entity_init(); action['first_max_read']['cost_decode']['normal']=normal
            actual=row(action)['capacity_reads'][0]
            self.assertTrue(actual['cost_decode_called_reference'])
            for key in future:self.assertIs(actual[key],False if normal is False else None)
        action=entity_init();action['first_max_read']['ordinary_native_path']=None
        actual=row(action)['capacity_reads'][0]
        for key in ('cost_decode_called_reference',*future):self.assertIsNone(actual[key])

    def test_independent_decode_can_differ_from_both_products(self):
        action=entity_init()
        action['first_max_read']['max_decode_read']['value']=11
        action['second_max_read']['max_decode_read']['value']=-9
        actual=row(action)
        self.assertEqual([r['signed32_product_reference'] for r in actual['capacity_reads']],[20,21])
        self.assertEqual([r['returned_max_sp_reference'] for r in actual['capacity_reads']],[11,-9])
        self.assertEqual(actual['initial_sp_prefix']['signed_min_reference'],11)
        self.assertEqual(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'],47244640256)
        self.assertEqual(actual['state_after_reference']['max_sp'],-9)
        for r in actual['capacity_reads']:self.assertIsNone(r['roundtrip_equality_reference'])

    def test_getter_failure_or_unknown_is_before_independent_outer_decode(self):
        for normal in (False,None):
            action=entity_init();action['first_max_read']['getter_returns_normally']=normal
            actual=row(action)['capacity_reads'][0]
            self.assertTrue(actual['getter_return_called_reference'])
            self.assertIs(actual['max_decode_called_reference'],False if normal is False else None)
            self.assertIsNone(actual['returned_max_sp_reference'])

    def test_normal_decode_with_unobserved_value_does_not_reuse_product(self):
        action=entity_init();action['first_max_read']['max_decode_read']['value']=None
        actual=row(action)
        self.assertEqual(actual['capacity_reads'][0]['signed32_product_reference'],20)
        self.assertIsNone(actual['capacity_reads'][0]['returned_max_sp_reference'])
        self.assertIsNone(actual['initial_sp_prefix']['encoder_constructor_argument_raw_reference'])
        invalid=entity_init();invalid['first_max_read']['max_decode_read']['value']=True
        with self.assertRaises(ValueError):report(invalid)
        invalid=entity_init();invalid['first_max_read']['max_decode_read']['id']='init-first-cost'
        with self.assertRaises(ValueError):report(invalid)


if __name__ == '__main__':
    unittest.main()
