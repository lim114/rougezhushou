from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_agency as model
from rouge.current_agency_view import CurrentAgencyDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_agency_340 import clone

class CurrentAgencyView340Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,*args):
        d=CurrentAgencyDialog(*args);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,key):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][key]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents()
    def test_overview_no_default_offer_or_irrelevant_resource_controls(self):
        p=self.dialog().panel;self.assertIsNone(p.choice_id);self.assertIsNone(p.offer.currentData());self.assertTrue(p.offer_controls.isHidden());self.assertFalse(any(hasattr(p,n)for n in('gold','difficulty','controller','action_points')))
    def test_four_profession_pairs_display_both_icons_and_plain_distinct_labels(self):
        p=self.dialog().panel
        for c in p.result['choices'].values():
            if c['role']=='promoted':
                self.choose(p,c['id']);self.assertTrue(p.offer_controls.isVisible());self.assertEqual(p.pair_label.text(),'或'.join(c['profession_pair'])+' · 只招募一名');self.assertTrue(all(not x.pixmap().isNull()for x in p.pair_icons));self.assertEqual([x.accessibleName()for x in p.pair_icons],[n+'职业图标'for n in c['profession_pair']])
    def test_mismatched_offer_blocks_only_reliable_followup_matching_can_read(self):
        p=self.dialog().panel;self.choose(p,'choice_ro6_hire1_1');p.offer.setCurrentIndex(p.offer.findData('重装或辅助'));self.assertFalse(p.follow_scene());self.assertIsNone(p.result['actual_profession_offer']);p.offer.setCurrentIndex(p.offer.findData('先锋或近卫'));self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0);self.assertTrue(p.offer_controls.isHidden())
    def test_six_star_and_leave_hide_pair_controls_and_do_not_inherit_offer(self):
        p=self.dialog().panel;self.choose(p,'choice_ro6_hire1_1');p.offer.setCurrentIndex(p.offer.findData('先锋或近卫'))
        for key in('choice_ro6_hire1_2','choice_ro6_hire1_3'):
            self.choose(p,key);self.assertTrue(p.offer_controls.isHidden());self.assertTrue(all(x.pixmap().isNull()for x in p.pair_icons));self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
        self.choose(p,'choice_ro6_hire1_1');self.assertEqual(p.offer.currentData(),'先锋或近卫')
    def test_two_nonzero_readings_choice_offer_and_tab_survive_parent_refresh(self):
        d=self.dialog('scene_ro6_hire1_enter','choice_ro6_hire1_4');d.resize(850,440);p=d.panel;p.offer.setCurrentIndex(p.offer.findData('重装或辅助'))
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.offer.currentData());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.offer.currentData()))
    def test_bad_icon_shows_profession_name_keeps_text_and_other_icon(self):
        p=self.dialog('scene_ro6_hire1_enter','choice_ro6_hire1_1').panel;before=p.player.toPlainText()
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/'rouge/data/profession-icons/pioneer.png';file.write_bytes(file.read_bytes()+b'x')
            with patch.object(model,'ROOT',root):
                self.assertTrue(p.refresh_reference());self.assertEqual(p.player.toPlainText(),before);self.assertIn('图标暂缺',p.pair_icons[0].text());self.assertFalse(p.pair_icons[1].pixmap().isNull())
    def test_real_source_loss_clears_reading_and_icons_recovery_is_manual(self):
        p=self.dialog('scene_ro6_hire1_enter','choice_ro6_hire1_1').panel
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.offer_controls.isHidden());self.assertTrue(all(x.pixmap().isNull()for x in p.pair_icons));file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.choice_id);self.assertIsNone(p.scene_id)
    def test_all_ten_exact_version_entries_repeated_open_and_source_loss(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference()
        for category in('scenes','choices'):
            p.category.setCurrentIndex(p.category.findData(category))
            for key in r['data']['originals'][category]:
                p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.open_documented_flow());t=model.locate(category,key);self.assertEqual((p.flow_dialog.panel.scene_id,p.flow_dialog.panel.choice_id),(t['scene_id'],t['choice_id']));self.assertIsNone(p.flow_dialog.panel.offer.currentData())
        old=p.flow_dialog;p.open_documented_flow();self.assertFalse(old.isVisible());p._unavailable();self.assertFalse(p.flow_dialog.isVisible())
    def test_node_overview_defaults_unknown_version_notice_refresh_and_close(self):
        p=NodeCatalogPanel();p.show();self.addCleanup(p.close);p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_018'));self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertIsNone(d.panel.offer.currentData());self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());p.refresh();self.assertTrue(d.isVisible());p.close();self.assertFalse(d.isVisible())
if __name__=='__main__':unittest.main()
