"""Prepared offscreen window cases; no tests or GUI executed by preparation."""
from copy import deepcopy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_elbert_reference as model
from rouge.current_elbert_view import CurrentElbertPanel,CurrentElbertDialog


class CurrentElbertView366Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance()or QApplication([])
        cls.packet=model.packet()
        assert cls.packet is not None,'Install the full candidate first.'

    def setUp(self):
        self.provider=patch.object(model,'packet',side_effect=lambda:deepcopy(self.packet));self.provider.start()
        self.panel=CurrentElbertPanel('ro6_b_3');self.panel.resize(680,410);self.panel.show();self.app.processEvents()

    def tearDown(self):self.panel.close();self.app.processEvents();self.provider.stop()

    def select(self,key):self.assertTrue(self.panel.entities.select_value(key));self.app.processEvents()

    def test_default_manual_and_separate_boss_fire_entity_branches(self):
        self.assertIsNone(self.panel.selected_key);self.assertIn('请选择',self.panel.player.toPlainText())
        self.assertEqual(len(self.panel.entities.groups),2);self.assertTrue(self.panel.topic.isHidden())
        self.select('0');self.assertEqual(self.panel.topic.count(),4)
        self.select('1');self.assertEqual(self.panel.topic.count(),3)
        self.assertNotIn('staff',[self.panel.topic.itemData(i)for i in range(self.panel.topic.count())])
        self.assertNotIn('闪现',self.panel.player.toPlainText())

    def test_exact_entry_selects_requested_firebrand_without_foreign_topic(self):
        other=CurrentElbertPanel('ro6_b_3_b','1')
        self.assertEqual(other.selected_key,'1');self.assertEqual(other.topic.currentData(),'overview')
        self.assertIn('本关火种使用独立配置',other.player.toPlainText());other.close()

    def test_same_source_preserves_entity_branch_topic_tab_and_both_nonzero_readings(self):
        self.panel.entities.select_branch('本关首领');self.select('0')
        self.panel.topic.setCurrentIndex(self.panel.topic.findData('overview'));self.app.processEvents()
        positions=[]
        for index,area in enumerate((self.panel.player,self.panel.technical)):
            self.panel.tabs.setCurrentIndex(index);self.app.processEvents()
            area.verticalScrollBar().setValue(min(8,area.verticalScrollBar().maximum()));positions.append(area.verticalScrollBar().value())
        self.assertTrue(all(n>0 for n in positions))
        self.assertTrue(self.panel.refresh_reference());self.app.processEvents()
        self.assertEqual(self.panel.selected_key,'0');self.assertEqual(self.panel.entities.branch.currentData(),'本关首领')
        self.assertEqual(self.panel.topic.currentData(),'overview');self.assertEqual(self.panel.tabs.currentIndex(),1)
        self.assertEqual([area.verticalScrollBar().value()for area in(self.panel.player,self.panel.technical)],positions)

    def test_related_exact_entity_button_works_both_ways_and_resets_foreign_topic(self):
        self.select('0');self.panel.topic.setCurrentIndex(self.panel.topic.findData('staff'))
        self.assertTrue(self.panel.follow_related());self.app.processEvents()
        self.assertEqual(self.panel.selected_key,'1');self.assertEqual(self.panel.topic.currentData(),'overview')
        self.assertTrue(self.panel.follow_related());self.app.processEvents();self.assertEqual(self.panel.selected_key,'0')

    def test_broken_source_clears_picture_topic_related_and_recovers_manual(self):
        self.select('0')
        with patch.object(model,'reference',return_value=None):self.assertFalse(self.panel.refresh_reference())
        self.assertIsNone(self.panel.result);self.assertIsNone(self.panel.base);self.assertIsNone(self.panel.selected_key)
        self.assertIsNone(self.panel.related_request);self.assertEqual(self.panel.topic.count(),0)
        self.assertTrue(self.panel.portrait.isHidden());self.assertTrue(self.panel.related_button.isHidden())
        self.assertEqual(self.panel.technical.toPlainText(),'');self.assertIn('旧说明',self.panel.player.toPlainText())
        self.assertTrue(self.panel.refresh_reference());self.app.processEvents()
        self.assertIsNone(self.panel.selected_key);self.assertIn('请选择',self.panel.player.toPlainText())

    def test_invalid_related_request_clears_instead_of_reusing_similar_enemy(self):
        self.select('0');self.panel.related_request={**self.panel.related_request,'stage_id':'ro6_b_3_b'}
        self.assertFalse(self.panel.follow_related());self.assertIsNone(self.panel.result)
        self.assertIn('重新核对',self.panel.status.text())

    def test_exact_missing_auxiliary_portrait_is_not_substituted(self):
        with patch.object(model.battle,'picture_bytes',return_value=None):self.select('1')
        self.assertIn('不借用',self.panel.portrait.text())

    def test_direct_dialog_close_clears_owned_document_and_related_state(self):
        dialog=CurrentElbertDialog('ro6_b_3','0');dialog.show();self.app.processEvents()
        self.assertIsNotNone(dialog.panel.result);self.assertIsNotNone(dialog.panel.related_request)
        dialog.close();self.app.processEvents()
        self.assertFalse(dialog.isVisible());self.assertIsNone(dialog.panel.base);self.assertIsNone(dialog.panel.result)
        self.assertIsNone(dialog.panel.related_request);self.assertEqual(dialog.panel.technical.toPlainText(),'')
        self.assertEqual(dialog.panel.topic.count(),0);self.assertTrue(dialog.panel.portrait.isHidden())

    def test_dialog_rejection_clears_document_without_waiting_for_parent_refresh(self):
        dialog=CurrentElbertDialog('ro6_b_3','1');dialog.show();self.app.processEvents()
        self.assertIsNotNone(dialog.panel.result)
        dialog.reject();self.app.processEvents()
        self.assertFalse(dialog.isVisible());self.assertIsNone(dialog.panel.base);self.assertIsNone(dialog.panel.result)
        self.assertIsNone(dialog.panel.related_request);self.assertEqual(dialog.panel.technical.toPlainText(),'')
        self.assertEqual(dialog.panel.topic.count(),0);self.assertTrue(dialog.panel.portrait.isHidden())


if __name__=='__main__':unittest.main()
