import unittest

import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.ocr_engine import create_engine


class DetectorInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = RapidOCR(intra_op_num_threads=4, inter_op_num_threads=2).text_det
        cls.optimized = create_engine().text_det

    def test_detect_tensor_matches_provider(self):
        rng = np.random.default_rng(825)
        levels = np.arange(256, dtype=np.uint8)
        ramp = np.tile(np.stack((levels, levels[::-1], levels ^ 87), axis=-1), (96, 1, 1))
        for image in (ramp, rng.integers(256, size=(721, 1365, 3), dtype=np.uint8),
                      ramp[:, ::2], ramp.astype(np.float32) / 255, ramp.astype(np.uint16)):
            with self.subTest(shape=image.shape, dtype=image.dtype):
                side = max(image.shape[:2])
                expected = self.original.get_preprocess(side)(image)
                actual = self.optimized.get_preprocess(side)(image)
                self.assertEqual(actual.shape, expected.shape)
                self.assertEqual(actual.dtype, expected.dtype)
                self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_channel_specific_settings_and_unscaled_byte_values(self):
        levels = np.arange(256, dtype=np.uint8)
        pixels = np.tile(np.stack((levels, levels ^ 91, levels[::-1]), axis=-1), (736, 3, 1))
        for det in (self.original, self.optimized):
            self.addCleanup(setattr, det, 'mean', det.mean)
            self.addCleanup(setattr, det, 'std', det.std)
            det.mean = [.2, .4, .6]
            det.std = [.3, .8, .1]
        expected = self.original.get_preprocess(768)(pixels)
        actual = self.optimized.get_preprocess(768)(pixels)
        self.assertEqual(actual.tobytes(), expected.tobytes())
