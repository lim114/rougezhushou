import unittest
from unittest.mock import Mock, patch

import cv2
import numpy as np

from rouge.gold_counter import gold_template, read_single_gold
from rouge.hud_gold_preview import read_gold_preview
from rouge.resource_recognition import read_resources


class SingleGoldTests(unittest.TestCase):
    def setUp(self):
        self.image = np.full((320, 800, 3), 8, np.uint8)
        self.icon = cv2.cvtColor(gold_template(), cv2.COLOR_GRAY2BGR)
        self.image[18:69, 440:498] = self.icon
        self.plate = self.image[37:73, 511:666]
        self.plate[:] = 49
        ink = (245, 245, 245)
        cv2.rectangle(self.plate, (114, 8), (130, 30), ink, 2)
        cv2.line(self.plate, (114, 30), (130, 8), ink, 2)
        self.life = self.label('目标生命值', 20, 18, 110, 46)
        self.labels = [self.life, self.label('指挥等级', 140, 18, 220, 46),
                       self.label('零件箱', 200, 220, 250, 240),
                       self.label('收藏品', 20, 220, 80, 240)]

    def label(self, text, x, y, u, v):
        return {'text': text, 'confidence': .99, 'box':
                [[a/800, b/320] for a, b in ((x,y), (u,y), (u,v), (x,v))]}

    def test_repeat_reads_must_agree_and_zero_is_a_reading(self):
        for answers, expected in [([('0', .99), ('0', .98)], 0),
                                  ([('4', .99), ('1', .99)], None),
                                  ([('4', .99), ('4', .94)], None),
                                  ([('5', .99), ('5', .99)], None),
                                  ([('7', .99), ('7', .99)], None)]:
            engine = Mock(side_effect=[([row], None) for row in answers])
            result = read_single_gold(self.image, self.life, engine)
            self.assertEqual((result or {}).get('value'), expected)
            self.assertEqual(engine.call_count, 2)

    def test_no_decode_for_second_glyph_occlusion_clipping_or_nonunique_icon(self):
        def second(plate):
            plate[7:32, 90:93] = 245
        def dark(plate):
            plate[3:30, 30:50] = 0
        def light(plate):
            plate[3:30, 30:50] = 80
        def colored(plate):
            plate[3:30, 30:50] = (160, 50, 0)
        for alter in (second, dark, light, colored):
            image = self.image.copy()
            alter(image[37:73, 511:666])
            engine = Mock()
            self.assertIsNone(read_single_gold(image, self.life, engine))
            engine.assert_not_called()
        self.assertIsNone(read_single_gold(self.image[:, :660], self.life, Mock()))
        self.image[18:69, 90:148] = self.icon
        self.assertIsNone(read_single_gold(self.image, self.life, Mock()))

    def test_lower_loop_on_six_contradicts_repeated_read_of_five(self):
        self.plate[:] = 49
        ink = (245, 245, 245)
        cv2.line(self.plate, (114, 23), (123, 8), ink, 2)
        cv2.ellipse(self.plate, (122, 24), (8, 6), 0, 0, 360, ink, 2)
        for claimed, expected in [('5', None), ('4', None), ('6', 6)]:
            engine = Mock(return_value=([(claimed, .99)], None))
            reading = read_single_gold(self.image, self.life, engine)
            self.assertEqual((reading or {}).get('value'), expected)

    def test_two_prior_amount_candidates_only_allow_an_independent_current_read(self):
        view = {'source_size': [800, 320], 'content_rect': [0, 0, 800, 320]}
        old = self.image.copy()
        old[37:73, 511:666] = 49
        previous = {'viewport': view, 'run': {'page': 'run_map', 'resources': {'gold': {'value': 3}}},
                    'texts': [*self.labels, self.label('3', 310, 30, 330, 55),
                              self.label('3', 610, 30, 630, 55)]}
        engine = Mock(return_value=([('0', .99)], None))
        with patch('rouge.hud_gold_preview.match_digits') as learn:
            self.assertEqual(read_gold_preview(self.image, old, previous, view, engine)['value'], 0)
            self.assertIsNone(read_gold_preview(old, old, previous, view, engine))
            learn.assert_not_called()

    def test_conflicting_text_inside_plate_or_missing_hud_cannot_fill_amount(self):
        engine = Mock(return_value=([('0', .99)], None))
        conflict = self.label('8', 625, 43, 645, 66)
        self.assertIsNone(read_single_gold(self.image, self.life, engine, texts=[conflict]))
        # No numeric box is present; partial page evidence cannot authorize a new read.
        with patch('rouge.hud_resources.read_hud_resources', return_value={}):
            self.assertNotIn('gold', read_resources(self.image, self.labels[:-1], engine))
            self.assertEqual(read_resources(self.image, self.labels, engine)['gold']['value'], 0)
