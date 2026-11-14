"""Real model calls, including the shared full-reader / HUD session boundary."""
from concurrent.futures import ThreadPoolExecutor
from importlib.util import find_spec
import unittest

import cv2
import numpy as np

from rouge.ocr_engine import create_engine


@unittest.skipUnless(find_spec('openvino'), 'OpenVINO is a Windows x64 runtime dependency')
class CPUBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = create_engine(backend='onnx')
        cls.optimized = create_engine(backend='openvino')

    def lines(self):
        result = []
        for text in ('012345', '98', '7001'):
            line = np.full((48, 210, 3), 255, np.uint8)
            cv2.putText(line, text, (4, 36), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            result.append(line)
        return result

    def test_cold_compiles_overlap_and_keep_model_roles(self):
        from pathlib import Path
        from threading import Barrier
        from types import SimpleNamespace
        from unittest.mock import patch
        from rouge.ocr_cpu_inference import use_cpu_inference

        all_started = Barrier(3, timeout=3)
        def compile_model(core, path):
            all_started.wait()
            return Path(path).name
        engine = SimpleNamespace(text_det=SimpleNamespace(), text_cls=SimpleNamespace(),
                                 text_rec=SimpleNamespace())
        with patch('rouge.ocr_cpu_inference.CPUInference', side_effect=compile_model):
            use_cpu_inference(engine)
        self.assertIn('_det_', engine.text_det.infer)
        self.assertIn('_cls_', engine.text_cls.infer)
        self.assertIn('_rec_', engine.text_rec.session)

    def test_upright_lines_match_original_without_changing_threshold(self):
        for image in self.lines():
            expected, _ = self.original(image, use_det=False, use_cls=False)
            actual, _ = self.optimized(image, use_det=False, use_cls=False)
            self.assertEqual([r[0] for r in actual], [r[0] for r in expected])
            np.testing.assert_allclose([r[1] for r in actual], [r[1] for r in expected], atol=2e-5, rtol=0)

    def test_shared_recognizer_concurrent_requests_own_their_outputs(self):
        recognizer = self.optimized.text_rec
        tensors = [recognizer.resize_norm_img(line, 320 / 48)[None].astype(np.float32)
                   for line in self.lines()]
        expected = [recognizer.session(t)[0].copy() for t in tensors]
        # The busy HUD preview and full page share this inference callable.
        # Submit different images repeatedly; later calls must not overwrite
        # arrays already returned to the other reader.
        with ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(lambda i: recognizer.session(tensors[i % 3])[0], range(18)))
        for i, output in enumerate(results):
            np.testing.assert_array_equal(output, expected[i % 3])

    def test_detector_boxes_and_orientation_match_original(self):
        image = np.vstack(self.lines())
        original, _ = self.original.text_det(image)
        optimized, _ = self.optimized.text_det(image)
        np.testing.assert_array_equal(optimized, original)
        a, _ = self.original.text_cls(self.lines())[1:]
        b, _ = self.optimized.text_cls(self.lines())[1:]
        self.assertEqual([x[0] for x in a], [x[0] for x in b])
