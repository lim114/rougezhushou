"""Independent parent controls; numerical dependency author is this reviewer.

This does not independently re-audit panel_native_precision or claim actual
game/Windows state. Production is the default; candidates require explicit path.
"""
import argparse
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
import uuid

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
MODULE_FILE = ROOT / 'rouge/panel_native_finalization.py'
Q = 4294967296
MAX_FP = 9223372036854775806
MIN_I64 = -(1 << 63)
MAIN_REFS = ('input_fp_raw', 'after_add_raw', 'multiplier_raw', 'after_multiplier_raw',
             'after_final_add_raw', 'after_final_scaler_raw', 'clamped_raw',
             'getter_result_raw', 'as_float', 'writer')
FIELDS = ('hp', 'attack', 'defense', 'resistance', 'attack_speed')
FIELD_FACTS = {'hp': ('ObscuredInt', Q, MAX_FP),
               'attack': ('ObscuredInt', 0, MAX_FP),
               'defense': ('ObscuredInt', 0, MAX_FP),
               'resistance': ('ObscuredFloat', 0, 100 * Q),
               'attack_speed': ('ObscuredFloat', 20 * Q, MAX_FP)}


def load_module(path):
    path = Path(path).resolve(strict=True)
    name = 'panel283_independent_' + uuid.uuid4().hex
    package = types.ModuleType(name)
    package.__path__ = [str(path.parent)]
    package.__package__ = name
    package.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
    sys.modules[name] = package
    spec = importlib.util.spec_from_file_location(name + '.panel_native_finalization', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, name


def unload_package(name):
    for key in tuple(sys.modules):
        if key == name or key.startswith(name + '.'):
            sys.modules.pop(key, None)


def field(label='panel', field='attack', phase='normal', raw=10 * Q, **values):
    row = {'id': label, 'field': field, 'phase': phase, 'model_value': 10,
           'basis_kind': 'nominal_fp', 'basis_single_bits': None, 'basis_fp_raw': raw,
           'addition_raw': 0, 'multiplier_delta_raw': 0, 'final_addition_raw': 0,
           'final_scaler_raw': Q}
    row.update(values)
    return row


def read(route='ObscuredInt', **values):
    row = {'value_exists': True, 'object_type_normal': True, 'int_type_normal': True,
           'int_assignable': {'normal': True, 'value': route == 'ObscuredInt'},
           'float_type_normal': True,
           'float_assignable': {'normal': True, 'value': route == 'ObscuredFloat'},
           'unbox_normal': True, 'decode_normal': True, 'int_to_single_normal': True,
           'decoded_int32': 10, 'decoded_single_bits': 0x41200000,
           'fallback_normal': True, 'fallback_bits': 0x40a00000}
    row.update(values)
    return row


def write(kind='ObscuredInt', raw=10 * Q, **values):
    row = {'fp_raw': raw, 'field_exists': True, 'as_float_normal': True,
           'field_type_read': {'normal': True, 'value': kind}, 'type_route_normal': True,
           'round_normal': True, 'encode_normal': True, 'copy_normal': True,
           'box_normal': True, 'set_value_normal': True}
    row.update(values)
    return row


def iteration(label='iteration', *, kind='ObscuredInt'):
    writer = write(kind)
    writer.pop('fp_raw'); writer.pop('field_exists')
    return {'id': label,
            'first_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                           'item_exists': True, 'field_read_normal': True, 'field_exists': True},
            'second_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                            'item_exists': True, 'range_read_normal': True, 'range_exists': True,
                            'attribute_read_normal': True, 'attribute': 1},
            'reflection_get_normal': True, 'read_field': read(), 'single_to_fp_normal': True,
            'arrays': {name: {'read_normal': True, 'exists': True, 'length': 8,
                              'element_normal': True, 'raw': Q if name == 'scaler' else 0}
                       for name in ('addition', 'multiplier', 'scaler')},
            'range_read': {'normal': True, 'lower_raw': 0, 'upper_raw': MAX_FP}, 'clamp_normal': True,
            'writer': writer}


def manager(*rows, **values):
    row = {'ordinary_native_path': True,
           'initial_metas': {'get_normal': True, 'exists': True, 'count_normal': True,
                             'count': len(rows)}, 'iterations': list(rows)}
    row.update(values)
    return row


