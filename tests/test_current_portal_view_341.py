from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_portal as m
from rouge.current_portal_view import CurrentPortalDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_portal_341 import clone

class CurrentPortalView341Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        d=CurrentPortalDialog(target);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,sid,cid=None):
        p.scene.setCurrentIndex(p.scene.findData(sid))
        if cid:p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid))
    def test_default_overview_no_assumed_fog_or_parts(self):
        p=self.dialog().panel;self.assertEqual(p.scene_id,'overview');self.assertIsNone(p.choice_id);self.assertEqual(p.parts.value(),-1);self.assertTrue(p.part_controls.isHidden());self.assertFalse(any(hasattr(p,k)for k in('gold','difficulty','controller','offer')))
    def test_six_fogs_green_two_distinct_leaves_and_red_only_alternative(self):
        p=self.dialog().panel
        for fog in('红雾','蓝雾','绿雾','金雾','橙雾','紫雾'):
            self.choose(p,'fog:'+fog);self.assertIn(fog,p.player.toPlainText());items={p.choices.item(i).data(Qt.ItemDataRole.UserRole):p.choices.item(i).text()for i in range(p.choices.count())};self.assertEqual('no-engine:alt'in items,fog=='红雾')
            if fog=='绿雾':self.assertIn('实际选择依据未知',p.player.toPlainText());self.assertNotEqual(items['leave:0'],items['leave:1'])
    def test_inventory0_1_conditions_confirmation_hidden_not_second_pay(self):
        p=self.dialog().panel;self.choose(p,'fog:红雾','pay:1');p.parts.setValue(0);self.assertFalse(p.follow_scene());self.choose(p,'fog:红雾','leave:0');self.assertFalse(p.follow_scene());self.choose(p,'fog:红雾','no-engine:normal');self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
        self.choose(p,'fog:红雾','pay:1');p.parts.setValue(1);self.assertTrue(p.follow_scene());self.choose(p,'after:1','confirm:1');self.assertTrue(p.part_controls.isHidden());self.assertFalse(p.next_button.isVisible());self.assertFalse(p.open_battle())
    def test_two_real_nonzero_readers_condition_choice_and_source_survive_refresh(self):
        d=self.dialog();d.resize(850,440);p=d.panel;self.choose(p,'fog:红雾','pay:2');p.parts.setValue(1)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.parts.value());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.parts.value()))
    def test_raw_scene_and_choice_have_exact_pointer_no_assumed_color_menu(self):
        for cat,key in [('scenes','scene_ro6_portal1a_enter'),('choices','choice_ro6_portal1a_1'),('choices','choice_ro6_portal1a_4'),('choices','choice_ro6_portal1a_6')]:
            p=self.dialog(m.locate(cat,key)).panel;self.assertEqual(p.source_request,{'category':cat,'key':key});self.assertEqual(p.scene_id,'source-scene'if cat=='scenes'else'source-choice')
            if cat=='scenes':self.assertEqual(p.choices.count(),0)
            elif key.endswith('_4'):self.assertTrue(p.part_controls.isHidden());self.assertFalse(p.next_button.isVisible())
            else:
                if key.endswith('_6'):self.assertTrue(p.part_controls.isHidden())
                self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'source-next');self.assertEqual(p.choices.count(),0)
    def test_source_damage_clears_and_manual_recovery_does_not_reselect(self):
        p=self.dialog().panel;self.choose(p,'fog:绿雾','leave:1')
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/m.DATA;raw=f.read_bytes()
            with patch.object(m,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.part_controls.isHidden());f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_version_source_entry_repeated_open_parent_refresh_and_clear(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('choices'));key='choice_ro6_portal1a_1';p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.open_documented_flow());d=p.flow_dialog;self.assertEqual(d.panel.source_request,{'category':'choices','key':key});d.panel.parts.setValue(1);p.refresh_reference();self.assertIs(p.flow_dialog,d);self.assertEqual(d.panel.parts.value(),1);p.open_documented_flow();self.assertFalse(d.isVisible());p._unavailable();self.assertFalse(p.flow_dialog.isVisible())
    def test_node_overview_starts_without_color_or_actual_inventory(self):
        p=NodeCatalogPanel();p.show();self.addCleanup(p.close);p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_027'));self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertEqual(d.panel.scene_id,'overview');self.assertIsNone(d.panel.source_request);self.assertEqual(d.panel.parts.value(),-1);self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());p.refresh();self.assertTrue(d.isVisible());p.close();self.assertFalse(d.isVisible())
if __name__=='__main__':unittest.main()
