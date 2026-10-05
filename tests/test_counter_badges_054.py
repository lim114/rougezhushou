"""Public-pixel glyph validation; scaled train copies are not holdout samples."""
from pathlib import Path
import hashlib
import json
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.counter_badges import read_counter_badges

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.cache/research/p1-counter-training-054'
SOURCE = ROOT / '.cache/research/p1-counter-images-054/source/taptap-hydra-100.jpg'
BOX = [[.172379, .619420], [.199093, .619420], [.199093, .647321], [.172379, .647321]]


def load(path):
    return cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)


def text(value='15', confidence=.99, box=BOX):
    return {'text': value, 'confidence': confidence, 'box': box}


class CounterBadgeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = load(SOURCE)

    def test_actual_train_badge_refines_digit_and_marker_boxes(self):
        result = read_counter_badges(self.image, [text()])
        self.assertEqual(len(result), 1)
        record = result[0]
        self.assertEqual(record['value'], 15)
        self.assertGreaterEqual(record['score'], .8)
        self.assertAlmostEqual(record['marker_box'][0][0], 549 / 3168)
        self.assertAlmostEqual(record['box'][0][0], 588 / 3168)
        self.assertLess(record['marker_box'][1][0], record['box'][0][0])
        self.assertFalse({'id', 'relic_id', 'used', 'complete'} & set(record))

    def test_digit_only_ocr_box_also_locates_adjacent_glyph(self):
        box = [[588 / 3168, 899 / 1440], [623 / 3168, 899 / 1440],
               [623 / 3168, 925 / 1440], [588 / 3168, 925 / 1440]]
        self.assertEqual(read_counter_badges(self.image, [text(box=box)])[0]['value'], 15)

    def test_prose_percentages_fractions_and_title_are_not_digit_candidates(self):
        for value in ('15%', '+15', '15/18', '攻击+15', '999', '1000', '15.0', ''):
            with self.subTest(value=value):
                self.assertEqual(read_counter_badges(self.image, [text(value=value)]), [])

    def test_low_confidence_and_invalid_boxes_remain_unknown(self):
        for record in (text(confidence=.94), text(confidence=None), text(confidence=float('nan')),
                       text(box=[]), text(box=[[0, 0], [2, 1]]), text(box=[[0, 0], [0, 0]])):
            with self.subTest(record=record):
                self.assertEqual(read_counter_badges(self.image, [record]), [])
        self.assertEqual(read_counter_badges(None, []), [])
        self.assertEqual(read_counter_badges(np.zeros((0, 0, 3), np.uint8), []), [])

    def test_duplicate_value_is_deduplicated_and_conflicting_value_is_unknown(self):
        self.assertEqual(len(read_counter_badges(self.image, [text(), text()])), 1)
        self.assertEqual(read_counter_badges(self.image, [text(), text('16')]), [])

    def test_actual_pixels_move_with_font_relative_search(self):
        crop = self.image[875:955, 530:652]
        # Derived fixture for geometry only, never counted as another source.
        canvas = np.zeros((260, 410, 3), np.uint8)
        canvas[105:185, 230:352] = crop
        pixel_box = [(x * 3168 - 530 + 230, y * 1440 - 875 + 105) for x, y in BOX]
        box = [[x / 410, y / 260] for x, y in pixel_box]
        for scale in (.5, .75, 1., 1.25):
            with self.subTest(scale=scale):
                image = cv2.resize(canvas, None, fx=scale, fy=scale,
                                   interpolation=cv2.INTER_AREA if scale <= 1 else cv2.INTER_LINEAR)
                result = read_counter_badges(image, [text(box=box)])
                self.assertEqual([r['value'] for r in result], [15])

    def test_no_full_frame_template_matching_or_ocr_is_called(self):
        with patch('rouge.counter_badges.cv2.matchTemplate', side_effect=AssertionError('No template sweep')):
            self.assertEqual(read_counter_badges(self.image, [text()])[0]['value'], 15)


class CounterBadgeIndependentValidationTests(unittest.TestCase):
    def test_frozen_parameters_precede_independent_ocr(self):
        freeze = json.loads((OUT / 'frozen-before-holdout.json').read_text(encoding='utf-8'))
        for path, digest in freeze.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        config = json.loads((ROOT / 'rouge/data/counter-badge-reference.json').read_text(encoding='utf-8'))
        self.assertFalse(config['calibration']['holdout_used'])
        annotation = json.loads((OUT / 'ANNOTATIONS.json').read_text(encoding='utf-8'))
        self.assertNotEqual(annotation['training']['split_group'], annotation['holdout']['split_group'])
        self.assertFalse(annotation['holdout']['pixels_loaded_by_build'])

    def test_actual_full_ocr_miss_retains_unknown(self):
        receipt = json.loads((OUT / 'independent-positive-ocr.json').read_text(encoding='utf-8'))
        source = ROOT / receipt['source']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), receipt['image_sha256'])
        result = read_counter_badges(load(source), receipt['texts'])
        # The frozen actual whole-frame OCR omitted this small isolated 1.
        # Glyph recognition must not invent the missing numeric candidate.
        self.assertEqual(result, [])

    def test_independent_glyph_generalizes_with_manual_numeric_anchor(self):
        receipt = json.loads((OUT / 'independent-positive-ocr.json').read_text(encoding='utf-8'))
        source = ROOT / receipt['source']
        manual = json.loads((OUT / 'manual-anchor-holdout.json').read_text(encoding='utf-8'))
        result = read_counter_badges(load(source),
                                     [text('1', manual['confidence_fixture'], manual['box'])])
        self.assertEqual([r['value'] for r in result], [1])
        self.assertNotIn('id', result[0])
        self.assertTrue(manual['actual_full_ocr_missed_digit'])
        self.assertFalse(manual['threshold_changed'])

    def test_independent_native_held_page_is_negative(self):
        receipt = json.loads((OUT / 'independent-negative-ocr.json').read_text(encoding='utf-8'))
        source = ROOT / receipt['source']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), receipt['image_sha256'])
        self.assertEqual(read_counter_badges(load(source), receipt['texts']), [])

    def test_calibration_negatives_have_no_badges(self):
        for image, ocr in [('run-relic-open.png', 'run-relic-open-ocr.json'),
                           ('run-map-closed.png', 'run-map-closed-ocr.json')]:
            with self.subTest(image=image):
                folder = ROOT / 'samples/native-client'
                texts = json.loads((folder / ocr).read_text(encoding='utf-8'))['texts']
                self.assertEqual(read_counter_badges(load(folder / image), texts), [])


if __name__ == '__main__':
    unittest.main()
