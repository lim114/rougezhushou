"""Explore-page squad/grade evidence through the public screen reader."""
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np

from rouge.recognition import ScreenReader
from rouge.run_state import RunState

ROOT = Path(__file__).resolve().parents[1]


def sample(name):
    return cv2.imdecode(np.fromfile(ROOT / 'samples/native-client' / name, np.uint8), 1)


class RunBadgeTests(unittest.TestCase):
    def test_exploration_badge_reads_trade_squad_and_grade_without_info_panel(self):
        result = ScreenReader().read(sample('exploration-map.png'))['run']['config']
        self.assertEqual(result['squad']['id'], 'rogue_6_band_19')
        self.assertEqual(result['squad']['name'], '多边贸易分队')
        self.assertIsNone(result['squad']['level'])
        self.assertFalse(result['squad']['effect_verified'])
        self.assertEqual(result['difficulty']['value'], 15)

    def test_other_squad_artwork_and_small_digits_are_read_without_hovering(self):
        result = ScreenReader().read(sample('run-map-closed.png'))['run']['config']
        self.assertEqual(result['squad']['id'], 'rogue_6_band_3')
        self.assertEqual(result['difficulty']['value'], 15)
        self.assertFalse(result['squad']['effect_verified'])

    def test_badges_follow_continuous_resize_and_changed_window_padding(self):
        original = sample('exploration-map.png')
        reader = ScreenReader()
        for width, left, top in ((1009, 43, 71), (1337, 101, 29), (1771, 37, 113)):
            with self.subTest(width=width):
                height = round(original.shape[0] * width / original.shape[1])
                content = cv2.resize(original, (width, height), interpolation=cv2.INTER_AREA)
                frame = cv2.copyMakeBorder(content, top, 47, left, 61, cv2.BORDER_CONSTANT, value=0)
                result = reader.read(frame)['run']['config']
                self.assertEqual(result['squad']['id'], 'rogue_6_band_19')
                self.assertEqual(result['difficulty']['value'], 15)
                box = result['squad']['badge']['box']
                self.assertGreater(min(p[0] for p in box), left / frame.shape[1])
                self.assertGreater(min(p[1] for p in box), top / frame.shape[0])

    def test_hidden_badge_and_hidden_grade_are_not_replaced_with_old_results(self):
        original = sample('run-map-closed.png')
        reader = ScreenReader()
        self.assertEqual(reader.read(original)['run']['config']['difficulty']['value'], 15)
        missing = original.copy()
        missing[1010:, :145] = 16
        result = reader.read(missing)['run']['config']
        self.assertNotIn('squad', result)
        self.assertNotIn('difficulty', result)
        grade_hidden = original.copy()
        grade_hidden[1079:1116, 16:61] = 16
        result = reader.read(grade_hidden)['run']['config']
        self.assertNotIn('difficulty', result)
        self.assertFalse((reader.read(np.full_like(original, 16)).get('run') or {}).get('config'))

    def test_plain_badge_does_not_downgrade_prior_confirmed_trade_effect(self):
        reader = ScreenReader()
        info = reader.read(sample('run-info-trade.png'))['run']
        main = reader.read(sample('exploration-map.png'))['run']
        self.assertEqual(info['config']['squad']['id'], 'rogue_6_band_20')
        self.assertEqual(main['config']['squad']['id'], 'rogue_6_band_19')
        with tempfile.TemporaryDirectory() as directory:
            state = RunState(Path(directory) / 'run.json')
            self.assertTrue(state.apply(info, time.time()))
            self.assertTrue(state.apply(main, time.time()))
            self.assertEqual(state.state['config']['squad']['id'], 'rogue_6_band_20')
            self.assertTrue(state.state['config']['squad']['effect_verified'])

