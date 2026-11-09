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

    def test_reduced_client_reads_complete_plate_and_rejects_clipped_plate(self):
        small = cv2.resize(self.image, (533, 213), interpolation=cv2.INTER_AREA)
        engine = Mock(return_value=([('0', .99)], None))
        result = read_single_gold(small, self.life, engine)
        self.assertEqual((result or {}).get('value'), 0)
        cropped = small.copy()
        cropped[:, 435:445] = 8
        self.assertIsNone(read_single_gold(cropped, self.life, engine))

    def test_enlarged_analysis_can_verify_missing_amount_on_same_native_content(self):
        small = cv2.resize(self.image, (533, 213), interpolation=cv2.INTER_AREA)
        enlarged = cv2.resize(small, (800, 320), interpolation=cv2.INTER_CUBIC)
        engine = Mock(return_value=([('0', .99)], None))
        with patch('rouge.hud_resources.read_hud_resources', return_value={}):
            self.assertNotIn('gold', read_resources(enlarged, self.labels, engine))
            result = read_resources(enlarged, self.labels, engine, native_content=small)
            self.assertEqual(result['gold']['value'], 0)
            conflict = self.label('8', 625, 43, 645, 66)
            self.assertIsNone(read_single_gold(small, self.life, engine, texts=[conflict]))

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

    def test_preview_reads_tens_and_units_from_current_plate(self):
        self.plate[:] = 49
        ink = (245, 245, 245)
        cv2.line(self.plate, (103, 8), (103, 30), ink, 2)
        cv2.line(self.plate, (98, 13), (103, 8), ink, 2)
        cv2.line(self.plate, (98, 30), (107, 30), ink, 2)
        cv2.rectangle(self.plate, (115, 8), (129, 30), ink, 2)
        cv2.line(self.plate, (115, 18), (129, 18), ink, 2)
        view = {'source_size': [800, 320], 'content_rect': [0, 0, 800, 320]}
        prev = {'viewport': view, 'texts': self.labels,
                'run': {'page': 'run_map', 'resources': {'gold': {'value': 23}}}}
        for rows, expected in [(['18', '1', '8'], 18), (['18', '1', '0'], None),
                               (['8'], None)]:
            engine = Mock(side_effect=[([(s, .99)], None) for s in rows])
            result = read_gold_preview(self.image, self.image.copy(), prev, view, engine)
            self.assertEqual((result or {}).get('value'), expected)
        # The same faint green cast qualifies only at the icon-facing edge.
        for col, expected in [(1, 18), (25, None)]:
            tinted = self.image.copy()
            tinted[40:68, 511+col] = (48, 53, 39)
            engine = Mock(side_effect=[([(s, .99)], None) for s in ('18', '1', '8')])
            result = read_gold_preview(tinted, self.image, prev, view, engine)
            self.assertEqual((result or {}).get('value'), expected)
        # A complete third glyph or a displaced leading price cannot become
        # the tens digit just because the last glyph is right-aligned.
        for shift in (False, True):
            extra = self.image.copy()
            plate = extra[37:73, 511:666]
            plate[:, 70:84] = plate[:, 96:110]
            if shift:
                plate[:, 96:110] = 49
            engine = Mock()
            self.assertIsNone(read_gold_preview(extra, self.image, prev, view, engine))
            engine.assert_not_called()
        # Removing the left wall opens both loops of the 8. An OCR claim
        # of 3 still contradicts the surviving upper right stroke.
        self.plate[12:26, 113:119] = 49
        engine = Mock(side_effect=[([(s, .99)], None) for s in ('13', '1', '3')])
        self.assertIsNone(read_gold_preview(self.image, self.image.copy(), prev, view, engine))

    def test_layout_only_requires_all_four_current_label_reads(self):
        view = {'source_size': [800, 320], 'content_rect': [0, 0, 800, 320]}
        seed = {'texts': self.labels, 'viewport': view}
        names = [r['text'] for r in self.labels]
        for last, expected in [('收藏品', 0), ('商品', None)]:
            reads = ['0', '0', *names[:-1], last]
            engine = Mock(side_effect=[([(s, .99)], None) for s in reads])
            result = read_gold_preview(self.image, None, seed, view, engine)
            self.assertEqual((result or {}).get('value'), expected)
            self.assertEqual(engine.call_count, 6)
