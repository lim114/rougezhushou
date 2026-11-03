from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge import box_event_reference as model
from rouge.box_event_view import BoxEventPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_box_event_reference_322 import SCENES,clone


class BoxEventView322Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,sid=None,cid=None):
        p=BoxEventPanel(sid,cid);p.resize(950,540);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,cid):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:p.choices.setCurrentRow(i);return
        self.fail('Missing actual choice '+cid)

    def test_all_scenes_and_options_no_unproven_parent_or_destination(self):
        p=self.panel()
        for sid,choices in SCENES.items():
            p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual([p.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(p.choices.count())],choices)
        p.go_start();self.select(p,'print');self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.next_button.isVisible());self.assertIn('不借用相邻',p.player.toPlainText());self.assertFalse(p.open_battle())

    def test_all_three_condition_states_keep_selected_choice_but_block_unmet_branch(self):
        p=self.panel();self.select(p,'covenant')
        for value in(None,False,True,None):
            p.covenant.setCurrentIndex(p.covenant.findData(value));self.assertEqual(p.choice_id,'covenant');self.assertIsNone(p.result['actual_eligible']);self.assertEqual(p.next_button.isEnabled(),value is not False);self.assertEqual(p.battle_button.isEnabled(),value is not False)
            if value is False:self.assertFalse(p.follow_scene());self.assertFalse(p.open_battle())

    def test_normal_and_conditional_maps_exact_source_links_and_condition_closes_open_child(self):
        p=self.panel('scene_ro6_end2_2','normal_battle');self.assertTrue(p.open_battle());old=p.battle_dialog;self.assertEqual(old.panel.stage_id,'ro6_b_5');self.assertTrue(old.isVisible())
        p.go_start();self.assertFalse(old.isVisible());self.select(p,'covenant');self.assertTrue(p.open_battle());old=p.battle_dialog;self.assertEqual(old.panel.stage_id,'ro6_b_5_b');self.assertIn('失恒常量',p.battle_button.text())
        p.covenant.setCurrentIndex(p.covenant.findData(False));self.assertFalse(old.isVisible());self.assertFalse(p.battle_button.isEnabled());self.assertFalse(p.follow_scene())

    def test_explicit_next_story_does_not_invent_confirm_option(self):
        p=self.panel();self.select(p,'covenant');self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'scene_ro6_end2_3');self.assertEqual(p.choices.count(),0);self.assertFalse(p.battle_button.isVisible());self.assertIn('不把别处',p.player.toPlainText())

    def test_same_source_refresh_both_nonzero_readers_and_condition_preserved(self):
        p=self.panel();p.resize(850,420);p.covenant.setCurrentIndex(p.covenant.findData(True));self.select(p,'covenant')
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(13,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.covenant.currentData())
            self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.covenant.currentData()))

    def test_actual_public_damage_clears_all_old_contents_and_recovery_is_manual(self):
        p=self.panel(None,'covenant');self.assertTrue(p.open_battle());old=p.battle_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(old.isVisible());self.assertIsNone(p.result);self.assertEqual(p.choices.count(),0);self.assertEqual(p.scene.count(),0);self.assertEqual(p.technical.toPlainText(),'')
                file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertFalse(p.open_battle())

    def test_real_update_all_four_scenes_and_seven_original_choices_exact_entry(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False))
        for category in('scenes','choices'):
            p.category.setCurrentIndex(p.category.findData(category));r=model.reference();ids=list(r['scenes'])if category=='scenes'else list(r['data']['originals']['choices'])
            for key in ids:
                row=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(row);self.assertTrue(p.flow_button.isVisible());QTest.mouseClick(p.flow_button,Qt.MouseButton.LeftButton);child=p.flow_dialog;target=model.locate(category,key)
                self.assertTrue(child.isVisible());self.assertEqual(child.panel.scene_id,target['scene_id']);self.assertEqual(child.panel.choice_id,target['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        self.assertTrue(p.open_documented_flow());self.assertFalse(child.isVisible());child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible());self.assertFalse(p.flow_button.isVisible())

    def test_parent_selection_change_and_close_and_source_recheck_close_owned_dialog(self):
        p=self.panel(None,'covenant');p.open_battle();old=p.battle_dialog
        with patch.object(model,'reference',return_value=None):self.assertFalse(p.open_battle());self.assertFalse(old.isVisible());self.assertIsNone(p.result)
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);p.go_start();self.select(p,'covenant');p.open_battle();old=p.battle_dialog;p.close();self.assertFalse(old.isVisible())


if __name__=='__main__':unittest.main()
