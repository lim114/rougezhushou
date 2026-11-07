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

    def test_raw_ignores_unrepresentable_inputs_and_exposes_internal_errors(self):
        from rouge import deployment
        for value in (None, True, '1', float('inf'), 1 << 31, 10**1000):
            self.assertIsNone(bridge._raw(value))
        self.assertEqual(bridge._raw(-(1 << 31)), -(1 << 63))
        with patch.object(deployment, '_fp', side_effect=ValueError('internal conversion')):
            with self.assertRaisesRegex(ValueError, 'internal conversion'):
                bridge._raw(1)

    def test_count_scaled_rune_uses_operand_rounding_before_fp(self):
        from rouge.relic_attributes import _apply_selected_runes
        from rouge import deployment
        effect = {'kind': 'attack_speed', 'formula_item': 'ADDITION',
                  'native_count_scale': 'float32_before_fp', 'native_rune_base': 16777217,
                  'native_rune_factor': 0.00000011920928955078125, 'value': 0}
        scenario = {}
        stats = {'attack_speed': 100}
        applied = _apply_selected_runes(stats, [effect])[0]
        bridge.prepare(scenario, stats, applied, [effect])
        row = scenario['_panel_native_prepared']['fields'][1]
        self.assertEqual(row['addition_raw'], 2 << 32)
        self.assertEqual(row['model_value'], 102)
        effect['native_rune_factor'] = float('inf')
        bridge.prepare(scenario, stats, stats, [effect])
        self.assertIsNone(scenario['_panel_native_prepared']['fields'][1]['addition_raw'])
        with patch.object(deployment, '_single', side_effect=ValueError('internal conversion')):
            with self.assertRaisesRegex(ValueError, 'internal conversion'):
                bridge.prepare(scenario, stats, stats, [effect])
