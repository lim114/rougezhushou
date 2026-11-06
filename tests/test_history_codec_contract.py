import struct
import unittest
from unittest.mock import patch
from rouge import player_history_codec as codec


class HistoryCodecContractTests(unittest.TestCase):
    def test_float_bits_roundtrip_and_noncanonical_input_rejected(self):
        for bits in ('0000000000000000', '8000000000000000', '7ff0000000000000',
                     'fff0000000000000', '7ff8000000000001', '3ff0000000000000'):
            value = codec.decode(['float64', bits])
            self.assertEqual(struct.pack('>d', value).hex(), bits)
            self.assertEqual(codec.encode(value), ['float64', bits])
        for raw in ('00000000000000  ', '7FF0000000000000', '00', 'x' * 16):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                codec.decode(['float64', raw])

    def test_bad_key_and_duplicate_key_keep_input_error(self):
        for rows in ([[['array', []], ['null']]],
                     [[['text', 'same'], ['null']], [['text', 'same'], ['bool', True]]]):
            with self.assertRaises(ValueError):
                codec.decode(['object', rows])

    def test_nested_internal_type_error_is_not_key_error(self):
        real_decode = codec.decode
        nested = ['text', 'value']
        def injected(value):
            if value is nested:
                raise TypeError('internal nested defect')
            return real_decode(value)
        with patch.object(codec, 'decode', side_effect=injected):
            with self.assertRaisesRegex(TypeError, 'internal nested defect'):
                real_decode(['object', [[['text', 'key'], nested]]])

    def test_cycles_rejected_and_stack_released(self):
        value = []; value.append(value)
        stack = set()
        with self.assertRaises(ValueError): codec.encode(value, stack)
        self.assertEqual(stack, set())
        shared = ['same']
        self.assertEqual(codec.decode(codec.encode([shared, shared])), [shared, shared])

    def test_nested_opaque_values_and_integer_canonical_form(self):
        value = {('tuple', 1): [None, True, -2, 10**100, '\ud800'], 'text': {False: '值'}}
        self.assertEqual(codec.decode(codec.encode(value)), value)
        for raw in ('0X1', '0x01', '1', '-0x0'):
            with self.assertRaises(ValueError): codec.decode(['int', raw])
