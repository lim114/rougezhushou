"""Independent fixed-contract controls, based on pinned source and literal inputs.

No live game state or DLL execution is involved. Unknown values and unknown
control flow are deliberately separate, and no cost/array alias is inherited.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
MODULE_FILE = ROOT / 'rouge/skill_sp_increment_reference.py'
ACTUAL_UNKNOWNS = ('actual_array_after', 'actual_sp_after', 'complete_cycle')
SLOT_STAGES = ('blackboard_check', 'key_format', 'lookup', 'mask_read', 'mask_set', 'mask_store',
               'increment_copy', 'increment_decode', 'array_read', 'array_check', 'length_read',
               'bounds_check', 'array_store')
SP_STAGES = ('blackboard_capture', 'inited_read', 'array_allocation', 'array_install', 'write_barrier') + tuple(
    f's{slot}.{name}' for slot in range(4) for name in SLOT_STAGES)
SKILL_STAGES = ('inited_read', 'duration_first_read', 'flag_store', 'duration_ge', 'first_blackboard_read',
                'duration_second_read', 'duration_assign', 'sp_data_read', 'second_blackboard_read', 'sp_init')
ATTACK_STAGES = ('sp_type_read', 'array_read', 'index', 'array_check', 'length_read', 'bounds_check',
                 'amount_read', 'single_to_fp', 'recover_request')
DAMAGE_STAGES = ('sp_type_read', 'cancelled_read', 'modifier_flag_read') + ATTACK_STAGES[1:]


def ptr(label, identity='public-instance', exists=True, normal=True):
    return {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}


def integer(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def boolean(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def single(label, bits, normal=True):
    return {'id': label, 'normal': normal, 'bits': bits}


def sp_init(label='sp', blackboard=False):
    slots = []
    for slot in range(4):
        key = f'{label}.s{slot}'
        slots.append({'slot': slot, 'key_format_normally': True, 'key_identity': None,
            'lookup': {'id': key + '.lookup', 'normal': True, 'found': False, 'bits': 0x3F400000},
            'mask_read': integer(key + '.mask', 0), 'mask_store_normally': True,
            'increment_copy_normally': True, 'increment_decode': single(key + '.decoded', 0x3FC00000),
            'array_read': ptr(key + '.array', 'observed-array'),
            'array_length_read': integer(key + '.length', 4), 'array_store_normally': True})
    return {'id': label, 'kind': 'sp_data_init', 'ordinary_native_path': True,
        'captured_blackboard': ptr(label + '.captured-bb', 'captured-blackboard' if blackboard else None, blackboard),
        'inited_read': boolean(label + '.inited', False),
        'array_allocation': ptr(label + '.allocation', 'requested-array'),
        'array_install_normally': True, 'write_barrier_normally': True, 'slots': slots}


def skill_init(label='skill', first_bits=0):
    return {'id': label, 'kind': 'skill_data_init', 'ordinary_native_path': True,
        'inited_read': boolean(label + '.inited', False),
        'duration_first_read': single(label + '.duration-first', first_bits),
        'flag_store_normally': True, 'ge_normally': True,
        'first_blackboard_read': ptr(label + '.first-bb', 'assignment-blackboard'),
        'duration_second_read': single(label + '.duration-second', 0x3FC00000),
        'assign_normally': True, 'sp_data_read': ptr(label + '.sp-data', 'nested-sp-data'),
        'second_blackboard_read': ptr(label + '.second-bb', 'nested-blackboard'),
        'sp_init_normally': True}


def gain(kind='attack_gain', label='gain', bits=0x3FC00000):
    row = {'id': label, 'kind': kind, 'ordinary_native_path': True,
        'sp_type_read': integer(label + '.type', 2 if kind == 'attack_gain' else 4),
        'array_read': ptr(label + '.array', 'controller-array'), 'index_normally': True,
        'array_length_read': integer(label + '.length', 4), 'amount_read': single(label + '.amount', bits),
        'single_to_fp_normally': True, 'recover_normally': True}
    if kind == 'damage_gain':
        row['cancelled_read'] = boolean(label + '.cancelled', False)
        row['modifier_flag_read'] = integer(label + '.ignore-for-sp', 0)
    return row


def payload(*actions):
    return {'receiver_exists': True, 'actions': list(actions)}


def install_prefix():
    return {'field': 'm_incrementsForAllSpTypes', 'identity': 'requested-array', 'exists': True, 'requested_length': 4}


def slot_prefix(slot, bits=0x3F800000, identity='observed-array'):
    return {'field': 'm_incrementsForAllSpTypes', 'identity': identity, 'index': slot, 'bits': bits}


class IndependentIncrementTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:
            spec = importlib.util.spec_from_file_location('independent_increment_subject_279', MODULE_FILE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.subject = module

    def run_action(self, action):
        out = self.subject.skill_sp_increment_reference(payload(action))
        self.assertEqual(out['kind'], 'skill_sp_increment_reference')
        self.assertTrue(out['source']['valid'])
        row = out['rows'][0]
        for key in ACTUAL_UNKNOWNS:
            self.assertIsNone(out[key])
            self.assertIsNone(row[key])
        stages = {stage['name']: stage for stage in row['stages']}
        expected = {'sp_data_init': SP_STAGES, 'skill_data_init': SKILL_STAGES,
                    'attack_gain': ATTACK_STAGES, 'damage_gain': DAMAGE_STAGES}[action['kind']]
        self.assertEqual(tuple(stages), expected)
        for stage in row['stages']:
            self.assertEqual(set(stage), {'name', 'called', 'normal', 'reference'})
        return row, stages

    def test_Single_GE_has_inclusive_literal_zero_rhs_boundary(self):
        for bits, expected in [(0xB727C5AC, True), (0xB727C5AD, False), (0xB727C5AB, True),
                               (0, True), (0x80000000, True), (0x3F800000, True)]:
            with self.subTest(bits=bits):
                value = self.subject.single_ge_zero_reference(bits)
                self.assertEqual(set(value), {'bits', 'status', 'rhs_bits', 'adjusted_rhs_bits', 'ge_boolean_reference'})
                self.assertEqual(value['rhs_bits'], 0)
                self.assertEqual(value['adjusted_rhs_bits'], 0xB727C5AC)
                self.assertIs(value['ge_boolean_reference'], expected)

    def test_Single_GE_unsafe_values_remain_unknown(self):
        for bits in [None, 0x00000001, 0x7FC00000, 0x7F800000, 0xFF800000]:
            with self.subTest(bits=bits):
                self.assertIsNone(self.subject.single_ge_zero_reference(bits)['ge_boolean_reference'])

    def test_mask_BTS_literals_signed_and_unnamed_slot(self):
        for mask, slot, expected, bit in [(0, 0, 1, 1), (0, 3, 8, 8),
                (-2147483648, 2, -2147483644, 4), (-1, 3, -1, 8),
                (2147483647, 1, 2147483647, 2), (None, 2, None, 4)]:
            with self.subTest(mask=mask, slot=slot):
                self.assertEqual(self.subject.mask_bit_reference(mask, slot),
                    {'mask_int32': mask, 'slot': slot, 'result_int32_reference': expected, 'known_set_bit': bit})

    def test_Single_increment_literal_toward_zero_and_signed64_boundaries(self):
        literals = [(0x3F800000, 4294967296), (0x3FC00000, 6442450944),
                    (0xBFC00000, -6442450944), (0x3DCCCCCD, 429496736),
                    (0x3F000000, 2147483648), (0x2F800000, 1),
                    (0x2F000000, 0), (0xAF000000, 0), (0, 0), (0x80000000, 0),
                    (0x00800000, 0), (0xCF000000, -9223372036854775808),
                    (0x4EFFFFFF, 9223371487098961920)]
        for bits, expected in literals:
            with self.subTest(bits=bits):
                value = self.subject.single_increment_reference(bits)
                self.assertEqual(set(value), {'bits', 'status', 'scale_q', 'scaled_numerator',
                                             'scaled_denominator', 'raw_reference'})
                self.assertEqual(value['scale_q'], 4294967296)
                self.assertEqual(value['raw_reference'], expected)

    def test_Single_increment_unknown_numeric_domain(self):
        for bits in [None, 0x00000001, 0x7FC00000, 0x7F800000, 0xFF800000,
                     0x4F000000, 0xCF000001]:
            with self.subTest(bits=bits):
                self.assertIsNone(self.subject.single_increment_reference(bits)['raw_reference'])

    def test_scalar_helpers_reject_bool_wrong_range_and_slot(self):
        for bits in [True, 1.0, -1, 4294967296]:
            with self.assertRaises((ValueError, TypeError)):
                self.subject.single_ge_zero_reference(bits)
            with self.assertRaises((ValueError, TypeError)):
                self.subject.single_increment_reference(bits)
        for mask, slot in [(True, 0), (2147483648, 0), (0, True), (0, 4), (0, -1)]:
            with self.assertRaises((ValueError, TypeError)):
                self.subject.mask_bit_reference(mask, slot)

    def test_default_one_four_stores_leave_mask_bits_disabled(self):
        row, stages = self.run_action(sp_init())
        self.assertTrue(row['normal'])
        self.assertEqual(row['stored_prefixes'], [install_prefix(), *[slot_prefix(i) for i in range(4)]])
        self.assertEqual([r['index_name'] for r in row['slot_references']], ['TIME', 'ATTACK', 'TAKEN_DAMAGE', 'NEVER_USE'])
        self.assertEqual([r['mask_bit'] for r in row['slot_references']], [1, 2, 4, 8])
        for slot in range(4):
            self.assertFalse(stages[f's{slot}.lookup']['called'])
            self.assertFalse(stages[f's{slot}.mask_store']['called'])
            self.assertEqual(row['slot_references'][slot]['value_source'], 'default_one')

    def test_nonnull_existing_array_getter_result_returns_without_four_slots(self):
        action = sp_init()
        action['inited_read']['value'] = True
        action['array_allocation']['normal'] = False
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertEqual(row['stored_prefixes'], [])
        self.assertEqual(row['slot_references'], [])
        for name in SP_STAGES[2:]:
            self.assertFalse(stages[name]['called'])

    def test_unknown_init_result_keeps_allocation_future_unknown(self):
        action = sp_init()
        action['inited_read']['value'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['array_allocation']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_allocation_or_barrier_failure_keeps_only_completed_prefix(self):
        action = sp_init()
        action['write_barrier_normally'] = False
        row, stages = self.run_action(action)
        self.assertFalse(row['normal'])
        self.assertEqual(row['stored_prefixes'], [install_prefix()])
        self.assertFalse(stages['s0.blackboard_check']['called'])

    def test_captured_blackboard_absent_skips_each_lookup_but_not_fallback(self):
        action = sp_init()
        for slot in action['slots']:
            slot['lookup']['normal'] = False
            slot['key_format_normally'] = False
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        for slot in range(4):
            self.assertFalse(stages[f's{slot}.key_format']['called'])
            self.assertFalse(stages[f's{slot}.lookup']['called'])
            self.assertTrue(stages[f's{slot}.mask_read']['called'])

    def test_unknown_captured_pointer_existence_preserves_install_prefix(self):
        action = sp_init()
        action['captured_blackboard']['exists'] = None
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [install_prefix()])
        self.assertIsNone(stages['s0.key_format']['called'])
        self.assertIsNone(stages['s0.array_read']['called'])

    def test_lookup_success_writes_mask_before_null_array_guard(self):
        action = sp_init(blackboard=True)
        action['slots'][0]['lookup'].update(found=True, bits=0x3FC00000)
        action['slots'][0]['array_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [install_prefix(), {'field': 'spType', 'value': 1, 'known_set_bit': 1}])
        self.assertTrue(stages['s0.mask_store']['normal'])
        self.assertTrue(stages['s0.array_read']['normal'])
        self.assertTrue(stages['s0.array_check']['normal'])
        self.assertFalse(row['normal'])
        self.assertFalse(stages['s0.array_store']['called'])
        self.assertFalse(stages['s1.blackboard_check']['called'])

    def test_unknown_mask_on_success_keeps_known_bit_and_continues_direct_store(self):
        action = sp_init(blackboard=True)
        action['slots'][0]['lookup'].update(found=True, bits=0x3FC00000)
        action['slots'][0]['mask_read']['value'] = None
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'][1], {'field': 'spType', 'value': None, 'known_set_bit': 1})
        self.assertEqual(row['stored_prefixes'][2], slot_prefix(0, 0x3FC00000))
        self.assertTrue(stages['s1.blackboard_check']['called'])
        self.assertTrue(row['normal'])

    def test_unknown_lookup_bits_can_be_normally_stored_without_guessing_value(self):
        action = sp_init(blackboard=True)
        action['slots'][0]['lookup'].update(found=True, bits=None)
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'][2], slot_prefix(0, None))
        self.assertTrue(stages['s0.array_store']['normal'])
        self.assertTrue(stages['s1.blackboard_check']['called'])

    def test_false_lookup_ignores_out_value_uses_independent_current_mask(self):
        row, stages = self.run_action(sp_init(blackboard=True))
        self.assertEqual(row['slot_references'][0]['value_bits'], 0x3F800000)
        self.assertEqual(row['slot_references'][0]['value_source'], 'default_one')
        self.assertTrue(stages['s0.lookup']['normal'])
        self.assertFalse(stages['s0.mask_store']['called'])

    def test_unknown_lookup_found_does_not_choose_BTS_or_default(self):
        action = sp_init(blackboard=True)
        action['slots'][0]['lookup']['found'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['s0.mask_read']['called'])
        self.assertIsNone(stages['s0.array_read']['called'])
        self.assertEqual(row['stored_prefixes'], [install_prefix()])

    def test_active_negative_mask_uses_independent_protected_increment(self):
        action = sp_init()
        action['slots'][0]['mask_read']['value'] = -1
        row, stages = self.run_action(action)
        self.assertEqual(row['slot_references'][0]['value_source'], 'protected_increment')
        self.assertEqual(row['slot_references'][0]['value_bits'], 0x3FC00000)
        self.assertTrue(stages['s0.increment_copy']['normal'])
        self.assertTrue(stages['s0.increment_decode']['normal'])
        self.assertFalse(stages['s0.mask_store']['called'])

    def test_unknown_active_decoded_value_keeps_qualified_direct_store(self):
        action = sp_init()
        action['slots'][0]['mask_read']['value'] = 1
        action['slots'][0]['increment_decode']['bits'] = None
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'][1], slot_prefix(0, None))
        self.assertTrue(stages['s1.blackboard_check']['called'])

    def test_unknown_fallback_mask_blocks_control_dependent_future(self):
        action = sp_init()
        action['slots'][0]['mask_read']['value'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['s0.increment_decode']['called'])
        self.assertIsNone(stages['s0.array_read']['called'])
        self.assertEqual(row['stored_prefixes'], [install_prefix()])

    def test_changed_mask_and_array_are_not_inherited_from_previous_slot(self):
        action = sp_init()
        action['slots'][0]['array_read']['identity'] = 'array-zero'
        action['slots'][1]['mask_read']['value'] = 2
        action['slots'][1]['increment_decode']['bits'] = 0x3F000000
        action['slots'][1]['array_read']['identity'] = 'array-one'
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'][1], slot_prefix(0, 0x3F800000, 'array-zero'))
        self.assertEqual(row['stored_prefixes'][2], slot_prefix(1, 0x3F000000, 'array-one'))
        self.assertEqual(row['slot_references'][1]['value_source'], 'protected_increment')
        self.assertTrue(stages['s2.array_store']['normal'])

    def test_short_array_after_prior_slot_preserves_prior_writes(self):
        action = sp_init()
        action['slots'][1]['array_length_read']['value'] = 1
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [install_prefix(), slot_prefix(0)])
        self.assertTrue(stages['s1.bounds_check']['normal'])
        self.assertFalse(stages['s1.array_store']['called'])
        self.assertFalse(stages['s2.blackboard_check']['called'])
        self.assertFalse(row['normal'])

    def test_unsigned_array_length_is_not_signed_clamped(self):
        action = sp_init()
        for slot in action['slots']:
            slot['array_length_read']['value'] = 4294967295
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertEqual(len(row['stored_prefixes']), 5)

    def test_unknown_array_identity_is_not_null_receiver(self):
        action = sp_init()
        action['slots'][0]['array_read']['identity'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(row['stored_prefixes'][1]['identity'])
        self.assertTrue(stages['s0.array_store']['normal'])

    def test_skill_existing_flag_skips_all_downstream_work(self):
        action = skill_init()
        action['inited_read']['value'] = True
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertEqual(row['stored_prefixes'], [])
        for name in SKILL_STAGES[1:]:
            self.assertFalse(stages[name]['called'])

    def test_skill_unknown_first_duration_keeps_flag_then_unknown_GE_future(self):
        action = skill_init(first_bits=None)
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [{'field': 'm_inited', 'value': True}])
        self.assertTrue(stages['flag_store']['normal'])
        self.assertIsNone(row['duration_ge_reference']['ge_boolean_reference'])
        self.assertIsNone(stages['first_blackboard_read']['called'])

    def test_skill_GE_failure_preserves_flag_and_skips_later_calls(self):
        action = skill_init()
        action['ge_normally'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [{'field': 'm_inited', 'value': True}])
        self.assertFalse(row['normal'])
        self.assertFalse(stages['first_blackboard_read']['called'])

    def test_skill_GE_false_skips_assign_but_still_calls_nested_init(self):
        row, stages = self.run_action(skill_init(first_bits=0xB727C5AD))
        self.assertIs(row['duration_ge_reference']['ge_boolean_reference'], False)
        for name in ['first_blackboard_read', 'duration_second_read', 'duration_assign']:
            self.assertFalse(stages[name]['called'])
        self.assertIsNone(row['assign_arguments'])
        self.assertTrue(stages['sp_data_read']['called'])
        self.assertTrue(stages['sp_init']['called'])

    def test_skill_independent_duration_and_blackboard_parameters(self):
        row, stages = self.run_action(skill_init(first_bits=0xB727C5AC))
        self.assertEqual(row['assign_arguments'], {'blackboard_identity': 'assignment-blackboard',
            'duration_bits': 0x3FC00000, 'key_identity': None})
        self.assertEqual(row['sp_init_arguments'], {'sp_data_identity': 'nested-sp-data',
            'blackboard_identity': 'nested-blackboard', 'blackboard_exists': True})
        self.assertTrue(stages['duration_assign']['normal'])

    def test_skill_unknown_second_duration_is_opaque_assign_not_control(self):
        action = skill_init()
        action['duration_second_read']['bits'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(row['assign_arguments']['duration_bits'])
        self.assertTrue(stages['duration_assign']['normal'])
        self.assertTrue(stages['sp_init']['called'])

    def test_skill_first_blackboard_null_fails_after_flag(self):
        action = skill_init()
        action['first_blackboard_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [{'field': 'm_inited', 'value': True}])
        self.assertTrue(stages['first_blackboard_read']['normal'])
        self.assertFalse(stages['duration_second_read']['called'])
        self.assertFalse(stages['sp_init']['called'])
        self.assertFalse(row['normal'])

    def test_skill_second_blackboard_null_is_forwarded_not_guarded(self):
        action = skill_init()
        action['second_blackboard_read'].update(exists=False, identity=None)
        row, stages = self.run_action(action)
        self.assertEqual(row['sp_init_arguments'], {'sp_data_identity': 'nested-sp-data',
            'blackboard_identity': None, 'blackboard_exists': False})
        self.assertTrue(stages['sp_init']['called'])
        self.assertTrue(row['normal'])

    def test_skill_nested_init_failure_retains_flag_and_arguments(self):
        action = skill_init()
        action['sp_init_normally'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [{'field': 'm_inited', 'value': True}])
        self.assertIsNotNone(row['assign_arguments'])
        self.assertIsNotNone(row['sp_init_arguments'])
        self.assertFalse(stages['sp_init']['normal'])

    def test_attack_and_damage_known_amount_requests_have_force_false(self):
        for kind in ['attack_gain', 'damage_gain']:
            with self.subTest(kind=kind):
                row, stages = self.run_action(gain(kind))
                self.assertEqual(row['recover_arguments'], {'amount_raw': 6442450944, 'force': False})
                self.assertEqual(row['increment_reference']['raw_reference'], 6442450944)
                self.assertTrue(stages['recover_request']['normal'])

    def test_gain_mask_low_byte_not_full_enum_equality(self):
        for value in [258, -1]:
            with self.subTest(value=value):
                action = gain()
                action['sp_type_read']['value'] = value
                row, stages = self.run_action(action)
                self.assertTrue(stages['recover_request']['called'])

    def test_gain_disabled_bit_is_normal_skip(self):
        for kind in ['attack_gain', 'damage_gain']:
            with self.subTest(kind=kind):
                action = gain(kind)
                action['sp_type_read']['value'] = 0
                row, stages = self.run_action(action)
                self.assertTrue(row['normal'])
                self.assertFalse(stages['array_read']['called'])
                self.assertIsNone(row['recover_arguments'])

    def test_damage_cancelled_skips_flag_and_array_normally(self):
        action = gain('damage_gain')
        action['cancelled_read']['value'] = True
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertFalse(stages['modifier_flag_read']['called'])
        self.assertFalse(stages['array_read']['called'])

    def test_damage_any_nonzero_ignore_flag_skips_array(self):
        for value in [1, 128, 255]:
            with self.subTest(value=value):
                action = gain('damage_gain')
                action['modifier_flag_read']['value'] = value
                row, stages = self.run_action(action)
                self.assertTrue(row['normal'])
                self.assertFalse(stages['array_read']['called'])

    def test_damage_unknown_cancel_or_flag_is_unknown_control(self):
        for name in ['cancelled_read', 'modifier_flag_read']:
            with self.subTest(name=name):
                action = gain('damage_gain')
                action[name]['value'] = None
                row, stages = self.run_action(action)
                self.assertIsNone(stages['array_read']['called'])
                self.assertIsNone(row['recover_arguments'])

    def test_gain_null_array_still_invokes_index_before_guard(self):
        action = gain()
        action['array_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertTrue(stages['array_read']['normal'])
        self.assertTrue(stages['index']['called'])
        self.assertTrue(stages['index']['normal'])
        self.assertTrue(stages['array_check']['normal'])
        self.assertFalse(stages['length_read']['called'])
        self.assertFalse(row['normal'])

    def test_gain_index_one_or_two_requires_corresponding_bounds(self):
        for kind, length in [('attack_gain', 1), ('damage_gain', 2)]:
            with self.subTest(kind=kind):
                action = gain(kind)
                action['array_length_read']['value'] = length
                row, stages = self.run_action(action)
                self.assertFalse(row['normal'])
                self.assertFalse(stages['amount_read']['called'])

    def test_gain_unknown_numeric_amount_can_have_qualified_normal_request(self):
        for bits in [None, 0x00000001, 0x7FC00000, 0x4F000000]:
            with self.subTest(bits=bits):
                row, stages = self.run_action(gain(bits=bits))
                self.assertEqual(row['recover_arguments'], {'amount_raw': None, 'force': False})
                self.assertTrue(stages['single_to_fp']['normal'])
                self.assertTrue(stages['recover_request']['called'])

    def test_gain_unknown_conversion_normality_keeps_recover_future_unknown(self):
        action = gain()
        action['single_to_fp_normally'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['recover_request']['called'])
        self.assertIsNone(row['recover_arguments'])

    def test_gain_recover_failure_keeps_request_arguments_without_actual_SP(self):
        action = gain()
        action['recover_normally'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['recover_arguments'], {'amount_raw': 6442450944, 'force': False})
        self.assertFalse(stages['recover_request']['normal'])

    def test_initializer_does_not_fill_later_gain_from_assumed_array_alias(self):
        init = sp_init('init')
        request = gain(label='event', bits=None)
        request['array_read']['identity'] = 'observed-array'
        out = self.subject.skill_sp_increment_reference(payload(init, request))
        self.assertEqual(out['rows'][1]['recover_arguments'], {'amount_raw': None, 'force': False})
        self.assertIsNone(out['actual_array_after'])
        self.assertIsNone(out['actual_sp_after'])

    def test_unqualified_native_does_not_claim_writes_or_requests(self):
        for route in [False, None]:
            with self.subTest(route=route):
                action = sp_init()
                action['ordinary_native_path'] = route
                row, stages = self.run_action(action)
                self.assertEqual(row['stored_prefixes'], [])
                self.assertIsNone(row['recover_arguments'])
                self.assertIsNone(row['sp_init_arguments'])

    def test_typed_slots_capture_and_duplicate_ids_rejected(self):
        action = sp_init()
        action['slots'][1]['slot'] = 0
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_sp_increment_reference(payload(action))
        action = sp_init()
        action['slots'][0]['captured_blackboard'] = ptr('extra')
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_sp_increment_reference(payload(action))
        action = gain('damage_gain')
        action['modifier_flag_read']['value'] = 256
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_sp_increment_reference(payload(action))
        one, two = sp_init('one'), gain(label='two')
        two['amount_read']['id'] = one['slots'][0]['lookup']['id']
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_sp_increment_reference(payload(one, two))

    def assert_invalid_source_blocks_every_reference(self):
        self.assertFalse(self.subject.source_data()['valid'])
        self.assertIsNone(self.subject.single_ge_zero_reference(0))
        self.assertIsNone(self.subject.single_increment_reference(0x3F800000))
        self.assertIsNone(self.subject.mask_bit_reference(0, 0))
        out = self.subject.skill_sp_increment_reference(payload(sp_init(), skill_init(), gain(label='attack'), gain('damage_gain', 'damage')))
        self.assertFalse(out['source']['valid'])
        self.assertEqual(len(out['rows']), 4)
        for row in out['rows']:
            self.assertEqual(row['stored_prefixes'], [])
            self.assertEqual(row['slot_references'], [])
            for key in ['duration_ge_reference', 'assign_arguments', 'sp_init_arguments', 'increment_reference', 'recover_arguments', *ACTUAL_UNKNOWNS]:
                self.assertIsNone(row[key])
            for stage in row['stages']:
                self.assertIsNone(stage['reference'])
        bad = payload(sp_init())
        bad['source'] = {'valid': True}
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_sp_increment_reference(bad)
        with self.assertRaises(TypeError):
            self.subject.skill_sp_increment_reference(payload(sp_init()), data={'valid': True})

    def test_source_one_byte_mutation_blocks_helpers_and_all_four_kinds(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json', *json.loads((original / 'source_manifest.json').read_bytes())['support_files_sha256'])
        package_files = tuple(p for p in original.iterdir() if p.is_file())
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for changed in names:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory(prefix='rouge279-public-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                for item in package_files:
                    shutil.copyfile(item, target / item.name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assertTrue(self.subject.source_data()['valid'])
                    raw = bytearray((target / changed).read_bytes())
                    raw[0] ^= 1
                    (target / changed).write_bytes(raw)
                    self.assert_invalid_source_blocks_every_reference()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})

    def test_missing_source_files_block_helpers_and_all_four_kinds(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json', *json.loads((original / 'source_manifest.json').read_bytes())['support_files_sha256'])
        package_files = tuple(p for p in original.iterdir() if p.is_file())
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for missing in names:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(prefix='rouge279-public-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                for item in package_files:
                    shutil.copyfile(item, target / item.name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assertTrue(self.subject.source_data()['valid'])
                    removed = (target / missing).resolve()
                    self.assertTrue(removed.is_relative_to(target))
                    removed.unlink()
                    self.assert_invalid_source_blocks_every_reference()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    spec = importlib.util.spec_from_file_location('independent_increment_subject_279', args.module_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    IndependentIncrementTests.subject = module
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__':
    main()
