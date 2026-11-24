import unittest
from unittest.mock import Mock, patch
from threading import Event
from time import monotonic, sleep

import cv2
import numpy as np

from rouge.map_text_preview import CurrentMapPreview, detached_marker
from rouge.map_recognition import _label_point, _label_rows, _ring_candidates, read_map


class MapPreviewRowTests(unittest.TestCase):
    def test_row_search_uses_all_rows_and_the_exit_label_offset(self):
        points = []
        for top, name in [(.226, '作战'), (.526, '作战'), (.85, '险路尽头')]:
            box = [[.2, top], [.3, top], [.3, top+.02], [.2, top+.02]]
            points.append(_label_point({'type': name, 'confidence': .99, 'box': box}))
        rows, pitch = _label_rows(points, 3)
        np.testing.assert_allclose(rows, [.2, .5, .8])
        self.assertAlmostEqual(pitch, .3)
        self.assertIsNone(_label_rows(points[:2], 3))

    def test_padding_gives_the_detector_context_but_cannot_supply_an_off_row_circle(self):
        gray = np.zeros((200, 250), np.uint8)
        circles = np.array([[[46, 3, 6], [84, 21, 6]]], dtype=np.float32)
        with patch.object(cv2, 'HoughCircles', return_value=circles) as detect:
            result = list(_ring_candidates(gray, 12, [(50, 90, 70, 6)]))
        self.assertEqual(detect.call_args.args[0].shape, (40, 250))
        self.assertEqual(result, [(84, 71, 6)])

    def test_circle_beyond_last_column_does_not_obscure_a_complete_set_of_labeled_rows(self):
        height, width = 1080, 1920
        image = np.full((height, width, 3), 180, np.uint8)
        layout = [
            ['', '未知的诡秘', None, '未知的凶戾', '未知的诡秘'],
            [None, '作战', None, '未知的诡秘', ''],
            ['', None, '未知的凶戾', '未知的诡秘', '险路尽头'],
        ]
        labels = []
        for row, cells in enumerate(layout):
            for col, name in enumerate(cells):
                x, y = .2 + .15*col, .24 + .24*row
                if name is None:
                    cv2.circle(image, (round(x*width), round(y*height)), 13, (28, 28, 28), 4, cv2.LINE_AA)
                elif name:
                    top = y + (.05 if name == '险路尽头' else .026)
                    box = [[x-.03, top], [x+.03, top], [x+.03, top+.02], [x-.03, top+.02]]
                    labels.append({'type': name, 'confidence': 1., 'box': box})
        cv2.circle(image, (1824, 205), 13, (28, 28, 28), 4, cv2.LINE_AA)
        graph = read_map(image, [], labels, {'config': {'zone': {'id': 'zone_1'}}}, use_label_rows=True)
        self.assertEqual(graph['template_id'], '1b')
        observed = {node['id']: node['observed_type'] for node in graph['nodes']}
        self.assertEqual(observed['1,0'], '林间空地')
        self.assertEqual(observed['2,4'], '险路尽头')


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
