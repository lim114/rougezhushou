from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_node_readers as model
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_node_readers_332 import clone
class CurrentNodeReadersView332Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self):
        p=NodeCatalogPanel();p.resize(1000,700);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,event_id):
        key='event:'+event_id;i=next(i for i,e in enumerate(p.entries)if e['key']==key);p.list.setCurrentRow(i);self.qt.processEvents();return p
    def test_all25_catalogue_groups_open_correct_existing_reader_without_run_inputs(self):
        p=self.panel();p.runtime_context={'gold':100,'has_fossil':True,'has_controller':True}
        for event_id,row in model.packet()['data']['bindings'].items():
            self.select(p,event_id);self.assertTrue(p.current_reference_button.isVisible());self.assertTrue(p.open_current_event_reference());child=p.current_reference_window;self.assertEqual(child.panel.event_id,row['current_event_id']);self.assertIn('请核对实际游戏版本',child.node_reference_banner.text());self.assertIsNone(child.panel.result['actual_eligible']);self.assertIsNone(child.panel.choice_id)
            if hasattr(child.panel,'gold'):self.assertEqual(child.panel.gold.value(),-1)
            if hasattr(child.panel,'controller'):self.assertIsNone(child.panel.controller.currentData())
            if hasattr(child.panel,'fossil'):self.assertIsNone(child.panel.fossil.currentData())
            self.assertTrue(child.isVisible())
    def test_same_source_refresh_keeps_two_nonzero_readers_local_condition_and_nested_map(self):
        p=self.select(self.panel(),'community_group_008');self.assertTrue(p.open_current_event_reference());dialog=p.current_reference_window;flow=dialog.panel;flow.controller.setCurrentIndex(flow.controller.findData(True));key=next(c['id']for c in flow.result['choices'].values()if 'choice_ro6_normal2_2'in c['variant_ids']);flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(flow.open_battle());child=flow.battle_dialog;child.panel.stages.setCurrentIndex(child.panel.stages.findData('ro6_t_13'));self.assertTrue(child.panel.open_battle());battle=child.panel.battle_dialog;dialog.resize(850,440)
        for reader in(flow.player,flow.technical):
            flow.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),flow.tabs.currentIndex(),flow.choice_id,flow.controller.currentData(),child.panel.stages.currentData());p.refresh();self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),flow.tabs.currentIndex(),flow.choice_id,flow.controller.currentData(),child.panel.stages.currentData()));self.assertTrue(dialog.isVisible());self.assertTrue(child.isVisible());self.assertTrue(battle.isVisible())
        p.close();self.assertFalse(dialog.isVisible());self.assertFalse(child.isVisible());self.assertFalse(battle.isVisible())
    def test_changed_catalogue_selection_repeated_open_and_unrelated_types_close(self):
        p=self.select(self.panel(),'community_group_000');p.open_current_event_reference();old=p.current_reference_window;p.open_current_event_reference();self.assertFalse(old.isVisible());old=p.current_reference_window;self.select(p,'community_group_001');self.assertFalse(old.isVisible());p.open_current_event_reference();old=p.current_reference_window;i=next(i for i,e in enumerate(p.entries)if e['kind']=='function');p.list.setCurrentRow(i);self.qt.processEvents();self.assertFalse(p.current_reference_button.isVisible());self.assertFalse(old.isVisible());self.assertFalse(p.open_current_event_reference())
    def test_historical_node_opens_reference_no_state_mutation_epoch_change_closes(self):
        p=self.panel();graph={'zone_id':'zone_1','template_id':'t','nodes':[{'id':'a','row':1,'col':2,'observed_type':'林间空地','remembered_type':'不期而遇','remembered_content':{'kind':'event','title':'桑尼的邀请'}}]};before=deepcopy(graph);p.set_map_context(graph,{'floor':1},epoch='first',historical=True);p.set_node(graph,'a',floor=1);p.bind_current_node();i=next(i for i,e in enumerate(p.entries)if e['kind']=='event'and e['title']=='桑尼的邀请');p.list.setCurrentRow(i);self.qt.processEvents();self.assertTrue(p.open_current_event_reference());child=p.current_reference_window;self.assertIn('历史节点',child.node_reference_banner.text());self.assertIsNone(child.panel.result['actual_eligible']);p.refresh();self.assertTrue(child.isVisible());p.set_map_context(graph,{'floor':1},epoch='second',historical=True);self.assertFalse(child.isVisible());self.assertEqual(graph,before)
    def test_real_bridge_damage_and_optional_current_reader_loss_keep_catalogue_text(self):
        p=self.select(self.panel(),'community_group_016');p.open_current_event_reference();old=p.current_reference_window;prior=p.player_detail.toPlainText()
        with patch('rouge.current_lake.reference',return_value=None):p.show_selected();self.assertFalse(p.current_reference_button.isVisible());self.assertFalse(old.isVisible());self.assertEqual(p.player_detail.toPlainText(),prior)
        p.show_selected();self.assertTrue(p.open_current_event_reference());old=p.current_reference_window
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');p.show_selected();self.assertFalse(old.isVisible());self.assertFalse(p.open_current_event_reference());self.assertEqual(p.player_detail.toPlainText(),prior);f.write_bytes(raw);p.show_selected();self.assertIsNone(p.current_reference_window);self.assertTrue(p.open_current_event_reference())
if __name__=='__main__':unittest.main()
