import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_hanko as model
from rouge.current_hanko_view import CurrentHankoPanel


class CurrentHankoView365Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.base = model.reference('ro6_b_1')
        assert cls.base is not None, 'Install the candidate before execution.'
        cls.boss = next(r['key'] for r in cls.base['rows'] if r['actor'] == 'hanko')
        cls.smoke = next(r['key'] for r in cls.base['rows'] if r['actor'] == 'smoke')

    def setUp(self):
        self.provider = patch.object(model, 'reference', side_effect=self._fresh); self.provider.start()
        self.panel = CurrentHankoPanel('ro6_b_1'); self.panel.resize(680, 410); self.panel.show(); self.app.processEvents()

    def _fresh(self, sid, key=None):
        if sid != 'ro6_b_1' or key not in (None, self.boss, self.smoke): return None
        row = copy.deepcopy(self.base); row['selected_key'] = key; return row

    def tearDown(self): self.panel.close(); self.app.processEvents(); self.provider.stop()

    def select(self, key): self.assertTrue(self.panel.entities.select_value(key)); self.app.processEvents()

    def test_default_manual_selection_and_real_entity_branches(self):
        self.assertIsNone(self.panel.selected_key)
        self.assertIn('请先选择', self.panel.player.toPlainText())
        self.assertEqual(len(self.panel.entities.groups), 2)
        self.select(self.boss); self.assertEqual(self.panel.topic.count(), 4)
        self.select(self.smoke); self.assertEqual(self.panel.topic.count(), 2)
        self.assertEqual(self.panel.topic.itemData(1), 'smoke')
        self.assertNotIn('闪现', [self.panel.topic.itemText(i) for i in range(self.panel.topic.count())])

    def test_exact_ordinary_enemy_entry_opens_requested_reference(self):
        other = CurrentHankoPanel('ro6_b_1', self.smoke)
        self.assertEqual(other.selected_key, self.smoke)
        self.assertEqual(other.topic.count(), 2); other.close()

    def test_same_refresh_preserves_entity_topic_tab_and_both_nonzero_reading_positions(self):
        self.select(self.boss); self.panel.topic.setCurrentIndex(self.panel.topic.findData('flare')); self.app.processEvents()
        positions = []
        for index, area in enumerate((self.panel.player, self.panel.technical)):
            self.panel.tabs.setCurrentIndex(index); self.app.processEvents()
            area.verticalScrollBar().setValue(min(8, area.verticalScrollBar().maximum()))
            positions.append(area.verticalScrollBar().value())
        self.assertTrue(all(p > 0 for p in positions))
        self.panel.refresh_reference(); self.app.processEvents()
        self.assertEqual(self.panel.selected_key, self.boss); self.assertEqual(self.panel.topic.currentData(), 'flare')
        self.assertEqual(self.panel.tabs.currentIndex(), 1)
        self.assertEqual([a.verticalScrollBar().value() for a in (self.panel.player, self.panel.technical)], positions)

    def test_related_button_selects_exact_smoke_and_resets_foreign_topic(self):
        self.select(self.boss); self.panel.topic.setCurrentIndex(self.panel.topic.findData('blink'))
        self.panel.related.setCurrentIndex(1)
        self.assertTrue(self.panel.follow_related()); self.app.processEvents()
        self.assertEqual(self.panel.selected_key, self.smoke); self.assertIsNone(self.panel.topic.currentData())
        self.assertEqual(self.panel.topic.count(), 2)

    def test_bad_source_clears_picture_topics_and_selection_then_recovers_manually(self):
        self.select(self.boss)
        with patch.object(model, 'reference', return_value=None): self.panel.refresh_reference()
        self.assertIsNone(self.panel.result); self.assertIsNone(self.panel.selected_key)
        self.assertEqual(self.panel.topic.count(), 0); self.assertEqual(self.panel.related.count(), 0)
        self.assertIn('旧实体', self.panel.player.toPlainText()); self.assertTrue(self.panel.portrait.isHidden())
        self.panel.refresh_reference(); self.app.processEvents()
        self.assertIsNone(self.panel.selected_key); self.assertIn('请先选择', self.panel.player.toPlainText())

    def test_bad_related_request_clears_stale_view_without_borrowing_name(self):
        self.select(self.boss)
        self.panel.related.addItem('烟雾弹', {'enemy_key': self.smoke, 'name': '烟雾弹', 'entity_id': 'foreign', 'level': 0})
        self.panel.related.setCurrentIndex(self.panel.related.count() - 1)
        self.assertFalse(self.panel.follow_related()); self.assertIsNone(self.panel.result)
        self.assertIn('无法重新核对', self.panel.status.text())


if __name__ == '__main__': unittest.main()
