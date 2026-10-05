"""A necessary energy bound may save work, never discard a plausible icon."""
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge import relic_recognition as icons


class RelicScreening024Tests(unittest.TestCase):
    def test_dark_empty_bar_rejects_bright_reference_before_correlations(self):
        roi = np.full((80, 500, 3), 8, np.uint8)
        template = np.full((55, 55, 3), 200, np.uint8)
        mask = np.full((55, 55), 255, np.uint8)
        binary = (mask != 0).astype(np.float32)
        pixels = template.astype(np.float32)
        prepared = [('bright', template, mask, pixels, binary, float(np.sum(pixels ** 2)))]
        with patch.object(icons, 'prepared_templates', return_value=prepared), \
                patch.object(icons, '_can_match', wraps=icons._can_match) as expensive:
            self.assertEqual(icons._match_bar(roi, 900, 1600, 0, 0), [])
        self.assertEqual(expensive.call_count, 0)

    def test_all_translated_masked_reference_patches_survive_energy_bound(self):
        # Different opaque areas and channel colors, including sparse masks;
        # the bound must not use rectangular template area as its energy.
        rng = np.random.default_rng(724)
        for fraction in (.03, .3, 1.):
            template = rng.integers(0, 256, (17, 23, 3), dtype=np.uint8)
            mask = (rng.random((17, 23)) < fraction).astype(np.uint8)
            template_energy = float(np.sum(template.astype(np.float64) ** 2 * mask[:, :, None]))
            for x, y in ((0, 0), (3, 5), (27, 19)):
                roi = np.zeros((36, 50, 3), np.uint8)
                roi[y:y+17, x:x+23] = template * mask[:, :, None]
                bound = icons.EnergyScreen(roi.astype(np.float32))
                self.assertTrue(bound.possible((17, 23), template_energy))

    def test_near_threshold_brightness_change_is_not_pruned(self):
        template = np.full((20, 24, 3), 160, np.uint8)
        mask = np.full((20, 24), 255, np.uint8)
        energy = float(np.sum(template.astype(np.float64) ** 2))
        for value in (114, 160, 224):
            roi = np.full((35, 60, 3), value, np.uint8)
            score = float(cv2.matchTemplate(roi, template, cv2.TM_SQDIFF_NORMED, mask=mask).min())
            self.assertLessEqual(score, .12)
            self.assertTrue(icons.EnergyScreen(roi.astype(np.float32)).possible((20, 24), energy))


if __name__ == '__main__':
    unittest.main()
