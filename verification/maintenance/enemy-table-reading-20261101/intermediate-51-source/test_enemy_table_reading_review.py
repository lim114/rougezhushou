"""Full mechanism table is actually readable, not merely stored in a tooltip."""
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication,QHeaderView,QAbstractItemView
from rouge.enemy_overview import overview_cells
from rouge.current_battle_view import CurrentBattlePanel

class EnemyTableReadingReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self):
  p=CurrentBattlePanel('ro6_b_5');p.resize(920,720);p.show();p.tabs.setCurrentIndex(1);self.qt.processEvents();self.addCleanup(p.close);return p
 def rows(self,t):return[t.topLevelItem(i).child(j)for i in range(t.topLevelItemCount())for j in range(t.topLevelItem(i).childCount())]
 def long_row(self,p):return max(self.rows(p.enemy_overview.tree),key=lambda i:len(i.text(6)))
 def width(self,t,w):t.header().setSectionResizeMode(6,QHeaderView.ResizeMode.Interactive);t.header().setStretchLastSection(False);t.setColumnWidth(6,w);t.doItemsLayout();self.qt.processEvents()
 def test_all_original_mechanism_paragraphs_are_in_exact_table_cells_and_tooltips(self):
  p=self.panel();lookup={e['key']:e for e in p.result['enemies']}
  for item in self.rows(p.enemy_overview.tree):
   e=lookup[item.data(0,Qt.ItemDataRole.UserRole)];text='\n'.join(e['abilities'])or e['description']or'尚无独立说明，请查看完整资料。';self.assertEqual(item.text(6),text);self.assertEqual(item.toolTip(6),'\n'.join(e['abilities'])or e['description']);self.assertEqual([item.text(i)for i in range(7)],overview_cells(e))
 def test_native_rows_grow_and_shrink_with_actual_mechanism_column_width(self):
  p=self.panel();t=p.enemy_overview.tree;item=self.long_row(p);idx=t.indexFromItem(item,6);heights=[]
  for width in(170,320,600):self.width(t,width);self.assertEqual(t.columnWidth(6),width);heights.append(t.visualRect(idx).height())
  self.assertGreater(heights[0],heights[1]);self.assertGreater(heights[1],heights[2]);self.assertGreater(heights[0],180);self.assertEqual(t.textElideMode(),Qt.TextElideMode.ElideNone)
 def test_actual_window_resize_reflows_mechanism_without_changing_exact_data_or_icons(self):
  p=self.panel();t=p.enemy_overview.tree;item=self.long_row(p);idx=t.indexFromItem(item,6);text=item.text(6);icons=[i.icon(0).cacheKey()for i in self.rows(t)];heights=[]
  for width in(760,1000,1250):p.resize(width,720);self.qt.processEvents();t.doItemsLayout();heights.append(t.visualRect(idx).height());self.assertEqual(item.text(6),text);self.assertEqual(icons,[i.icon(0).cacheKey()for i in self.rows(t)])
  self.assertGreater(heights[0],heights[-1])
 def test_larger_current_font_reflows_real_rows(self):
  p=self.panel();t=p.enemy_overview.tree;item=self.long_row(p);self.width(t,320);idx=t.indexFromItem(item,6);before=t.visualRect(idx).height();font=QFont(t.font());font.setPointSizeF(font.pointSizeF()+5);t.setFont(font);self.qt.processEvents();t.doItemsLayout();self.assertGreater(t.visualRect(idx).height(),before)
 def test_taller_than_viewport_row_can_be_read_in_pixel_steps(self):
  p=self.panel();t=p.enemy_overview.tree;item=self.long_row(p);item.setText(6,'\n'.join('完整说明第'+str(i)+'行'for i in range(80)));self.width(t,200);idx=t.indexFromItem(item,6);t.scrollTo(idx,QAbstractItemView.ScrollHint.PositionAtTop);self.qt.processEvents();top=t.visualRect(idx).top();self.assertGreater(t.visualRect(idx).height(),t.viewport().height());before=t.verticalScrollBar().value();t.verticalScrollBar().setValue(before+23);self.qt.processEvents();self.assertEqual(t.visualRect(idx).top(),top-23);self.assertEqual(t.verticalScrollMode(),QAbstractItemView.ScrollMode.ScrollPerPixel);self.assertIn('第79行',item.text(6))
 def test_same_source_retains_both_scroll_offsets_widths_and_fold_state(self):
  p=self.panel();t=p.enemy_overview.tree;self.width(t,600);t.verticalScrollBar().setValue(30);t.horizontalScrollBar().setValue(40);self.qt.processEvents();before=(t.verticalScrollBar().value(),t.horizontalScrollBar().value(),t.columnWidth(6));self.assertGreater(before[0],0);self.assertGreater(before[1],0);self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertEqual((t.verticalScrollBar().value(),t.horizontalScrollBar().value(),t.columnWidth(6)),before)
 def test_new_scope_does_not_borrow_previous_offsets_or_folds(self):
  p=self.panel();o=p.enemy_overview;t=o.tree;self.width(t,600);t.verticalScrollBar().setValue(25);t.horizontalScrollBar().setValue(30);t.topLevelItem(0).setExpanded(False);o.set_rows(p.result['enemies'],p.enemy_choices.entries(),('new-public-stage','new-public-source'));self.qt.processEvents();self.assertEqual((t.verticalScrollBar().value(),t.horizontalScrollBar().value()),(0,0));self.assertTrue(t.topLevelItem(0).isExpanded())
 def test_long_free_text_is_not_html_or_silently_elided(self):
  value='<b>字面名称</b> & 标记\n'+'甲'*500+'结尾';e={'name':'公开测试','abilities':[value],'description':'备用','declared_traits':None};self.assertEqual(overview_cells(e)[6],value);e['abilities']=[];self.assertEqual(overview_cells(e)[6],'备用')
 def test_qualified_numbers_and_complete_total_unknown_survive_same_current_environment(self):
  p=CurrentBattlePanel('ro6_n_1_1');self.addCleanup(p.close);p.set_context({'difficulty':{'value':15},'zone':{'id':'zone_1'}});lookup={e['key']:e for e in p.result['enemies']}
  for item in self.rows(p.enemy_overview.tree):
   key=item.data(0,Qt.ItemDataRole.UserRole);self.assertEqual([item.text(i)for i in range(7)],overview_cells(lookup[key],p.enemy_forecasts[key]));self.assertIsNone(p.enemy_forecasts[key]['complete_current_total']);self.assertIn('完整本局总量未知',item.toolTip(1))
  self.assertIn('不用白值',p.enemy_overview.notice.text())

if __name__=='__main__':unittest.main()
