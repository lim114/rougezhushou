import struct
from unittest import TestCase
from unittest.mock import patch
from rouge import panel_native_bridge as bridge


class PanelBitsBoundaryTests(TestCase):
    def test_finite_float32_bits_and_out_of_range(self):
        for value,expected in [(0,0),(1,0x3f800000),(-1,0xbf800000),(1.5,0x3fc00000)]:
            self.assertEqual(bridge._bits(value),expected)
        for value in (1e300,-1e300,None,True,float('inf'),float('nan')):
            self.assertIsNone(bridge._bits(value))

    def test_structural_packing_error_is_exposed(self):
        with patch.object(bridge.struct,'pack',side_effect=struct.error('internal format defect')):
            with self.assertRaisesRegex(struct.error,'internal format defect'):bridge._bits(1)

    def test_unpacking_error_is_not_treated_as_numeric_overflow(self):
        with patch.object(bridge.struct,'unpack',side_effect=OverflowError('internal decode defect')):
            with self.assertRaisesRegex(OverflowError,'internal decode defect'):bridge._bits(1)
