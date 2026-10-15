"""Only new max-range/qualification/known-skip correction controls.

The old28 methods are not rerun or reattributed to this new implementation.
Their original builders are reused as declarations, with the two new facts.
"""
import importlib.util
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('original_author_cases283', BASE / 'verify_draft_283.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
m, Q = old.m, old.Q


def read():
    return {**old.read(), 'int_to_single_normal': True}


def iteration(i='a'):
    item = old.iteration(i)
    item.update(read_field=read(), clamp_normal=True)
    return item


def stages(value):
    return old.stages(value)


class Correction(unittest.TestCase):
    def test_four_default_ranges_use_initialized_fp_max(self):
        for field in ('hp', 'attack', 'defense', 'attack_speed'):
            with self.subTest(field=field):
                item = old.row(field, 'normal', (1 << 63) - 1)
                result = m.panel_native_finalization({'fields': [item]})
                self.assertTrue(result['source_valid'])
                row = result['fields'][0]
                self.assertEqual(row['references']['input_fp_raw'], 9223372036854775807)
                self.assertEqual(row['metadata_range']['upper_raw'], 9223372036854775806)
                self.assertEqual(row['references']['getter_result_raw'], 9223372036854775806)
                self.assertIsNone(row['actual_getter_raw'])

    def test_int_conversion_failure_does_not_inherit_decoder_normality(self):
        item = read()
        item['int_to_single_normal'] = False
        result = m.read_field_reference(item)
        self.assertTrue(stages(result)['decode']['normal'])
        self.assertTrue(stages(result)['int_to_single']['called'])
        self.assertFalse(stages(result)['int_to_single']['normal'])
        self.assertFalse(result['normal'])
        self.assertEqual(result['single_bits_candidates'], [])
        self.assertEqual(stages(result)['int_to_single']['reference']['normal_result_bits_candidates'], [0x42c80000])

    def test_int_conversion_unknown_keeps_later_manager_unknown(self):
        item = iteration()
        item['read_field']['int_to_single_normal'] = None
        item['single_to_fp_normal'] = True
        result = m.manager_flow_reference(old.manager([item]))
        row = result['rows'][0]
        self.assertIsNone(result['normal'])
        self.assertTrue(stages(row['read_reference'])['decode']['normal'])
        self.assertIsNone(stages(row)['single_to_fp']['called'])
        self.assertIsNone(stages(row)['addition_array_read']['called'])
        self.assertIsNone(row['writer_reference']['stages'][0]['called'])

    def test_clamp_failure_preserves_earlier_arithmetic_not_writer_call(self):
        item = iteration()
        item['clamp_normal'] = False
        result = m.manager_flow_reference(old.manager([item]))['rows'][0]
        self.assertFalse(result['normal'])
        self.assertTrue(stages(result)['range_get']['normal'])
        self.assertTrue(stages(result)['clamp']['called'])
        self.assertFalse(stages(result)['write_attributes_field']['called'])
        self.assertFalse(stages(result['writer_reference'])['as_float']['called'])
        self.assertEqual(result['arithmetic_reference']['after_scaler_raw'], 100 * Q)
        self.assertIsNone(result['arithmetic_reference']['clamped_raw'])
        self.assertEqual(stages(result)['clamp']['reference']['normal_result_raw_reference'], 100 * Q)

    def test_clamp_unknown_keeps_future_and_next_iteration_unknown(self):
        item = iteration()
        item['clamp_normal'] = None
        result = m.manager_flow_reference(old.manager([item, iteration('b')]))
        self.assertIsNone(result['normal'])
        self.assertIsNone(stages(result['rows'][0])['write_attributes_field']['called'])
        self.assertIsNone(stages(result['rows'][0])['loop_increment']['called'])
        self.assertIsNone(stages(result['rows'][1])['first_metas_get']['called'])

    def test_writer_known_route_skips_survive_later_unknown(self):
        for kind, point, excluded in (
            ('Single', 'box_normal', ('round', 'encode', 'struct_copy')),
            ('ObscuredFloat', 'encode_normal', ('round',)),
            ('Int32', 'round_normal', ('encode', 'struct_copy')),
        ):
            with self.subTest(kind=kind):
                item = old.write(kind)
                item[point] = None
                result = m.write_field_reference(item)
                self.assertIsNone(result['normal'])
                for name in excluded:
                    self.assertFalse(stages(result)[name]['called'])
                self.assertIsNone(stages(result)['set_value']['called'])

    def test_read_known_route_skips_survive_later_unknown(self):
        item = read()
        item['decode_normal'] = None
        result = m.read_field_reference(item)
        for name in ('float_target_type', 'float_assignability', 'fallback_convert'):
            self.assertFalse(stages(result)[name]['called'])
        self.assertIsNone(stages(result)['int_to_single']['called'])
        item['int_assignable']['value'] = False
        item['float_assignable']['value'] = True
        result = m.read_field_reference(item)
        self.assertFalse(stages(result)['int_to_single']['called'])
        self.assertFalse(stages(result)['fallback_convert']['called'])
        item['float_assignable']['value'] = False
        item['fallback_normal'] = None
        result = m.read_field_reference(item)
        for name in ('unbox_and_copy', 'decode', 'int_to_single'):
            self.assertFalse(stages(result)[name]['called'])

    def test_new_qualifications_are_strict_and_independent(self):
        item = read()
        del item['int_to_single_normal']
        with self.assertRaises(ValueError):
            m.read_field_reference(item)
        item = iteration()
        del item['clamp_normal']
        with self.assertRaises(ValueError):
            m.manager_flow_reference(old.manager([item]))
        item = read()
        item['int_assignable']['value'] = False
        item['float_assignable']['value'] = False
        item['fallback_bits'] = 0x3f800000
        item['int_to_single_normal'] = False
        result = m.read_field_reference(item)
        self.assertTrue(result['normal'])
        self.assertFalse(stages(result)['int_to_single']['called'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
