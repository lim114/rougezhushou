"""Independent source-bound literal controls for the fixed section277 API.

No actor cost/clock/SP data is obtained from the game. No model implementation
is copied into this test: expected arithmetic is literal signed-integer data.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in (HERE, *HERE.parents) if (path / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
MODULE_FILE = ROOT / 'rouge/skill_sp_cost_reference.py'

ADMISSION_STAGES = ('owner_read', 'unity_null_read', 'first_min_read', 'free_read',
                    'sp_owner_read', 'sp_read', 'decoded_cost_read', 'second_min_read', 'ge_comparison')
REDUCE_STAGES = ('free_read', 'skip_virtual_read', 'newsp_owner_read', 'newsp_call',
                 'apply_owner_read', 'modifier_copy', 'apply_call')
ACTUAL_UNKNOWNS = ('actual_owner_sp_after', 'actual_cost_paid', 'actual_cast_success', 'complete_cycle')


def read_bool(label, value=False, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def read_int(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def read_owner(label, identity='public-owner', exists=True, normal=True):
    return {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}


def admission(label='gate', first_min=-1, second_min=5, decoded_cost=5, sp_raw=21474836480):
    return {'id': label, 'kind': 'admission', 'ordinary_native_path': True,
        'owner_read': read_owner(label + '.raw-owner', 'initial-owner'),
        'unity_null_read': read_bool(label + '.unity', False),
        'first_min_read': read_int(label + '.first-min', first_min),
        'free_read': read_bool(label + '.free', False),
        'sp_owner_read': read_owner(label + '.getter-owner', 'SP-getter-owner'),
        'sp_read': {'id': label + '.sp', 'normal': True, 'raw': sp_raw},
        'decoded_cost_read': read_int(label + '.decoded-cost', decoded_cost),
        'second_min_read': read_int(label + '.second-min', second_min)}


def reduce(label='debit', delta=20):
    return {'id': label, 'kind': 'reduce', 'ordinary_native_path': True, 'delta': delta,
        'free_read': read_bool(label + '.free', False),
        'skip_virtual_read': read_bool(label + '.virtual-skip', False),
        'newsp_owner_read': read_owner(label + '.first-owner', 'NewSp-owner'),
        'newsp_ordinary_native_path': True, 'newsp_returns_normally': True,
        'returned_modifier_identity': 'opaque-public-modifier',
        'modifier_copy_returns_normally': True,
        'apply_owner_read': read_owner(label + '.second-owner', 'Apply-owner'),
        'apply_returns_normally': True, 'apply_return': False}


def payload(*actions):
    return {'skill_exists': True, 'state': {'cost_min_sp': -1, 'cast_with_no_sp': False},
            'actions': list(actions)}


def ge_literal(raw, threshold, threshold_raw, rhs, result):
    return {'threshold_int32': threshold, 'threshold_raw': threshold_raw,
            'epsilon_raw': 42950, 'comparison_rhs_raw': rhs, 'sp_raw': raw, 'result': result}


def debit_literal(delta, negated, raw, magnitude, direction, name):
    return {'delta_int32': delta, 'negated_int32': negated, 'input_raw': raw,
            'magnitude_raw': magnitude, 'delta_type_value': direction, 'delta_type_name': name,
            'target_type_value': 1, 'target_type_name': 'SP',
            'player_side_value': 0, 'player_side_name': 'DEFAULT'}


class IndependentSkillSpCost277Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('rouge._independent277_subject', MODULE_FILE)
        cls.subject = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.subject
        spec.loader.exec_module(cls.subject)

    def result(self, *actions):
        result = self.subject.skill_sp_cost_reference(payload(*actions))
        self.assertIs(result['source']['valid'], True, result['source'])
        for key in ACTUAL_UNKNOWNS:
            self.assertIsNone(result[key], key)
        for row in result['rows']:
            for key in ACTUAL_UNKNOWNS:
                self.assertIsNone(row[key], (row['id'], key))
        return result

    def row(self, action):
        result = self.result(action)
        self.assertEqual(len(result['rows']), 1)
        return result['rows'][0]

    def stages(self, row, names):
        self.assertEqual([x['name'] for x in row['stages']], list(names))
        return {x['name']: x for x in row['stages']}

    def assert_debit_prefix_and_ctor(self, row, delta, negated, raw, magnitude, direction, name):
        # Distinct source boundaries: NEG prefix versus normally reached NewSp
        # constructor arguments. Every number below is supplied as a literal.
        self.assertEqual(row['arithmetic_reference'],
                         {'delta_int32': delta, 'negated_int32': negated, 'input_raw': raw})
        self.assertEqual(row['modifier_constructor_arguments'],
            {'magnitude_raw': magnitude, 'delta_type_value': direction, 'delta_type_name': name,
             'target_type_value': 1, 'target_type_name': 'SP',
             'player_side_value': 0, 'player_side_name': 'DEFAULT',
             'source_identity': 'NewSp-owner', 'target_identity': 'NewSp-owner',
             'source_exists': True, 'target_exists': True,
             'returned_payload_fields': None, 'cancel_reason_mask': None})

    def test_exact_epsilon_threshold5_three_adjacent_raw_values(self):
        for raw, expected in ((21474793529, False), (21474793530, False), (21474793531, True)):
            with self.subTest(raw=raw):
                self.assertEqual(self.subject.ge_reference(raw, 5),
                                 ge_literal(raw, 5, 21474836480, 21474793530, expected))

    def test_zero_threshold_signed_negative_SP_at_strict_epsilon_boundary(self):
        for raw, expected in ((-42951, False), (-42950, False), (-42949, True), (0, True)):
            with self.subTest(raw=raw):
                self.assertEqual(self.subject.ge_reference(raw, 0), ge_literal(raw, 0, 0, -42950, expected))

    def test_MIN32_threshold_subtraction_wraps_before_signed_comparison(self):
        for raw, expected in ((-9223372036854775808, False), (-1, False),
                              (9223372036854732858, False), (9223372036854732859, True)):
            with self.subTest(raw=raw):
                self.assertEqual(self.subject.ge_reference(raw, -2147483648),
                    ge_literal(raw, -2147483648, -9223372036854775808, 9223372036854732858, expected))

    def test_MAX32_threshold_uses_exact_integer_Q_without_float(self):
        self.assertEqual(self.subject.ge_reference(9223372032559765562, 2147483647),
            ge_literal(9223372032559765562, 2147483647, 9223372032559808512, 9223372032559765562, False))
        self.assertEqual(self.subject.ge_reference(9223372036854775807, 2147483647),
            ge_literal(9223372036854775807, 2147483647, 9223372032559808512, 9223372032559765562, True))

    def test_debit_argument_literal_SIGNED32_NEG_and_special_Abs(self):
        rows = [(0, 0, 0, 0, 1, 'ADD'), (20, -20, -85899345920, 85899345920, 2, 'MINUS'),
                (-1, 1, 4294967296, 4294967296, 1, 'ADD'),
                (-2147483648, -2147483648, -9223372036854775808, 9223372036854775806, 2, 'MINUS'),
                (2147483647, -2147483647, -9223372032559808512, 9223372032559808512, 2, 'MINUS')]
        for row in rows:
            with self.subTest(delta=row[0]):
                self.assertEqual(self.subject.debit_argument_reference(row[0]), debit_literal(*row))

    def test_helpers_reject_bool_float_text_and_out_of_range(self):
        for bad in (True, False, 1.0, '1', -2147483649, 2147483648):
            with self.subTest(kind='delta', bad=bad):
                with self.assertRaises((ValueError, TypeError)):self.subject.debit_argument_reference(bad)
            with self.subTest(kind='threshold', bad=bad):
                with self.assertRaises((ValueError, TypeError)):self.subject.ge_reference(0, bad)
        for bad in (True, False, 1.0, '1', -9223372036854775809, 9223372036854775808):
            with self.subTest(kind='SP', bad=bad):
                with self.assertRaises((ValueError, TypeError)):self.subject.ge_reference(bad, 0)

    def test_nonnegative_first_threshold_skips_free_and_decoded_cost(self):
        action = admission(first_min=5, second_min=5, decoded_cost=20)
        action['free_read']['value'] = True
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)
        self.assertEqual(row['arithmetic_reference'], ge_literal(21474836480, 5, 21474836480, 21474793530, True))
        self.assertIs(stages['free_read']['called'], False)
        self.assertIs(stages['decoded_cost_read']['called'], False)
        self.assertIs(stages['second_min_read']['called'], True)

    def test_second_threshold_is_independent_and_may_increase_after_SP_read(self):
        row = self.row(admission(first_min=5, second_min=20, decoded_cost=1))
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)
        self.assertEqual(row['arithmetic_reference'], ge_literal(21474836480, 20, 85899345920, 85899302970, False))

    def test_second_threshold_may_be_negative_without_switching_back_to_data(self):
        row = self.row(admission(first_min=0, second_min=-1, decoded_cost=20, sp_raw=-4295010246))
        stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['result_reference'], False)
        self.assertEqual(row['arithmetic_reference'], ge_literal(-4295010246, -1, -4294967296, -4295010246, False))
        self.assertIs(stages['decoded_cost_read']['called'], False)

    def test_negative_first_threshold_uses_decoded_cost_and_skips_second_read(self):
        row = self.row(admission(first_min=-77, second_min=1, decoded_cost=20))
        stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['result_reference'], False)
        self.assertEqual(row['arithmetic_reference'], ge_literal(21474836480, 20, 85899345920, 85899302970, False))
        self.assertIs(stages['free_read']['called'], True)
        self.assertIs(stages['decoded_cost_read']['called'], True)
        self.assertIs(stages['second_min_read']['called'], False)

    def test_negative_first_free_cast_is_normal_true_with_no_SP_cost_read(self):
        action = admission(first_min=-1)
        action['free_read']['value'] = True
        action['sp_owner_read']['normal'] = False
        action['decoded_cost_read']['normal'] = False
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)
        self.assertIsNone(row['arithmetic_reference'])
        for name in ('sp_owner_read', 'sp_read', 'decoded_cost_read', 'second_min_read', 'ge_comparison'):
            self.assertIs(stages[name]['called'], False, name)

    def test_Unity_null_comparison_false_return_is_not_an_alive_check(self):
        action = admission(); action['owner_read']['exists'] = False
        action['owner_read']['identity'] = None; action['unity_null_read']['value'] = True
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)
        for name in ADMISSION_STAGES[2:]:self.assertIs(stages[name]['called'], False, name)

    def test_missing_owner_label_does_not_turn_confirmed_existing_pointer_null(self):
        action = admission()
        action['owner_read']['identity'] = None; action['sp_owner_read']['identity'] = None
        row = self.row(action)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)

    def test_SP_owner_null_is_separate_from_the_initial_valid_Unity_owner(self):
        action = admission(); action['sp_owner_read']['exists'] = False
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['normal'], False); self.assertIsNone(row['result_reference'])
        for name in ('sp_read', 'decoded_cost_read', 'second_min_read', 'ge_comparison'):
            self.assertIs(stages[name]['called'], False, name)

    def test_unknown_free_cast_leaves_possible_future_SP_and_cost_calls_unknown(self):
        action = admission(); action['free_read']['value'] = None
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIsNone(row['normal']); self.assertIsNone(row['result_reference'])
        for name in ('sp_owner_read', 'sp_read', 'decoded_cost_read', 'ge_comparison'):
            self.assertIsNone(stages[name]['called'], name)

    def test_unknown_first_threshold_does_not_default_negative_or_zero(self):
        action = admission(); action['first_min_read']['value'] = None
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIsNone(row['result_reference']); self.assertIsNone(row['arithmetic_reference'])
        for name in ('free_read', 'sp_owner_read', 'decoded_cost_read', 'second_min_read', 'ge_comparison'):
            self.assertIsNone(stages[name]['called'], name)

    def test_unknown_SP_normality_leaves_selected_later_threshold_call_unknown(self):
        action = admission(first_min=0); action['sp_read']['normal'] = None
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(stages['free_read']['called'], False)
        self.assertIsNone(stages['second_min_read']['called'])
        self.assertIsNone(stages['ge_comparison']['called'])

    def test_known_SP_read_failure_proves_later_threshold_was_not_called(self):
        action = admission(first_min=0); action['sp_read']['normal'] = False
        row = self.row(action); stages = self.stages(row, ADMISSION_STAGES)
        self.assertIs(row['normal'], False)
        self.assertIs(stages['second_min_read']['called'], False)
        self.assertIs(stages['ge_comparison']['called'], False)

    def test_zero_delta_early_normal_true_is_not_payment_success(self):
        action = reduce(delta=0); action['free_read']['normal'] = False
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)
        self.assertIsNone(row['arithmetic_reference']); self.assertIsNone(row['modifier_constructor_arguments'])
        for name in REDUCE_STAGES:self.assertIs(stages[name]['called'], False, name)

    def test_free_cast_reduce_early_return_does_not_reuse_admission_value(self):
        action = reduce(); action['free_read']['value'] = True
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)
        for name in REDUCE_STAGES[1:]:self.assertIs(stages[name]['called'], False, name)

    def test_virtual_skip_is_independently_declared_and_short_circuits_debit(self):
        action = reduce(); action['skip_virtual_read']['value'] = True
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)
        for name in REDUCE_STAGES[2:]:self.assertIs(stages[name]['called'], False, name)

    def test_Apply_normal_false_return_is_normal_row_not_paid_SP(self):
        row = self.row(reduce())
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)
        self.assert_debit_prefix_and_ctor(row, 20, -20, -85899345920, 85899345920, 2, 'MINUS')
        self.assertIs(row['apply_arguments']['force'], False)
        self.assertNotIn('mask', row['apply_arguments'])

    def test_Apply_normal_true_return_still_has_unknown_paid_cost_and_SP(self):
        action = reduce(); action['apply_return'] = True
        row = self.row(action)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], True)

    def test_negative_delta_constructs_ADD_request_not_clamped_zero(self):
        row = self.row(reduce(delta=-1))
        self.assert_debit_prefix_and_ctor(row, -1, 1, 4294967296, 4294967296, 1, 'ADD')

    def test_MIN32_debit_Abs_limit_is_MAX64_minus1_not_python_abs(self):
        row = self.row(reduce(delta=-2147483648))
        self.assert_debit_prefix_and_ctor(row, -2147483648, -2147483648,
            -9223372036854775808, 9223372036854775806, 2, 'MINUS')

    def test_null_first_NewSp_owner_can_precede_existing_different_Apply_owner(self):
        action = reduce(); action['newsp_owner_read']['exists'] = False
        action['newsp_owner_read']['identity'] = None
        row = self.row(action)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)
        self.assertIsNone(row['modifier_constructor_arguments']['source_identity'])
        self.assertIsNone(row['modifier_constructor_arguments']['target_identity'])

    def test_known_null_Apply_owner_is_checked_after_full_copy(self):
        action = reduce(); action['apply_owner_read']['exists'] = False
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(stages['apply_owner_read']['called'], True)
        self.assertIs(stages['modifier_copy']['called'], True)
        self.assertIs(stages['modifier_copy']['normal'], True)
        self.assertEqual(stages['modifier_copy']['reference'],
                         {'byte_count': 136, 'modifier_identity': 'opaque-public-modifier', 'fields': None})
        self.assertIs(stages['apply_call']['called'], False)
        self.assertIs(row['normal'], False); self.assertIsNone(row['result_reference'])

    def test_unknown_Apply_owner_existence_does_not_cancel_known_copy_prefix(self):
        action = reduce(); action['apply_owner_read']['exists'] = None
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(stages['modifier_copy']['called'], True)
        self.assertIs(stages['modifier_copy']['normal'], True)
        self.assertIsNone(stages['apply_call']['called'])
        self.assertIsNone(row['result_reference'])

    def test_unknown_virtual_skip_does_not_assert_future_NewSp_was_skipped(self):
        action = reduce(); action['skip_virtual_read']['value'] = None
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        for name in ('newsp_owner_read', 'newsp_call', 'apply_owner_read', 'modifier_copy', 'apply_call'):
            self.assertIsNone(stages[name]['called'], name)

    def test_unknown_NewSp_normal_return_does_not_claim_later_owner_copy_or_Apply(self):
        action = reduce(); action['newsp_returns_normally'] = None
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        for name in ('apply_owner_read', 'modifier_copy', 'apply_call'):
            self.assertIsNone(stages[name]['called'], name)

    def test_known_NewSp_failure_proves_later_owner_copy_or_Apply_not_called(self):
        action = reduce(); action['newsp_returns_normally'] = False
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(row['normal'], False)
        for name in ('apply_owner_read', 'modifier_copy', 'apply_call'):
            self.assertIs(stages[name]['called'], False, name)

    def test_unknown_NewSp_normal_return_retains_only_NEG_prefix_not_ctor_fields(self):
        action = reduce(delta=-2147483648); action['newsp_returns_normally'] = None
        row = self.row(action)
        self.assertEqual(row['arithmetic_reference'],
                         {'delta_int32': -2147483648, 'negated_int32': -2147483648,
                          'input_raw': -9223372036854775808})
        self.assertIsNone(row['modifier_constructor_arguments'])

    def test_normally_returning_unknown_NewSp_path_keeps_opaque_copy_and_Apply_only(self):
        action = reduce(); action['newsp_ordinary_native_path'] = None
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIsNone(row['modifier_constructor_arguments'])
        self.assertEqual(stages['newsp_call']['reference'],
                         {'value_raw': -85899345920, 'source_identity': 'NewSp-owner',
                          'target_identity': 'NewSp-owner', 'source_exists': True, 'target_exists': True})
        self.assertEqual(stages['modifier_copy']['reference'],
                         {'byte_count': 136, 'modifier_identity': 'opaque-public-modifier', 'fields': None})
        self.assertEqual(row['apply_arguments'],
                         {'owner_identity': 'Apply-owner', 'modifier_identity': 'opaque-public-modifier', 'force': False})
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)

    def test_missing_Apply_owner_label_does_not_skip_the_confirmed_existing_receiver(self):
        action = reduce(); action['apply_owner_read']['identity'] = None
        row = self.row(action)
        self.assertIs(row['normal'], True); self.assertIs(row['result_reference'], False)
        self.assertIsNone(row['apply_arguments']['owner_identity'])

    def test_unknown_copy_normality_leaves_Apply_call_unknown(self):
        action = reduce(); action['modifier_copy_returns_normally'] = None
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIsNone(stages['apply_call']['called']); self.assertIsNone(row['normal'])

    def test_known_copy_failure_does_not_claim_Apply_invoked(self):
        action = reduce(); action['modifier_copy_returns_normally'] = False
        row = self.row(action); stages = self.stages(row, REDUCE_STAGES)
        self.assertIs(stages['apply_call']['called'], False); self.assertIs(row['normal'], False)

    def test_parameter_stores_do_not_supply_independent_admission_read_values(self):
        modify = {'id': 'modify', 'kind': 'modify_min', 'ordinary_native_path': True,
                  'value': 5, 'store_returns_normally': True}
        action = admission(first_min=20, second_min=20, decoded_cost=1)
        result = self.result(modify, action)
        self.assertEqual(result['final_declared_parameter_state']['cost_min_sp'], 5)
        self.assertIs(result['rows'][1]['result_reference'], False)

    def test_assign_min_declared_BB_result_has_no_clamp_or_missing_default_substitution(self):
        action = {'id': 'assign', 'kind': 'assign_min', 'ordinary_native_path': True,
                  'blackboard_read': read_int('assign.BB', -77), 'store_returns_normally': True}
        result = self.result(action)
        self.assertEqual(result['final_declared_parameter_state']['cost_min_sp'], -77)
        self.assertIs(result['rows'][0]['normal'], True)

    def test_MIN32_modify_parameter_not_clamped_before_later_independent_reads(self):
        action = {'id': 'modify', 'kind': 'modify_min', 'ordinary_native_path': True,
                  'value': -2147483648, 'store_returns_normally': True}
        result = self.result(action)
        self.assertEqual(result['final_declared_parameter_state']['cost_min_sp'], -2147483648)

    def test_modify_free_state_does_not_override_separately_declared_reduce_getter(self):
        action = {'id': 'modify-free', 'kind': 'modify_free', 'ordinary_native_path': True,
                  'value': True, 'store_returns_normally': True}
        result = self.result(action, reduce())
        self.assertIs(result['final_declared_parameter_state']['cast_with_no_sp'], True)
        self.assertIs(result['rows'][1]['result_reference'], False)
        self.assertIsNotNone(result['rows'][1]['apply_arguments'])

    def test_same_group_gate5_and_cost20_stay_different_and_not_pay_success(self):
        gate = admission('group-gate', first_min=5, second_min=5, decoded_cost=20)
        debit = reduce('group-debit', delta=20)
        result = self.result(gate, debit)
        self.assertIs(result['rows'][0]['result_reference'], True)
        self.assertIs(result['rows'][1]['result_reference'], False)
        self.assertEqual(result['rows'][1]['arithmetic_reference']['delta_int32'], 20)
        self.assertEqual(result['rows'][1]['modifier_constructor_arguments']['magnitude_raw'], 85899345920)

    def test_ordinary_false_or_unknown_does_not_promote_action_arithmetic(self):
        for ordinary in (False, None):
            with self.subTest(ordinary=ordinary):
                action = reduce(); action['ordinary_native_path'] = ordinary
                row = self.row(action)
                self.assertIsNone(row['arithmetic_reference'])
                self.assertIsNone(row['modifier_constructor_arguments'])
                self.assertIsNone(row['apply_arguments'])

    def test_unknown_delta_does_not_assume_nonzero_or_no_future_call(self):
        row = self.row(reduce(delta=None)); stages = self.stages(row, REDUCE_STAGES)
        self.assertIsNone(row['result_reference']); self.assertIsNone(row['arithmetic_reference'])
        for name in REDUCE_STAGES:self.assertIsNone(stages[name]['called'], name)

    def test_skill_pointer_unknown_leaves_action_call_unknown(self):
        value = payload(reduce()); value['skill_exists'] = None
        result = self.subject.skill_sp_cost_reference(value)
        self.assertIsNone(result['rows'][0]['called'])
        self.assertIsNone(result['rows'][0]['arithmetic_reference'])

    def test_API_no_public_data_injection_or_unproved_alive_storage_fields(self):
        with self.assertRaises(TypeError):self.subject.skill_sp_cost_reference(payload(reduce()), data={})
        for key, value in (('alive', True), ('maxChargeTime', 2), ('data', {})):
            with self.subTest(key=key):
                action = admission(); action[key] = value
                with self.assertRaises((ValueError, TypeError)):self.subject.skill_sp_cost_reference(payload(action))

    def test_unique_action_and_read_identity_domains_are_enforced(self):
        action = reduce(); action['free_read']['id'] = action['id']
        with self.assertRaises((ValueError, TypeError)):self.subject.skill_sp_cost_reference(payload(action))
        first, second = admission('a'), reduce('b')
        second['free_read']['id'] = first['free_read']['id']
        with self.assertRaises((ValueError, TypeError)):self.subject.skill_sp_cost_reference(payload(first, second))

    def test_tri_scalar_types_and_int32_delta_bools_are_not_coerced(self):
        for value in (0, 1, 'false'):
            with self.subTest(value=value):
                action = reduce(); action['free_read']['value'] = value
                with self.assertRaises((ValueError, TypeError)):self.subject.skill_sp_cost_reference(payload(action))
        for value in (True, False, 1.0, '1', -2147483649, 2147483648):
            with self.subTest(delta=value):
                with self.assertRaises((ValueError, TypeError)):self.subject.skill_sp_cost_reference(payload(reduce(delta=value)))

    def test_complete_payload_and_state_preserve_caller_and_repeat(self):
        value = payload(admission('a', first_min=5), reduce('b', delta=-2147483648))
        before = copy.deepcopy(value)
        first = self.subject.skill_sp_cost_reference(value)
        second = self.subject.skill_sp_cost_reference(value)
        self.assertEqual(value, before); self.assertEqual(first, second)
        self.assertEqual(first['final_declared_parameter_state'], value['state'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    options, remaining = parser.parse_known_args()
    MODULE_FILE = options.module_file.resolve()
    unittest.main(argv=[__file__, *remaining], verbosity=2)
