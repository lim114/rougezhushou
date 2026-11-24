import unittest
from unittest.mock import Mock
from threading import Event
from time import monotonic, sleep

import cv2
import numpy as np

from rouge.map_text_preview import CurrentMapPreview, detached_marker


class MapPreviewMarkerTests(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((600, 800, 3), np.uint8)
        self.arrow = np.array([(92, 200), (108, 200), (100, 214)])
        cv2.fillConvexPoly(self.image, self.arrow, (255, 255, 255))
        self.image[188:195, 65:133] = (50, 80, 100)
        self.reader = Mock()

    def test_verifies_current_pixels_above_the_arrow(self):
        self.reader.text_rec.return_value = ([('YOU ARE HERE', .97)], 0.)
        box, score, height = detached_marker(self.image, self.reader)
        left, top = box[0].astype(int)
        right, bottom = box[2].astype(int)
        crop, = self.reader.text_rec.call_args.args[0]
        np.testing.assert_array_equal(crop, self.image[top:bottom, left:right])
        self.assertTrue(np.any(crop))
        self.assertLessEqual(bottom, 200)
        self.assertEqual(score, .97)
        self.assertGreater(height, 0)

    def test_requires_both_the_exact_word_and_its_confidence(self):
        for result in [('YQUAREHERE', .99), ('YOUAREHERE', .89)]:
            with self.subTest(result=result):
                self.reader.text_rec.return_value = ([result], 0.)
                self.assertIsNone(detached_marker(self.image, self.reader))

    def test_two_arrows_do_not_schedule_text_recognition(self):
        cv2.fillConvexPoly(self.image, self.arrow + [200, 0], (255, 255, 255))
        self.assertIsNone(detached_marker(self.image, self.reader))
        self.reader.text_rec.assert_not_called()


class MapPreviewQueueTests(unittest.TestCase):
    def test_busy_worker_coalesces_frames_and_checks_eligibility_before_reading(self):
        from PySide6.QtWidgets import QApplication
        qt = QApplication.instance() or QApplication([])
        for still_visible in (True, False):
            with self.subTest(still_visible=still_visible):
                reader = CurrentMapPreview(None)
                release = Event()
                calls = []
                def first():
                    calls.append(1)
                    release.wait(3)
                reader.offer(1, lambda: True, first)
                for index in (2, 4, 3):
                    reader.offer(index, lambda: still_visible, lambda i=index: calls.append(i))
                release.set()
                until = monotonic() + 3
                while reader.running and monotonic() < until:
                    qt.processEvents()
                    sleep(.002)
                self.assertFalse(reader.running)
                self.assertEqual(calls, [1, 4] if still_visible else [1])
