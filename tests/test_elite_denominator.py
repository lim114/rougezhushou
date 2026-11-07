import unittest
from unittest.mock import patch
import cv2
import numpy as np
from rouge import elite_recognition as model


class EliteDenominatorTests(unittest.TestCase):
    def templates(self):
        result = {}
        for elite in range(3):
            image = np.zeros((32, 32, 4), dtype=np.uint8)
            image[:, :, 3] = 255
            if elite == 0:
                image[4:28, 13:19, :3] = 255
            elif elite == 1:
                image[13:19, 4:28, :3] = 255
            else:
                image[5:27, 5:27, :3] = 255
            result[elite] = image
        return result

    def test_blank_observation_has_zero_score_without_zero_denominator(self):
        with patch.object(model, 'references', return_value=self.templates()):
            self.assertIsNone(model.card_elite(np.zeros((1000, 1000, 3), dtype=np.uint8), .5, .5))

    def test_card_region_is_read_once_per_size_and_offset(self):
        image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        original = cv2.cvtColor
        regions = []
        def capture(pixels, code):
            if np.shares_memory(pixels, image):
                regions.append((pixels.shape, pixels.ctypes.data))
            return original(pixels, code)
        with patch.object(model, 'references', return_value=self.templates()), \
                patch.object(cv2, 'cvtColor', side_effect=capture):
            model.card_elite(image, .5, .5)
        self.assertGreater(len(regions), 0)
        self.assertEqual(len(regions), len(set(regions)))

    def test_empty_masks_skip_scoring(self):
        icons = {i: np.zeros((32, 32, 4), dtype=np.uint8) for i in range(3)}
        with patch.object(model, 'references', return_value=icons):
            self.assertIsNone(model.card_elite(np.zeros((1000, 1000, 3), dtype=np.uint8), .5, .5))

    def test_exact_silhouettes_keep_identity_and_full_score(self):
        icons = self.templates()
        for elite, icon in icons.items():
            frame = np.zeros((1000, 1000, 3), dtype=np.uint8)
            template = cv2.resize(icon, (40, 40), interpolation=cv2.INTER_AREA)
            mask = (cv2.cvtColor(template[:, :, :3], cv2.COLOR_BGR2GRAY) > 150) & (template[:, :, 3] > 150)
            frame[428:468, 496:536] = mask[:, :, None].astype(np.uint8) * 255
            with self.subTest(elite=elite), patch.object(model, 'references', return_value=icons):
                found = model.card_elite(frame, .5, .5)
                self.assertEqual(found['value'], elite)
                self.assertEqual(found['score'], 1)
