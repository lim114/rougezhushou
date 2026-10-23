from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import documented_event_flows as model
from rouge.documented_event_flow_view import DocumentedEventFlowPanel
from rouge.ending_event_view import EndingEventPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_documented_event_flows_321 import EXPECTED,clone


class DocumentedEventFlowView321Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,event='button',scene=None):
        p=DocumentedEventFlowPanel(event,scene);p.resize(950,550);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,cid):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:p.choices.setCurrentRow(i);return
        self.fail('Absent actual choice '+cid)

    def test_all_ten_scenes_only_documented_choices_and_manual_transitions(self):
        for event in ('button','blueprint','revive'):
            p=self.panel(event)
            for sid in p.result['event']['scene_ids']:
                p.scene.setCurrentIndex(p.scene.findData(sid))
                self.assertEqual([p.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(p.choices.count())],EXPECTED[sid]);self.assertIsNone(p.choice_id)
                self.assertFalse(p.next_button.isVisible());self.assertFalse(p.battle_button.isVisible())
                for cid in EXPECTED[sid]:
                    p.scene.setCurrentIndex(p.scene.findData(sid));self.select(p,cid);c=p.result['choices'][cid]
                    self.assertEqual(p.next_button.isVisible(),c['next_scene_id']is not None);self.assertEqual(p.battle_button.isVisible(),bool(c['stage_ids']))
                    if c['next_scene_id']:
                        QTest.mouseClick(p.next_button,Qt.MouseButton.LeftButton);self.assertEqual(p.scene_id,c['next_scene_id']);self.assertIsNone(p.choice_id)
                        QTest.mouseClick(p.start_button,Qt.MouseButton.LeftButton);self.assertEqual(p.scene_id,p.result['event']['entry_scene_id'])

    def test_nonzero_both_readers_choice_and_tab_preserved_on_refresh(self):
        p=self.panel('revive');p.resize(850,410);self.select(p,'choice_ro6_revive_1')
        for reader in (p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(3,bar.maximum()))
            before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id)
            self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id))

    def test_exact_battle_dialog_repeat_scene_change_and_parent_close(self):
        p=self.panel('button','scene_ro6_end4_1');self.assertFalse(p.open_battle());self.select(p,'choice_ro6_end4_3');self.assertTrue(p.open_battle());old=p.battle_dialog
        self.assertEqual(old.panel.stage_id,'ro6_s_1');self.assertTrue(old.isVisible());self.assertTrue(p.open_battle());self.assertFalse(old.isVisible());old=p.battle_dialog
        self.assertTrue(p.go_start());self.assertFalse(old.isVisible());p.scene.setCurrentIndex(p.scene.findData('scene_ro6_end4_1'));self.select(p,'choice_ro6_end4_3');p.open_battle();old=p.battle_dialog;p.close();self.assertFalse(old.isVisible())

    def test_real_public_file_damage_clears_scene_choice_readers_and_battle_then_manual_recovery(self):
        p=self.panel('button','scene_ro6_end4_1');self.select(p,'choice_ro6_end4_3');p.open_battle();old=p.battle_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(old.isVisible());self.assertIsNone(p.result);self.assertEqual(p.scene.count(),0);self.assertEqual(p.choices.count(),0);self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.battle_button.isVisible())
                file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertFalse(p.follow_scene());self.assertFalse(p.open_battle())

    def test_action_rechecks_source_before_following_or_opening(self):
        p=self.panel();self.select(p,'choice_ro6_end4_1')
        with patch.object(model,'reference',return_value=None):self.assertFalse(p.follow_scene());self.assertIsNone(p.result)
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id)

    def test_real_ending_entry_hidden_elsewhere_and_owned_dialog_lifecycle(self):
        p=EndingEventPanel();p.show();self.addCleanup(p.close);self.assertFalse(p.flow_button.isVisible());self.assertFalse(p.open_documented_flow())
        for key in ('entry','side_path','path_bonus','hidden_region'):
            p.choices.select_value(key);self.assertFalse(p.flow_button.isVisible());self.assertFalse(p.open_documented_flow())
        for key in ('button','blueprint','revive'):
            p.choices.select_value(key);self.assertTrue(p.flow_button.isVisible());QTest.mouseClick(p.flow_button,Qt.MouseButton.LeftButton);child=p.flow_dialog;self.assertTrue(child.isVisible());self.assertEqual(child.panel.event_id,key)
            self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());self.assertTrue(p.open_documented_flow());self.assertFalse(child.isVisible());child=p.flow_dialog;p.choices.select_value('entry');self.assertFalse(child.isVisible())
        p.choices.select_value('button');p.open_documented_flow();child=p.flow_dialog;p.close();self.assertFalse(child.isVisible())

    def test_exact_update_scene_entry_and_source_loss_closes_children(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('scenes'))
        def choose(sid):
            for i in range(p.entries.count()):
                if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid:p.entries.setCurrentRow(i);return
            self.fail('missing actual scene')
        for sid in EXPECTED:
            choose(sid);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;self.assertEqual(child.panel.scene_id,sid);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        choose('scene_ro6_final1_enter');self.assertFalse(child.isVisible());self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;self.assertEqual(child.panel.event_id,'exit')
        p.category.setCurrentIndex(p.category.findData('regions'));p.entries.setCurrentRow(0);self.assertFalse(p.flow_button.isVisible());self.assertFalse(child.isVisible());self.assertFalse(p.open_documented_flow())
        p.category.setCurrentIndex(p.category.findData('scenes'))
        choose('scene_ro6_end4_1');p.open_documented_flow();child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible());self.assertFalse(p.flow_button.isVisible())


if __name__=='__main__':unittest.main()
