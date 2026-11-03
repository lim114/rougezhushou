from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_named_reward_origins as model
from rouge.current_reward_origins_view import CurrentRewardOriginsDialog
from rouge.current_named_reward_origins_view import make_event_dialog
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_named_reward_origins_347 import clone
class CurrentNamedRewardOriginsView347Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,iid='rogue_6_relic_cargo_13'):
        d=CurrentRewardOriginsDialog('relics',iid);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def version(self,iid):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('relics'));p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==iid));self.qt.processEvents();return p
    def test_default_no_selection_claim_or_auto_open(self):
        p=self.dialog().panel;self.assertEqual(p.entries.count(),1);self.assertIsNone(p.entries.currentItem());self.assertFalse(p.open_button.isEnabled());self.assertIsNone(p.event_dialog);self.assertIn('不是全部掉落方式',p.player.toPlainText());self.assertEqual(p.entries.maximumHeight(),120);self.assertGreater(p.player.height(),p.entries.height())
    def test_all11_new_items_open_exact_existing_seven_reader_targets(self):
        for row in model.packet()['data']['rows']:
            p=self.dialog(row['item_id']).panel;p.entries.setCurrentRow(0);self.assertTrue(p.open_event(),row['item']['name']);c=p.event_dialog.panel;target=row['target']
            if 'source_request'in target:self.assertEqual(c.result['source_request'],target['source_request']);self.assertEqual(c.result['requested_original'],row['choice']);self.assertEqual(c.choice_id,'source-choice')
            else:self.assertEqual((c.scene_id,c.choice_id),(target['scene_id'],target['choice_id']))
            self.assertIsNone(c.result['actual_eligible']);self.assertFalse(c.result['run_updated']);p.close()
    def test_held_control_only_hunter_and_peace_move_control_absent_on_get(self):
        p=self.dialog('rogue_6_relic_cargo_12').panel;p.entries.setCurrentRow(0);p.open_event();self.assertIsNone(p.event_dialog.panel.controller.currentData());self.assertIn('持有笼控器是条件',p.player.toPlainText());self.assertNotIn('笼控器 ·',p.entries.item(0).text())
        p=self.dialog('rogue_6_relic_cargo_11').panel;p.entries.setCurrentRow(0);p.open_event();self.assertTrue(p.event_dialog.panel.completion_controls.isHidden());self.assertIn('不等于已经前往',p.player.toPlainText())
    def test_same_parent_refresh_keeps_two_nonzero_readings_selection_tab_and_child(self):
        d=self.dialog();d.resize(720,390);p=d.panel;p.entries.setCurrentRow(0);self.assertTrue(p.open_event());child=p.event_dialog;self.assertTrue(child.panel.follow_scene())
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(3,bar.maximum()));old=(cursor.anchor(),cursor.position(),bar.value(),p.tabs.currentIndex(),p.entries.currentRow());self.assertTrue(p.refresh_reference());cursor=reader.textCursor();self.assertEqual(old,(cursor.anchor(),cursor.position(),bar.value(),p.tabs.currentIndex(),p.entries.currentRow()))
        self.assertIs(p.event_dialog,child);self.assertTrue(child.isVisible());self.assertEqual(child.panel.scene_id,'source-next')
    def test_repeat_open_switch_and_parent_close_closes_owned_event(self):
        p=self.dialog().panel;p.entries.setCurrentRow(0);p.open_event();old=p.event_dialog;p.open_event();self.assertFalse(old.isVisible());old=p.event_dialog;p.entries.setCurrentRow(-1);self.assertFalse(old.isVisible());p.entries.setCurrentRow(0);p.open_event();old=p.event_dialog;p.close();self.assertFalse(old.isVisible())
    def test_real_addon_source_damage_clears_tree_and_manual_reselection(self):
        p=self.dialog().panel;p.entries.setCurrentRow(0);p.open_event();old=p.event_dialog
        with TemporaryDirectory()as f:
            root=Path(f);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b'x');self.assertFalse(p.refresh_reference());self.assertFalse(old.isVisible());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.entries.currentItem());self.assertFalse(p.open_event())
    def test_forged_reader_item_and_target_rejected_before_dialog_open(self):
        row=deepcopy(model.packet()['data']['rows'][0])
        for field,value in[('reader_key','ritual'),('item_id','rogue_6_relic_cargo_13'),('target',{'source_request':{'category':'choices','key':'choice_ro6_end3_1'}})]:
            bad=deepcopy(row);bad[field]=value;self.assertIsNone(make_event_dialog(bad))
        p=self.dialog().panel;p.entries.setCurrentRow(0);p.result['rows'][0]['choice']['title']='changed';self.assertFalse(p.open_event());self.assertIsNone(p.result)
    def test_version_entry_parent_refresh_and_close_keeps_then_cleans_tree(self):
        p=self.version('rogue_6_relic_artifact_4');self.assertFalse(p.origins_button.isHidden());self.assertTrue(p.open_reward_origins());d=p.origins_dialog;d.panel.entries.setCurrentRow(0);d.panel.open_event();child=d.panel.event_dialog;self.assertTrue(child.panel.reward_card.isVisible());self.assertTrue(p.refresh_reference());self.assertIs(p.origins_dialog,d);self.assertTrue(child.isVisible());p._unavailable();self.assertFalse(d.isVisible());self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
