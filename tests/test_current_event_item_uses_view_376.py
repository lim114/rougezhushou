from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import current_event_item_uses as model
from rouge.current_event_item_uses_view import CurrentEventItemUsesPanel, CurrentEventItemUsesDialog
from tests.test_current_event_item_uses_376 import clone
_APP = QApplication.instance() or QApplication([])


def select(widget, key):
    matches = [i for i in range(widget.count()) if widget.item(i).data(Qt.ItemDataRole.UserRole) == key]
    if len(matches) != 1: raise AssertionError('Unique exact record required')
    widget.setCurrentRow(matches[0]); _APP.processEvents()


class CurrentEventItemUsesViewTests(TestCase):
    def tearDown(self):
        for w in QApplication.topLevelWidgets(): w.close()
        _APP.processEvents()

    def test_overview_has7_items12_records_no_default(self):
        p = CurrentEventItemUsesPanel(); self.assertEqual(p.entries.count(), 12); self.assertEqual(p.item.count(), 8)
        self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_button.isEnabled()); self.assertTrue(p.origins_button.isHidden())

    def test_key_filter_four_uses_and_three_offerings(self):
        p = CurrentEventItemUsesPanel(); p.item.setCurrentIndex(p.item.findData('rogue_6_relic_cargo_13')); self.assertEqual(p.entries.count(), 4)
        p.role.setCurrentIndex(p.role.findData('offered')); self.assertEqual(p.entries.count(), 3)

    def test_exact_use_dialog_and_no_actual_possession_declaration(self):
        p = CurrentEventItemUsesPanel(); row = p.result['rows'][0]; select(p.entries, row['id']); self.assertTrue(p.open_event())
        self.assertEqual((p.event_dialog.panel.scene_id, p.event_dialog.panel.choice_id), (row['entry']['scene_id'], row['entry']['choice_id']))
        self.assertIsNone(p.event_dialog.panel.result['declared_has_controller'])

    def test_source_button_only_visible_when_existing_source_is_known(self):
        p = CurrentEventItemUsesPanel(); rows = p.result['rows']; clover = next(r for r in rows if r['item_id'] == 'rogue_6_relic_legacy_113')
        select(p.entries, clover['id']); self.assertTrue(p.origins_button.isHidden())
        controller = next(r for r in rows if r['item_id'] == 'rogue_6_scrap_G_12'); select(p.entries, controller['id'])
        self.assertFalse(p.origins_button.isHidden()); self.assertTrue(p.open_origins()); self.assertEqual(p.origins_dialog.panel.entries.count(), 2)

    def test_origins_nested_event_cleared_when_parent_closes(self):
        d = CurrentEventItemUsesDialog(); row = next(r for r in d.panel.result['rows'] if r['item_id'] == 'rogue_6_scrap_G_12'); select(d.panel.entries, row['id']); d.panel.open_origins(); origins = d.panel.origins_dialog
        first = origins.panel.result['rows'][0]; select(origins.panel.entries, first['key']); self.assertTrue(origins.panel.open_event()); child = origins.panel.event_dialog
        d.close(); self.assertIsNone(d.panel.result); self.assertIsNone(origins.panel.result); self.assertIsNone(child.panel.result)

    def test_same_source_keeps_filters_choice_and_owned_readers(self):
        p = CurrentEventItemUsesPanel(); p.query.setText('愈创之心'); row = p.result['rows'][0]; select(p.entries, row['id']); p.open_event(); child = p.event_dialog
        self.assertTrue(p.refresh_reference()); self.assertEqual(p.query.text(), '愈创之心'); self.assertEqual(p.selected_key, row['id']); self.assertIs(p.event_dialog, child)

    def test_filter_change_clears_actual_use_and_origins(self):
        p = CurrentEventItemUsesPanel(); row = p.result['rows'][0]; select(p.entries, row['id']); p.open_event(); event = p.event_dialog; p.open_origins(); source = p.origins_dialog
        p.query.setText('祭日之契'); self.assertIsNone(p.selected_key); self.assertIsNone(event.panel.result); self.assertIsNone(source.panel.result)

    def test_bad_source_and_recovery_clear_then_manual_select(self):
        p = CurrentEventItemUsesPanel(); row = p.result['rows'][0]; select(p.entries, row['id']); p.open_event(); child = p.event_dialog
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertFalse(p.refresh_reference()); self.assertIsNone(p.result); self.assertEqual(p.entries.count(), 0); self.assertIsNone(child.panel.result)
                path.write_bytes(raw); self.assertTrue(p.refresh_reference()); self.assertIsNone(p.selected_key); self.assertFalse(p.open_button.isEnabled()); self.assertTrue(p.origins_button.isHidden())

    def test_reject_and_nested_reject_clear_actual_data(self):
        d = CurrentEventItemUsesDialog(); row = d.panel.result['rows'][0]; select(d.panel.entries, row['id']); d.panel.open_event(); child = d.panel.event_dialog
        child.reject(); self.assertIsNone(child.panel.result); self.assertIsNotNone(d.panel.result)
        d.panel.open_event(); child = d.panel.event_dialog; d.reject(); self.assertIsNone(d.panel.result); self.assertIsNone(child.panel.result)

    def test_forged_role_cannot_open_or_acquire(self):
        p = CurrentEventItemUsesPanel(); row = p.result['rows'][0]; select(p.entries, row['id']); p.result['selected']['role'] = 'consumed'
        self.assertFalse(p.open_event()); self.assertIsNone(p.result)

    def test_actual_ordinary_event_page_button_opens_exported_dialog_class(self):
        from rouge.expansion_view import ExpansionUpdatePanel
        p = ExpansionUpdatePanel(categories=('scenes', 'choices', 'regions', 'endings'), full_catalog=True)
        p.show(); _APP.processEvents(); self.assertTrue(p.event_item_uses_button.isVisible()); self.assertTrue(p.event_item_uses_button.isEnabled())
        QTest.mouseClick(p.event_item_uses_button, Qt.MouseButton.LeftButton); _APP.processEvents()
        child = p.event_item_uses_dialog; self.assertIsInstance(child, CurrentEventItemUsesDialog)
        self.assertTrue(child.isVisible()); self.assertEqual(child.panel.entries.count(), 12)
        p.close_children(); self.assertIsNone(child.panel.result)

    def test_actual_item_page_entry_uses_parent_current_item_filter(self):
        from rouge.expansion_view import ExpansionUpdatePanel
        p = ExpansionUpdatePanel(categories=('relics', 'scrap'), full_catalog=True); p.show(); _APP.processEvents()
        select(p.entries, 'rogue_6_relic_cargo_13'); self.assertEqual(p.result['row']['id'], 'rogue_6_relic_cargo_13')
        QTest.mouseClick(p.event_item_uses_button, Qt.MouseButton.LeftButton); _APP.processEvents(); child = p.event_item_uses_dialog
        self.assertIsInstance(child, CurrentEventItemUsesDialog); self.assertEqual(child.panel.item.currentData(), 'rogue_6_relic_cargo_13')
        self.assertEqual(child.panel.entries.count(), 4); self.assertIsNone(child.panel.selected_key)
        p.close_children(); self.assertIsNone(child.panel.result)

    def test_actual_ordinary_parent_recheck_restores_failed_entry(self):
        from rouge.expansion_view import ExpansionUpdatePanel
        p = ExpansionUpdatePanel(categories=('scenes', 'choices', 'regions', 'endings'), full_catalog=True); p.show(); _APP.processEvents()
        QTest.mouseClick(p.event_item_uses_button, Qt.MouseButton.LeftButton); _APP.processEvents(); child = p.event_item_uses_dialog
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertTrue(p.refresh_reference()); self.assertFalse(p.event_item_uses_button.isEnabled())
                self.assertIsNone(child.panel.result); self.assertFalse(child.isVisible()); path.write_bytes(raw)
                QTest.mouseClick(p.refresh_button, Qt.MouseButton.LeftButton); _APP.processEvents()
                self.assertTrue(p.event_item_uses_button.isEnabled()); QTest.mouseClick(p.event_item_uses_button, Qt.MouseButton.LeftButton); _APP.processEvents()
                recovered = p.event_item_uses_dialog; self.assertIsInstance(recovered, CurrentEventItemUsesDialog)
                self.assertIsNone(recovered.panel.selected_key); self.assertFalse(recovered.panel.open_button.isEnabled())
        p.close_children()
