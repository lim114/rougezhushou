"""Approved hover boundary behavior; isolated Qt objects, no game capture."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication, QWidget
from rouge.player_game_hover import GameHover


class HoverDefenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.companion = QWidget()
        self.companion.hidden_windows = None
        self.companion.game_binding = SimpleNamespace(snapshot={
            'active': True, 'cursor_on_game': True, 'key': (1, 2),
            'physical_client': (0, 0, 100, 100), 'cursor': (50, 50),
            'target': {'hwnd': 1, 'pid': 2},
        })
        self.owner = SimpleNamespace(closing=False, run=SimpleNamespace(
            recognition_context=lambda: {'run_id': 'isolated', 'config': {}}))
        self.provider = Mock(side_effect=RuntimeError('isolated failure'))
        self.hover = GameHover(self.companion, self.owner, frame_provider=self.provider)
        self.hover.timer.stop()
        self.hover.gate.delay = 0
        self.addCleanup(self.companion.deleteLater)
        self.addCleanup(self.hover.close)

    def test_worker_failure_emits_once_releases_busy_and_allows_next_hover(self):
        received = []
        self.hover.received.connect(received.append)
        for expected in (1, 2):
            self.hover.invalidate()
            self.hover.tick()
            self.hover.tick()
            deadline = time.monotonic() + 3
            while len(received) < expected and time.monotonic() < deadline:
                self.qt.processEvents()
                time.sleep(.005)
            self.assertEqual(len(received), expected)
            self.assertFalse(self.hover.busy)
            self.assertEqual(self.provider.call_count, expected)
            self.assertIsNone(received[-1]['item'])
            self.assertIn('RuntimeError', received[-1]['reason'])

    def test_user_hidden_state_stops_sampling_and_rejects_inflight_item(self):
        self.companion.hidden_windows = []
        self.hover.tick()
        self.hover.tick()
        self.provider.assert_not_called()
        self.hover.busy = True
        self.hover.accept({'request': {}, 'item': {'confirmed': True}})
        self.assertFalse(self.hover.busy)
        self.assertFalse(self.hover.last_report['accepted'])
        self.assertIsNone(self.hover.card)

    def test_missing_required_companion_attribute_is_not_silently_accepted(self):
        del self.companion.hidden_windows
        with self.assertRaises(AttributeError):
            self.hover.tick()
        with self.assertRaises(AttributeError):
            self.hover.accept({'request': {}, 'item': None})
