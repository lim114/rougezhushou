"""Necessary numeric preparation checks, not final production acceptance."""
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
MODULE = HERE / 'rouge/panel_native_precision.py'
spec = importlib.util.spec_from_file_location('sp283_numeric_candidate', MODULE)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)
Q = 1 << 32

# Fixed literals independently obtained from neighboring binary32 encodings.
# Columns: FP raw, final Single bit set, safe integer set, all branches safe,
# unique integer (null when ambiguity or even one unsafe branch remains).
LITERALS = [
    (0, [0x00000000], [0], True, 0),
    (1, [0x2f800000], [0], True, 0),
    (-1, [0xaf800000], [0], True, 0),
    (Q, [0x3f800000], [1], True, 1),
    (-Q, [0xbf800000], [-1], True, -1),
    (Q // 2, [0x3f000000], [0], True, 0),
    (Q // 2 - 1, [0x3effffff, 0x3f000000], [0], True, 0),
    (Q // 2 + 1, [0x3f000000, 0x3f000001], [0, 1], True, None),
    (-Q // 2, [0xbf000000], [0], True, 0),
    (-Q // 2 + 1, [0xbeffffff, 0xbf000000], [0], True, 0),
    (-Q // 2 - 1, [0xbf000000, 0xbf000001], [-1, 0], True, None),
    (3 * Q // 2, [0x3fc00000], [2], True, 2),
    (3 * Q // 2 - 1, [0x3fbfffff, 0x3fc00000], [1, 2], True, None),
    (3 * Q // 2 + 1, [0x3fc00000, 0x3fc00001], [2], True, 2),
    (5 * Q // 2, [0x40200000], [2], True, 2),
    (7 * Q // 2, [0x40600000], [4], True, 4),
    (16777217, [0x3b800000, 0x3b800001], [0], True, 0),
    (-(1 << 63), [0xcf000000], [-2147483648], True, -2147483648),
    (-(1 << 63) + 1, [0xceffffff, 0xcf000000], [-2147483648, -2147483520], True, None),
    ((1 << 63) - 1, [0x4effffff, 0x4f000000], [2147483520], False, None),
    ((1 << 63) - 2, [0x4effffff, 0x4f000000], [2147483520], False, None),
]


def fraction(bits):
    """Independent exponent interpretation, without candidate round logic."""
    e, mantissa = (bits >> 23) & 255, bits & 0x7fffff
    assert e != 255
    if e == 0:
        assert mantissa == 0
        return Fraction(0)
    power = e - 127
    magnitude = Fraction(1) + Fraction(mantissa, 1 << 23)
    magnitude *= Fraction(1 << power) if power >= 0 else Fraction(1, 1 << -power)
    return -magnitude if bits >> 31 else magnitude


def next_up_bits(bits):
    return bits - 1 if bits >> 31 else bits + 1


class NumericPreparation(unittest.TestCase):
    def test_fixed_fp_and_integer_literals(self):
        for raw, bits, integers, complete, consensus in LITERALS:
            with self.subTest(raw=raw):
                fp = subject.fp_single_reference(raw)
                self.assertTrue(fp['complete'])
                self.assertEqual(fp['single_bits_candidates'], bits)
                self.assertEqual([r['conversion_rc'] for r in fp['candidates']], [0, 1, 2, 3])
                writer = subject.writer_integer_reference(raw)
                self.assertEqual(writer['single_bits_candidates'], bits)
                self.assertEqual(writer['integer_candidates'], integers)
                self.assertIs(writer['complete'], complete)
                self.assertEqual(writer['integer_consensus'], consensus)

    def test_minimum_nonzero_and_maximum_scaled_value_are_normal(self):
        for raw in (1, -1, -(1 << 63), (1 << 63) - 1):
            for row in subject.fp_single_reference(raw)['candidates']:
                bits = row['bits']
                self.assertGreater((bits >> 23) & 255, 0)
                self.assertLess((bits >> 23) & 255, 255)
                self.assertGreaterEqual(abs(fraction(bits)), Fraction(1, Q))
                self.assertLessEqual(abs(fraction(bits)), 1 << 31)

    def test_independent_directed_neighbor_and_nearest_even_controls(self):
        values = {0, 1, -1, -(1 << 63), (1 << 63) - 1}
        for exponent in range(24, 64):
            step = 1 << (exponent - 23)
            for offset in (-1, 0, 1, step // 2, step - 1):
                for sign in (-1, 1):
                    raw = sign * ((1 << exponent) + offset)
                    if -(1 << 63) <= raw < (1 << 63):
                        values.add(raw)
        for raw in sorted(values):
            with self.subTest(raw=raw):
                rows = subject.fp_single_reference(raw)['candidates']
                vals = [fraction(r['bits']) * Q for r in rows]
                nearest, down, up, trunc = vals
                self.assertLessEqual(down, raw)
                self.assertGreaterEqual(up, raw)
                self.assertEqual(trunc, down if raw >= 0 else up)
                if down == up:
                    self.assertEqual(nearest, raw)
                else:
                    self.assertEqual(next_up_bits(rows[1]['bits']), rows[2]['bits'])
                    self.assertIn(nearest, (down, up))
                    self.assertLessEqual(abs(nearest - raw), max(raw - down, up - raw))
                    if raw - down == up - raw:
                        self.assertEqual(rows[0]['bits'] & 1, 0)
                    else:
                        self.assertEqual(nearest, down if raw - down < up - raw else up)

    def test_single_writer_ties_signedzero_domain_and_environment(self):
        for bits, integer in [(0, 0), (0x80000000, 0), (0x3f000000, 0),
                              (0xbf000000, 0), (0x3fc00000, 2), (0xbfc00000, -2),
                              (0x40200000, 2), (0xc0200000, -2),
                              (0x4effffff, 2147483520), (0xcf000000, -2147483648)]:
            with self.subTest(bits=bits):
                result = subject.single_integer_reference(bits)
                self.assertTrue(result['complete'])
                self.assertEqual(result['integer_consensus'], integer)
        for bits in [0x4f000000, 0xcf000001, 0x7f7fffff, 0xff7fffff,
                     0x7f800000, 0xff800000, 0x7fc00000, 1, 0x80000001]:
            with self.subTest(bits=bits):
                result = subject.single_integer_reference(bits)
                self.assertFalse(result['complete'])
                self.assertIsNone(result['integer_consensus'])

    def test_strict_unknown_and_width(self):
        for fn in (subject.fp_single_reference, subject.writer_integer_reference,
                   subject.single_integer_reference):
            self.assertFalse(fn(None)['complete'])
            for value in (True, False, 1.0, '1'):
                with self.subTest(fn=fn.__name__, value=value), self.assertRaises(ValueError):
                    fn(value)
        for fn in (subject.fp_single_reference, subject.writer_integer_reference):
            for value in (-(1 << 63) - 1, 1 << 63):
                with self.assertRaises(ValueError): fn(value)
        for value in (-1, 1 << 32):
            with self.assertRaises(ValueError): subject.single_integer_reference(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