def stage(row, name):
    return next(s for s in row['stages'] if s['name'] == name)


class IndependentPanelParentTests(unittest.TestCase):
    subject = None
    package_name = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:
            cls.subject, cls.package_name = load_module(MODULE_FILE)
        if cls.subject.source_data() is None:
            raise AssertionError('default or explicit candidate source binding must be valid')

    @classmethod
    def tearDownClass(cls):
        if cls.package_name:
            unload_package(cls.package_name)

    def main(self, *rows):
        return self.subject.panel_native_finalization({'fields': list(rows)})

    def test_main_all17_field_phase_pairs_preserve_model_and_unknown_actuals(self):
        rows = [field(phase + '-' + name, name, phase, raw=100 * Q, model_value=123.25)
                for phase in ('cultivation', 'rune', 'normal', 'skill') for name in FIELDS
                if phase != 'skill' or name in ('attack', 'attack_speed')]
        result = self.main(*rows)
        self.assertTrue(result['source_valid'])
        self.assertEqual(len(result['fields']), 17)
        self.assertFalse(result['complete_native_panel'])
        self.assertIsNone(result['actual_panel'])
        self.assertEqual(set(result), {'source_valid', 'fields', 'complete_native_panel', 'actual_panel', 'limitations'})
        for source, row in zip(rows, result['fields']):
            self.assertEqual({key: row[key] for key in ('id', 'field', 'phase', 'model_value')},
                             {key: source[key] for key in ('id', 'field', 'phase', 'model_value')})
            self.assertEqual(row['basis'], 'nominal_model_snapshot')
            storage, lower, upper = FIELD_FACTS[row['field']]
            self.assertEqual(row['storage_type'], storage)
            self.assertEqual(row['metadata_range'], {'lower_raw': lower, 'upper_raw': upper})
            self.assertEqual(tuple(row['references']), MAIN_REFS)
            self.assertTrue(row['conditional_complete'])
            self.assertFalse(row['complete_native_value'])
            self.assertIsNone(row['actual_decoded_value'])
            self.assertIsNone(row['actual_getter_raw'])

    def test_cultivation_does_not_invent_range_recompute_or_typed_writer(self):
        result = self.main(field('hp-zero', 'hp', 'cultivation', 0),
                           field('negative', 'attack', 'cultivation', -Q))
        for row, expected in zip(result['fields'], (0, -Q)):
            self.assertEqual(row['references']['input_fp_raw'], expected)
            self.assertTrue(all(row['references'][name] is None for name in MAIN_REFS[1:]))

    def test_rune_three_buckets_and_ordinary_max_zero_are_distinct(self):
        common = {'addition_raw': 2 * Q, 'multiplier_delta_raw': -2 * Q, 'final_scaler_raw': -Q}
        rune, normal = self.main(field('rune', phase='rune', **common),
                                 field('normal', final_addition_raw=5 * Q, **common))['fields']
        self.assertEqual(rune['references']['multiplier_raw'], -Q)
        self.assertEqual(rune['references']['after_multiplier_raw'], -12 * Q)
        self.assertEqual(rune['references']['clamped_raw'], 12 * Q)
        self.assertEqual(rune['references']['writer']['encoder_argument_reference'], 12)
        self.assertEqual(normal['references']['multiplier_raw'], 0)
        self.assertEqual(normal['references']['after_final_add_raw'], 5 * Q)
        self.assertEqual(normal['references']['getter_result_raw'], 0)
        self.assertIsNone(normal['references']['writer'])

    def test_final_addition_is_ordinary_fourth_bucket_before_final_scaler(self):
        row = self.main(field(addition_raw=2 * Q, multiplier_delta_raw=Q // 2,
                              final_addition_raw=3 * Q, final_scaler_raw=2 * Q))['fields'][0]
        ref = row['references']
        self.assertEqual([ref[k] for k in ('after_add_raw', 'after_multiplier_raw',
                                         'after_final_add_raw', 'after_final_scaler_raw')],
                         [12 * Q, 18 * Q, 21 * Q, 42 * Q])
        self.assertEqual(ref['getter_result_raw'], 42 * Q)

    def test_metadata_hp_mr_and_as_ranges_do_not_import_timing_cap(self):
        inputs = [field('hp', 'hp', raw=-Q), field('mr', 'resistance', raw=120 * Q),
                  field('as-low', 'attack_speed', raw=-Q), field('as-high', 'attack_speed', raw=700 * Q),
                  field('atk', 'attack', raw=-Q), field('def', 'defense', raw=-Q)]
        rows = self.main(*inputs)['fields']
        self.assertEqual([r['references']['getter_result_raw'] for r in rows],
                         [Q, 100 * Q, 20 * Q, 700 * Q, 0, 0])
        self.assertEqual(rows[3]['metadata_range'], {'lower_raw': 20 * Q, 'upper_raw': MAX_FP})
        upper_rows = self.main(*[field('upper-' + name, name, raw=(1 << 63) - 1)
                                 for name in ('hp', 'attack', 'defense', 'attack_speed')])['fields']
        self.assertEqual([r['references']['getter_result_raw'] for r in upper_rows], [MAX_FP] * 4)

    def test_signed_wrap_precedes_metadata_clamp(self):
        row = self.main(field(raw=MAX_FP, addition_raw=4))['fields'][0]
        self.assertEqual(row['references']['after_add_raw'], MIN_I64 + 2)
        self.assertEqual(row['references']['getter_result_raw'], 0)

    def test_nominal_single_and_unknown_inputs_never_alias_previous_writer(self):
        rows = self.main(field('single', phase='cultivation', raw=None, basis_kind='nominal_single',
                               basis_single_bits=0x3fc00000),
                         field('unknown', raw=None),
                         field('zero-closes', raw=None, final_scaler_raw=0))['fields']
        self.assertEqual(rows[0]['references']['input_fp_raw'], 3 * Q // 2)
        self.assertIsNone(rows[1]['references']['getter_result_raw'])
        self.assertFalse(rows[1]['conditional_complete'])
        self.assertEqual(rows[2]['references']['getter_result_raw'], 0)
        self.assertTrue(rows[2]['conditional_complete'])

    def test_rune_writer_type_bytes_and_float_ambiguity_are_separate(self):
        integer, floating = self.main(field('integer', phase='rune', raw=Q // 2 + 1),
                                      field('float', 'resistance', 'rune', raw=Q // 2 + 1))['fields']
        self.assertEqual(integer['storage_type'], 'ObscuredInt')
        self.assertEqual(integer['references']['writer']['copied_byte_count_reference'], 20)
        self.assertIsNone(integer['references']['writer']['encoder_argument_reference'])
        self.assertEqual(floating['storage_type'], 'ObscuredFloat')
        self.assertEqual(floating['references']['writer']['copied_byte_count_reference'], 24)
        self.assertIsNone(floating['references']['writer']['encoder_argument_bits_reference'])
        self.assertFalse(integer['conditional_complete'])
        self.assertFalse(floating['conditional_complete'])

    def test_parent_single_to_fp_domain_is_not_unknown_to_zero_coercion(self):
        bits = [0, 0x80000000, 1, 0x7f800000, 0x7fc00000, 0x4f000000, 0xcf000000]
        expected = [0, 0, None, None, None, None, MIN_I64]
        rows = self.main(*[field(str(b), phase='cultivation', raw=None, basis_kind='nominal_single',
                                 basis_single_bits=b) for b in bits])['fields']
        self.assertEqual([r['references']['input_fp_raw'] for r in rows], expected)
        self.assertEqual([r['conditional_complete'] for r in rows], [x is not None for x in expected])

    def test_main_strict_input_shape_scope_width_and_neutral_buckets(self):
        variants = []
        row = field(); row['source'] = {}; variants.append({'fields': [row]})
        variants.extend([{'fields': [], 'data': {}}, {'fields': [], 'evaluator': None},
                         {'fields': [field(), field()]},
                         {'fields': [field(field='hp', phase='skill')]},
                         {'fields': [field(phase='rune', final_addition_raw=Q)]},
                         {'fields': [field(phase='cultivation', addition_raw=Q)]},
                         {'fields': [field(basis_single_bits=0)]},
                         {'fields': [field(model_value=True)]},
                         {'fields': [field(model_value=float('inf'))]},
                         {'fields': [field(raw=1 << 63)]},
                         {'fields': [field(addition_raw=True)]}])
        for payload in variants:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.subject.panel_native_finalization(payload)
        self.assertEqual(self.main()['fields'], [])

    def test_read_null_returns_zero_without_type_or_decode(self):
        row = self.subject.read_field_reference(read(value_exists=False))
        self.assertTrue(row['normal'])
        self.assertEqual(row['route'], 'null_zero')
        self.assertEqual(row['single_bits_candidates'], [0])
        self.assertTrue(stage(row, 'argument_null_check')['called'])
        self.assertTrue(all(s['called'] is False for s in row['stages'][1:]))
        self.assertIsNone(row['actual_decoded_value'])

    def test_read_integer_conversion_is_independent_of_decoder(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = self.subject.read_field_reference(read(int_to_single_normal=normal))
                self.assertTrue(stage(row, 'decode')['normal'])
                self.assertTrue(stage(row, 'int_to_single')['called'])
                self.assertIs(stage(row, 'int_to_single')['normal'], normal)
                self.assertIs(row['normal'], normal)
                self.assertEqual(row['single_bits_candidates'], [])
                self.assertFalse(stage(row, 'float_target_type')['called'])
                self.assertFalse(stage(row, 'fallback_convert')['called'])

    def test_read_type_routing_uses_independent_boolean_results(self):
        floating = self.subject.read_field_reference(read('ObscuredFloat', decoded_single_bits=0x40e00000))
        fallback = self.subject.read_field_reference(read('fallback', fallback_bits=0x40800000))
        self.assertEqual(floating['route'], 'ObscuredFloat')
        self.assertEqual(floating['single_bits_candidates'], [0x40e00000])
        self.assertFalse(stage(floating, 'int_to_single')['called'])
        self.assertEqual(fallback['route'], 'Convert.ToSingle')
        self.assertEqual(fallback['single_bits_candidates'], [0x40800000])
        self.assertFalse(stage(fallback, 'decode')['called'])

    def test_read_unknown_predicate_and_failed_callee_have_distinct_future(self):
        unknown = self.subject.read_field_reference(read(int_assignable={'normal': True, 'value': None}))
        failed = self.subject.read_field_reference(read(object_type_normal=False))
        self.assertIsNone(unknown['normal'])
        self.assertIsNone(stage(unknown, 'float_target_type')['called'])
        self.assertIsNone(stage(unknown, 'decode')['called'])
        self.assertFalse(failed['normal'])
        self.assertFalse(stage(failed, 'int_target_type')['called'])
        self.assertFalse(stage(failed, 'decode')['called'])

    def test_read_normal_opaque_unknown_does_not_manufacture_value(self):
        for payload in (read(decoded_int32=None), read('ObscuredFloat', decoded_single_bits=None),
                        read('fallback', fallback_bits=None)):
            with self.subTest(payload=payload):
                row = self.subject.read_field_reference(payload)
                self.assertTrue(row['normal'])
                self.assertEqual(row['single_bits_candidates'], [])
                self.assertIsNone(row['actual_decoded_value'])

    def test_write_asfloat_precedes_null_field_guard(self):
        row = self.subject.write_field_reference(write(field_exists=False))
        self.assertTrue(stage(row, 'as_float')['called'])
        self.assertTrue(stage(row, 'as_float')['normal'])
        self.assertIsNotNone(row['as_float_reference'])
        self.assertFalse(stage(row, 'field_null_check')['normal'])
        self.assertFalse(stage(row, 'field_type_read')['called'])
        self.assertFalse(row['normal'])

    def test_write_expected_type_route_has_own_normality(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = self.subject.write_field_reference(write(type_route_normal=normal))
                self.assertTrue(stage(row, 'field_type_read')['normal'])
                self.assertIs(stage(row, 'type_route')['normal'], normal)
                self.assertIs(stage(row, 'round')['called'], False if normal is False else None)
                self.assertIs(row['normal'], normal)

    def test_write_asfloat_failure_and_unknown_type_leave_distinct_future(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = self.subject.write_field_reference(write(field_exists=False, as_float_normal=normal))
                self.assertIs(stage(row, 'field_null_check')['called'], False if normal is False else None)
                self.assertIs(row['normal'], normal)
        row = self.subject.write_field_reference(write(field_type_read={'normal': True, 'value': None}))
        self.assertTrue(stage(row, 'type_route')['normal'])
        self.assertIsNone(stage(row, 'box')['called'])
        self.assertIsNone(stage(row, 'set_value')['called'])
        self.assertIsNone(row['return_boolean'])

    def test_write_unsupported_returns_false_normally_without_setter(self):
        row = self.subject.write_field_reference(write('unsupported'))
        self.assertTrue(row['normal'])
        self.assertIs(row['return_boolean'], False)
        for name in ('round', 'encode', 'struct_copy', 'box', 'set_value'):
            self.assertFalse(stage(row, name)['called'])

    def test_write_int_primitive_boxes_double_without_protected_encoder(self):
        row = self.subject.write_field_reference(write('Int32', raw=3 * Q // 2))
        self.assertTrue(row['normal'])
        self.assertEqual(row['boxed_type_reference'], 'Double')
        self.assertTrue(stage(row, 'round')['called'])
        self.assertFalse(stage(row, 'encode')['called'])
        self.assertFalse(stage(row, 'struct_copy')['called'])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertIsNone(row['stored_prefix'])
        self.assertTrue(row['return_boolean'])
        unknown_round = self.subject.write_field_reference(write('Int32', round_normal=None))
        self.assertFalse(stage(unknown_round, 'encode')['called'])
        self.assertFalse(stage(unknown_round, 'struct_copy')['called'])
        self.assertIsNone(stage(unknown_round, 'box')['called'])

    def test_write_float_primitive_is_not_protected_struct_copy(self):
        row = self.subject.write_field_reference(write('Single'))
        self.assertTrue(row['normal'])
        self.assertEqual(row['boxed_type_reference'], 'Single')
        self.assertFalse(stage(row, 'round')['called'])
        self.assertFalse(stage(row, 'encode')['called'])
        self.assertFalse(stage(row, 'struct_copy')['called'])
        self.assertIsNone(row['stored_prefix'])

    def test_write_protected_types_have_distinct_completed_copy_prefixes(self):
        for kind, count in (('ObscuredInt', 20), ('ObscuredFloat', 24)):
            with self.subTest(kind=kind):
                row = self.subject.write_field_reference(write(kind))
                self.assertTrue(row['normal'])
                self.assertTrue(row['return_boolean'])
                self.assertEqual(row['stored_prefix']['kind'], 'protected_struct_copy')
                self.assertEqual(row['stored_prefix']['byte_count'], count)
                self.assertIsNone(row['actual_decoded_value'])

    def test_write_normal_unknown_number_retains_opaque_chain_not_fake_zero(self):
        row = self.subject.write_field_reference(write(raw=None))
        self.assertTrue(row['normal'])
        self.assertTrue(row['return_boolean'])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertEqual(row['stored_prefix'], {'kind': 'protected_struct_copy', 'byte_count': 20,
                                               'encoder_argument_reference': None})
        self.assertTrue(stage(row, 'set_value')['normal'])

    def test_write_late_setter_failure_retains_completed_temporary_copy(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = self.subject.write_field_reference(write(set_value_normal=normal))
                self.assertIs(row['normal'], normal)
                self.assertEqual(row['stored_prefix']['byte_count'], 20)
                self.assertEqual(row['encoder_argument_reference'], 10)
                self.assertIsNone(row['return_boolean'])
                self.assertIsNone(row['actual_decoded_value'])
        failed_copy = self.subject.write_field_reference(write(copy_normal=False))
        self.assertIsNone(failed_copy['stored_prefix'])
        self.assertFalse(stage(failed_copy, 'box')['called'])

    def test_manager_void_ignores_normal_false_writer_and_continues(self):
        payload = manager(iteration('first', kind='unsupported'), iteration('second'))
        result = self.subject.manager_flow_reference(payload)
        self.assertTrue(result['normal'])
        self.assertNotIn('return_boolean', result)
        self.assertFalse(result['complete_native_panel'])
        self.assertIsNone(result['actual_attributes'])
        first, second = result['rows']
        self.assertFalse(first['writer_reference']['return_boolean'])
        self.assertTrue(first['loop_continues_reference'])
        self.assertTrue(stage(second, 'first_metas_get')['called'])
        self.assertTrue(second['normal'])

    def test_manager_missing_second_range_skips_before_first_field_null(self):
        first = iteration('skipped'); first['first_meta']['field_exists'] = False
        first['second_meta']['range_exists'] = False
        result = self.subject.manager_flow_reference(manager(first, iteration('next')))
        row, following = result['rows']
        self.assertTrue(row['normal'])
        self.assertTrue(stage(row, 'range_meta_check')['normal'])
        self.assertFalse(stage(row, 'field_null_check')['called'])
        self.assertFalse(stage(row, 'attribute_read')['called'])
        self.assertTrue(row['loop_continues_reference'])
        self.assertIsNone(row['writer_reference'])
        self.assertTrue(following['normal'])
        present = iteration('field-null'); present['first_meta']['field_exists'] = False
        checked = self.subject.manager_flow_reference(manager(present))['rows'][0]
        self.assertTrue(stage(checked, 'attribute_read')['called'])
        self.assertFalse(stage(checked, 'field_null_check')['normal'])
        self.assertFalse(stage(checked, 'reflection_get')['called'])
        self.assertFalse(stage(checked['writer_reference'], 'as_float')['called'])

    def test_manager_two_metadata_reads_cannot_share_normality_or_item(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = iteration(); row['second_meta']['item_normal'] = normal
                result = self.subject.manager_flow_reference(manager(row))['rows'][0]
                self.assertTrue(stage(result, 'field_read')['normal'])
                self.assertIs(stage(result, 'second_item_get')['normal'], normal)
                self.assertIs(stage(result, 'reflection_get')['called'], False if normal is False else None)

    def test_manager_unknown_range_predicate_does_not_become_normal_skip(self):
        row = iteration(); row['first_meta']['field_exists'] = False
        row['second_meta']['range_exists'] = None
        result = self.subject.manager_flow_reference(manager(row))['rows'][0]
        self.assertTrue(stage(result, 'range_meta_check')['normal'])
        self.assertIsNone(stage(result, 'field_null_check')['called'])
        self.assertIsNone(stage(result, 'loop_increment')['called'])
        self.assertIsNone(result['loop_continues_reference'])
        self.assertIsNone(result['normal'])

    def test_manager_range_get_does_not_establish_subsequent_clamp_normality(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = iteration(); row['clamp_normal'] = normal
                result = self.subject.manager_flow_reference(manager(row))['rows'][0]
                self.assertTrue(stage(result, 'range_get')['normal'])
                self.assertIs(stage(result, 'clamp')['normal'], normal)
                self.assertEqual(result['arithmetic_reference']['after_scaler_raw'], 10 * Q)
                self.assertIsNone(result['arithmetic_reference']['clamped_raw'])
                self.assertIs(stage(result, 'write_attributes_field')['called'], False if normal is False else None)
                self.assertIsNone(result['writer_reference']['encoder_argument_reference'])

    def test_manager_three_bucket_negative_multiplier_and_independent_range(self):
        row = iteration()
        row['arrays']['addition']['raw'] = 2 * Q
        row['arrays']['multiplier']['raw'] = -2 * Q
        row['arrays']['scaler']['raw'] = -Q
        row['range_read'] = {'normal': True, 'lower_raw': 0, 'upper_raw': 11 * Q}
        result = self.subject.manager_flow_reference(manager(row))['rows'][0]
        self.assertEqual(result['arithmetic_reference'], {'basis_raw': 10 * Q, 'after_add_raw': 12 * Q,
                         'multiplier_raw': -Q, 'after_multiplier_raw': -12 * Q,
                         'after_scaler_raw': 12 * Q, 'clamped_raw': 11 * Q})
        self.assertEqual(result['writer_reference']['encoder_argument_reference'], 11)

    def test_manager_negative_attribute_uses_unsigned_index_bounds(self):
        row = iteration(); row['second_meta']['attribute'] = -1
        result = self.subject.manager_flow_reference(manager(row))['rows'][0]
        bounds = stage(result, 'addition_bounds')
        self.assertEqual(bounds['reference']['unsigned_index'], 4294967295)
        self.assertFalse(bounds['normal'])
        self.assertFalse(stage(result, 'addition_element')['called'])
        self.assertFalse(stage(result, 'write_attributes_field')['called'])

    def test_manager_arrays_independent_and_late_failure_preserves_arguments(self):
        for name in ('addition', 'multiplier', 'scaler'):
            with self.subTest(name=name):
                row = iteration(); row['arrays'][name]['exists'] = False
                result = self.subject.manager_flow_reference(manager(row))['rows'][0]
                self.assertTrue(stage(result, name + '_array_read')['called'])
                self.assertFalse(stage(result, name + '_array_check')['normal'])
                self.assertFalse(stage(result, name + '_element')['called'])
                self.assertFalse(stage(result, 'write_attributes_field')['called'])
        for normal in (False, None):
            with self.subTest(setter_normal=normal):
                row = iteration(); row['writer']['set_value_normal'] = normal
                result = self.subject.manager_flow_reference(manager(row, iteration('next')))
                first, following = result['rows']
                self.assertEqual(first['arithmetic_reference']['clamped_raw'], 10 * Q)
                self.assertEqual(first['writer_reference']['stored_prefix']['byte_count'], 20)
                self.assertIs(stage(first, 'loop_increment')['called'], False if normal is False else None)
                self.assertIs(stage(following, 'first_metas_get')['called'], False if normal is False else None)

    def test_manager_unknown_qualification_and_count_preserve_unknown_future(self):
        result = self.subject.manager_flow_reference(manager(iteration(), ordinary_native_path=None))
        self.assertIsNone(result['normal'])
        self.assertTrue(all(s['called'] is None for s in result['stages']))
        self.assertIsNone(stage(result['rows'][0], 'reflection_get')['called'])
        payload = manager(iteration()); payload['initial_metas']['count'] = None
        result = self.subject.manager_flow_reference(payload)
        self.assertTrue(stage(result, 'initial_count')['called'])
        self.assertIsNone(stage(result['rows'][0], 'first_metas_get')['called'])
        for count in (0, -3):
            payload = manager(); payload['initial_metas']['count'] = count
            result = self.subject.manager_flow_reference(payload)
            self.assertTrue(result['normal']); self.assertEqual(result['rows'], [])

    def test_manager_opaque_read_and_reverse_range_can_close_without_decode_alias(self):
        row = iteration(); row['read_field']['decoded_int32'] = None
        row['range_read'] = {'normal': True, 'lower_raw': 5 * Q, 'upper_raw': 2 * Q}
        result = self.subject.manager_flow_reference(manager(row))['rows'][0]
        self.assertTrue(result['normal'])
        self.assertIsNone(result['arithmetic_reference']['basis_raw'])
        self.assertEqual(result['arithmetic_reference']['clamped_raw'], 5 * Q)
        self.assertEqual(result['writer_reference']['encoder_argument_reference'], 5)
        self.assertIsNone(result['actual_attributes'])

    def test_strict_flows_reject_source_overrides_aliases_and_partial_count(self):
        cases = []
        for function, payload in ((self.subject.read_field_reference, read()),
                                  (self.subject.write_field_reference, write()),
                                  (self.subject.manager_flow_reference, manager(iteration()))):
            for key in ('source', 'data', 'evaluator'):
                altered = copy.deepcopy(payload); altered[key] = None; cases.append((function, altered))
        payload = manager(iteration()); payload['initial_metas']['count'] = 2
        cases.append((self.subject.manager_flow_reference, payload))
        payload = manager(iteration()); payload['iterations'][0]['writer']['fp_raw'] = 3 * Q
        cases.append((self.subject.manager_flow_reference, payload))
        payload = manager(iteration()); payload['iterations'][0]['writer']['field_exists'] = False
        cases.append((self.subject.manager_flow_reference, payload))
        payload = read(); payload['int_assignable']['normal'] = 1
        cases.append((self.subject.read_field_reference, payload))
        payload = write(); payload['type_route_normal'] = 1
        cases.append((self.subject.write_field_reference, payload))
        for function, payload in cases:
            with self.subTest(function=function.__name__, payload=payload), self.assertRaises(ValueError):
                function(payload)
        with self.assertRaises(TypeError): self.subject.panel_native_finalization({'fields': []}, data={})
        with self.assertRaises(TypeError): self.subject.source_data(source={})

    def test_all_input_payloads_remain_unchanged(self):
        for function, payload in ((self.subject.panel_native_finalization, {'fields': [field()]}),
                                  (self.subject.read_field_reference, read()),
                                  (self.subject.write_field_reference, write()),
                                  (self.subject.manager_flow_reference, manager(iteration()))):
            before = copy.deepcopy(payload)
            function(payload)
            self.assertEqual(payload, before)

    def pin_paths(self):
        root = Path(self.subject.__file__).resolve().parents[1]
        manifest = Path(self.subject.SOURCE)
        data = self.subject.source_data()
        self.assertIsNotNone(data)
        paths = [Path(name) for name in data['files']] + [manifest]
        self.assertEqual(len(paths), len(set(paths)))
        for path in paths:
            self.assertFalse(path.is_absolute())
            self.assertTrue((root / path).resolve().is_relative_to(root))
        return root, paths

    def clone_public(self, original, paths, target):
        core = Path('rouge/panel_native_finalization.py')
        for path in [*paths, core]:
            dest = target / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((original / path).read_bytes())
        return load_module(target / core)

    def assert_valid_clone_warms_all_apis(self, subject):
        self.assertIsNotNone(subject.source_data())
        result = subject.panel_native_finalization({'fields': [field(phase='rune')]})
        self.assertTrue(result['source_valid'])
        self.assertEqual(result['fields'][0]['references']['writer']['encoder_argument_reference'], 10)
        self.assertTrue(subject.read_field_reference(read())['normal'])
        self.assertTrue(subject.write_field_reference(write())['normal'])
        self.assertTrue(subject.manager_flow_reference(manager(iteration()))['normal'])

    def assert_invalid_clone_suppresses_all_apis(self, subject):
        self.assertIsNone(subject.source_data())
        result = subject.panel_native_finalization({'fields': [field(phase='rune')]})
        self.assertFalse(result['source_valid'])
        self.assertTrue(all(v is None for v in result['fields'][0]['references'].values()))
        self.assertIsNone(result['fields'][0]['metadata_range'])
        self.assertIsNone(result['fields'][0]['storage_type'])
        self.assertFalse(result['fields'][0]['conditional_complete'])
        rd = subject.read_field_reference(read())
        self.assertFalse(rd['source_valid']); self.assertEqual(rd['single_bits_candidates'], [])
        wr = subject.write_field_reference(write())
        self.assertFalse(wr['source_valid']); self.assertIsNone(wr['as_float_reference'])
        self.assertIsNone(wr['encoder_argument_reference']); self.assertIsNone(wr['stored_prefix'])
        mg = subject.manager_flow_reference(manager(iteration()))
        self.assertFalse(mg['source_valid']); self.assertIsNone(mg['rows'][0]['arithmetic_reference'])
        self.assertIsNone(mg['rows'][0]['writer_reference']['as_float_reference'])
        with self.assertRaises(ValueError): subject.panel_native_finalization({'fields': [], 'data': None})

    def test_every_pin_byte_change_is_freshly_detected_after_all_api_execution(self):
        original, paths = self.pin_paths()
        before = {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths}
        for changed in paths:
            with self.subTest(changed=str(changed)), tempfile.TemporaryDirectory(prefix='panel283-public-', dir=HERE) as folder:
                target = Path(folder).resolve(); self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject, package_name = self.clone_public(original, paths, target)
                try:
                    self.assert_valid_clone_warms_all_apis(subject)
                    path = (target / changed).resolve(); self.assertTrue(path.is_relative_to(target))
                    raw = bytearray(path.read_bytes()); raw[0] ^= 1; path.write_bytes(raw)
                    self.assert_invalid_clone_suppresses_all_apis(subject)
                finally: unload_package(package_name)
        self.assertEqual(before, {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths})

    def test_every_missing_pin_is_freshly_detected_after_all_api_execution(self):
        original, paths = self.pin_paths()
        before = {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths}
        for missing in paths:
            with self.subTest(missing=str(missing)), tempfile.TemporaryDirectory(prefix='panel283-public-', dir=HERE) as folder:
                target = Path(folder).resolve(); self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject, package_name = self.clone_public(original, paths, target)
                try:
                    self.assert_valid_clone_warms_all_apis(subject)
                    path = (target / missing).resolve(); self.assertTrue(path.is_relative_to(target)); path.unlink()
                    self.assert_invalid_clone_suppresses_all_apis(subject)
                finally: unload_package(package_name)
        self.assertEqual(before, {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    IndependentPanelParentTests.subject, IndependentPanelParentTests.package_name = load_module(args.module_file)
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__': main()
