"""Readable declared tile information keeps unknown placement and map scope."""
from copy import deepcopy
import unittest
from rouge.player_tile_information import tile_information_text


class PlayerTileInformation288Tests(unittest.TestCase):
    def test_ground_road_labels_are_chinese_and_do_not_predict_battle_deployment(self):
        tile = {'tileKey': 'tile_road', 'heightType': 'LOWLAND',
                'buildableType': 'MELEE', 'passableMask': 'ALL'}
        original = deepcopy(tile)
        text = tile_information_text({'row': 1, 'col': 2}, tile, mapped=True)
        for expected in ('第2行、第3列', '道路', '位置高度：地面', '近战位', '全部类型',
                         '不包含战斗中的变化', '不等于本局一定没有敌人经过', '已标出本格近似中心'):
            self.assertIn(expected, text)
        for raw in ('tile_road', 'LOWLAND', 'MELEE', 'passableMask'):
            self.assertNotIn(raw, text)
        self.assertEqual(tile, original)

    def test_unknown_values_remain_untranslated_until_explicit_technical_view(self):
        tile = {'tileKey': 'unreviewed', 'heightType': 'unknown-height',
                'buildableType': 'unknown-buildable', 'passableMask': 'unknown-pass'}
        plain = tile_information_text({'row': 0, 'col': 0}, tile)
        self.assertIn('名称尚未整理', plain)
        self.assertIn('本格位置尚未核对', plain)
        self.assertNotIn('unreviewed', plain)
        raw = tile_information_text({'row': 0, 'col': 0}, tile, technical=True)
        self.assertTrue(raw.startswith(plain))
        for key, value in tile.items():
            self.assertIn(key, raw)
            self.assertIn(value, raw)

    def test_invalid_cells_never_produce_a_misleading_positive_location(self):
        for cell in (None, {}, {'row': True, 'col': 0}, {'row': -1, 'col': 0},
                     {'row': 1.5, 'col': 0}):
            with self.subTest(cell=cell):
                self.assertIn('无法确认', tile_information_text(cell, {}, mapped=True))


if __name__ == '__main__':
    unittest.main()
