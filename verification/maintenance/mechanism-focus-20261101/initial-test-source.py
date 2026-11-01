"""Unknown values do not crowd out usable mechanisms in the homepage table."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_battle_reference as model

class MechanismFocusReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self):
  p=CurrentBattlePanel('ro6_n_2_6');p.resize(920,720);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
 def test_default_home_has_three_useful_columns_but_keeps_all_original_data_and_full_reader(self):
  p=self.panel();v=p.quick_table;t=p.enemy_overview.tree;self.assertEqual([i for i in range(7)if not v.isColumnHidden(i)],[0,5,6]);self.assertEqual([i for i in range(7)if not t.isColumnHidden(i)],list(range(7)));self.assertIs(v.model(),t.model());self.assertIn('尚未核验',p.quick_table_notice.text());self.assertIn('不用白值',p.quick_table_notice.text());self.assertEqual(p.quick_table_notice.text(),p.enemy_overview.notice.text());self.assertEqual(p.result,model.stage_reference(p.stage_id))
  index=v.model().index(0,0,v.model().index(0,0))
  for c in range(1,5):self.assertEqual(index.siblingAtColumn(c).data(),'未知')
 def test_zero_is_available_and_each_column_requires_a_visible_candidate_value(self):
  p=self.panel();key=p.result['enemies'][0]['key'];p.enemy_forecasts={key:{'environment_component':{'atk':0},'conditions_label':'公开布局夹具'}};p._sync_enemy_grid();self.qt.processEvents();self.assertEqual([i for i in range(7)if not p.quick_table.isColumnHidden(i)],[0,2,5,6]);self.assertIn('环境分项',p.quick_table_notice.text());self.assertIn('完整本局总量仍未知',p.quick_table_notice.text());item=next(p.enemy_overview.tree.topLevelItem(i).child(j)for i in range(p.enemy_overview.tree.topLevelItemCount())for j in range(p.enemy_overview.tree.topLevelItem(i).childCount())if p.enemy_overview.tree.topLevelItem(i).child(j).data(0,Qt.ItemDataRole.UserRole)==key);self.assertEqual(item.text(2),'0')
  p.enemy_forecasts[key]['environment_component'].update({'maxHp':100,'def':None,'magicResistance':0});p._sync_enemy_grid();self.assertEqual([i for i in range(7)if not p.quick_table.isColumnHidden(i)],[0,1,2,4,5,6])
 def test_filtering_out_only_verified_reference_hides_empty_columns_without_other_values(self):
  p=self.panel();key=p.result['enemies'][0]['key'];p.enemy_forecasts={key:{'environment_component':{'atk':12},'conditions_label':'公开布局夹具'}};p._sync_enemy_grid();self.assertFalse(p.quick_table.isColumnHidden(2));other=next(e for e in p.result['enemies']if e['key']!=key and e['name']!=p.result['enemies'][0]['name']);p.enemy_search.setText(other['name']);self.qt.processEvents();self.assertTrue(p.quick_table.isColumnHidden(2));p.enemy_search.clear();self.qt.processEvents();self.assertFalse(p.quick_table.isColumnHidden(2))
 def test_refresh_keeps_original_choice_mechanism_width_fold_and_exact_sources(self):
  p=self.panel();v=p.quick_table;root=v.model().index(0,0);index=v.model().index(0,0,root);key=index.data(Qt.ItemDataRole.UserRole);v.setCurrentIndex(index);v.setColumnWidth(6,500);v.setExpanded(root,False);self.qt.processEvents();before=deepcopy(p.result);p.refresh_reference();self.qt.processEvents();self.assertEqual(p.result,before);self.assertEqual(v.columnWidth(6),500);self.assertFalse(v.isExpanded(v.model().index(0,0)));self.assertEqual(v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole),key);self.assertEqual([i for i in range(7)if not v.isColumnHidden(i)],[0,5,6])
 def test_known_and_unknown_transitions_do_not_retain_old_visible_numeric_columns(self):
  p=self.panel();key=p.result['enemies'][0]['key'];p.enemy_forecasts={key:{'environment_component':{'maxHp':100,'atk':12,'def':0,'magicResistance':0},'conditions_label':'公开布局夹具'}};p._sync_enemy_grid();self.assertTrue(all(not p.quick_table.isColumnHidden(i)for i in range(7)));p.enemy_forecasts={};p._sync_enemy_grid();self.assertTrue(all(p.quick_table.isColumnHidden(i)for i in range(1,5)));self.assertIn('尚未核验',p.quick_table_notice.text())
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertEqual(p.quick_table.model().rowCount(),0)
  self.assertTrue(p.refresh_reference());self.assertIsNone(p.enemy_key);self.assertTrue(all(p.quick_table.isColumnHidden(i)for i in range(1,5)))
 def test_actual_default_mechanism_column_is_readable_at_narrow_and_wide_sizes(self):
  from rouge.player_map_reader import make_reader
  owner=QWidget();self.addCleanup(owner.close);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开资料'},owner);d.show();self.addCleanup(d.close);p=d.panel
  for w,h in((640,650),(920,720),(1250,720),(640,650)):
   d.resize(w,h);QTest.qWait(80);self.qt.processEvents();p.overview_scroll.ensureWidgetVisible(p.quick_table);self.qt.processEvents();self.assertEqual((d.width(),d.height()),(w,h));self.assertEqual(p.overview_scroll.horizontalScrollBar().maximum(),0);self.assertGreaterEqual(p.quick_table.columnWidth(6),240)

if __name__=='__main__':unittest.main()
