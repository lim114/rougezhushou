from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from rouge import current_event_directory as model
from rouge.current_event_directory_view import CurrentEventDirectoryPanel, CurrentEventDirectoryDialog, make_event_dialog
from tests.test_current_event_directory_372 import clone

_APP = QApplication.instance() or QApplication([])


def select(widget, key):
    rows = [i for i in range(widget.count()) if widget.item(i).data(Qt.ItemDataRole.UserRole) == key]
    if len(rows) != 1: raise AssertionError('Unique exact selection required')
    widget.setCurrentRow(rows[0]); _APP.processEvents()


class CurrentEventDirectoryViewTests(TestCase):
    def tearDown(self):
        for w in QApplication.topLevelWidgets(): w.close()
        _APP.processEvents()

    def test_initial_overview_no_automatic_selection(self):
        p = CurrentEventDirectoryPanel(); self.assertEqual(p.events.count(), 39)
        self.assertIsNone(p.events.currentItem()); self.assertFalse(p.open_button.isEnabled())
        self.assertEqual(p.entries.count(), 0); self.assertIsNone(p.event_dialog)

    def test_search_choice_and_filter_explicit_unclassified(self):
        p = CurrentEventDirectoryPanel(); p.query.setText('生命蓝图')
        self.assertEqual(p.events.count(), 1); self.assertIn('制图桌', p.events.item(0).text())
        p.query.clear(); p.node_type.setCurrentIndex(p.node_type.findData('unclassified'))
        self.assertEqual(p.events.count(), 4); self.assertIsNone(p.event_id)

    def test_exact_selected_dialogue_not_name_based(self):
        p = CurrentEventDirectoryPanel(); select(p.events, 'memory336:memorytree')
        row = p.result['selected']; entry = next(e for e in row['entries'] if e['choice_id'] == 'choice_ro6_normal5_3')
        select(p.entries, entry['key']); self.assertTrue(p.open_event())
        self.assertEqual((p.event_dialog.panel.scene_id, p.event_dialog.panel.choice_id), (entry['scene_id'], entry['choice_id']))
        self.assertIsNone(p.event_dialog.panel.result['declared']['source_key'])

    def test_all21_reader_classes_support_exact_document_target(self):
        seen = set()
        for row in model.reference()['rows']:
            if row['reader'] in seen: continue
            seen.add(row['reader']); result = model.reference(row['id']); entry = row['entries'][-1]
            target = model.resolve(result, entry['key']); dialog = make_event_dialog(target)
            self.assertIsNotNone(dialog, row['reader'])
            self.assertEqual((dialog.panel.scene_id, dialog.panel.choice_id), (entry['scene_id'], entry['choice_id']))
            dialog.close()
        self.assertEqual(len(seen), 21)

    def test_same_source_preserves_filters_event_entry_and_child(self):
        p = CurrentEventDirectoryPanel(); p.query.setText('愈创之心'); select(p.events, 'memory336:memorytree')
        entry = p.result['selected']['entries'][0]; select(p.entries, entry['key']); self.assertTrue(p.open_event()); child = p.event_dialog
        self.assertTrue(p.refresh_reference()); self.assertEqual(p.query.text(), '愈创之心')
        self.assertEqual(p.event_id, 'memory336:memorytree'); self.assertEqual(p.entry_key, entry['key'])
        self.assertIs(p.event_dialog, child)

    def test_event_and_filter_change_close_and_clear_old_child(self):
        p = CurrentEventDirectoryPanel(); select(p.events, 'flows321:button'); self.assertTrue(p.open_event()); old = p.event_dialog
        p.query.setText('制图桌'); self.assertFalse(old.isVisible()); self.assertIsNone(old.panel.result)
        self.assertIsNone(p.event_id); self.assertIsNone(p.entry_key); self.assertEqual(p.entries.count(), 0)

    def test_bad_source_parent_clears_real_child_and_recovery_unselected(self):
        p = CurrentEventDirectoryPanel(); select(p.events, 'flows321:button'); p.open_event(); old = p.event_dialog
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertFalse(p.refresh_reference())
                self.assertIsNone(p.result); self.assertEqual(p.events.count(), 0); self.assertEqual(p.technical.toPlainText(), '')
                self.assertEqual(p.player.toPlainText(), model.UNAVAILABLE); self.assertIsNone(old.panel.result)
                path.write_bytes(raw); self.assertTrue(p.refresh_reference())
                self.assertIsNone(p.event_id); self.assertIsNone(p.events.currentItem()); self.assertFalse(p.open_button.isEnabled())

    def test_local_forgery_clears_and_refuses_child(self):
        p = CurrentEventDirectoryPanel(); select(p.events, 'flows321:button')
        p.result['selected']['event_id'] = 'revive'
        self.assertFalse(p.open_event()); self.assertIsNone(p.result)

    def test_dialog_close_clears_actual_readings_and_nested_child(self):
        d = CurrentEventDirectoryDialog(); select(d.panel.events, 'flows321:button'); d.panel.open_event(); child = d.panel.event_dialog
        d.close(); self.assertIsNone(d.panel.result); self.assertIsNone(child.panel.result); self.assertFalse(child.isVisible())

    def test_directory_reject_clears_actual_owned_data(self):
        d = CurrentEventDirectoryDialog(); select(d.panel.events, 'flows321:button'); d.panel.open_event(); child = d.panel.event_dialog
        d.reject(); self.assertIsNone(d.panel.result); self.assertIsNone(child.panel.result); self.assertFalse(child.isVisible())

    def test_owned_reader_reject_clears_actual_data(self):
        p = CurrentEventDirectoryPanel(); select(p.events, 'flows321:button'); p.open_event(); child = p.event_dialog
        child.reject(); self.assertIsNone(child.panel.result)
