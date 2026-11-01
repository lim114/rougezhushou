"""Native map and enemy reference reading, using one Qt model."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_battle_reference as model

class BattleDocumentReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self):
  p=CurrentBattlePanel('ro6_n_2_6');p.resize(920,720);p.show();self.qt.processEvents();self.addCleanup(p.close);return p
 def index(self,p):return p.quick_table.model().index(0,0,p.quick_table.model().index(0,0))
 def test_map_and_full_mechanism_view_share_exact_existing_model_without_duplicate_image_reads(self):
  p=self.panel();v=p.quick_table;t=p.enemy_overview.tree;self.assertTrue(v.isVisible());self.assertTrue(p.map_image.isVisible());self.assertIs(v.model(),t.model());self.assertIsNot(v.itemDelegate(),t.itemDelegate());self.assertIsNot(v.selectionModel(),t.selectionModel());self.assertEqual(v.model().columnCount(),7);self.assertEqual(p.quick_table_notice.text(),p.enemy_overview.notice.text());self.assertIsNone(p.enemy_key)
  with patch.object(model,'picture_for_enemy',side_effect=AssertionError('No extra picture lookup for second view')):p._sync_enemy_grid()
  for i in range(t.topLevelItemCount()):
   root=v.model().index(i,0);self.assertTrue(v.isFirstColumnSpanned(i,root.parent()))
   for j in range(v.model().rowCount(root)):
    item=t.topLevelItem(i).child(j);index=v.model().index(j,0,root);self.assertEqual(index.data(Qt.ItemDataRole.UserRole),item.data(0,Qt.ItemDataRole.UserRole));self.assertEqual(index.data(Qt.ItemDataRole.DecorationRole).cacheKey(),item.icon(0).cacheKey())
    for c in range(7):self.assertEqual(v.model().index(j,c,root).data(),item.text(c))
 def test_actual_click_enters_exact_existing_full_reader_while_group_click_stays_on_map(self):
  p=self.panel();v=p.quick_table;p.overview_scroll.ensureWidgetVisible(v);self.qt.processEvents();root=v.model().index(0,0);v.scrollTo(root);self.qt.processEvents();QTest.mouseClick(v.viewport(),Qt.MouseButton.LeftButton,pos=v.visualRect(root).center());self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),0);index=self.index(p);v.expand(root);v.scrollTo(index);self.qt.processEvents();QTest.mouseClick(v.viewport(),Qt.MouseButton.LeftButton,pos=v.visualRect(index).center());self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),1);key=index.data(Qt.ItemDataRole.UserRole);self.assertEqual(p.enemy_key,key);enemy=next(e for e in p.result['enemies']if e['key']==key);self.assertIn(enemy['name'],p.enemy_player.toPlainText())
 def test_keyboard_can_read_rows_without_navigation_until_enter(self):
  p=self.panel();v=p.quick_table;p.overview_scroll.ensureWidgetVisible(v);self.qt.processEvents();index=self.index(p);v.setCurrentIndex(index);v.setFocus();QTest.keyClick(v,Qt.Key.Key_Down);self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),0);key=v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole);self.assertIsNotNone(key);QTest.keyClick(v,Qt.Key.Key_Return);self.qt.processEvents();self.assertEqual(p.tabs.currentIndex(),1);self.assertEqual(p.enemy_key,key)
 def test_same_source_keeps_independent_fold_width_and_both_scroll_positions(self):
  p=self.panel();v=p.quick_table;p.overview_scroll.ensureWidgetVisible(v);self.qt.processEvents();v.setColumnWidth(6,500);v.doItemsLayout();v.setCurrentIndex(self.index(p));v.horizontalScrollBar().setValue(25);v.verticalScrollBar().setValue(20);self.qt.processEvents();root=v.model().index(0,0);v.setExpanded(root,False);self.qt.processEvents();before=(v.columnWidth(6),v.horizontalScrollBar().value(),v.verticalScrollBar().value(),v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole));self.assertTrue(p.enemy_overview.tree.topLevelItem(0).isExpanded());p.refresh_reference();self.qt.processEvents();self.assertFalse(v.isExpanded(v.model().index(0,0)));self.assertEqual((v.columnWidth(6),v.horizontalScrollBar().value(),v.verticalScrollBar().value(),v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)),before);self.assertTrue(p.enemy_overview.tree.topLevelItem(0).isExpanded())
 def test_search_and_source_loss_update_both_views_and_clear_old_selection(self):
  p=self.panel();v=p.quick_table;v.setCurrentIndex(self.index(p));p.enemy_search.setText('公开测试没有匹配对象');self.qt.processEvents();self.assertEqual(v.model().rowCount(),0);self.assertFalse(v.currentIndex().isValid());p.enemy_search.clear();self.qt.processEvents();self.assertGreater(v.model().rowCount(),0)
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertEqual(v.model().rowCount(),0);self.assertFalse(v.currentIndex().isValid())
  self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertIsNone(p.enemy_key);self.assertFalse(v.currentIndex().isValid());self.assertTrue(v.isExpanded(v.model().index(0,0)))
 def test_wide_narrow_and_return_keep_window_dimensions_and_full_mechanism_text(self):
  from rouge.player_map_reader import make_reader
  owner=QWidget();self.addCleanup(owner.close);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},owner);self.addCleanup(d.close);d.show();p=d.panel
  for w,h in((920,720),(640,650),(1250,720),(640,650)):
   d.resize(w,h);QTest.qWait(80);self.qt.processEvents();self.assertEqual((d.width(),d.height()),(w,h));self.assertEqual(p.overview_scroll.horizontalScrollBar().maximum(),0);p.overview_scroll.ensureWidgetVisible(p.quick_table);self.qt.processEvents();self.assertTrue(p.quick_table.isVisible());index=self.index(p);self.assertEqual(index.siblingAtColumn(6).data(),p.enemy_overview.tree.topLevelItem(0).child(0).text(6))

 def test_identical_intro_and_ability_are_read_once_without_losing_other_mechanisms(self):
  p=self.panel();e=next(e for e in p.result['enemies']if e['description']and e['description']in e['abilities']);self.assertEqual(e['abilities'].count(e['description']),1);text=model.enemy_text(e);part=text.split('【介绍与机制】',1)[1].split('【适用提醒】',1)[0];self.assertEqual(part.count(e['description']),1)
  for ability in e['abilities']:self.assertIn(ability,part)
 def test_distinct_intro_and_empty_mechanism_states_preserve_source_meaning(self):
  p=self.panel();e=dict(p.result['enemies'][0]);e.update(description='独立介绍',abilities=['独立能力']);text=model.enemy_text(e);self.assertIn('独立介绍\n独立能力',text);e.update(description='',abilities=[]);self.assertIn('未取得独立介绍或图鉴能力',model.enemy_text(e));self.assertNotIn('独立能力',model.enemy_text(e))

if __name__=='__main__':unittest.main()
