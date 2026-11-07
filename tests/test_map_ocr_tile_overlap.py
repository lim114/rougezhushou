"""Map OCR tiles overlap; distinct nodes may legitimately share one label."""
import unittest

import numpy as np

from rouge.recognition import refine_map_texts


class MapTileOverlapTests(unittest.TestCase):
    def test_first_read_is_kept_only_for_same_text_at_same_position(self):
        image = np.zeros((400, 1900, 3), np.uint8)
        nodes = [{'box': [(0, .4), (1, .4), (1, .5), (0, .5)]}]

        def hit(x, text, score):
            return ([[x, 70], [x+20, 70], [x+20, 90], [x, 90]], text, score)

        tiles = iter([
            [hit(1040, '作战', .83), hit(200, '作战', .98)],
            [hit(40, '作 战', .99), hit(40, '商店', .96), hit(400, '作战', .92)],
        ])
        result = refine_map_texts(image, [], nodes, lambda roi: (next(tiles), None))
        self.assertEqual([(r['text'], r['confidence']) for r in result],
                         [('作战', .83), ('作战', .98), ('商店', .96), ('作战', .92)])
        self.assertEqual([round(r['box'][0][0]*1900) for r in result],
                         [1040, 200, 1040, 1400])
