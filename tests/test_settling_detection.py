"""Speculative text boxes may serve only the detector input that produced them."""
from concurrent.futures import Future
import unittest
from unittest.mock import Mock

import numpy as np

from rouge.frame_buffer import FrameBuffer
from rouge.page_detection import SettlingDetection, detect_boxes


class SettlingDetectionTests(unittest.TestCase):
    def test_prepared_text_requires_same_model_and_every_viewport_pixel(self):
        from rouge.page_ocr import PageOCR
        image = np.zeros((30, 40, 3), np.uint8)
        prepared = PageOCR(Mock())
        prepared._current_frame = image.copy()
        prepared.metrics = {'complete_current_texts': True}
        future = Future()
        rows = ([('current text',)], None)
        future.set_result(('original', prepared, rows))
        class Selected(PageOCR):
            configuration = 'original'
            def _configuration(self):return self.configuration
            def __call__(self, image, *, detection):return 'fresh OCR'
        reader = Selected(Mock())
        self.assertIs(reader.read_prepared(image.copy(), future, None), rows)
        self.assertTrue(reader.metrics['settling_text_reused'])
        reader.configuration = 'other'
        self.assertEqual(reader.read_prepared(image, future, None), 'fresh OCR')
        reader.configuration = 'original'
        image[-1, -1, -1] = 1
        self.assertEqual(reader.read_prepared(image, future, None), 'fresh OCR')

    def test_current_detector_input_must_match_and_unfinished_work_never_blocks(self):
        provider = Mock()
        image = np.zeros((20, 30, 3), np.uint8)
        future = Future()
        self.assertIs(detect_boxes(provider, image, future), provider.auto_text_det.return_value)
        prepared = object()
        future.set_result((provider, image.copy(), prepared))
        self.assertIs(detect_boxes(provider, image.copy(), future), prepared)
        other = Mock()
        self.assertIs(detect_boxes(other, image, future), other.auto_text_det.return_value)
        image[0, 0, 0] = 1
        self.assertIs(detect_boxes(provider, image, future), provider.auto_text_det.return_value)
        self.assertEqual(provider.auto_text_det.call_count, 2)

    def test_selected_page_after_transition_cannot_use_prior_frame_task(self):
        buffer = FrameBuffer(settle_seconds=60)
        preview = SettlingDetection()
        self.addCleanup(preview.close)
        first = np.full((360, 640, 3), 40, np.uint8)
        target = {'hwnd': 1, 'pid': 2}
        buffer.offer(first, 1., target=target)
        provider = Mock()
        provider.load_img.side_effect = lambda image: image
        provider.preprocess.side_effect = lambda image: (image, 1., 1.)
        provider.maybe_add_letterbox.side_effect = lambda image, op: (image, op)
        preview.offer(buffer, provider)
        selected = buffer.latest()
        future = preview.for_frame(selected)
        self.assertIsNotNone(future)
        self.assertIs(future.result(timeout=5)[0], provider)
        self.assertIsNone(buffer.take())
        preview.offer(buffer, provider)
        self.assertIs(preview.for_frame(selected), future)
        buffer.offer(255-first, 2., target=target)
        newer = buffer.take(prefer_latest=True)
        self.assertIsNotNone(newer)
        self.assertIsNone(preview.for_frame(newer))
        self.assertIsNone(preview.for_frame({**selected, 'generation': buffer.clear()}))
