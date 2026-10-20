from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_vine_events as model
from rouge.current_vine_events_view import CurrentVineEventsDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_vine_events_333 import clone,by_original
class CurrentVineEventsView333Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,title):
  d=CurrentVineEventsDialog(title);d.show();self.addCleanup(d.close);self.qt.processEvents();return d
 def pick(self,p,key):
  p.go_start();c=by_original(p.result,key);p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==c['id']));return c
 def test_only_relevant_controls_gold7_8_seed0_1_controller_three_states_independent(self):
  h=self.dialog('沉寂之屋').panel;r=self.dialog('呼吸的红苔').panel;self.assertTrue(hasattr(h,'gold'));self.assertFalse(hasattr(h,'controller'));self.assertFalse(hasattr(h,'seeds'));self.assertFalse(hasattr(r,'gold'));self.assertIsNone(r.controller.currentData());self.assertEqual(r.seeds.value(),-1)
  self.pick(h,'choice_ro6_normal1_2');h.gold.setValue(7);self.assertFalse(h.follow_scene());h.gold.setValue(8);self.assertTrue(h.follow_scene());self.pick(h,'choice_ro6_normal1_1');h.gold.setValue(0);self.assertTrue(h.follow_scene())
  self.pick(r,'choice_ro6_normal3_1');r.controller.setCurrentIndex(r.controller.findData(False));self.assertFalse(r.follow_scene());r.controller.setCurrentIndex(r.controller.findData(True));self.assertTrue(r.follow_scene());self.pick(r,'choice_ro6_normal3_2');r.seeds.setValue(0);self.assertFalse(r.follow_scene());r.seeds.setValue(1);r.controller.setCurrentIndex(r.controller.findData(False));self.assertTrue(r.follow_scene());self.pick(r,'choice_ro6_normal3_3');r.seeds.setValue(0);self.assertTrue(r.follow_scene())
 def test_refresh_keeps_two_nonzero_reading_states_conditions_exact_choice(self):
  d=self.dialog('呼吸的红苔');d.resize(850,440);p=d.panel;self.pick(p,'choice_ro6_normal3_1');p.controller.setCurrentIndex(p.controller.findData(True));p.seeds.setValue(3)
  for reader in(p.player,p.technical):
   p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.choice_id,p.tabs.currentIndex());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.choice_id,p.tabs.currentIndex()));self.assertEqual((p.controller.currentData(),p.seeds.value()),(True,3))
 def test_all14_exact_version_entries_and_repeated_parent_open_source_loss(self):
  p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
  for category,rows in(('scenes',d['originals']['scenes']),('choices',d['originals']['choices'])):
   p.category.setCurrentIndex(p.category.findData(category))
   for key in rows:
    p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.flow_button.isVisible());old=getattr(p,'flow_dialog',None);self.assertTrue(p.open_documented_flow());target=model.locate(category,key);self.assertEqual((p.flow_dialog.panel.event_id,p.flow_dialog.panel.scene_id,p.flow_dialog.panel.choice_id),(target['event_id'],target['scene_id'],target['choice_id']));self.assertTrue(old is None or not old.isVisible())
  old=p.flow_dialog;p._unavailable();self.assertFalse(old.isVisible())
 def test_new_catalogue_entries_open_reference_not_runtime_values_parent_refresh_and_close(self):
  p=NodeCatalogPanel();p.show();self.addCleanup(p.close);p.runtime_context={'gold':888,'seeds':5,'has_controller':True}
  for key in model.CATALOGUE_IDS:
   p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:'+key));self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;r=d.panel;self.assertIsNone(r.choice_id);self.assertIsNone(r.result['actual_eligible']);self.assertIn('请核对实际游戏版本',d.node_reference_banner.text())
   if hasattr(r,'gold'):self.assertEqual(r.gold.value(),-1)
   else:self.assertIsNone(r.controller.currentData());self.assertEqual(r.seeds.value(),-1)
   p.refresh();self.assertTrue(d.isVisible());p.close();self.assertFalse(d.isVisible());p.show()
 def test_actual_source_damage_clears_old_reading_manual_recovery_and_catalogue_isolated(self):
  d=self.dialog('呼吸的红苔');p=d.panel;self.pick(p,'choice_ro6_normal3_1')
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
   with patch.object(model,'ROOT',root):
    f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
if __name__=='__main__':unittest.main()
