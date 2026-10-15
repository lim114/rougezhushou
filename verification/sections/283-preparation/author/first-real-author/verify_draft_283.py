"""Necessary author controls for the cache parent workflow, no game access."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import types
import unittest

BASE = Path(__file__).resolve().parent
pkg = types.ModuleType('candidate283')
pkg.__path__ = [str(BASE / 'rouge')]
sys.modules['candidate283'] = pkg
m = importlib.import_module('candidate283.panel_native_finalization')
Q = 1 << 32


def row(field='attack', phase='rune', raw=100 * Q):
    return {'id': 'r', 'field': field, 'phase': phase, 'model_value': 100,
            'basis_kind': 'nominal_fp', 'basis_single_bits': None, 'basis_fp_raw': raw,
            'addition_raw': 0, 'multiplier_delta_raw': 0, 'final_addition_raw': 0, 'final_scaler_raw': Q}


def read():
    return {'value_exists': True, 'object_type_normal': True, 'int_type_normal': True,
            'int_assignable': {'normal': True, 'value': True}, 'float_type_normal': True,
            'float_assignable': {'normal': True, 'value': False}, 'unbox_normal': True,
            'decode_normal': True, 'decoded_int32': 100, 'decoded_single_bits': None,
            'fallback_normal': True, 'fallback_bits': None}


def write(kind='ObscuredInt', raw=100 * Q):
    return {'fp_raw': raw, 'field_exists': True, 'as_float_normal': True,
            'field_type_read': {'normal': True, 'value': kind}, 'type_route_normal': True,
            'round_normal': True, 'encode_normal': True, 'copy_normal': True,
            'box_normal': True, 'set_value_normal': True}


def iteration(i='a'):
    w = write()
    del w['fp_raw'], w['field_exists']
    return {'id': i,
            'first_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                           'item_exists': True, 'field_read_normal': True, 'field_exists': True},
            'second_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                            'item_exists': True, 'range_read_normal': True, 'range_exists': True,
                            'attribute_read_normal': True, 'attribute': 1},
            'reflection_get_normal': True, 'read_field': read(), 'single_to_fp_normal': True,
            'arrays': {k: {'read_normal': True, 'exists': True, 'length': 8,
                           'element_normal': True, 'raw': Q if k == 'scaler' else 0}
                       for k in ('addition', 'multiplier', 'scaler')},
            'range_read': {'normal': True, 'lower_raw': 0, 'upper_raw': (1 << 63) - 1}, 'writer': w}


def manager(items):
    return {'ordinary_native_path': True,
            'initial_metas': {'get_normal': True, 'exists': True, 'count_normal': True, 'count': len(items)},
            'iterations': items}


def stages(value):
    return {r['name']: r for r in value['stages']}


class Necessary(unittest.TestCase):
    def calc(self, item):
        return m.panel_native_finalization({'fields': [item]})['fields'][0]

    def test_public_example_17_nominal_and_no_actual(self):
        r = m.panel_native_finalization(m.public_example())
        self.assertTrue(r['source_valid'])
        self.assertEqual(len(r['fields']), 17)
        self.assertFalse(r['complete_native_panel'])
        self.assertIsNone(r['actual_panel'])
        for item in r['fields']:
            self.assertTrue(item['conditional_complete'])
            self.assertEqual(item['basis'], 'nominal_model_snapshot')
            self.assertIsNone(item['actual_decoded_value'])
            self.assertIsNone(item['actual_getter_raw'])
            self.assertFalse(item['complete_native_value'])

    def test_rune_vs_ordinary_multiplier_negative(self):
        a = row(raw=-10 * Q)
        a['multiplier_delta_raw'] = -2 * Q
        self.assertEqual(self.calc(a)['references']['writer']['encoder_argument_reference'], 10)
        a['phase'] = 'normal'
        self.assertEqual(self.calc(a)['references']['getter_result_raw'], 0)
        self.assertIsNone(self.calc(a)['references']['writer'])

    def test_ordinary_final_addition_and_fractional_getter(self):
        a = row(phase='normal', raw=100 * Q + Q // 2)
        a['final_addition_raw'] = Q
        self.assertEqual(self.calc(a)['references']['getter_result_raw'], 101 * Q + Q // 2)
        self.assertIsNone(self.calc(a)['references']['as_float'])

    def test_rune_bankers_not_ordinary_getter_round(self):
        a = row(raw=100 * Q + Q // 2)
        self.assertEqual(self.calc(a)['references']['writer']['encoder_argument_reference'], 100)
        a['phase'] = 'normal'
        self.assertEqual(self.calc(a)['references']['getter_result_raw'], 100 * Q + Q // 2)

    def test_metadata_bounds_no_attack_speed_600(self):
        self.assertEqual(self.calc(row('hp', raw=-Q))['references']['writer']['encoder_argument_reference'], 1)
        self.assertEqual(self.calc(row('resistance', raw=101 * Q))['references']['writer']['encoder_argument_bits_reference'], 0x42c80000)
        self.assertEqual(self.calc(row('attack_speed', raw=10 * Q))['references']['writer']['encoder_argument_bits_reference'], 0x41a00000)
        self.assertEqual(self.calc(row('attack_speed', raw=700 * Q))['references']['writer']['encoder_argument_bits_reference'], 0x442f0000)

    def test_ambiguous_int_and_float_keep_model_value(self):
        a = row(raw=100 * Q + Q // 2 + 1)
        r = self.calc(a)
        self.assertFalse(r['conditional_complete'])
        self.assertEqual(r['model_value'], 100)
        self.assertEqual(r['references']['writer']['integer_reference']['integer_candidates'], [100, 101])
        r = self.calc(row('attack_speed', raw=100 * Q + 1))
        self.assertFalse(r['conditional_complete'])
        self.assertIsNone(r['references']['writer']['encoder_argument_bits_reference'])

    def test_cultivation_single_basis_without_writer(self):
        a = row(phase='cultivation')
        a.update(basis_kind='nominal_single', basis_single_bits=0x3fc00000, basis_fp_raw=None)
        r = self.calc(a)
        self.assertEqual(r['references']['input_fp_raw'], 6442450944)
        self.assertIsNone(r['references']['writer'])
        self.assertIsNone(r['references']['getter_result_raw'])
        a['basis_single_bits'] = 0x7f800000
        self.assertFalse(self.calc(a)['conditional_complete'])

    def test_unknown_basis_can_close_zero_product(self):
        a = row(phase='normal', raw=None)
        a['multiplier_delta_raw'] = -Q
        self.assertEqual(self.calc(a)['references']['getter_result_raw'], 0)

    def test_strict_input_and_source_injection(self):
        for a in [row('hp', phase='skill'), row(raw=True)]:
            with self.assertRaises(ValueError):
                self.calc(a)
        a = row()
        a['final_addition_raw'] = 1
        with self.assertRaises(ValueError):
            self.calc(a)
        with self.assertRaises(ValueError):
            m.panel_native_finalization({'fields': [], 'data': {}})
        with self.assertRaises(TypeError):
            m.panel_native_finalization({'fields': []}, data={})

    def test_null_read_zero_before_type_calls(self):
        a = read()
        a['value_exists'] = False
        r = m.read_field_reference(a)
        self.assertTrue(r['normal'])
        self.assertEqual(r['single_bits_candidates'], [0])
        self.assertFalse(stages(r)['object_type']['called'])

    def test_int_read_independent_candidates(self):
        a = read()
        a['decoded_int32'] = 2147483647
        self.assertEqual(m.read_field_reference(a)['single_bits_candidates'], [0x4effffff, 0x4f000000])

    def test_float_and_fallback_independent_read(self):
        a = read()
        a['int_assignable']['value'] = False
        a['float_assignable']['value'] = True
        a['decoded_single_bits'] = 0x3fc00000
        self.assertEqual(m.read_field_reference(a)['single_bits_candidates'], [0x3fc00000])
        a['float_assignable']['value'] = False
        a['fallback_bits'] = 0x80000000
        r = m.read_field_reference(a)
        self.assertEqual(r['single_bits_candidates'], [0x80000000])
        self.assertFalse(stages(r)['unbox_and_copy']['called'])

    def test_unknown_assignability_future_not_false(self):
        a = read()
        a['int_assignable']['value'] = None
        r = m.read_field_reference(a)
        self.assertIsNone(r['normal'])
        self.assertIsNone(stages(r)['float_target_type']['called'])
        self.assertIsNone(stages(r)['decode']['called'])

    def test_fp_writer_asfloat_precedes_null_field(self):
        a = write()
        a['field_exists'] = False
        r = m.write_field_reference(a)
        self.assertFalse(r['normal'])
        self.assertTrue(stages(r)['as_float']['called'])
        self.assertFalse(stages(r)['field_type_read']['called'])

    def test_unsupported_writer_normal_false(self):
        r = m.write_field_reference(write('unsupported'))
        self.assertTrue(r['normal'])
        self.assertFalse(r['return_boolean'])
        self.assertFalse(stages(r)['box']['called'])
        self.assertFalse(stages(r)['set_value']['called'])

    def test_protected_copy_prefix_survives_box_failure(self):
        a = write(raw=100 * Q + Q // 2)
        a['box_normal'] = False
        r = m.write_field_reference(a)
        self.assertFalse(r['normal'])
        self.assertEqual(r['encoder_argument_reference'], 100)
        self.assertEqual(r['stored_prefix']['byte_count'], 20)
        self.assertFalse(stages(r)['set_value']['called'])
        self.assertIsNone(r['actual_decoded_value'])

    def test_opaque_unknown_numeric_normal_writer(self):
        r = m.write_field_reference(write(raw=None))
        self.assertTrue(r['normal'])
        self.assertTrue(r['return_boolean'])
        self.assertIsNone(r['stored_prefix']['encoder_argument_reference'])

    def test_route_normality_is_not_field_type_normality(self):
        a = write()
        a['type_route_normal'] = None
        r = m.write_field_reference(a)
        self.assertIsNone(r['normal'])
        self.assertIsNone(stages(r)['round']['called'])

    def test_primitive_int_selector_boxes_double(self):
        r = m.write_field_reference(write('Int32', 100 * Q + Q // 2))
        self.assertTrue(r['normal'])
        self.assertEqual(r['boxed_type_reference'], 'Double')
        self.assertFalse(stages(r)['encode']['called'])
        self.assertIsNone(r['stored_prefix'])

    def test_float_copy_24_and_single_no_encoder(self):
        r = m.write_field_reference(write('ObscuredFloat', 100 * Q))
        self.assertEqual(r['stored_prefix']['byte_count'], 24)
        self.assertEqual(r['encoder_argument_bits_reference'], 0x42c80000)
        r = m.write_field_reference(write('Single', 100 * Q))
        self.assertFalse(stages(r)['encode']['called'])
        self.assertEqual(r['boxed_type_reference'], 'Single')

    def test_manager_null_range_skips_null_field(self):
        a = iteration()
        a['first_meta']['field_exists'] = False
        a['second_meta']['range_exists'] = False
        r = m.manager_flow_reference(manager([a]))
        self.assertTrue(r['normal'])
        self.assertFalse(stages(r['rows'][0])['field_null_check']['called'])
        self.assertTrue(r['rows'][0]['loop_continues_reference'])

    def test_manager_field_null_after_second_item(self):
        a = iteration()
        a['first_meta']['field_exists'] = False
        r = m.manager_flow_reference(manager([a]))['rows'][0]
        self.assertFalse(r['normal'])
        self.assertTrue(stages(r)['attribute_read']['called'])
        self.assertFalse(stages(r)['reflection_get']['called'])

    def test_manager_writer_false_still_next_iteration(self):
        a = iteration()
        a['writer']['field_type_read']['value'] = 'unsupported'
        r = m.manager_flow_reference(manager([a, iteration('b')]))
        self.assertTrue(r['normal'])
        self.assertFalse(r['rows'][0]['writer_reference']['return_boolean'])
        self.assertTrue(r['rows'][1]['writer_reference']['return_boolean'])
        self.assertTrue(stages(r['rows'][0])['loop_increment']['called'])

    def test_manager_different_second_attribute_unsigned_guard(self):
        a = iteration()
        a['second_meta']['attribute'] = -1
        r = m.manager_flow_reference(manager([a]))['rows'][0]
        self.assertFalse(r['normal'])
        self.assertFalse(stages(r)['addition_element']['called'])
        self.assertEqual(stages(r)['addition_bounds']['reference']['unsigned_index'], 4294967295)

    def test_manager_no_multiplier_clamp_and_independent_range(self):
        a = iteration()
        a['read_field']['decoded_int32'] = -10
        a['arrays']['multiplier']['raw'] = -2 * Q
        r = m.manager_flow_reference(manager([a]))['rows'][0]
        self.assertEqual(r['arithmetic_reference']['clamped_raw'], 10 * Q)
        self.assertEqual(r['writer_reference']['encoder_argument_reference'], 10)

    def test_unknown_second_range_stops_future_as_unknown(self):
        a = iteration()
        a['second_meta']['range_exists'] = None
        r = m.manager_flow_reference(manager([a, iteration('b')]))
        self.assertIsNone(r['normal'])
        self.assertIsNone(stages(r['rows'][0])['reflection_get']['called'])
        self.assertIsNone(stages(r['rows'][1])['first_metas_get']['called'])

    def test_captured_count_zero_and_strict_full_list(self):
        self.assertTrue(m.manager_flow_reference(manager([]))['normal'])
        a = manager([iteration()])
        a['initial_metas']['count'] = 2
        with self.assertRaises(ValueError):
            m.manager_flow_reference(a)

    def test_fresh_source_guard_after_warm_dependency(self):
        with tempfile.TemporaryDirectory(prefix='rouge283-author-') as name:
            folder = Path(name).resolve()
            manifest = json.loads((BASE / m.SOURCE).read_bytes())
            for relative in [m.SOURCE, 'rouge/panel_native_finalization.py', *manifest['files']]:
                target = folder / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(BASE / relative, target)
            package = types.ModuleType('guard283')
            package.__path__ = [str(folder / 'rouge')]
            sys.modules['guard283'] = package
            c = importlib.import_module('guard283.panel_native_finalization')
            self.assertTrue(c.panel_native_finalization({'fields': [row()]})['source_valid'])
            target = folder / 'rouge/panel_native_precision.py'
            target.write_bytes(target.read_bytes() + b'\n# source mutation\n')
            result = c.panel_native_finalization({'fields': [row()]})
            self.assertFalse(result['source_valid'])
            self.assertTrue(all(v is None for v in result['fields'][0]['references'].values()))
            self.assertIsNone(c.write_field_reference(write())['as_float_reference'])
            self.assertEqual(c.read_field_reference(read())['single_bits_candidates'], [])
            result = c.manager_flow_reference(manager([iteration()]))
            self.assertFalse(result['source_valid'])
            self.assertIsNone(result['rows'][0]['arithmetic_reference'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
