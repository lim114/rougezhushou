"""Conservative projection filtering must preserve RGB matches and ambiguity."""
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge import relic_recognition as icons


def screen(image):
    pixels = image.astype(np.float32)
    return icons.ProjectionScreen(pixels, icons.EnergyScreen(pixels))


def prepared(rid, template, mask):
    binary = (mask != 0).astype(np.float32)
    pixels = template.astype(np.float32) * binary[:, :, None]
    energy = float(np.sum(pixels * pixels, dtype=np.float64))
    return rid, template, mask, pixels, binary, energy


class ProjectionScreen029Tests(unittest.TestCase):
    def test_necessary_bound_is_no_larger_than_true_normalized_rgb_error(self):
        rng = np.random.default_rng(2901)
        for shape in ((3, 5), (7, 4), (13, 17)):
            h, w = shape
            image = rng.integers(0, 256, (h + 6, w + 8, 3), dtype=np.uint8)
            template = rng.integers(0, 256, (h, w, 3), dtype=np.uint8)
            mask = (rng.random(shape) < .4).astype(np.uint8) * 255
            ref = prepared('test', template, mask)
            bound = screen(image)
            rectangle = bound.window_energy(shape)
            for y in range(7):
                for x in range(9):
                    patch_pixels = image[y:y+h, x:x+w].astype(np.float64)
                    difference = (patch_pixels - template) * (mask != 0)[:, :, None]
                    projected_ssd = float(np.sum(np.sum(difference, axis=2) ** 2 / 3))
                    rgb_ssd = float(np.sum(difference ** 2))
                    masked_energy = float(np.sum(patch_pixels ** 2 * (mask != 0)[:, :, None]))
                    true_ssd = rgb_ssd / np.sqrt(masked_energy * ref[-1])
                    lower = projected_ssd / np.sqrt(rectangle[y, x] * ref[-1])
                    self.assertLessEqual(lower, true_ssd + 1e-12)

    def test_translated_sparse_and_opaque_positive_matches_are_never_screened(self):
        rng = np.random.default_rng(2902)
        for fraction in (.02, .2, .7, 1):
            for x, y in ((0, 0), (3, 9), (25, 18)):
                template = rng.integers(1, 256, (17, 23, 3), dtype=np.uint8)
                mask = (rng.random((17, 23)) < fraction).astype(np.uint8) * 255
                if not np.any(mask):
                    mask[0, 0] = 255
                roi = rng.integers(0, 60, (36, 50, 3), dtype=np.uint8)
                region = roi[y:y+17, x:x+23]
                region[mask != 0] = template[mask != 0]
                _, _, _, t, m, energy = prepared('test', template, mask)
                self.assertTrue(screen(roi).possible(t, m, energy), (fraction, x, y))

    def test_brightness_changes_at_coarse_seed_margin_survive(self):
        template = np.full((20, 24, 3), 160, np.uint8)
        mask = np.full((20, 24), 255, np.uint8)
        _, _, _, t, m, energy = prepared('test', template, mask)
        for value in (114, 160, 224):
            roi = np.full((35, 60, 3), value, np.uint8)
            score = float(cv2.matchTemplate(roi, template, cv2.TM_SQDIFF_NORMED, mask=mask).min())
            self.assertLessEqual(score, .12)
            self.assertTrue(screen(roi).possible(t, m, energy))

    def test_random_near_matches_accepted_by_old_screen_survive(self):
        rng = np.random.default_rng(2903)
        checked = 0
        for size in (3, 8, 21):
            for alpha in (.1, .5, 1):
                for noise in (0, 2, 10, 30):
                    template = rng.integers(40, 216, (size, size+2, 3), dtype=np.uint8)
                    mask = (rng.random((size, size+2)) < alpha).astype(np.uint8) * 255
                    mask[0, 0] = 255
                    roi = rng.integers(0, 100, (size+7, size+12, 3), dtype=np.uint8)
                    noisy = np.clip(template.astype(np.int32) + rng.integers(-noise, noise+1, template.shape), 0, 255).astype(np.uint8)
                    roi[3:3+size, 4:6+size] = noisy
                    _, _, _, t, m, energy = prepared('test', template, mask)
                    differences = cv2.matchTemplate(roi, template, cv2.TM_SQDIFF_NORMED, mask=mask)
                    if float(np.nanmin(differences)) <= .12:
                        self.assertTrue(screen(roi).possible(t, m, energy), (size, alpha, noise))
                        checked += 1
        self.assertGreaterEqual(checked, 30)

    def test_distinct_shape_is_rejected_before_expensive_rgb_correlation(self):
        template = np.full((20, 24, 3), 200, np.uint8)
        mask = np.full((20, 24), 255, np.uint8)
        template[:, 12:] = 20
        roi = np.full((35, 60, 3), 110, np.uint8)
        refs = [prepared('striped', template, mask)]
        with patch.object(icons, 'prepared_templates', return_value=refs), \
                patch.object(icons, '_can_match', wraps=icons._can_match) as expensive:
            self.assertEqual(icons._match_bar(roi, 900, 1600, 0, 0), [])
        self.assertEqual(expensive.call_count, 0)

    def test_equal_projection_does_not_confirm_different_rgb_color(self):
        template = np.full((20, 24, 3), [230, 20, 20], np.uint8)
        distractor = np.full_like(template, [20, 230, 20])
        mask = np.full((20, 24), 255, np.uint8)
        image = np.zeros((50, 200, 3), np.uint8)
        image[14:34, 60:84] = template
        refs = [prepared('red', template, mask), prepared('green', distractor, mask)]
        _, _, _, t, m, energy = refs[1]
        self.assertTrue(screen(image).possible(t, m, energy))
        with patch.object(icons, 'prepared_templates', return_value=refs), \
                patch.object(icons, 'artwork_families', return_value={}):
            found = icons._match_bar(image, 900, 1600, 0, 0)
        self.assertEqual([r['id'] for r in found], ['red'])
        self.assertTrue(found[0]['confirmed'])

    def test_similar_rgb_references_keep_ambiguity_and_exact_scores(self):
        rng = np.random.default_rng(2904)
        template = rng.integers(80, 201, (20, 24, 3), dtype=np.uint8)
        similar = template + 1
        mask = np.full((20, 24), 255, np.uint8)
        image = np.zeros((50, 200, 3), np.uint8)
        image[14:34, 60:84] = template
        refs = [prepared('one', template, mask), prepared('two', similar, mask)]
        with patch.object(icons, 'prepared_templates', return_value=refs), \
                patch.object(icons, 'artwork_families', return_value={}):
            after = icons._match_bar(image, 900, 1600, 0, 0)
            with patch.object(icons.ProjectionScreen, 'possible', return_value=True):
                before = icons._match_bar(image, 900, 1600, 0, 0)
        self.assertEqual(after, before)
        self.assertEqual(after[0]['candidates'], ['one', 'two'])
        self.assertFalse(after[0]['confirmed'])

    def test_window_integrals_equal_direct_energy_at_every_translation(self):
        rng = np.random.default_rng(2905)
        image = rng.integers(0, 256, (19, 23, 3), dtype=np.uint8)
        bound = screen(image)
        for shape in ((2, 3), (5, 7), (18, 22)):
            result = bound.window_energy(shape)
            h, w = shape
            for y in range(20-h):
                for x in range(24-w):
                    value = np.sum(image[y:y+h, x:x+w].astype(np.float64) ** 2)
                    self.assertEqual(result[y, x], value)

    def test_window_cache_evicts_by_entry_count_without_changing_sums(self):
        bound = screen(np.full((30, 60, 3), 180, np.uint8))
        bound.max_cache_entries = 3
        first = bound.window_energy((3, 4)).copy()
        for size in range(4, 15):
            bound.window_energy((size, size))
        self.assertLessEqual(len(bound.windows), 3)
        np.testing.assert_array_equal(first, bound.window_energy((3, 4)))
        self.assertEqual(bound.cache_bytes, sum(a.nbytes for a in bound.windows.values()))

    def test_window_cache_byte_limit_and_large_uncached_array(self):
        bound = screen(np.full((30, 60, 3), 180, np.uint8))
        bound.max_cache_bytes = 3000
        for size in range(3, 29):
            bound.window_energy((size, size))
            self.assertLessEqual(bound.cache_bytes, bound.max_cache_bytes)
        self.assertEqual(bound.cache_bytes, sum(a.nbytes for a in bound.windows.values()))
        bound.max_cache_bytes = 1
        bound.windows.clear()
        bound.cache_bytes = 0
        value = bound.window_energy((3, 4))
        self.assertGreater(value.nbytes, 1)
        self.assertFalse(bound.windows)

    def test_new_frame_has_new_projection_and_sums(self):
        image = np.zeros((40, 80, 3), np.uint8)
        before = screen(image)
        image[:] = 200
        after = screen(image)
        self.assertFalse(np.any(before.scalar))
        self.assertTrue(np.all(after.scalar > 0))
        self.assertTrue(np.all(after.window_energy((10, 10)) > before.window_energy((10, 10))))

    def test_bad_energy_and_nonfinite_correlations_fall_back_to_verifier(self):
        bound = screen(np.full((30, 60, 3), 100, np.uint8))
        template = np.full((5, 7, 3), 100, np.float32)
        mask = np.ones((5, 7), np.float32)
        for energy in (0, -1, np.nan, np.inf):
            self.assertTrue(bound.possible(template, mask, energy))
        with patch.object(icons.cv2, 'matchTemplate', return_value=np.full((26, 54), np.nan, np.float32)):
            self.assertTrue(bound.possible(template, mask, 10000))


if __name__ == '__main__':
    unittest.main()
