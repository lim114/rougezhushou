from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from rouge import current_event_resources as model
from rouge.current_event_resources_view import CurrentEventResourcesPanel, CurrentEventResourcesDialog
from tests.test_current_event_resources_374 import clone, find
_APP = QApplication.instance() or QApplication([])


def select(widget, key):
    matches = [i for i in range(widget.count()) if widget.item(i).data(Qt.ItemDataRole.UserRole) == key]
    if len(matches) != 1: raise AssertionError('Unique exact record required')
    widget.setCurrentRow(matches[0]); _APP.processEvents()


class CurrentEventResourcesViewTests(TestCase):
    def test_ordinary_events_entry_constructs_actual_resources_reader(self):
        from rouge.expansion_view import ExpansionUpdatePanel
        p = ExpansionUpdatePanel(categories=('scenes',), full_catalog=True)
        self.assertTrue(p.open_event_resources())
        self.assertIsInstance(p.event_resources_dialog, CurrentEventResourcesDialog)
        self.assertIsNotNone(p.event_resources_dialog.panel.result)

    def tearDown(self):
        for w in QApplication.topLevelWidgets(): w.close()
        _APP.processEvents()

    def test_overview_no_default_or_claim(self):
        p = CurrentEventResourcesPanel(); self.assertEqual(p.entries.count(), 88)
        self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_button.isEnabled()); self.assertIsNone(p.event_dialog)

    def test_resource_and_gain_filters_keep_cost_context(self):
        p = CurrentEventResourcesPanel(); p.resource.setCurrentIndex(p.resource.findData('processed')); p.kind.setCurrentIndex(p.kind.findData('item'))
        row = find(p.result, '货从口出'); select(p.entries, row['id'])
        self.assertIn('源石锭：4', p.player.toPlainText()); self.assertIn('加工品：1件', p.player.toPlainText())

    def test_exact_original_entry_and_manual_unknowns(self):
        p = CurrentEventResourcesPanel(); row = find(p.result, '沉重的契约', '推翻石磨'); select(p.entries, row['id'])
        self.assertTrue(p.open_event()); child = p.event_dialog
        self.assertEqual((child.panel.scene_id, child.panel.choice_id), (row['entry']['scene_id'], row['entry']['choice_id']))
        self.assertIsNone(child.panel.result['actual_eligible'])

    def test_same_source_keeps_filters_selection_and_child(self):
        p = CurrentEventResourcesPanel(); p.query.setText('推翻石磨'); row = p.result['rows'][0]; select(p.entries, row['id']); p.open_event(); child = p.event_dialog
        self.assertTrue(p.refresh_reference()); self.assertEqual(p.query.text(), '推翻石磨'); self.assertEqual(p.selected_key, row['id']); self.assertIs(p.event_dialog, child)

    def test_filter_change_clears_selected_data_and_child(self):
        p = CurrentEventResourcesPanel(); row = find(p.result, '沉重的契约'); select(p.entries, row['id']); p.open_event(); child = p.event_dialog
        p.resource.setCurrentIndex(p.resource.findData('shield')); self.assertIsNone(p.selected_key); self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)

    def test_damaged_source_clear_and_recovery_unselected(self):
        p = CurrentEventResourcesPanel(); row = p.result['rows'][0]; select(p.entries, row['id']); p.open_event(); child = p.event_dialog
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertFalse(p.refresh_reference()); self.assertIsNone(p.result)
                self.assertEqual(p.entries.count(), 0); self.assertEqual(p.technical.toPlainText(), ''); self.assertIsNone(child.panel.result)
                path.write_bytes(raw); self.assertTrue(p.refresh_reference()); self.assertIsNone(p.selected_key); self.assertFalse(p.open_button.isEnabled())

    def test_local_mutation_refuses_jump(self):
        p = CurrentEventResourcesPanel(); row = p.result['rows'][0]; select(p.entries, row['id'])
        p.result['selected']['effects'][0]['quantity'] = 999; self.assertFalse(p.open_event()); self.assertIsNone(p.result)

    def test_close_clears_actual_parent_child_data(self):
        d = CurrentEventResourcesDialog(); row = d.panel.result['rows'][0]; select(d.panel.entries, row['id']); d.panel.open_event(); child = d.panel.event_dialog
        d.close(); self.assertIsNone(d.panel.result); self.assertIsNone(child.panel.result); self.assertFalse(child.isVisible())

    def test_reject_clears_actual_parent_and_child_readings(self):
        d = CurrentEventResourcesDialog(); row = d.panel.result['rows'][0]; select(d.panel.entries, row['id']); d.panel.open_event(); child = d.panel.event_dialog
        d.reject(); self.assertIsNone(d.panel.result); self.assertIsNone(child.panel.result); self.assertFalse(child.isVisible())

    def test_nested_reader_reject_clears_its_actual_data(self):
        d = CurrentEventResourcesDialog(); row = d.panel.result['rows'][0]; select(d.panel.entries, row['id']); d.panel.open_event(); child = d.panel.event_dialog
        child.reject(); self.assertIsNone(child.panel.result); self.assertIsNotNone(d.panel.result)
