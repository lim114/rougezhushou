import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np
from PySide6.QtCore import QCoreApplication, QObject
from PySide6.QtWidgets import QApplication

from rouge.busy_gold import BusyGold, GoldReference
from rouge.frame_buffer import FrameBuffer


class BusyGoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.w = QObject()
        self.buffer = FrameBuffer()
        self.w.capture = SimpleNamespace(buffer=self.buffer, stats=self.buffer.stats, check_health=Mock(),
                                         target={'hwnd': 1, 'pid': 2})
        self.w.run = SimpleNamespace(state={'id': 'one'})
        self.w.closing = False
        self.w.busy = True
        self.w.auto = Mock()
        self.w.auto.isChecked.return_value = True
        self.w.sample_epoch = 4
        self.w.last_sample_at = 0
        self.w.last_sample_seq = 0
        self.w.compact_window = Mock()
        self.w.refresh_display_hud = Mock()
        self.probe = BusyGold(self.w)
        self.offer(20)
        self.ref = GoldReference(self.probe.current_marker(), self.buffer.latest(), {}, Mock())
        self.probe.accept_reference(self.ref)

    def offer(self, value, target=None):
        image = np.full((200, 360, 3), value, np.uint8)
        self.buffer.offer(image, time.time(), [0, 0, 360, 200], target or self.w.capture.target)

    def wait_idle(self):
        deadline = time.monotonic() + 3
        while self.probe.running and time.monotonic() < deadline:
            QCoreApplication.processEvents()
            time.sleep(.003)
        self.assertFalse(self.probe.running)

    def test_only_newest_frame_is_peeked_and_backlog_is_not_consumed(self):
        started, release = threading.Event(), threading.Event()
        seen = []
        def check(frame, *args):
            value = int(frame[0, 0, 0])
            seen.append(value)
            started.set()
            release.wait(3)
            return {'value': value}
        with patch('rouge.busy_gold.read_gold_preview', side_effect=check):
            self.offer(22)
            self.probe.poll()
            self.assertTrue(started.wait(2))
            self.offer(28)
            self.offer(30)
            backlog = self.buffer.stats()['pending']
            self.probe.poll()
            release.set()
            self.wait_idle()
            self.probe.poll()
            self.wait_idle()
            self.probe.poll()
            self.assertEqual(seen, [22, 30])
            self.assertEqual(self.buffer.stats()['pending'], backlog)
            self.assertEqual(self.probe.shown[1]['value'], 30)
            self.probe.complete(self.ref.marker, 2, map_read=True)
            self.assertEqual(self.probe.shown[1]['value'], 30)
            self.probe.complete(self.ref.marker, 4, map_read=True)
            self.assertIsNone(self.probe.shown)

    def test_idle_pending_candidate_previews_before_full_sampler_selects_it(self):
        self.w.busy = False
        self.buffer.take(force=True)
        self.offer(22)
        with patch('rouge.busy_gold.read_gold_preview', return_value={'value': 22}) as read:
            self.w.compact_window.visible_current_resource_strips.return_value = []
            self.probe.poll()
            self.wait_idle()
            read.assert_not_called()
            self.w.compact_window.visible_current_resource_strips.return_value = [object()]
            self.probe.poll()
            self.wait_idle()
            self.assertIsNotNone(self.probe.shown)
            self.assertEqual(self.probe.shown[1]['value'], 22)
            self.assertEqual(self.buffer.stats()['pending'], 1)
            self.probe.poll()
            read.assert_called_once()
            self.buffer.take(force=True)
            self.offer(22)
            self.assertEqual(self.buffer.stats()['pending'], 0)
            self.probe.poll()
            self.wait_idle()
            read.assert_called_once()

    def test_inflight_result_after_reset_minimize_or_canonical_commit_is_ignored(self):
        payload = (self.ref, time.time(), 2, {'value': 22})
        self.w.sample_epoch += 1
        self.probe.accept_result(payload)
        self.assertIsNone(self.probe.shown)
        self.w.sample_epoch -= 1
        self.probe.accept_reference(self.ref)
        self.w.last_sample_at, self.w.last_sample_seq = payload[1:3]
        self.probe.accept_result(payload)
        self.assertIsNone(self.probe.shown)
        self.w.last_sample_seq = 1
        self.w.capture.check_health.side_effect = RuntimeError('minimized')
        self.probe.accept_result(payload)
        self.assertIsNone(self.probe.reference)
        self.assertIsNone(self.probe.shown)

    def test_unqualified_frame_withdraws_and_window_change_invalidates_source(self):
        self.offer(22)
        self.probe.accept_result((self.ref, time.time(), 2, {'value': 22}))
        self.probe.accept_result((self.ref, time.time(), 3, None))
        self.assertIsNone(self.probe.shown)
        self.offer(8, {'hwnd': 45, 'pid': 6})
        self.probe.poll()
        self.assertIsNone(self.probe.reference)
        self.assertFalse(self.probe.running)
