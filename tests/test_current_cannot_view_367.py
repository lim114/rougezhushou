"""Prepared temporary widgets; no tests were run in delegated preparation."""
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import current_cannot_reference as model
from rouge.current_cannot_view import CurrentCannotPanel,CurrentCannotDialog


class CurrentCannotView367Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def setUp(self):
        self.panel=CurrentCannotPanel();self.panel.resize(1030,800);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.app.processEvents()

    def test_shop_floor_filters_and_exact_per_stage_entry_branches(self):
        p=self.panel
        self.assertTrue(p.floor_row.isVisible());self.assertFalse(p.entries_row.isVisible())
        p.floor.setCurrentIndex(3);self.assertEqual([s['id']for s in p.result['stages']],['ro6_t_6'])
        self.assertTrue(p.open_link({'kind':'stage','stage_id':'ro6_t_6','key':None}))
        self.assertFalse(p.floor_row.isVisible());self.assertTrue(p.entries_row.isVisible());self.assertEqual(p.entries.count(),9)
        p.entries.setCurrentIndex(2);self.assertEqual(p.result['target'],model.target_for_reward('ro6_t_6','$.predefines.tokenInsts[0]'))
        self.assertEqual(p.result['selected']['pickup_free_slots_reference'],2)
        self.assertIn('不是实际已领取',p.player.toPlainText())
        self.assertTrue(p.open_link({'kind':'shop','stage_id':None,'key':None}))
        p.floor.setCurrentIndex(4);self.assertEqual([s['id']for s in p.result['stages']],['ro6_t_7'])

    def test_refresh_preserves_topic_exact_selection_related_and_both_readers(self):
        p=self.panel;p.navigate(model.target_for_reward('ro6_t_6','$.predefines.tokenInsts[0]'))
        p.topic.setCurrentIndex(p.topic.findData('free'));p.related.setCurrentRow(2)
        target=p.result['target'];related=p.related.currentItem().data(Qt.ItemDataRole.UserRole)
        p.tabs.setCurrentIndex(1);self.app.processEvents();p.technical.verticalScrollBar().setValue(25)
        pos=p.technical.verticalScrollBar().value();self.assertGreater(pos,0)
        self.assertTrue(p.refresh_reference());self.assertEqual(p.result['target'],target)
        self.assertEqual(p.topic.currentData(),'free');self.assertEqual(p.tabs.currentIndex(),1)
        self.assertEqual(p.technical.verticalScrollBar().value(),pos)
        self.assertEqual(p.related.currentItem().data(Qt.ItemDataRole.UserRole),related)
        p.topic.setCurrentIndex(0);p.tabs.setCurrentIndex(0);self.app.processEvents();p.player.verticalScrollBar().setValue(7)
        pos=p.player.verticalScrollBar().value();self.assertGreater(pos,0)
        p.refresh_reference();self.assertEqual(p.player.verticalScrollBar().value(),pos)

    def test_actual_exact_enemy_and_reward_previews_and_repeated_open_cleanup(self):
        p=self.panel;p.navigate({'kind':'stage','stage_id':'ro6_t_6','key':None})
        enemy={'kind':'battle','stage_id':'ro6_t_6','enemy_key':'0','reward_id':None}
        self.assertTrue(p.open_link(enemy));first=p.battle_dialog
        self.assertEqual(first.panel.stage_id,'ro6_t_6');self.assertEqual(first.panel.enemy_combo.currentData(),'0')
        self.assertEqual(first.panel.tabs.currentIndex(),1)
        target={'kind':'battle','stage_id':'ro6_t_6','enemy_key':None,'reward_id':'$.predefines.tokenInsts[0]'}
        self.assertTrue(p.open_link(target));self.assertFalse(first.isVisible())
        self.assertEqual(p.battle_dialog.panel.rewards.combo.currentData(),target['reward_id'])
        self.assertIs(p.battle_dialog.panel.tabs.currentWidget(),p.battle_dialog.panel.rewards)
        self.assertFalse(p.open_link({**target,'stage_id':'ro6_t_7'}))
        child=p.battle_dialog;p.close();self.assertFalse(child.isVisible());self.assertIsNone(p.battle_dialog)

    def test_source_failure_clears_old_content_child_and_requires_new_stage_selection(self):
        p=self.panel;p.navigate(model.target_for_enemy('ro6_t_6','0'));p.topic.setCurrentIndex(2)
        with patch.object(model,'packet',return_value=None):
            self.assertFalse(p.refresh_reference());self.assertIsNone(p.result)
            self.assertEqual(p.entries.count(),0);self.assertEqual(p.related.count(),0)
            self.assertFalse(p.floor_row.isVisible());self.assertFalse(p.entries_row.isVisible())
            self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.open_button.isEnabled())
        self.assertTrue(p.refresh_reference());self.assertEqual(p.result['target']['kind'],'shop')
        self.assertIsNone(p.result['stage_id']);self.assertIsNone(p.floor.currentData())
        d=CurrentCannotDialog(model.target_for_reward('ro6_t_7','$.predefines.tokenInsts[9]'))
        self.assertEqual(d.panel.result['selected']['grade'],1);d.close()
        self.assertIsNone(d.panel.result);self.assertEqual(d.panel.related.count(),0)


if __name__=='__main__':unittest.main()
