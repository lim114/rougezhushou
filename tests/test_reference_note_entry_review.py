from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QMenu
from rouge import player_reference_notes as notes


class ReferenceNoteEntryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def window(self):
        menu = QMenu()
        self.addCleanup(menu.close)
        panel = SimpleNamespace(allowed_categories=['stages'], query_menu=SimpleNamespace(menu=menu), result={'row': {'category': 'stages', 'id': 'stage'}})
        window = SimpleNamespace(player_notes=SimpleNamespace(openReference=Mock(), status=Mock()), diagnostic_layout=False, common_reference_panels={'stages': panel}, show_compact=Mock(), compact_window=SimpleNamespace(open_saved_note=Mock(return_value=True)))
        notes.install(window)
        return window, panel

    def test_menu_and_click_revalidate_separately_but_click_reads_once(self):
        window, panel = self.window()
        content = {'kind': 'reference-stage', 'title': '公开资料', 'event_id': 'stage', 'variant_id': 'source'}
        with patch.object(notes, 'note_for', return_value=content) as read:
            panel.query_menu.menu.aboutToShow.emit()
            self.assertEqual(read.call_count, 1)
            panel.reference_note_action.trigger()
            self.assertEqual(read.call_count, 2)
        window.compact_window.open_saved_note.assert_called_once_with(content)

    def test_source_loss_between_menu_and_click_refuses_open(self):
        window, panel = self.window()
        with patch.object(notes, 'note_for', side_effect=[{'title': '可用'}, None]):
            panel.query_menu.menu.aboutToShow.emit()
            panel.reference_note_action.trigger()
        window.show_compact.assert_not_called()
        window.compact_window.open_saved_note.assert_not_called()

    def test_independent_open_entry_still_validates(self):
        window, _ = self.window()
        with patch.object(notes, 'reference_target', return_value=None) as check:
            self.assertFalse(notes.open_note(window, {}))
        check.assert_called_once_with({})
        window.show_compact.assert_not_called()

    def test_missing_required_source_name_is_exposed(self):
        with patch.object(notes.model, 'detail', return_value={'row': {}}):
            with self.assertRaises(KeyError):
                notes.note_for('stages', 'stage')
