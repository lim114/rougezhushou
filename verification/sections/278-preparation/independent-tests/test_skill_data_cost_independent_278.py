"""Independent literals for the section278 fixed source-bound cost contract.

No native DLL is executed and no candidate arithmetic implementation is copied.
Expected values are exact, manually listed source-domain controls. This file may
be run against an isolated cache module using --module-file before promotion.
"""
import argparse
import copy
import hashlib
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in (HERE, *HERE.parents) if (path / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
MODULE_FILE = ROOT / 'rouge/skill_data_cost_reference.py'

SINGLE_STAGES = ('owner_read', 'character_data_read', 'skill_data_read', 'blackboard_read',
                 'modifier_read', 'sp_data_read', 'cost_copy', 'cost_decode',
                 'single_conversion', 'single_arithmetic', 'round', 'encode', 'store')
SCALE_STAGES = ('first_data_read', 'first_sp_data_read', 'cost_copy', 'cost_decode',
                'scale_read', 'imul', 'encode', 'store', 'owner_read', 'second_data_read', 'update')
REPLACE_STAGES = ('first_data_read', 'first_sp_data_read', 'encode', 'first_sp_data_check',
                  'store', 'modify_type_read', 'second_data_read', 'second_sp_data_read',
                  'type_value_read', 'type_store', 'first_owner_read', 'unity_truth_read',
                  'second_owner_read', 'third_data_read', 'update')
SINGLE_KEYS = {'operation', 'cost_int32', 'modifier_bits', 'status', 'cost_single_exact',
               'binary_operation_exact', 'mathematical_numerator', 'mathematical_denominator',
               'result_single_bits', 'rounded_int32_reference'}
ACTUAL_UNKNOWNS = ('actual_cost_after', 'actual_sp_after', 'complete_cycle')


def ptr(label, identity='public-instance', exists=True, normal=True):
    return {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}


def integer(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def boolean(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def single_action(kind='rune_mul', label='single', cost=3, bits=0x3FC00000):
    row = {'id': label, 'kind': kind, 'ordinary_native_path': True,
        'owner_read': ptr(label + '.owner', 'single-owner'),
        'character_data_read': ptr(label + '.character-data', 'character-data'),
        'skill_data_read': ptr(label + '.skill-data', 'skill-data'),
        'blackboard_read': ptr(label + '.blackboard', 'blackboard'),
        'sp_data_read': ptr(label + '.sp-data', 'single-sp-data'),
        'modifier_read': {'id': label + '.modifier', 'normal': True, 'bits': bits},
        'cost_decode': integer(label + '.cost-decode', cost),
        'cost_copy_normally': True, 'single_conversion_normally': True,
        'single_arithmetic_normally': True, 'round_normally': True,
        'encode_normally': True, 'store_normally': True,
        'encoded_payload_identity': 'opaque-single-payload'}
    if kind != 'relic_mul':
        row['modifier_read']['found'] = True
    return row


def scale_action(label='scale', cost=2147483647, scale=2):
    return {'id': label, 'kind': 'scale_cost', 'ordinary_native_path': True,
        'first_data_read': ptr(label + '.data1', 'scale-data-1'),
        'first_sp_data_read': ptr(label + '.sp-data1', 'scale-sp-data-1'),
        'owner_read': ptr(label + '.owner', 'scale-update-owner'),
        'second_data_read': ptr(label + '.data2', 'scale-data-2'),
        'cost_decode': integer(label + '.decoded-cost', cost),
        'scale_read': integer(label + '.scale', scale),
        'cost_copy_normally': True, 'encode_normally': True, 'store_normally': True,
        'update_normally': True, 'encoded_payload_identity': 'opaque-scale-payload',
        'update_sp_data_identity': 'scale-sp-data-2'}


def replace_action(label='replace', new_cost=-7, modify_type=True, sp_type=6):
    return {'id': label, 'kind': 'replace_cost', 'ordinary_native_path': True,
        'new_cost': new_cost,
        'first_data_read': ptr(label + '.data1', 'replace-data-1'),
        'first_sp_data_read': ptr(label + '.sp-data1', 'replace-sp-data-1'),
        'second_data_read': ptr(label + '.data2', 'replace-data-2'),
        'second_sp_data_read': ptr(label + '.sp-data2', 'replace-sp-data-2'),
        'first_owner_read': ptr(label + '.owner1', 'replace-truth-owner'),
        'second_owner_read': ptr(label + '.owner2', 'replace-update-owner'),
        'third_data_read': ptr(label + '.data3', 'replace-data-3'),
        'modify_type_read': boolean(label + '.modify-type', modify_type),
        'type_value_read': integer(label + '.sp-type', sp_type),
        'unity_truth_read': boolean(label + '.unity-truth', True),
        'encode_normally': True, 'store_normally': True,
        'type_store_normally': True, 'update_normally': True,
        'encoded_payload_identity': 'opaque-replace-payload',
        'update_sp_data_identity': 'replace-sp-data-3'}


def payload(*actions):
    return {'receiver_exists': True, 'actions': list(actions)}


def cost_prefix(identity):
    return {'field': 'spCost', 'byte_count': 20, 'payload_identity': identity, 'decoded_value': None}


class IndependentCostTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        # unittest discovery bypasses main(); explicit candidate main already sets this.
        if cls.subject is None:
            spec = importlib.util.spec_from_file_location('independent_cost_subject_278', MODULE_FILE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.subject = module

    def run_action(self, action):
        out = self.subject.skill_data_cost_reference(payload(action))
        self.assertEqual(out['kind'], 'skill_data_cost_reference')
        self.assertTrue(out['source']['valid'])
        self.assertEqual(len(out['rows']), 1)
        row = out['rows'][0]
        for key in ACTUAL_UNKNOWNS:
            self.assertIsNone(out[key])
            self.assertIsNone(row[key])
        stages = {stage['name']: stage for stage in row['stages']}
        for stage in row['stages']:
            self.assertEqual(set(stage), {'name', 'called', 'normal', 'reference'})
        expected = REPLACE_STAGES if action['kind'] == 'replace_cost' else SCALE_STAGES if action['kind'] == 'scale_cost' else SINGLE_STAGES
        self.assertEqual(tuple(stages), expected)
        return row, stages

    def test_exact_single_manual_literals(self):
        # operation, cost, modifier bits, exact output bits, ratio, half-even argument
        cases = [
            ('mul', 3, 0x3FC00000, 0x40900000, 9, 2, 4),
            ('mul', 5, 0x3FC00000, 0x40F00000, 15, 2, 8),
            ('mul', -3, 0x3FC00000, 0xC0900000, -9, 2, -4),
            ('mul', -5, 0x3FC00000, 0xC0F00000, -15, 2, -8),
            ('mul', 1, 0x3F000000, 0x3F000000, 1, 2, 0),
            ('mul', -1, 0x3F000000, 0xBF000000, -1, 2, 0),
            ('mul', -7, 0x3F800000, 0xC0E00000, -7, 1, -7),
            ('mul', -2147483648, 0x3F800000, 0xCF000000, -2147483648, 1, -2147483648),
            ('mul', 2147483520, 0x3F800000, 0x4EFFFFFF, 2147483520, 1, 2147483520),
            ('add', 4, 0x3F000000, 0x40900000, 9, 2, 4),
            ('add', 5, 0x3F000000, 0x40B00000, 11, 2, 6),
            ('add', -4, 0xBF000000, 0xC0900000, -9, 2, -4),
            ('add', -5, 0xBF000000, 0xC0B00000, -11, 2, -6),
        ]
        for operation, cost, bits, output_bits, num, den, argument in cases:
            with self.subTest(operation=operation, cost=cost, bits=bits):
                out = self.subject.single_cost_reference(operation, cost, bits)
                self.assertEqual(set(out), SINGLE_KEYS)
                self.assertTrue(out['cost_single_exact'])
                self.assertTrue(out['binary_operation_exact'])
                self.assertEqual(out['result_single_bits'], output_bits)
                self.assertEqual((out['mathematical_numerator'], out['mathematical_denominator']), (num, den))
                self.assertEqual(out['rounded_int32_reference'], argument)

    def test_exact_zero_has_closed_integer_without_invented_signedzero(self):
        for args in [('mul', 0, 0x3FC00000), ('add', -1, 0x3F800000), ('mul', 7, 0x80000000)]:
            with self.subTest(args=args):
                out = self.subject.single_cost_reference(*args)
                self.assertEqual(out['rounded_int32_reference'], 0)
                self.assertIn(out['result_single_bits'], (None, 0, 0x80000000))

    def test_inexact_Int32_conversion_not_defaulted_to_nearest(self):
        out = self.subject.single_cost_reference('mul', 16777217, 0x3F800000)
        self.assertFalse(out['cost_single_exact'])
        self.assertIsNone(out['result_single_bits'])
        self.assertIsNone(out['rounded_int32_reference'])

    def test_inexact_operation_unknown_on_both_signs(self):
        for cost in [10, -10]:
            with self.subTest(cost=cost):
                out = self.subject.single_cost_reference('mul', cost, 0x3D4CCCCD)
                self.assertFalse(out['binary_operation_exact'])
                self.assertIsNone(out['result_single_bits'])
                self.assertIsNone(out['rounded_int32_reference'])

    def test_same_integer_interval_is_not_exact_only_qualification(self):
        out = self.subject.single_cost_reference('mul', 10, 0x3E4CCCCD)
        self.assertFalse(out['binary_operation_exact'])
        self.assertIsNone(out['rounded_int32_reference'])

    def test_nonfinite_subnormal_overflow_and_signed32_overflow_unknown(self):
        for args in [('mul', 3, 0x7FC00000), ('mul', 3, 0x7F800000), ('mul', 3, 0xFF800000),
                     ('mul', 1, 0x00000001), ('mul', 3, 0x7F7FFFFF), ('mul', 2147483647, 0x3F800000)]:
            with self.subTest(args=args):
                out = self.subject.single_cost_reference(*args)
                self.assertIsNone(out['result_single_bits'])
                self.assertIsNone(out['rounded_int32_reference'])

    def test_signed_low32_manual_literals(self):
        for cost, scale, expect in [(2147483647, 2, -2), (-2147483648, -1, -2147483648),
            (-2147483648, 2, 0), (-3, -2, 6), (17, 0, 0), (65536, 65536, 0),
            (1073741824, 4, 0), (2147483647, 1, 2147483647), (-2147483648, -2147483648, 0)]:
            with self.subTest(cost=cost, scale=scale):
                self.assertEqual(self.subject.signed_scale_reference(cost, scale),
                    {'cost_int32': cost, 'scale_int32': scale, 'product_int32_reference': expect})

    def test_scalar_typed_boundaries_reject_bool_float_range_and_unknown_operation(self):
        for bad in [True, False, 1.0, 2147483648, -2147483649]:
            with self.subTest(bad=bad):
                with self.assertRaises((ValueError, TypeError)):
                    self.subject.signed_scale_reference(bad, 1)
                with self.assertRaises((ValueError, TypeError)):
                    self.subject.single_cost_reference('mul', bad, 0x3F800000)
        for bits in [True, -1, 4294967296, 1.0]:
            with self.assertRaises((ValueError, TypeError)):
                self.subject.single_cost_reference('mul', 1, bits)
        with self.assertRaises((ValueError, TypeError)):
            self.subject.single_cost_reference('percentage', 1, 0x3F800000)

    def test_each_single_kind_has_independent_exact_encoder_argument(self):
        for kind, cost, bits, argument in [('rune_mul', 3, 0x3FC00000, 4),
                ('rune_add', 5, 0x3F000000, 6), ('relic_mul', -3, 0x3FC00000, -4)]:
            with self.subTest(kind=kind):
                row, stages = self.run_action(single_action(kind, cost=cost, bits=bits))
                self.assertEqual(row['encoder_argument_reference'], argument)
                self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-single-payload')])
                self.assertIsNone(row['update_arguments'])
                self.assertTrue(row['normal'])
                self.assertTrue(stages['store']['called'])

    def test_zero_integer_argument_does_not_skip_single_encode_or_store(self):
        row, stages = self.run_action(single_action(cost=1, bits=0x3F000000))
        self.assertEqual(row['encoder_argument_reference'], 0)
        self.assertTrue(stages['encode']['called'])
        self.assertTrue(stages['store']['called'])

    def test_skill_absent_is_normal_return_before_blackboard(self):
        action = single_action()
        action['skill_data_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertTrue(stages['skill_data_read']['normal'])
        self.assertTrue(row['normal'])
        for name in SINGLE_STAGES[3:]:
            self.assertFalse(stages[name]['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_rune_modifier_false_skips_sp_data_normally(self):
        for kind in ['rune_add', 'rune_mul']:
            with self.subTest(kind=kind):
                action = single_action(kind)
                action['modifier_read']['found'] = False
                action['sp_data_read']['normal'] = False
                row, stages = self.run_action(action)
                self.assertTrue(row['normal'])
                for name in SINGLE_STAGES[5:]:
                    self.assertFalse(stages[name]['called'])

    def test_relic_unknown_GetFloat_does_not_invent_missing_key_skip(self):
        action = single_action('relic_mul')
        action['modifier_read']['normal'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(row['normal'])
        self.assertIsNone(stages['sp_data_read']['called'])
        self.assertIsNone(stages['encode']['called'])

    def test_unknown_pointer_existence_is_not_null(self):
        action = single_action()
        action['owner_read']['exists'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(row['normal'])
        self.assertIsNone(stages['character_data_read']['called'])

    def test_unknown_identity_is_not_pointer_null(self):
        action = single_action()
        action['owner_read']['identity'] = None
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertEqual(row['encoder_argument_reference'], 4)
        self.assertTrue(stages['store']['called'])

    def test_unknown_decode_does_not_fill_from_protected_copy(self):
        action = single_action()
        action['cost_decode']['value'] = None
        row, stages = self.run_action(action)
        self.assertTrue(stages['cost_copy']['normal'])
        self.assertTrue(stages['cost_decode']['called'])
        self.assertIsNone(stages['single_conversion']['called'])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_unsafe_Single_reference_keeps_future_unknown(self):
        row, stages = self.run_action(single_action(cost=10, bits=0x3D4CCCCD))
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertIsNone(stages['round']['called'])
        self.assertIsNone(stages['encode']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_failed_encoder_has_no_store(self):
        action = single_action()
        action['encode_normally'] = False
        row, stages = self.run_action(action)
        self.assertFalse(row['normal'])
        self.assertFalse(stages['store']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_unknown_encoder_future_store_unknown(self):
        action = single_action()
        action['encode_normally'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(row['normal'])
        self.assertIsNone(stages['store']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_failed_store_retains_argument_but_does_not_claim_written_payload(self):
        action = single_action()
        action['store_normally'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['encoder_argument_reference'], 4)
        self.assertFalse(stages['store']['normal'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_scale_wrap_and_distinct_update_data_argument(self):
        row, stages = self.run_action(scale_action())
        self.assertEqual(row['encoder_argument_reference'], -2)
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-scale-payload')])
        self.assertEqual(row['update_arguments'], {'owner_identity': 'scale-update-owner',
            'sp_data_identity': 'scale-sp-data-2', 'only_update_sp_cost': True})
        self.assertTrue(stages['update']['normal'])

    def test_scale_zero_still_encodes_stores_and_updates(self):
        row, stages = self.run_action(scale_action(cost=17, scale=0))
        self.assertEqual(row['encoder_argument_reference'], 0)
        for name in ['encode', 'store', 'owner_read', 'second_data_read', 'update']:
            self.assertTrue(stages[name]['called'])

    def test_scale_null_owner_still_reads_second_data_before_guard(self):
        action = scale_action()
        action['owner_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertTrue(stages['owner_read']['normal'])
        self.assertTrue(stages['second_data_read']['called'])
        self.assertTrue(stages['second_data_read']['normal'])
        self.assertFalse(stages['update']['called'])
        self.assertFalse(row['normal'])
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-scale-payload')])

    def test_scale_second_data_unknown_keeps_known_cost_write(self):
        action = scale_action()
        action['second_data_read']['normal'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['update']['called'])
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-scale-payload')])

    def test_scale_first_spdata_null_fails_before_decode_and_encode(self):
        action = scale_action()
        action['first_sp_data_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertFalse(row['normal'])
        for name in SCALE_STAGES[2:]:
            self.assertFalse(stages[name]['called'])

    def test_scale_unknown_update_parameter_identity_does_not_invent_first_identity(self):
        action = scale_action()
        action['update_sp_data_identity'] = None
        row, stages = self.run_action(action)
        self.assertTrue(stages['update']['called'])
        self.assertIsNone(row['update_arguments']['sp_data_identity'])

    def test_replace_cost_type_and_update_use_independent_receivers(self):
        row, stages = self.run_action(replace_action())
        self.assertEqual(row['encoder_argument_reference'], -7)
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-replace-payload'), {'field': 'spType', 'value': 6}])
        self.assertEqual(row['update_arguments'], {'owner_identity': 'replace-update-owner',
            'sp_data_identity': 'replace-sp-data-3', 'only_update_sp_cost': False})
        self.assertTrue(stages['update']['normal'])

    def test_replace_first_spdata_null_does_not_skip_encoder(self):
        action = replace_action()
        action['first_sp_data_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertTrue(stages['first_sp_data_read']['normal'])
        self.assertTrue(stages['encode']['called'])
        self.assertTrue(stages['encode']['normal'])
        self.assertTrue(stages['first_sp_data_check']['called'])
        self.assertTrue(stages['first_sp_data_check']['normal'])
        self.assertEqual(stages['first_sp_data_check']['reference'], {'exists': False})
        self.assertFalse(stages['store']['called'])
        self.assertFalse(row['normal'])

    def test_replace_unknown_encoder_keeps_later_null_check_unknown(self):
        action = replace_action()
        action['first_sp_data_read']['exists'] = False
        action['encode_normally'] = None
        row, stages = self.run_action(action)
        self.assertIsNone(stages['first_sp_data_check']['called'])
        self.assertIsNone(stages['store']['called'])
        self.assertIsNone(row['normal'])

    def test_replace_no_type_change_skips_second_reads_and_only_cost_true(self):
        row, stages = self.run_action(replace_action(modify_type=False))
        for name in ['second_data_read', 'second_sp_data_read', 'type_value_read', 'type_store']:
            self.assertFalse(stages[name]['called'])
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-replace-payload')])
        self.assertTrue(row['update_arguments']['only_update_sp_cost'])

    def test_replace_Unity_false_is_normal_return_after_writes(self):
        action = replace_action()
        action['unity_truth_read']['value'] = False
        row, stages = self.run_action(action)
        self.assertTrue(row['normal'])
        self.assertEqual(len(row['stored_prefixes']), 2)
        self.assertIsNone(row['update_arguments'])
        for name in ['second_owner_read', 'third_data_read', 'update']:
            self.assertFalse(stages[name]['called'])

    def test_replace_Unity_truth_unknown_does_not_infer_from_nonnull_owner(self):
        action = replace_action()
        action['unity_truth_read']['value'] = None
        row, stages = self.run_action(action)
        self.assertTrue(stages['first_owner_read']['normal'])
        self.assertIsNone(stages['second_owner_read']['called'])
        self.assertIsNone(stages['update']['called'])
        self.assertEqual(len(row['stored_prefixes']), 2)

    def test_replace_null_second_owner_still_reads_third_data_before_guard(self):
        action = replace_action()
        action['second_owner_read']['exists'] = False
        row, stages = self.run_action(action)
        self.assertTrue(stages['second_owner_read']['normal'])
        self.assertTrue(stages['third_data_read']['called'])
        self.assertTrue(stages['third_data_read']['normal'])
        self.assertFalse(stages['update']['called'])
        self.assertFalse(row['normal'])
        self.assertEqual(len(row['stored_prefixes']), 2)

    def test_replace_unknown_type_value_keeps_qualified_direct_write(self):
        action = replace_action()
        action['type_value_read']['value'] = None
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-replace-payload'), {'field': 'spType', 'value': None}])
        self.assertTrue(stages['type_value_read']['normal'])
        self.assertTrue(stages['type_store']['called'])
        self.assertTrue(stages['type_store']['normal'])
        self.assertTrue(stages['first_owner_read']['called'])
        self.assertTrue(stages['update']['called'])
        self.assertFalse(row['update_arguments']['only_update_sp_cost'])

    def test_replace_type_store_failure_preserves_cost_write(self):
        action = replace_action()
        action['type_store_normally'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-replace-payload')])
        self.assertFalse(stages['first_owner_read']['called'])
        self.assertFalse(row['normal'])

    def test_replace_second_data_failure_preserves_cost_write(self):
        action = replace_action()
        action['second_data_read']['normal'] = False
        row, stages = self.run_action(action)
        self.assertEqual(row['stored_prefixes'], [cost_prefix('opaque-replace-payload')])
        self.assertFalse(stages['second_sp_data_read']['called'])
        self.assertFalse(stages['first_owner_read']['called'])

    def test_update_failure_does_not_undo_already_written_cost_or_type(self):
        action = replace_action()
        action['update_normally'] = False
        row, stages = self.run_action(action)
        self.assertFalse(stages['update']['normal'])
        self.assertEqual(len(row['stored_prefixes']), 2)
        self.assertIsNotNone(row['update_arguments'])

    def test_replace_unnamed_type_bit_is_not_enum_clamped(self):
        row, stages = self.run_action(replace_action(sp_type=8))
        self.assertEqual(row['stored_prefixes'][1], {'field': 'spType', 'value': 8})
        self.assertTrue(stages['type_store']['normal'])

    def test_second_action_cost_is_independent_of_previous_encode_argument(self):
        first = single_action(label='first', cost=3)
        second = single_action(label='second', cost=-7, bits=0x3F800000)
        out = self.subject.skill_data_cost_reference(payload(first, second))
        self.assertEqual([row['encoder_argument_reference'] for row in out['rows']], [4, -7])
        self.assertIsNone(out['actual_cost_after'])

    def test_two_step_rounds_are_not_collapsed_into_product(self):
        first = single_action(label='first', cost=1)
        second = single_action(label='second', cost=2)
        out = self.subject.skill_data_cost_reference(payload(first, second))
        self.assertEqual([row['encoder_argument_reference'] for row in out['rows']], [2, 3])
        self.assertIsNone(out['actual_cost_after'])

    def test_unqualified_native_path_does_not_claim_numeric_or_store(self):
        for path in [False, None]:
            with self.subTest(path=path):
                action = scale_action()
                action['ordinary_native_path'] = path
                row, stages = self.run_action(action)
                self.assertIsNone(row['encoder_argument_reference'])
                self.assertEqual(row['stored_prefixes'], [])
                self.assertIsNone(row['update_arguments'])
                self.assertIn(stages['imul']['called'], [False, None])

    def test_no_public_source_data_injection(self):
        with self.assertRaises(TypeError):
            self.subject.skill_data_cost_reference(payload(scale_action()), data={})

    def assert_invalid_source_has_no_references(self):
        self.assertFalse(self.subject.source_data()['valid'])
        self.assertIsNone(self.subject.single_cost_reference('mul', 3, 0x3FC00000))
        self.assertIsNone(self.subject.signed_scale_reference(2147483647, 2))
        actions = [single_action('rune_add', 'add'), single_action('rune_mul', 'mul'),
                   single_action('relic_mul', 'relic'), scale_action(), replace_action()]
        out = self.subject.skill_data_cost_reference(payload(*actions))
        self.assertFalse(out['source']['valid'])
        self.assertEqual(len(out['rows']), 5)
        for row in out['rows']:
            self.assertIsNone(row['arithmetic_reference'])
            self.assertIsNone(row['encoder_argument_reference'])
            self.assertEqual(row['stored_prefixes'], [])
            self.assertIsNone(row['update_arguments'])
            for stage in row['stages']:
                self.assertIsNone(stage['reference'])
            for key in ACTUAL_UNKNOWNS:
                self.assertIsNone(row[key])
        for key in ACTUAL_UNKNOWNS:
            self.assertIsNone(out[key])
        # A failed source cannot be overridden through a public payload or kwarg.
        supplied = payload(scale_action())
        supplied['source'] = {'valid': True}
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_data_cost_reference(supplied)
        with self.assertRaises(TypeError):
            self.subject.skill_data_cost_reference(payload(scale_action()), data={'valid': True})

    def test_source_one_byte_proof_or_manifest_tamper_blocks_all_references(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json')
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for changed in names:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory(prefix='rouge278-public-source-') as folder:
                target = Path(folder)
                for name in names:
                    shutil.copyfile(original / name, target / name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assertTrue(self.subject.source_data()['valid'])
                    raw = bytearray((target / changed).read_bytes())
                    raw[0] ^= 1
                    (target / changed).write_bytes(raw)
                    self.assert_invalid_source_has_no_references()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})

    def test_source_missing_proof_or_manifest_blocks_all_references(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json')
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for missing in names:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(prefix='rouge278-public-source-') as folder:
                target = Path(folder)
                for name in names:
                    if name != missing:
                        shutil.copyfile(original / name, target / name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assert_invalid_source_has_no_references()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})

    def test_duplicate_ids_and_bool_values_rejected(self):
        first, second = scale_action('one'), scale_action('two')
        second['scale_read']['id'] = first['cost_decode']['id']
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_data_cost_reference(payload(first, second))
        for action in [scale_action(), replace_action()]:
            if action['kind'] == 'scale_cost':
                action['scale_read']['value'] = True
            else:
                action['new_cost'] = True
            with self.assertRaises((ValueError, TypeError)):
                self.subject.skill_data_cost_reference(payload(action))

    def test_read_schema_does_not_treat_unknown_identity_as_exists(self):
        action = replace_action()
        del action['first_owner_read']['exists']
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_data_cost_reference(payload(action))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    spec = importlib.util.spec_from_file_location('independent_cost_subject_278', args.module_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    IndependentCostTests.subject = module
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__':
    main()
