"""Speculative text boxes may serve only the detector input that produced them."""
from concurrent.futures import Future
import unittest
from unittest.mock import Mock

import numpy as np

from rouge.frame_buffer import FrameBuffer
from rouge.page_detection import SettlingDetection, detect_boxes


class SettlingDetectionTests(unittest.TestCase):
    def test_busy_page_preparation_uses_only_the_free_reader(self):
        from rouge.app import MainWindow
        app = Mock(closing=False, busy=True)
        app.settling_detection.whole_page_only = False
        app.auto.isChecked.return_value = True
        app.recognition_mode.currentData.return_value = 'ocr'
        popup = app.compact_window.inventory_popup
        app.compact_window.active_popup = popup
        popup.panel.isVisible.return_value = True
        for slot, free in ((0, app.secondary_reader), (1, app.reader)):
            app.sample_jobs = {8: {'slot': slot, 'seq': 27}}
            MainWindow.prepare_settling_page(app)
            app.settling_detection.offer.assert_called_once_with(
                app.capture.buffer, free._discovery_ocr.provider, discovery=free._discovery_ocr,
                previous=free._last_frame, inventory_visible=True)
            app.settling_detection.offer.reset_mock()
        for jobs in ({8: {'slot': 0, 'seq': 0}},
                     {8: {'slot': 0, 'seq': 27}, 9: {'slot': 1, 'seq': 28}}):
            app.sample_jobs = jobs
            MainWindow.prepare_settling_page(app)
            app.settling_detection.offer.assert_not_called()
        app.sample_jobs = {8: {'slot': 0, 'seq': 27}}
        popup.panel.isVisible.return_value = False
        app.compact_window.map_popup = None
        MainWindow.prepare_settling_page(app)
        app.settling_detection.offer.assert_not_called()
        app.settling_detection.whole_page_only = True
        popup.panel.isVisible.return_value = True
        MainWindow.prepare_settling_page(app)
        app.settling_detection.offer.assert_not_called()
        app.busy = False
        app.sample_jobs = {}
        MainWindow.prepare_settling_page(app)
        app.settling_detection.offer.assert_called_once_with(
            app.capture.buffer, app.reader._discovery_ocr.provider, discovery=app.reader._discovery_ocr,
            previous=app.reader._last_frame, inventory_visible=True)

    def test_cpu_ignores_local_animation_and_releases_previous_detection(self):
        buffer = FrameBuffer(settle_seconds=60)
        preview = SettlingDetection(whole_page_only=True)
        self.addCleanup(preview.close)
        image = np.full((360, 640, 3), 40, np.uint8)
        buffer.offer(image, 1.)
        preview.future = Future()
        preview.future.set_result(None)
        previous = image.copy()
        previous[:16] = 255
        preview.offer(buffer, Mock(), discovery=Mock(), previous=previous)
        self.assertIsNone(preview.for_frame(buffer.latest()))

    def test_new_reader_does_not_wait_for_previous_readers_text(self):
        preview = SettlingDetection()
        self.addCleanup(preview.close)
        owner = Mock()
        future = Future()
        preview.text_provider, preview.text_future = owner.provider, future
        self.assertIsNone(preview.take_text(Mock()))
        self.assertIs(preview.take_text(owner), future)
        self.assertIsNone(preview.take_text(owner))

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
