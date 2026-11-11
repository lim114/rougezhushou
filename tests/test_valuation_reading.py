import unittest

import cv2
import numpy as np

from rouge.hud_resources import read_hud_resources


class ValuationReadingTests(unittest.TestCase):
    def image(self, digits='10', color=(170, 255, 0)):
        image = np.zeros((240, 400, 3), np.uint8)
        cv2.putText(image, digits, (95, 123), cv2.FONT_HERSHEY_SIMPLEX, 1., color, 2)
        # Tiny coloured highlights on the neighbouring grey icon are not digits.
        image[107, 78] = color
        texts = [{'text': '总估价', 'confidence': .99,
                  'box': [[.2, .25], [.45, .25], [.45, .375], [.2, .375]]}]
        return image, texts

    def test_complete_coloured_line_corrects_partial_fallback_detection(self):
        image, texts = self.image()
        calls = []

        def engine(pixels, **options):
            calls.append((pixels.copy(), options))
            if options['use_det']:
                return [[[], '1', .99]], None
            return [['10', .99]], None

        actual = read_hud_resources(image, texts, engine)
        self.assertEqual(actual['valuation']['value'], 10)
        self.assertEqual(len(calls), 1)
        pixels, options = calls[0]
        self.assertEqual(options, {'use_cls': False, 'use_det': False})
        # Both printed digits reach the recognizer, without the icon highlight.
        foreground = (pixels[:, :, 0] > 127).astype(np.uint8)
        self.assertEqual(cv2.connectedComponents(foreground)[0] - 1, 2)

    def test_zero_and_multiple_digits_use_one_recognition_call(self):
        for digits in ('0', '7', '10', '127'):
            with self.subTest(digits=digits):
                image, texts = self.image(digits)
                calls = []

                def engine(pixels, **options):
                    calls.append(options)
                    return [[digits, .99]], None

                self.assertEqual(read_hud_resources(image, texts, engine)['valuation']['value'], int(digits))
                self.assertEqual(calls, [{'use_cls': False, 'use_det': False}])

    def test_unreadable_colour_line_keeps_original_detection(self):
        image, texts = self.image()
        calls = []

        def engine(pixels, **options):
            calls.append(options)
            if not options['use_det']:
                return [['10', .6]], None
            return [[[], '10', .99]], None

        self.assertEqual(read_hud_resources(image, texts, engine)['valuation']['value'], 10)
        self.assertEqual([c['use_det'] for c in calls], [False, True])

    def test_other_colour_uses_original_detector(self):
        image, texts = self.image(color=(240, 240, 240))
        calls = []

        def engine(pixels, **options):
            calls.append(options)
            return [[[], '10', .99]], None

        self.assertEqual(read_hud_resources(image, texts, engine)['valuation']['value'], 10)
        self.assertEqual(calls, [{'use_cls': False, 'use_det': True}])

    def test_colour_without_current_label_does_not_supply_a_resource(self):
        image, _ = self.image()

        def engine(*args, **kwargs):
            self.fail('Unlabelled pixels must not be read as valuation')

        self.assertEqual(read_hud_resources(image, [], engine), {})

    def test_existing_confident_number_needs_no_crop_read(self):
        image, texts = self.image()
        texts.append({'text': '10', 'confidence': .99,
                      'box': [[.24, .4], [.34, .4], [.34, .5], [.24, .5]]})

        def engine(*args, **kwargs):
            self.fail('The full-frame number is already available')

        self.assertEqual(read_hud_resources(image, texts, engine)['valuation']['value'], 10)
