"""Reference menu callbacks retain their own panel and fresh selection."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QApplication, QMenu, QListWidget, QListWidgetItem
from rouge import player_reference_notes as subject


class NotesSignal(QObject):
    openReference = Signal(dict)


class ReferenceNoteMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.notes = NotesSignal()
        self.panels = []
        for category in ('stages', 'scenes'):
            menu = QMenu()
            self.addCleanup(menu.deleteLater)
            self.panels.append(SimpleNamespace(
                allowed_categories=(category,), query_menu=SimpleNamespace(menu=menu),
                result={'row': {'category': category, 'id': category + '-first'}}))
        self.window = SimpleNamespace(player_notes=self.notes, diagnostic_layout=False,
                                      common_reference_panels=dict(enumerate(self.panels)))

    def test_each_menu_follows_its_own_latest_selection(self):
        with patch.object(subject, 'note_for', side_effect=lambda category, identity: {'category': category, 'id': identity}), \
                patch.object(subject, 'open_note') as opened:
            subject.install(self.window)
            for panel in self.panels:
                panel.query_menu.menu.aboutToShow.emit()
                self.assertTrue(panel.reference_note_action.isVisible())
            for panel in reversed(self.panels):
                row = panel.result['row']
                row['id'] += '-changed'
                panel.reference_note_action.trigger()
                opened.assert_called_with(self.window, row)
            self.assertEqual(opened.call_count, 2)

    def test_source_loss_between_menu_and_click_does_not_open_stale_note(self):
        with patch.object(subject, 'note_for', return_value={'id': 'source'}) as source, \
                patch.object(subject, 'open_note') as opened:
            subject.install(self.window)
            panel = self.panels[0]
            panel.query_menu.menu.aboutToShow.emit()
            self.assertTrue(panel.reference_note_action.isVisible())
            source.return_value = None
            panel.reference_note_action.trigger()
            opened.assert_not_called()
            panel.query_menu.menu.aboutToShow.emit()
            self.assertFalse(panel.reference_note_action.isVisible())

    def test_standalone_return_selects_exact_id_among_same_name_entries(self):
        entries = QListWidget()
        self.addCleanup(entries.deleteLater)
        for identity in ('different-stage', 'wanted-stage'):
            item = QListWidgetItem('相同关卡名')
            item.setData(Qt.ItemDataRole.UserRole, identity)
            entries.addItem(item)
        panel = SimpleNamespace(entries=entries, search=Mock(), stage_floor=Mock(),
                                stage_kind=Mock(), scope=Mock(), refresh_reference=Mock(),
                                result={'row': {'id': 'wanted-stage'}})
        window = SimpleNamespace(reference_panel=Mock(return_value=panel), show=Mock(),
                                 raise_=Mock(), activateWindow=Mock())
        content = {'kind': 'reference-stage', 'event_id': 'wanted-stage'}
        with patch.object(subject, 'reference_target', return_value=('stages', 'wanted-stage')), \
                patch('rouge.player_note_reference.open_shared', return_value=None), \
                patch.object(subject, 'note_for', return_value=content):
            self.assertTrue(subject.open_reference(window, content))
        self.assertEqual(entries.currentRow(), 1)
        panel.refresh_reference.assert_called_once_with()
        window.activateWindow.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
