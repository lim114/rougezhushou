import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_sun_boss as model
from rouge.current_sun_boss_view import CurrentSunBossPanel, CurrentSunBossDialog


class CurrentSunBossView368Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.base = model.reference('ro6_b_7'); assert cls.base is not None, 'Install the candidate before execution.'
        cls.keys = {r['form']: r['key'] for r in cls.base['rows']}

    def setUp(self):
        self.provider = patch.object(model, 'reference', side_effect=self._fresh); self.provider.start()
        self.panel = CurrentSunBossPanel('ro6_b_7'); self.panel.resize(720, 440); self.panel.show(); self.app.processEvents()

    def _fresh(self, sid, key=None):
        if sid != 'ro6_b_7' or key not in (None, *self.keys.values()): return None
        row = copy.deepcopy(self.base); row['selected_key'] = key; return row

    def tearDown(self): self.panel.close(); self.app.processEvents(); self.provider.stop()

    def select(self, form): self.assertTrue(self.panel.forms.select_value(self.keys[form])); self.app.processEvents()
    def topic(self, key): self.panel.topic.setCurrentIndex(self.panel.topic.findData(key)); self.app.processEvents()

    def test_default_and_exact_enemy_entry_keep_form_selection_distinct_from_actual_state(self):
        self.assertIsNone(self.panel.selected_key); self.assertIn('不是三名', self.panel.player.toPlainText())
        self.assertEqual(len(self.panel.forms.groups), 2)
        other = CurrentSunBossPanel('ro6_b_7', self.keys['sun'])
        self.assertEqual(other.selected_key, self.keys['sun']); self.assertIsNone(other.result['actual_form']); other.close()

    def test_only_current_form_cards_and_relevant_controls(self):
        self.select('normal'); self.assertEqual(self.panel.card.count(), 4); self.assertTrue(self.panel.card.isHidden())
        self.topic('skills'); self.assertFalse(self.panel.card.isHidden()); self.assertTrue(self.panel.map_button.isHidden())
        self.select('sun'); self.assertEqual(self.panel.card.count(), 7); self.topic('skills')
        self.assertNotIn('熄日的祭坛', [self.panel.card.itemText(i) for i in range(self.panel.card.count())])
        self.select('eclipse'); self.topic('skills')
        self.assertIn('熄日的祭坛', [self.panel.card.itemText(i) for i in range(self.panel.card.count())])
        self.topic('terrain'); self.assertFalse(self.panel.map_button.isHidden())

    def test_same_refresh_preserves_form_topic_card_tab_and_two_nonzero_reading_positions(self):
        self.select('sun'); self.topic('skills'); self.panel.card.setCurrentIndex(self.panel.card.findData(5)); self.app.processEvents()
        positions = []
        for index, area in enumerate((self.panel.player, self.panel.technical)):
            self.panel.tabs.setCurrentIndex(index); self.app.processEvents()
            area.verticalScrollBar().setValue(min(9, area.verticalScrollBar().maximum())); positions.append(area.verticalScrollBar().value())
        self.assertTrue(all(value > 0 for value in positions))
        self.panel.refresh_reference(); self.app.processEvents()
        self.assertEqual(self.panel.selected_key, self.keys['sun']); self.assertEqual(self.panel.topic.currentData(), 'skills')
        self.assertEqual(self.panel.card.currentData(), 5); self.assertEqual(self.panel.tabs.currentIndex(), 1)
        self.assertEqual([area.verticalScrollBar().value() for area in (self.panel.player, self.panel.technical)], positions)

    def test_related_form_keeps_exact_reference_and_resets_foreign_card(self):
        self.select('normal'); self.panel.related.setCurrentIndex(1)
        request = self.panel.related.currentData(); self.assertTrue(self.panel.follow_form()); self.app.processEvents()
        self.assertEqual(self.panel.selected_key, request['key']); self.assertIsNone(self.panel.card.currentData())
        self.assertEqual(self.panel.topic.currentData(), 'overview')

    def test_fixed_map_owned_window_and_bad_source_manual_recovery(self):
        self.select('normal'); self.topic('terrain'); self.assertTrue(self.panel.open_map()); self.app.processEvents()
        child = self.panel.map_dialog; self.assertTrue(child.isVisible()); self.assertEqual(child.panel.stage_id, 'ro6_b_7')
        self.assertIsNone(child.panel.selected)
        with patch.object(model, 'reference', return_value=None): self.panel.refresh_reference()
        self.app.processEvents(); self.assertFalse(child.isVisible()); self.assertIsNone(self.panel.map_dialog)
        self.assertIsNone(self.panel.result); self.assertEqual(self.panel.card.count(), 0)
        self.panel.refresh_reference(); self.app.processEvents(); self.assertIsNone(self.panel.selected_key)

    def test_map_source_failure_closes_only_old_map_and_never_borrows_same_name(self):
        self.select('normal'); self.topic('terrain'); self.assertTrue(self.panel.open_map())
        child = self.panel.map_dialog
        with patch.object(model, 'map_reference', return_value=None): self.panel.refresh_reference()
        self.app.processEvents(); self.assertFalse(child.isVisible()); self.assertIsNotNone(self.panel.result)
        self.assertIn('旧地图窗口已关闭', self.panel.status.text())

    def test_parent_close_closes_owned_map(self):
        self.select('normal'); self.topic('altar'); self.assertTrue(self.panel.open_map())
        child = self.panel.map_dialog; self.panel.close(); self.app.processEvents(); self.assertFalse(child.isVisible())

    def test_foreign_related_request_clears_stale_state(self):
        self.select('normal')
        self.panel.related.addItem('same name', {'key': self.keys['sun'], 'entity_id': 'foreign', 'name': 'same name', 'level': 0})
        self.panel.related.setCurrentIndex(self.panel.related.count() - 1)
        self.assertFalse(self.panel.follow_form()); self.assertIsNone(self.panel.result)

    def test_direct_dialog_close_clears_mechanism_and_owned_map_contents(self):
        dialog = CurrentSunBossDialog('ro6_b_7', self.keys['normal']); dialog.show(); self.app.processEvents()
        dialog.panel.topic.setCurrentIndex(dialog.panel.topic.findData('terrain'))
        self.assertTrue(dialog.panel.open_map()); child = dialog.panel.map_dialog
        dialog.close(); self.app.processEvents()
        self.assertFalse(dialog.isVisible()); self.assertIsNone(dialog.panel.result); self.assertIsNone(dialog.panel.selected_key)
        self.assertIsNone(dialog.panel.map_dialog); self.assertEqual(dialog.panel.technical.toPlainText(), '')
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
        self.assertTrue(child.panel.original.pixmap.isNull()); self.assertTrue(dialog.panel.portrait.isHidden())

    def test_dialog_rejection_clears_mechanism_and_owned_map_without_parent_refresh(self):
        dialog = CurrentSunBossDialog('ro6_b_7', self.keys['sun']); dialog.show(); self.app.processEvents()
        dialog.panel.topic.setCurrentIndex(dialog.panel.topic.findData('terrain'))
        self.assertTrue(dialog.panel.open_map()); child = dialog.panel.map_dialog
        dialog.reject(); self.app.processEvents()
        self.assertFalse(dialog.isVisible()); self.assertIsNone(dialog.panel.result); self.assertIsNone(dialog.panel.selected_key)
        self.assertIsNone(dialog.panel.map_dialog); self.assertEqual(dialog.panel.technical.toPlainText(), '')
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
        self.assertTrue(child.panel.original.pixmap.isNull())

    def test_foreign_map_result_after_refresh_is_cleared_without_losing_independent_mechanism(self):
        self.select('normal'); self.topic('terrain'); self.assertTrue(self.panel.open_map())
        child = self.panel.map_dialog; child.panel.result = copy.deepcopy(child.panel.result)
        child.panel.result['source_identity'] = ('foreign-map-source',)
        with patch.object(child.panel, 'refresh_reference', return_value=True):
            self.assertTrue(self.panel.refresh_reference())
        self.assertIsNotNone(self.panel.result); self.assertIsNone(self.panel.map_dialog)
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)
        self.assertIn('与本关不一致', self.panel.status.text())

    def test_changed_valid_source_requires_manual_form_and_clears_owned_map(self):
        self.select('normal'); self.topic('terrain'); self.assertTrue(self.panel.open_map()); child = self.panel.map_dialog
        def changed(sid, key=None):
            fresh = self._fresh(sid, key)
            if fresh is not None: fresh['source_identity'] = ('different-reviewed-source',)
            return fresh
        with patch.object(model, 'reference', side_effect=changed):
            self.assertTrue(self.panel.refresh_reference())
        self.assertIsNone(self.panel.selected_key); self.assertIsNone(self.panel.form_combo.currentData())
        self.assertIsNone(self.panel.map_dialog); self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)

    def test_direct_owned_map_close_or_rejection_clears_map_but_keeps_mechanism(self):
        self.select('normal'); self.topic('terrain')
        for method in ('close', 'reject'):
            self.assertTrue(self.panel.open_map()); child = self.panel.map_dialog
            getattr(child, method)(); self.app.processEvents()
            self.assertIsNone(self.panel.map_dialog); self.assertFalse(child.isVisible())
            self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
            self.assertTrue(child.panel.original.pixmap.isNull()); self.assertIsNotNone(self.panel.result)
            self.assertEqual(self.panel.selected_key, self.keys['normal'])


if __name__ == '__main__': unittest.main()
