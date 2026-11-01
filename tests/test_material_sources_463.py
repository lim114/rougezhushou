import unittest
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QWidget,QPushButton
from PySide6.QtGui import QTextCursor
from rouge.player_reference_window import ReferenceWindow,ToolPage
from rouge.current_ritual_view import CurrentRitualPanel
from rouge.current_exchange_view import CurrentExchangePanel
from rouge import current_ritual_reference as model,current_exchange_reference as exchange

class MaterialSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.owner=QWidget();self.owner.reference_window=self.host=ReferenceWindow(self.owner)
  self.owner.present=self.host.present;self.addCleanup(self.owner.close);self.addCleanup(self.host.close)
 def ritual(self,sid='scene_ro6_end3_1',cid='choice_ro6_end3_3'):
  p=CurrentRitualPanel('ritual',sid,cid);page=ToolPage('调谐仪式',p,self.owner);page.panel=p;page.prepare=p.refresh_reference;page.finished.connect(p._close_material);page.finished.connect(p._close_battle);self.assertTrue(self.host.present(page));self.qt.processEvents();return page,p
 def select(self,p,cid):p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid))
 def test_three_material_sources_use_exact_target_and_one_native_host(self):
  root,p=self.ritual();handle=int(self.host.winId());self.assertTrue(p.open_material());event=self.host.pages.currentWidget();self.assertEqual((event.panel.event_id,event.panel.scene_id,event.panel.choice_id),('tears','scene_ro6_chimera2_enter','choice_ro6_chimera2_1'));self.assertIn('全部源石锭',event.panel.player.toPlainText());self.assertIs(event.source_parent,root)
  self.host.navigate(0);p.scene.setCurrentIndex(p.scene.findData('scene_ro6_end3_3'));self.select(p,'choice_ro6_end3_6');self.assertTrue(p.open_material());doc=self.host.pages.currentWidget();target=exchange.target_entry('choices','choice_ro6_sacrifice2_21');self.assertEqual(doc.panel.group_id,target['group_id']);self.assertEqual(doc.panel.tabs.currentIndex(),1);self.assertIn('焚毁',doc.panel.doc_player.toPlainText());self.assertIsNone(doc.panel.result['actual_reward_pool']);recipe=next(b for b in doc.header.findChildren(QPushButton)if b.text()=='查看复原条件');recipe.click();self.assertEqual(doc.panel.group_id,exchange.target_entry('choices','choice_ro6_sacrifice2_20')['group_id']);self.assertIn('随机消耗2件自然物',doc.panel.doc_player.toPlainText())
  self.host.navigate(0);p.scene.setCurrentIndex(p.scene.findData('scene_ro6_end3_4'));self.select(p,'choice_ro6_end3_9');self.assertTrue(p.open_material());stage=self.host.pages.currentWidget();self.assertEqual(stage.panel.stage_id,'ro6_t_12');self.assertIs(stage.source_parent,root);self.assertEqual(int(self.host.winId()),handle);self.assertIsNone(p.material_dialog);self.assertFalse(any(w.isVisible()and w not in(self.owner,self.host)for w in self.qt.topLevelWidgets()))
 def test_event_source_reopen_keeps_exact_scene_choice_and_reading(self):
  root,p=self.ritual();p.open_material();page=self.host.pages.currentWidget();reader=page.panel.player;cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);selected=cursor.selectedText();self.host.navigate(0);self.assertTrue(p.open_material());self.assertIs(self.host.pages.currentWidget(),page);self.assertEqual(reader.textCursor().selectedText(),selected);self.assertEqual(page.panel.choice_id,'choice_ro6_chimera2_1')
 def test_exchange_reopen_keeps_search_tabs_and_selected_text(self):
  root,p=self.ritual('scene_ro6_end3_3','choice_ro6_end3_6');p.open_material();page=self.host.pages.currentWidget();r=page.panel;r.search.setText('生命');r.tabs.setCurrentIndex(1);cursor=r.doc_player.textCursor();cursor.setPosition(2);cursor.setPosition(10,QTextCursor.MoveMode.KeepAnchor);r.doc_player.setTextCursor(cursor);selected=cursor.selectedText();self.host.navigate(0);self.assertTrue(p.open_material());self.assertIs(self.host.pages.currentWidget(),page);self.assertEqual(r.search.text(),'生命');self.assertEqual(r.doc_player.textCursor().selectedText(),selected);self.assertEqual(r.tabs.currentIndex(),1)
 def test_changed_parent_choice_removes_material_page_on_forward(self):
  root,p=self.ritual();p.open_material();page=self.host.pages.currentWidget();self.host.navigate(0);self.select(p,'choice_ro6_end3_4');self.host.navigate(1);self.assertIs(self.host.pages.currentWidget(),root);self.assertNotIn(page,self.host.history);self.assertFalse(self.host.forward.isEnabled());self.assertFalse(p.open_material())
 def test_changed_parent_source_clears_old_source_chain(self):
  root,p=self.ritual();p.open_material();page=self.host.pages.currentWidget();self.host.navigate(0);fresh=deepcopy(p.result);fresh['source_identity']=('isolated-source-change',)
  with patch.object(p,'_fresh_reference',return_value=fresh):self.host.navigate(1)
  self.assertIs(self.host.pages.currentWidget(),root);self.assertNotIn(page,self.host.history);self.assertIsNone(p.choice_id)
 def test_missing_exchange_destination_discards_old_material_reader(self):
  root,p=self.ritual('scene_ro6_end3_3','choice_ro6_end3_6');p.open_material();page=self.host.pages.currentWidget();self.host.navigate(0)
  with patch('rouge.current_exchange_reference.packet',return_value=None):self.host.navigate(1)
  self.assertIs(self.host.pages.currentWidget(),root);self.assertNotIn(page,self.host.history);self.assertIsNotNone(p.result);self.assertFalse(p.material_button.isEnabled())
 def test_same_battle_ancestor_is_reused_for_material_source(self):
  from rouge.player_map_reader import make_reader
  stage=make_reader('battle',{'id':'ro6_t_12','title':'材料来源作战'},self.owner,historical=True,page_owner=self.owner);self.assertTrue(self.host.present(stage))
  p=CurrentRitualPanel('ritual','scene_ro6_end3_4','choice_ro6_end3_9')
  def create(owner):
   page=ToolPage('调谐仪式',p,owner);page.panel=p;return page
  self.assertTrue(self.host.open_reference(stage.panel,('ritual-test',),lambda:'fixture',create));size=self.host.pages.count();self.assertTrue(p.open_material());self.assertIs(self.host.pages.currentWidget(),stage);self.assertEqual(self.host.pages.count(),size)
 def test_exchange_copy_keeps_effect_amount_and_full_original_notes(self):
  p=CurrentExchangePanel(exchange.target_entry('relics','rogue_6_relic_final_8'));self.addCleanup(p.close);raw=exchange.item_text(p.result,p.item_id);self.assertIn('不可交出',p.item_player.toPlainText());self.assertNotIn('不能说明能否换到',p.item_player.toPlainText());self.assertIn('不能说明能否换到',p.item_technical.toPlainText());self.assertIn('【作用说明】',p.item_player.toPlainText());self.assertIn('目录共284件',p.count.text())
  target=exchange.target_entry('choices','choice_ro6_sacrifice2_23');p._select(p.groups,target['group_id']);self.assertIn('1件零件',p.doc_player.toPlainText());self.assertIn('数量来自选项原文',p.doc_technical.toPlainText());self.assertNotIn('尚未核验完整',p.doc_player.toPlainText());self.assertIsNone(p.result['actual_reward_pool']);self.assertFalse(p.result['run_updated'])

if __name__=='__main__':unittest.main()
