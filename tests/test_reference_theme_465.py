import unittest,json,re
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QPlainTextEdit
from PySide6.QtGui import QPalette,QIcon,QTextCursor
from rouge.player_reference_window import ReferenceWindow,ToolPage
from rouge.player_map_reader import make_reader
from rouge import current_cannot_reference as model
from rouge.player_theme import DATA,assets

class CannotSharedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.owner=QWidget();self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present;self.addCleanup(self.owner.close);self.addCleanup(self.host.close)
 def battle(self):
  root=make_reader('battle',{'id':'ro6_t_6','title':'商店挑战'},self.owner,historical=True,page_owner=self.owner);root.prepare=root.panel.refresh_reference;self.assertTrue(self.host.present(root));root.panel.enemy_choices.select_value('0',emit=True);self.qt.processEvents();return root,root.panel
 def source(self,p):self.assertTrue(p.open_shop_vault());self.qt.processEvents();return self.host.pages.currentWidget()
 def back(self,page):self.host.navigate(self.host.history.index(page));self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),page)
 def test_exact_enemy_reference_opens_in_same_host_and_returns_to_matching_ancestor(self):
  root,p=self.battle();h=int(self.host.winId());page=self.source(p);self.assertEqual(page.panel.target,model.target_for_enemy('ro6_t_6','0'));self.assertIs(page.source_parent,root);self.assertEqual(int(self.host.winId()),h);target={'kind':'battle','stage_id':'ro6_t_6','enemy_key':'0','reward_id':None};self.assertTrue(page.panel.open_link(target));self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.enemy_key,'0');self.assertEqual(p.tabs.currentIndex(),1);self.assertIs(self.source(p),page);self.assertIsNone(p.shop_vault_dialog);self.assertIsNone(page.panel.battle_dialog)
 def test_vault_reward_link_focuses_exact_record_in_original_battle(self):
  root,p=self.battle();page=self.source(p);r=page.panel;vault=model.target_for_reward('ro6_t_6','$.predefines.tokenInsts[0]');self.assertTrue(r.navigate(vault));target={'kind':'battle','stage_id':'ro6_t_6','enemy_key':None,'reward_id':vault['key']};self.assertTrue(r.open_link(target));self.assertIs(self.host.pages.currentWidget(),root);self.assertEqual(p.rewards.combo.currentData(),vault['key']);self.assertIs(p.tabs.currentWidget(),p.rewards);self.assertIs(self.source(p),page);self.assertEqual(r.target,vault)
 def test_reopen_preserves_topic_exact_reference_related_choice_and_reading(self):
  root,p=self.battle();page=self.source(p);r=page.panel;r.topic.setCurrentIndex(r.topic.findData('free'));r.tabs.setCurrentIndex(1);r.related.setCurrentRow(2);selected=r.related.currentItem().data(256);cursor=r.technical.textCursor();cursor.setPosition(5);cursor.setPosition(20,QTextCursor.MoveMode.KeepAnchor);r.technical.setTextCursor(cursor);text=cursor.selectedText();self.back(root);self.assertIs(self.source(p),page);self.assertEqual(r.topic.currentData(),'free');self.assertEqual(r.tabs.currentIndex(),1);self.assertEqual(r.related.currentItem().data(256),selected);self.assertEqual(r.technical.textCursor().selectedText(),text)
 def test_other_stage_retains_source_chain_and_floor_change_invalidates_it(self):
  root,p=self.battle();page=self.source(p);r=page.panel;r.navigate({'kind':'shop','stage_id':None,'key':None});r.floor.setCurrentIndex(r.floor.findData(4));target={'kind':'battle','stage_id':'ro6_t_7','enemy_key':None,'reward_id':None};self.assertTrue(r.open_link(target));stage=self.host.pages.currentWidget();self.assertIs(stage.source_parent,page);self.assertEqual(stage.panel.stage_id,'ro6_t_7');self.back(page)
  with patch('rouge.player_cannot_links.make_reader',side_effect=AssertionError('reader should be retained')):self.assertTrue(r.open_link(target))
  self.assertIs(self.host.pages.currentWidget(),stage);self.back(page);r.floor.setCurrentIndex(r.floor.findData(3));self.host.navigate(self.host.cursor+1);self.assertNotIn(stage,self.host.history);self.assertIs(self.host.pages.currentWidget(),page)
 def test_parent_enemy_change_removes_reference_and_other_stage_descendants(self):
  root,p=self.battle();page=self.source(p);r=page.panel;r.navigate({'kind':'shop','stage_id':None,'key':None});r.floor.setCurrentIndex(r.floor.findData(4));r.open_link({'kind':'battle','stage_id':'ro6_t_7','enemy_key':None,'reward_id':None});stage=self.host.pages.currentWidget();self.back(root);key=next(e['key']for e in p.result['enemies']if e['key']!='0');p.enemy_choices.select_value(key,emit=True);self.host.navigate(self.host.cursor+1);self.assertNotIn(page,self.host.history);self.assertNotIn(stage,self.host.history);self.assertIs(self.host.pages.currentWidget(),root)
 def test_missing_reference_source_drops_old_page_and_preserves_parent(self):
  root,p=self.battle();page=self.source(p);self.back(root)
  with patch.object(model,'packet',return_value=None):self.host.navigate(self.host.cursor+1)
  self.assertIs(self.host.pages.currentWidget(),root);self.assertNotIn(page,self.host.history);self.assertIsNotNone(p.result)
 def test_identical_source_refresh_keeps_reader_without_rebuilding_controls(self):
  root,p=self.battle();page=self.source(p);r=page.panel
  with patch.object(r.entries,'clear',side_effect=AssertionError('no repeated entries build')),patch.object(r.related,'clear',side_effect=AssertionError('no repeated links build')),patch.object(r.technical,'setPlainText',side_effect=AssertionError('no repeated text build')):self.assertTrue(r.refresh_reference())
 def test_invalid_link_cannot_open_a_guessed_stage_or_enemy(self):
  root,p=self.battle();page=self.source(p);count=self.host.pages.count();self.assertFalse(page.panel.open_link({'kind':'battle','stage_id':'ro6_t_7','enemy_key':'0','reward_id':None}));self.assertEqual(self.host.pages.count(),count);self.assertIs(self.host.pages.currentWidget(),page)
 def test_player_copy_keeps_pickup_and_recovery_conditions_with_full_sources_in_details(self):
  root,p=self.battle();r=self.source(p).panel;r.navigate(model.target_for_reward('ro6_t_6','$.predefines.tokenInsts[0]'))
  text=r.player.toPlainText();self.assertIn('干员成功拾取后：增加2个免费商品栏位',text);self.assertIn('同一保险柜只计一次',text);self.assertIn('最多50%',text);self.assertIn('该干员本场无法再次部署',text)
  for phrase in ('不代表','不等于','不能把','不以','仍未知','不是实际已领取'):self.assertNotIn(phrase,text)
  self.assertIn('大保险柜的处理有待核对',text);self.assertIn('不是实际已领取',r.technical.toPlainText());self.assertIn('完整说明',r.technical.toPlainText())

class ReferenceThemeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def test_reference_inventory_and_light_pages_keep_distinct_scoped_palettes(self):
  owner=QWidget();owner.reference_window=host=ReferenceWindow(owner);self.addCleanup(owner.close);self.addCleanup(host.close);before=self.qt.palette()
  for name,theme,key,color in [('inventory','dark','playerPopover','#111213'),('reference','dark','mapReferenceWindow','#262528'),('notes','light','sceneNotesWindow','#f5f5f7')]:
   page=ToolPage(name,QPlainTextEdit('公开阅读文字'),owner,theme=theme,object_name=key);self.assertTrue(host.present(page));self.qt.processEvents();self.assertEqual(host.palette().color(QPalette.ColorRole.Window).name(),color);self.assertEqual(page.palette().color(QPalette.ColorRole.Window).name(),color);self.assertEqual(host.property('playerTheme'),theme)
  self.assertEqual(self.qt.palette(),before)
 def test_reference_icons_resolve_and_manifest_tracks_all_current_bytes(self):
  manifest=json.loads((DATA/'source.json').read_bytes());self.assertIn('reference',manifest['colors']);sheet,_=assets('reference');self.assertNotIn('@ICONS@',sheet)
  paths=set(re.findall(r'url\("([^"]+)"\)',sheet));self.assertGreater(len(paths),20)
  for path in paths:self.assertTrue(Path(path).is_file());self.assertFalse(QIcon(path).pixmap(18,18).isNull())
  baseline=json.loads((Path(__file__).parents[1]/'verification/sections/465-reference-theme/baseline-light-palette.json').read_bytes());self.assertEqual(json.loads((DATA/'palettes.json').read_bytes())['light'],baseline)
 def test_fixed_map_margins_follow_owned_page_palette_without_changing_markers(self):
  from rouge.current_map_position_view import CurrentTileGrid,CurrentOriginalCenters
  owner=QWidget();owner.reference_window=host=ReferenceWindow(owner);self.addCleanup(owner.close);self.addCleanup(host.close);content=QWidget();layout=QVBoxLayout(content);grid=CurrentTileGrid();original=CurrentOriginalCenters();layout.addWidget(grid);layout.addWidget(original);page=ToolPage('位置',content,owner,object_name='mapReferenceWindow');self.assertTrue(host.present(page));self.qt.processEvents()
  for widget in [grid,original]:self.assertEqual(widget.grab().toImage().pixelColor(1,1).name(),'#262528')
  self.assertIsNone(grid.selected);self.assertIsNone(original.point_center())

if __name__=='__main__':unittest.main()
