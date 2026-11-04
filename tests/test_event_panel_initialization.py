"""Event-specific controls exist before the first reference read."""
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.current_agency_view import CurrentAgencyPanel
from rouge.current_startup_view import CurrentStartupPanel
from rouge.documented_event_flow_view import DocumentedEventFlowPanel


class EventInitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_agency_reads_once_with_controls_already_present(self):
        reads = []
        original = CurrentAgencyPanel._fresh_reference
        def read(panel):
            reads.append((panel.offer.currentData(), len(panel.pair_icons)))
            return original(panel)
        with patch.object(CurrentAgencyPanel, '_fresh_reference', read):
            panel = CurrentAgencyPanel()
        self.addCleanup(panel.close)
        self.assertEqual(reads, [(None, 2)])
        self.assertIsNotNone(panel.result)

    def test_startup_reads_once_after_reward_controls_exist(self):
        reads = []
        original = CurrentStartupPanel._fresh_reference
        def read(panel):
            reads.append((panel.group.currentData(), panel.gold.value(), panel.reward_name.text()))
            return original(panel)
        with patch.object(CurrentStartupPanel, '_fresh_reference', read):
            panel = CurrentStartupPanel()
        self.addCleanup(panel.close)
        self.assertEqual(reads, [('all', -1, '')])
        self.assertIsNotNone(panel.result)

    def test_deferred_base_does_not_read_until_explicit_refresh(self):
        with patch.object(DocumentedEventFlowPanel, '_fresh_reference', return_value=None) as read:
            panel = DocumentedEventFlowPanel('button', defer_initial_refresh=True)
            self.addCleanup(panel.close)
            read.assert_not_called()
            panel.refresh_reference(initial=True)
            read.assert_called_once()
