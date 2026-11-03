"""Actual native list layout and exact source selection, never a battle clock."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QStyleOptionViewItem
from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_battle_reference as model


class SpawnReadingReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self,sid='ro6_n_2_6'):
  p=CurrentBattlePanel(sid);p.resize(920,720);p.show();p.tabs.setCurrentIndex(2);self.qt.processEvents();self.addCleanup(p.close);return p
 def test_all_labels_keys_and_exact_single_candidate_images_match_original_sources(self):
  p=self.panel();self.assertIsNone(p.actions.currentItem());self.assertEqual(p.actions.count(),len(p.result['actions']))
  for i,a in enumerate(p.result['actions']):
   item=p.actions.item(i);self.assertEqual(item.text(),model.action_label(a));self.assertEqual(item.data(Qt.ItemDataRole.UserRole),a['key'])
   candidates=a['enemy_candidates'];expected=len(candidates)==1 and model.picture_for_enemy(candidates[0])is not None
   self.assertEqual(not item.icon().isNull(),expected,(a['key'],len(candidates)))
 def test_multiple_candidates_and_non_enemy_never_borrow_an_arbitrary_picture(self):
  p=self.panel();result=deepcopy(p.result);single=next(a for a in result['actions']if len(a['enemy_candidates'])==1);multiple=deepcopy(single);multiple['key']='public-test-multiple';multiple['enemy_candidates']=result['enemies'][:2];self.assertEqual(len(multiple['enemy_candidates']),2);empty=deepcopy(single);empty['key']='public-test-no-enemy';empty['enemy_candidates']=[];result['actions']=[multiple,empty];p.result=result;p._actions_changed()
  self.assertTrue(p.actions.item(0).icon().isNull());self.assertIn('多个引用候选',p.actions.item(0).toolTip());self.assertTrue(p.actions.item(1).icon().isNull());self.assertIsNone(p.action_key)
 def test_search_reuses_verified_images_and_does_not_remove_unfiltered_action_portraits(self):
  p=self.panel();icons={k:v.cacheKey()for k,v in p._enemy_icons.items()}
  with patch.object(model,'picture_for_enemy',side_effect=AssertionError('search must not reread each picture')):p.enemy_search.setText('不存在的公开测试词');p._actions_changed()
  self.assertEqual(icons,{k:v.cacheKey()for k,v in p._enemy_icons.items()});self.assertEqual(p.enemy_grid.count(),0);self.assertTrue(any(not p.actions.item(i).icon().isNull()for i in range(p.actions.count())))
 def test_refresh_revalidates_pictures_and_source_loss_clears_icons_and_rows(self):
  p=self.panel()
  with patch.object(model,'picture_for_enemy',return_value=None):p.refresh_reference();self.assertTrue(all(p.actions.item(i).icon().isNull()for i in range(p.actions.count())))
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertEqual(p._enemy_icons,{});self.assertEqual(p.actions.count(),0);self.assertFalse(p.action_position_button.isEnabled())
  self.assertTrue(p.refresh_reference());self.assertIsNone(p.action_key);self.assertTrue(any(not p.actions.item(i).icon().isNull()for i in range(p.actions.count())))
 def test_actual_click_and_keyboard_select_exact_original_full_text(self):
  p=self.panel();p.actions.scrollToItem(p.actions.item(1));self.qt.processEvents();QTest.mouseClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=p.actions.visualItemRect(p.actions.item(1)).center());self.qt.processEvents();self.assertEqual(p.action_key,p.result['actions'][1]['key']);self.assertEqual(p.action_player.toPlainText(),model.action_text(p.result['actions'][1]));QTest.keyClick(p.actions,Qt.Key.Key_Down);self.qt.processEvents();self.assertEqual(p.action_key,p.result['actions'][2]['key']);self.assertIn('准确时刻：未知',p.action_player.toPlainText())
 def test_continuous_width_changes_keep_selected_text_and_per_direction_manual_sizes(self):
  p=self.panel();p.actions.setCurrentRow(1);p.action_split.setSizes([300,540]);self.qt.processEvents();wide=p.action_split.sizes();key=p.action_key;cursor=p.action_player.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);p.action_player.setTextCursor(cursor)
  p.resize(640,650);self.qt.processEvents();self.assertEqual(p.action_split.orientation(),Qt.Orientation.Vertical);self.assertTrue(all(x>0 for x in p.action_split.sizes()));p.action_split.setSizes([120,300]);self.qt.processEvents();narrow=p.action_split.sizes()
  p.resize(920,720);self.qt.processEvents();self.assertEqual(p.action_split.orientation(),Qt.Orientation.Horizontal);self.assertEqual(p.action_split.sizes(),wide)
  p.resize(640,650);self.qt.processEvents();self.assertEqual(p.action_split.sizes(),narrow);self.assertEqual(p.action_key,key);self.assertEqual((p.action_player.textCursor().anchor(),p.action_player.textCursor().position()),(3,15));self.assertEqual((p.width(),p.height()),(640,650))
 def test_long_chinese_entry_reflows_without_elision_and_refresh_keeps_list_reading(self):
  p=self.panel();p.resize(640,650);self.qt.processEvents();item=p.actions.item(0);item.setText('长条目测试：'+'同名不同引用保留为独立候选，不能相加。'*20);p.actions.doItemsLayout();self.qt.processEvents();rect=p.actions.visualItemRect(item);self.assertGreater(rect.height(),p.actions.fontMetrics().height()*5);self.assertEqual(p.actions.textElideMode(),Qt.TextElideMode.ElideNone)
  p.refresh_reference();p.tabs.setCurrentIndex(2);self.qt.processEvents();p.actions.setCurrentRow(p.actions.count()-1);p.actions.verticalScrollBar().setValue(p.actions.verticalScrollBar().maximum()//2);self.qt.processEvents();old=p.actions.verticalScrollBar().value();key=p.action_key;self.assertGreater(old,0);p.refresh_reference();self.qt.processEvents();self.assertEqual(p.actions.verticalScrollBar().value(),old);self.assertEqual(p.action_key,key)

if __name__=='__main__':unittest.main()
