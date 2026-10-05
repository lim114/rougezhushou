"""The public reader may reuse identical pixels, never mutable caller state."""
import unittest
from pathlib import Path
import cv2
import numpy as np
from rouge.recognition import ScreenReader

ROOT = Path(__file__).resolve().parents[1]


class RecognitionReuseTests(unittest.TestCase):
    def test_identical_frame_keeps_evidence_and_refreshes_observation_without_sharing_mutations(self):
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client/module-mechanist.png', dtype=np.uint8), 1)
        reader = ScreenReader()
        first = reader.read(image)
        self.assertEqual(first['operator']['id'], 'mechanist')
        first['operator']['fields']['module_level'] = 99
        second = reader.read(image.copy())
        self.assertEqual(second['operator']['fields']['module_level'], 3)
        self.assertEqual(second['page'], 'operator_module')
        self.assertGreater(second['observed_at'], first['observed_at'])
        self.assertEqual(second['performance']['reuse'], 'exact_frame')

    def test_animation_reuses_only_unchanged_bar_and_removed_artwork_is_read_again(self):
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client/run-map-closed.png', dtype=np.uint8), 1)
        reader = ScreenReader()
        first = reader.read(image)
        self.assertEqual(first['run']['relics']['ids'], ['rogue_6_relic_legacy_52'])
        animated = image.copy()
        animated[400:420, 50:70] = 255 - animated[400:420, 50:70]
        second = reader.read(animated)
        self.assertEqual(second['performance']['reuse'], 'none')
        self.assertEqual(second['performance']['icon_cache_hits'], 1)
        self.assertGreater(second['performance']['ocr_cache_hits'], 0)
        self.assertEqual(second['run']['relics']['ids'], ['rogue_6_relic_legacy_52'])
        removed = animated.copy()
        removed[1020:1110, 300:900] = 0
        third = reader.read(removed)
        self.assertEqual(third['performance']['icon_cache_hits'], 0)
        self.assertEqual(third['run']['relics']['ids'], [])

    def test_changed_operator_background_preserves_verified_potential_and_skills(self):
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client/operator-mechanist.png', dtype=np.uint8), 1)
        reader = ScreenReader()
        first = reader.read(image)
        self.assertEqual(first['operator']['fields']['potential'], 6)
        image[400:408, 40:48] = 255-image[400:408, 40:48]
        second = reader.read(image)
        self.assertEqual(second['performance']['reuse'], 'none')
        self.assertGreater(second['performance']['icon_cache_hits'], 0)
        self.assertEqual(second['operator']['fields']['potential'], 6)
        self.assertEqual(second['operator']['skill_ranks'], {1:10,2:9,3:10})

    def test_client_rectangle_change_recomputes_viewport_for_the_same_pixels(self):
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client/module-mechanist.png', dtype=np.uint8), 1)
        reader = ScreenReader()
        reader.read(image)
        rectangle = [2,45,image.shape[1]-2,image.shape[0]-2]
        cropped = reader.read(image,client_rect=rectangle)
        self.assertEqual(cropped['performance']['reuse'], 'none')
        self.assertEqual(cropped['viewport']['content_rect'], rectangle)
        self.assertEqual(cropped['operator']['id'], 'mechanist')

