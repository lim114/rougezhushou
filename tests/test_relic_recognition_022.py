"""Owned-bar behavior at the existing public recognition interfaces."""
import copy
from pathlib import Path
import unittest

import cv2
import numpy as np

from rouge.recognition import ScreenReader
from rouge.relic_recognition import match_held_icons
from rouge.recognition_cache import ExactImageCache

ROOT = Path(__file__).resolve().parents[1]


class RelicRecognition022Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = cv2.imdecode(np.fromfile(
            ROOT/'samples/native-client/run-relic-multicard-closed.png', dtype=np.uint8), 1)
        cls.observed = ScreenReader(cache_enabled=False).read(cls.image)
        cls.anchor = next(t for t in cls.observed['texts'] if t['text'] == '收藏品')

    def test_captured_three_item_bar_keeps_tactical_tool_and_relics_distinct(self):
        run = self.observed['run']
        self.assertEqual(run['relics']['count'], 3)
        self.assertEqual(set(run['relics']['ids']),
                         {'rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26'})
        self.assertEqual(run['tactical_tools']['ids'], ['rogue_6_active_tool_5'])
        self.assertEqual(len(run['relics']['icons']), 3)
        self.assertTrue(all(i['confirmed'] for i in run['relics']['icons']))

    def test_moving_page_and_anchor_preserves_slots_and_cached_centers(self):
        image = cv2.copyMakeBorder(self.image, 75, 110, 137, 90, cv2.BORDER_CONSTANT)
        anchor = copy.deepcopy(self.anchor)
        anchor['box'] = [[(p[0]*self.image.shape[1]+137)/image.shape[1],
                          (p[1]*self.image.shape[0]+75)/image.shape[0]] for p in anchor['box']]
        cache = ExactImageCache()
        first = match_held_icons(image, anchor, 3, cache=cache)
        again = match_held_icons(image, anchor, 3, cache=cache)
        self.assertEqual(first, again)
        self.assertEqual({i['id'] for i in first},
                         {'rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26', 'rogue_6_active_tool_5'})
        for item in first:
            original = next(i for i in self.observed['run']['relics']['icons'] if i['id'] == item['id'])
            expected = [(original['center'][0]*self.image.shape[1]+137)/image.shape[1],
                        (original['center'][1]*self.image.shape[0]+75)/image.shape[0]]
            np.testing.assert_allclose(item['center'], expected, atol=.001)

    def test_obscured_bar_does_not_confirm_items_from_old_page(self):
        cache = ExactImageCache()
        self.assertEqual(len(match_held_icons(self.image, self.anchor, 3, cache=cache)), 3)
        obscured = self.image.copy()
        obscured[1010:1120, 300:900] = 0
        self.assertEqual(match_held_icons(obscured, self.anchor, 3, cache=cache), [])
        self.assertEqual(match_held_icons(np.zeros_like(self.image), self.anchor, 3), [])

    def test_intermediate_resolution_reads_all_three_captured_items(self):
        for width in (1280,1600,2560):
            with self.subTest(width=width):
                image=cv2.resize(self.image,(width,round(self.image.shape[0]*width/self.image.shape[1])))
                items=match_held_icons(image,self.anchor,3)
                self.assertEqual({i['id'] for i in items},
                                 {'rogue_6_relic_cargo_1','rogue_6_relic_fight_26','rogue_6_active_tool_5'})
                self.assertTrue(all(i['confirmed'] and i['score']>=.90 for i in items))
