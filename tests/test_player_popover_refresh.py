"""Qt lifecycle integration: hidden readers rest, restored readers are current."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from PySide6.QtCore import Qt, QEvent, QPoint, QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit

from rouge.player_compact import CompactAssistant, ToolPopover


class Reader(QWidget):
    def __init__(self, run):
        super().__init__()
        self.run = run
        self.calls = 0
        self.snapshot = None
        self.query = QLineEdit(self)

    def refresh(self):
        self.calls += 1
        self.snapshot = self.run.state.get('test_revision')


class PopoverRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.run = SimpleNamespace(state={'test_revision': 1})
        self.owner.closing = True
        self.owner.open_scene_notes = lambda: None
        self.owner.open_public_statistics = lambda: None
        self.bar = CompactAssistant(self.owner)
        self.addCleanup(self.owner.deleteLater)
        self.addCleanup(self.bar.close)
        self.addCleanup(self.close_children)

    def close_children(self):
        for child in self.bar.findChildren(ToolPopover):
            child.hide()

    def reader(self, slot):
        reader = Reader(self.owner.run)
        popup = ToolPopover('只读测试', reader, self.bar, on_show=self.bar.refresh)
        popup.panel = reader
        setattr(self.bar, slot, popup)
        return popup, reader

    def test_closed_readers_do_no_work_during_repeated_run_updates(self):
        readers = [self.reader(slot)[1] for slot in (
            'map_popup', 'scene_popup', 'team_popup', 'replay_popup')]
        for _ in range(50):
            self.bar.refresh()
        self.assertEqual([r.calls for r in readers], [0] * 4)

    def test_visible_reader_updates_and_direct_restore_reads_latest(self):
        popup, reader = self.reader('map_popup')
        reader.query.setText('保留我的搜索')
        self.bar.present(popup)
        self.assertEqual((reader.calls, reader.snapshot), (1, 1))
        self.owner.run.state['test_revision'] = 2
        self.bar.refresh()
        self.assertEqual((reader.calls, reader.snapshot), (2, 2))
        popup.hide()
        self.owner.run.state['test_revision'] = 3
        self.bar.refresh()
        self.assertEqual(reader.calls, 2)
        # Hotkey and game binding use show() rather than open_map().
        popup.show()
        self.assertEqual((reader.calls, reader.snapshot), (3, 3))
        self.assertEqual(reader.query.text(), '保留我的搜索')

    def test_reopening_visible_reader_refreshes_once_without_show_event(self):
        popup, reader = self.reader('map_popup')
        self.bar.present(popup)
        self.owner.run.state['test_revision'] = 4
        self.bar.present(popup)
        self.assertEqual((reader.calls, reader.snapshot), (2, 4))

    def test_inventory_bundle_sleeps_and_restores_together(self):
        popup, reader = self.reader('inventory_popup')
        popup.parts = SimpleNamespace(refresh=Mock(), refresh_exchange=Mock())
        popup.tools = SimpleNamespace(refresh=Mock())
        popup.shop = SimpleNamespace(refresh=Mock())
        self.bar.refresh()
        self.assertEqual(reader.calls, 0)
        self.bar.present(popup)
        self.assertEqual(reader.calls, 1)
        for method in (popup.parts.refresh, popup.parts.refresh_exchange,
                       popup.tools.refresh, popup.shop.refresh):
            self.assertEqual(method.call_count, 1)
        popup.hide()
        self.bar.refresh()
        self.assertEqual(popup.parts.refresh.call_count, 1)

    def test_exchange_rechecks_its_source_while_inventory_is_hidden(self):
        inventory, reader = self.reader('inventory_popup')
        reader.source_index = None
        reader.source_signature = None
        reader.reload_sources = Mock()
        popup, exchange = self.reader('exchange_popup')
        exchange.refresh_source = Mock()
        self.bar.present(popup)
        self.assertFalse(inventory.isVisible())
        reader.reload_sources.assert_called_once()
        exchange.refresh_source.assert_called_once_with(None, None)

    def test_generic_history_popup_does_not_refresh_its_parent(self):
        owner = QWidget()
        owner.refresh = Mock()
        popup = ToolPopover('独立历史资料', QWidget(), owner)
        self.addCleanup(owner.deleteLater)
        self.addCleanup(popup.close)
        popup.show()
        owner.refresh.assert_not_called()

    def test_unsaved_reader_can_still_veto_navigation(self):
        class Unsaved(ToolPopover):
            def closeEvent(self, event):
                event.ignore()
        veto = Unsaved('尚未保存', QWidget(), self.bar)
        veto.show()
        self.bar.active_popup = veto
        popup, reader = self.reader('map_popup')
        self.assertFalse(self.bar.present(popup))
        self.assertFalse(popup.isVisible())
        self.assertEqual(reader.calls, 0)

    def test_button_drag_keeps_native_toolbar_movement_without_parent_fallback(self):
        self.bar.show()
        self.bar.move(500, 500)
        self.qt.processEvents()
        button = self.bar.tool_buttons[0]
        clicked = Mock()
        button.clicked.connect(clicked)
        start = self.bar.pos()
        QTest.mousePress(button, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(45, 25),
                            QPointF(button.mapToGlobal(QPoint(45, 25))),
                            Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
                            Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(button, event)
        QTest.mouseRelease(button, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))
        self.assertNotEqual(self.bar.pos(), start)
        clicked.assert_not_called()


class MapDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_optional_map_search_is_collapsed_and_keeps_reading_when_reopened(self):
        from copy import deepcopy
        from tests.test_batch185_mainwindow import Batch185WindowTests
        from rouge.player_map_acceptance import fixtures
        Batch185WindowTests.setUp(self)
        graphs, *_ = fixtures()
        self.window.run.state['maps'] = {g['zone_id']:g for g in graphs}
        self.window.show_compact()
        bar = self.window.compact_window
        bar.open_map()
        panel = bar.map_popup.panel
        self.qt.processEvents()
        self.assertFalse(panel.finder.isVisible())
        self.assertTrue(panel.view.isVisible())
        panel.finder_toggle.click()
        self.assertTrue(panel.node_query.isVisible())
        panel.node_query.setText('作战')
        panel.read_scope.setCurrentIndex(panel.read_scope.findData('fixed'))
        selected = panel.node_results.currentData()
        before = deepcopy(self.window.run.state)
        panel.finder_toggle.click()
        panel.refresh()
        panel.finder_toggle.click()
        self.assertTrue(panel.coverage_notice.isVisible())
        self.assertEqual(panel.node_query.text(), '作战')
        self.assertEqual(panel.read_scope.currentData(), 'fixed')
        self.assertEqual(panel.node_results.currentData(), selected)
        self.assertEqual(self.window.run.state, before)


if __name__ == '__main__':
    unittest.main()
