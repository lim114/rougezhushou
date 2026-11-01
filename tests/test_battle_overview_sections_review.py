"""One native model powers both the quick strip and exact enemy reader."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_battle_reference as model
from rouge.collapsible_section import QCollapsible

class BattleOverviewSectionsReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self):
  p=CurrentBattlePanel('ro6_n_2_6');p.resize(900,720);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
 def test_public_collapsible_sections_preserve_existing_four_categories_and_full_summary(self):
  p=self.panel();self.assertEqual([p.tabs.tabText(i)for i in range(p.tabs.count())],['地图与关卡','敌人和机制','出怪与条件','奖励与条件']);self.assertIs(p.tabs.widget(0),p.overview_scroll)
  for section in (p.map_section,p.quick_section,p.map_details):self.assertIsInstance(section,QCollapsible)
  self.assertTrue(p.map_section.isExpanded());self.assertTrue(p.quick_section.isExpanded());self.assertFalse(p.map_details.isExpanded());self.assertFalse(p.summary.isVisible());self.assertEqual(p.summary.toPlainText(),model.summary_text(p.result));self.assertFalse(p.map_image.original.isNull())
 def test_quick_view_shares_actual_items_selection_and_icons_without_another_image_read(self):
  p=self.panel();self.assertIs(p.quick_enemies.model(),p.enemy_grid.model());self.assertIs(p.quick_enemies.selectionModel(),p.enemy_grid.selectionModel());self.assertIsNot(p.quick_enemies.itemDelegate(),p.enemy_grid.itemDelegate());self.assertEqual(p.quick_enemies.model().rowCount(),p.enemy_grid.count())
  for i in range(p.enemy_grid.count()):
   index=p.quick_enemies.model().index(i,0);item=p.enemy_grid.item(i);self.assertEqual(index.data(Qt.ItemDataRole.UserRole),item.data(Qt.ItemDataRole.UserRole));self.assertEqual(index.data(Qt.ItemDataRole.DecorationRole).cacheKey(),item.icon().cacheKey())
  with patch.object(model,'picture_for_enemy',wraps=model.picture_for_enemy)as pictures:p._sync_enemy_grid();self.assertEqual(pictures.call_count,0)
 def test_actual_quick_portrait_click_opens_the_exact_original_enemy_detail(self):
  p=self.panel();view=p.quick_enemies;p.overview_scroll.ensureWidgetVisible(view);self.qt.processEvents();index=view.model().index(1,0);key=index.data(Qt.ItemDataRole.UserRole);QTest.mouseClick(view.viewport(),Qt.MouseButton.LeftButton,pos=view.visualRect(index).center());self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),1);self.assertEqual(p.enemy_key,key);self.assertEqual(p.enemy_combo.currentData(),key);self.assertIn(p.enemy_grid.item(1).text(),p.enemy_player.toPlainText())
 def test_native_keyboard_selection_and_activation_have_the_same_exact_target(self):
  p=self.panel();view=p.quick_enemies;p.overview_scroll.ensureWidgetVisible(view);view.setFocus();QTest.keyClick(view,Qt.Key.Key_Home);QTest.keyClick(view,Qt.Key.Key_Right);self.qt.processEvents();key=view.currentIndex().data(Qt.ItemDataRole.UserRole);QTest.keyClick(view,Qt.Key.Key_Return);self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),1);self.assertEqual(p.enemy_key,key);self.assertEqual(p.enemy_combo.currentData(),key)
 def test_filtered_quick_rows_are_qualified_and_empty_search_never_keeps_stale_portraits(self):
  p=self.panel();total=len(p.result['enemies']);p.enemy_search.setText('公开测试没有这样的敌人');self.qt.processEvents();self.assertEqual(p.quick_enemies.model().rowCount(),0);self.assertIn(f'0 / {total}',p.quick_notice.text());self.assertIn('不是实际出怪数量',p.quick_notice.text());p.enemy_search.clear();self.qt.processEvents();self.assertEqual(p.quick_enemies.model().rowCount(),total)
 def test_refresh_keeps_real_folds_horizontal_offset_and_original_text_selection(self):
  p=self.panel();p.map_section.collapse(animate=False);p.map_details.expand(animate=False);self.qt.processEvents();self.assertGreater(p.quick_enemies.horizontalScrollBar().maximum(),30);p.quick_enemies.horizontalScrollBar().setValue(30);cursor=p.summary.textCursor();cursor.setPosition(3);cursor.setPosition(12,cursor.MoveMode.KeepAnchor);p.summary.setTextCursor(cursor);before=(p.map_section.isExpanded(),p.quick_section.isExpanded(),p.map_details.isExpanded(),p.quick_enemies.horizontalScrollBar().value(),cursor.selectedText())
  self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertEqual((p.map_section.isExpanded(),p.quick_section.isExpanded(),p.map_details.isExpanded(),p.quick_enemies.horizontalScrollBar().value(),p.summary.textCursor().selectedText()),before)
 def test_loss_and_recovery_clear_same_shared_model_then_reset_only_invalid_view_state(self):
  p=self.panel();p.map_details.expand(animate=False);p.map_section.collapse(animate=False)
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertEqual(p.quick_enemies.model().rowCount(),0);self.assertIn('暂不可用',p.quick_notice.text());self.assertEqual(p.summary.toPlainText(),'');self.assertTrue(p.map_image.original.isNull())
  self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertTrue(p.map_section.isExpanded());self.assertTrue(p.quick_section.isExpanded());self.assertFalse(p.map_details.isExpanded());self.assertEqual(p.quick_enemies.horizontalScrollBar().value(),0);self.assertIsNone(p.enemy_combo.currentData())
 def test_open_details_and_resize_leave_all_original_controls_reachable_by_scroll(self):
  p=self.panel();p.map_details.expand(animate=False)
  for width in (480,640,900,1200):
   p.resize(width,620);self.qt.processEvents();p.overview_scroll.ensureWidgetVisible(p.summary);self.qt.processEvents();self.assertTrue(p.summary.isVisible());self.assertGreaterEqual(p.summary.height(),160);self.assertEqual(p.overview_scroll.horizontalScrollBar().maximum(),0);self.assertTrue(p.overview_scroll.widget().rect().contains(p.summary.mapTo(p.overview_scroll.widget(),p.summary.rect().bottomRight())))
 def test_same_model_context_update_keeps_quick_selection_and_does_not_claim_new_spawn_counts(self):
  p=self.panel();key=p.enemy_grid.item(1).data(Qt.ItemDataRole.UserRole);p.enemy_choices.select_value(key);self.qt.processEvents();p.set_context({'difficulty':{'value':15},'zone':{'id':'zone_2'}});self.qt.processEvents();self.assertEqual(p.enemy_combo.currentData(),key);self.assertEqual(p.quick_enemies.currentIndex().data(Qt.ItemDataRole.UserRole),key);self.assertIn('不是实际出怪数量',p.quick_notice.text())
 def test_shared_battle_pages_render_the_same_video_neutral_background(self):
  from PySide6.QtWidgets import QWidget
  from rouge.player_map_reader import make_reader
  owner=QWidget();self.addCleanup(owner.close);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开测试'},owner);d.show();self.addCleanup(d.close);self.qt.processEvents();p=d.panel
  for i in range(p.tabs.count()):
   p.tabs.setCurrentIndex(i);self.qt.processEvents();image=p.tabs.currentWidget().grab().toImage();self.assertEqual(image.pixelColor(image.width()-3,image.height()-3).name(),'#262528')
if __name__=='__main__':unittest.main()
