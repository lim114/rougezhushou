from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_lone_dog as model
from rouge.current_lone_dog_view import CurrentLoneDogDialog
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_lone_dog_335 import clone
class CurrentLoneDogView335Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,sid=None,cid=None):
  d=CurrentLoneDogDialog(sid,cid);d.show();self.addCleanup(d.close);self.qt.processEvents();return d
 def test_move_and_mark_no_next_battle_or_extra_controls_and_leave_independent(self):
  for key in('choice_ro6_task2_3','choice_ro6_task2_4'):
   t=model.locate('choices',key);p=self.dialog(t['scene_id'],key).panel;self.assertEqual(p.choice_id,key);self.assertFalse(p.follow_scene());self.assertFalse(p.next_button.isVisible());self.assertFalse(p.battle_button.isVisible());self.assertFalse(any(hasattr(p,n)for n in('gold','controller','seeds','fossil')))
  t=model.locate('choices','choice_ro6_task2_2');p=self.dialog(t['scene_id'],t['choice_id']).panel;self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
 def test_same_source_refresh_keeps_two_nonzero_readers_and_selected_move(self):
  t=model.locate('choices','choice_ro6_task2_3');d=self.dialog(t['scene_id'],t['choice_id']);d.resize(850,440);p=d.panel
  for reader in(p.player,p.technical):
   p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));prior=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id);self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(prior,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id))
 def test_version7_and_catalogue_overview_defaults_repeated_open_and_parent_close(self):
  p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference()
  for category in('scenes','choices'):
   p.category.setCurrentIndex(p.category.findData(category))
   for key in r['data']['originals'][category]:
    p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.open_documented_flow());t=model.locate(category,key);self.assertEqual((p.flow_dialog.panel.scene_id,p.flow_dialog.panel.choice_id),(t['scene_id'],t['choice_id']))
  old=p.flow_dialog;p.open_documented_flow();self.assertFalse(old.isVisible());p._unavailable();self.assertFalse(p.flow_dialog.isVisible());n=NodeCatalogPanel();n.show();self.addCleanup(n.close);n.list.setCurrentRow(next(i for i,e in enumerate(n.entries)if e['key']=='event:community_group_020'));self.assertTrue(n.open_current_event_reference());d=n.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertIsNone(d.panel.result['actual_eligible']);n.refresh();self.assertTrue(d.isVisible());n.close();self.assertFalse(d.isVisible())
 def test_real_source_damage_clears_and_manual_recovery_does_not_restore_choice(self):
  p=self.dialog('scene_ro6_task2_1','choice_ro6_task2_4').panel
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
   with patch.object(model,'ROOT',root):
    f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
if __name__=='__main__':unittest.main()
