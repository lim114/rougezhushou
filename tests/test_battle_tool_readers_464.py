import unittest,json
from unittest.mock import patch
from copy import deepcopy
from types import SimpleNamespace
from PySide6.QtCore import Qt,QRect
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_reference_window import ReferenceWindow
from rouge.player_map_reader import make_reader

class BattleToolReaderTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.owner=QWidget();self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present;self.addCleanup(self.owner.close);self.addCleanup(self.host.close)
 def battle(self,sid='ro6_n_1_1'):
  page=make_reader('battle',{'id':sid,'title':'公开固定关卡'},self.owner,historical=True,page_owner=self.owner);page.prepare=page.panel.refresh_reference;self.assertTrue(self.host.present(page));self.qt.processEvents();return page,page.panel
 def back(self,page):self.host.navigate(self.host.history.index(page));self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),page)
 def tool(self,parent,name):
  self.assertTrue(getattr(parent,'open_'+name)());self.qt.processEvents();return self.host.pages.currentWidget()
 def member(self,p,key=None):
  relation,member=next((r,m)for r in p.result['groups']for m in r['members']if key is None or m['action_key']==key)
  p.relation_combo.setCurrentIndex(p.relation_combo.findData(relation['key']));p.member_combo.setCurrentIndex(p.member_combo.findData(member['action_key']));return member
 def test_four_tools_share_native_host_and_original_battle_identity(self):
  root,p=self.battle();h=int(self.host.winId());p.enemy_choices.select_value('5',emit=True)
  for name in ['spawn_candidates','enemy_spawns','stage_objects','route_itinerary']:
   self.back(root);child=self.tool(p,name);self.assertIs(child.source_parent,root);self.assertEqual(child.panel.result['battle_source_identity'],p.result['source_identity']);self.assertIsNone(getattr(p,name+'_dialog',None));self.assertEqual(int(self.host.winId()),h)
 def test_spawn_action_returns_to_exact_original_record_and_reuses_reader(self):
  root,p=self.battle();page=self.tool(p,'spawn_candidates');member=self.member(page.panel,'0');self.assertTrue(page.panel.follow_action());self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.action_key,member['action_key']);self.assertEqual(p.tabs.currentIndex(),2);self.assertIs(self.tool(p,'spawn_candidates'),page);self.assertEqual(page.panel.member_combo.currentData(),member['action_key'])
 def test_spawn_map_is_child_of_tool_and_keeps_map_selection_on_reopen(self):
  root,p=self.battle('ro6_n_2_3');page=self.tool(p,'spawn_candidates');self.member(page.panel,'1');self.assertTrue(page.panel.follow_position());position=self.host.pages.currentWidget();self.assertIs(position.source_parent,page);self.assertEqual(position.panel.action_key,'1');position.panel.combo.setCurrentIndex(1);selected=position.panel.grid.selected;self.assertIsNotNone(selected);self.back(page);self.assertTrue(page.panel.follow_position());self.assertIs(self.host.pages.currentWidget(),position);self.assertEqual(position.panel.grid.selected,selected)
 def test_enemy_action_returns_and_enemy_change_discards_tool_and_map(self):
  root,p=self.battle();p.enemy_choices.select_value('5',emit=True);page=self.tool(p,'enemy_spawns');page.panel.entries.setCurrentIndex(1);key=page.panel.entries.currentData();self.assertTrue(page.panel.follow_action());self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.action_key,key);self.assertIs(self.tool(p,'enemy_spawns'),page);self.assertTrue(page.panel.follow_position());position=self.host.pages.currentWidget();self.assertIs(position.source_parent,page);self.back(root);p.enemy_choices.select_value('0',emit=True);self.host.navigate(self.host.cursor+1);self.assertNotIn(page,self.host.history);self.assertNotIn(position,self.host.history);self.assertIs(self.host.pages.currentWidget(),root)
 def test_object_map_keeps_exact_cell_and_parent_selection_changes_remove_it(self):
  root,p=self.battle();page=self.tool(p,'stage_objects');r=page.panel;r.entries.setCurrentIndex(1);row=r.selected();self.assertTrue(r.open_position());position=self.host.pages.currentWidget();self.assertIs(position.source_parent,page);self.assertEqual(position.panel.key,row['key']);self.assertEqual(position.panel.result['row']['raw']['position'],row['raw']['position']);self.assertIn('资料说明',[position.panel.tabs.tabText(i)for i in range(position.panel.tabs.count())]);self.back(page);r.entries.setCurrentIndex(2);self.host.navigate(self.host.cursor+1);self.assertNotIn(position,self.host.history);self.assertIs(self.host.pages.currentWidget(),page)
 def test_object_action_returns_to_original_battle_without_legacy_dialog(self):
  root,p=self.battle();page=self.tool(p,'stage_objects');r=page.panel;r.entries.setCurrentIndex(1);r.activations.setCurrentIndex(1);key=r.selected_action()['key'];self.assertTrue(r.follow_action());self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.action_key,key);self.assertIsNone(r.position_dialog)
 def test_route_map_retains_route_step_and_invalidates_changed_step(self):
  root,p=self.battle('ro6_n_1_3');page=self.tool(p,'route_itinerary');r=page.panel;r.entries.setCurrentIndex(r.entries.findData('$.routes[10]'));r.steps.setCurrentIndex(1);step=r.selected_step();self.assertTrue(r.open_position());position=self.host.pages.currentWidget();self.assertEqual(position.panel.result['cell'],step['cell']);self.assertIs(position.source_parent,page);self.back(page);self.assertTrue(r.open_position());self.assertIs(self.host.pages.currentWidget(),position);self.back(page);r.steps.setCurrentIndex(2);self.host.navigate(self.host.cursor+1);self.assertNotIn(position,self.host.history)
 def test_route_action_returns_to_exact_battle_entry(self):
  root,p=self.battle();page=self.tool(p,'route_itinerary');r=page.panel;r.entries.setCurrentIndex(r.entries.findData('$.routes[10]'));r.actions.setCurrentIndex(1);key=r.selected_action()['key'];self.assertTrue(r.follow_action());self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.action_key,key)
 def test_direct_map_and_action_map_use_host_and_only_action_selection_binds_action_map(self):
  root,p=self.battle('ro6_n_2_3');self.assertTrue(p.open_map_positions());grid=self.host.pages.currentWidget();self.assertIs(grid.source_parent,root);self.assertEqual(grid.panel.stage_id,p.stage_id);self.back(root);p.actions.setCurrentRow(next(i for i in range(p.actions.count())if p.actions.item(i).data(Qt.ItemDataRole.UserRole)=='1'));self.assertTrue(p.open_action_positions());action=self.host.pages.currentWidget();self.assertIs(action.source_parent,root);self.assertEqual(action.panel.action_key,'1');self.back(root);p.actions.setCurrentRow(next(i for i in range(p.actions.count())if p.actions.item(i).data(Qt.ItemDataRole.UserRole)=='2'));self.host.navigate(self.host.cursor+1);self.assertNotIn(action,self.host.history);self.assertIsNone(getattr(p,'position_dialog',None));self.assertIsNone(getattr(p,'action_position_dialog',None))
 def test_same_tool_reopen_preserves_query_tab_and_selection_without_constructor(self):
  root,p=self.battle();page=self.tool(p,'stage_objects');r=page.panel;r.search.setText('支援');r.entries.setCurrentIndex(1);r.tabs.setCurrentIndex(1);cursor=r.technical.textCursor();cursor.setPosition(4);cursor.setPosition(18,QTextCursor.MoveMode.KeepAnchor);r.technical.setTextCursor(cursor);selected=cursor.selectedText();key=r.entries.currentData();self.back(root)
  with patch('rouge.current_stage_objects_view.CurrentStageObjectsPanel',side_effect=AssertionError('same reader must be retained')):self.assertIs(self.tool(p,'stage_objects'),page)
  self.assertEqual((r.search.text(),r.entries.currentData(),r.tabs.currentIndex()),('支援',key,1));self.assertEqual(r.technical.textCursor().selectedText(),selected)
 def test_missing_destination_source_clears_tool_and_dependent_map(self):
  root,p=self.battle();page=self.tool(p,'stage_objects');page.panel.entries.setCurrentIndex(1);page.panel.open_position();position=self.host.pages.currentWidget();self.back(root)
  with patch('rouge.current_stage_objects.stage_reference',return_value=None):self.host.navigate(self.host.cursor+1)
  self.assertNotIn(page,self.host.history);self.assertNotIn(position,self.host.history);self.assertIs(self.host.pages.currentWidget(),root)
 def test_larger_reader_is_repositioned_inside_available_screen_without_moving_valid_position(self):
  root,p=self.battle();self.host.move(4000,4000);area=QRect(10,20,800,600)
  with patch.object(self.host,'screen',return_value=SimpleNamespace(availableGeometry=lambda:area)):
   self.assertTrue(p.open_map_positions());self.qt.processEvents();self.assertTrue(area.contains(self.host.geometry()));self.assertLessEqual(self.host.width(),776);self.assertLessEqual(self.host.height(),576)
   self.back(root);self.host.resize(600,400);self.host.move(25,35);self.assertTrue(p.open_stage_objects());self.qt.processEvents();self.assertEqual(self.host.pos().x(),25);self.assertEqual(self.host.pos().y(),35)
 def test_copy_keeps_full_original_notes_and_fields_in_details(self):
  root,p=self.battle();p.enemy_choices.select_value('5',emit=True)
  for name in ['spawn_candidates','enemy_spawns','stage_objects','route_itinerary']:
   self.back(root);page=self.tool(p,name);r=page.panel;raw=json.loads(r.technical.toPlainText());self.assertIn('完整说明',raw);self.assertTrue(raw['完整说明']);self.assertNotIn('【重要边界】',r.player.toPlainText());self.assertNotIn('【使用提醒】',r.player.toPlainText());self.assertEqual(r.result['battle_source_identity'],p.result['source_identity'])

if __name__=='__main__':unittest.main()
