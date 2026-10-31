"""Mechanism overview is a projection of existing exact references and icons."""
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge.current_battle_view import CurrentBattlePanel
from rouge.enemy_overview import overview_cells
from rouge import current_battle_reference as model

ROOT=Path(__file__).resolve().parents[1]

class EnemyOverviewReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self,sid='ro6_n_2_6'):
  p=CurrentBattlePanel(sid);p.resize(860,720);p.show();p.tabs.setCurrentIndex(1);self.qt.processEvents();self.addCleanup(p.close);return p
 def rows(self,p):
  tree=p.enemy_overview.tree
  return [tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())]
 def test_overview_shows_all_exact_references_and_reuses_verified_icons_without_base_stats(self):
  p=self.panel();self.assertTrue(p.enemy_overview.isVisible());self.assertFalse(p.enemy_player.isVisible());self.assertIsNone(p.enemy_key)
  rows=self.rows(p);self.assertEqual([r.data(0,Qt.ItemDataRole.UserRole)for r in rows],[key for _,key,_ in p.enemy_choices.entries()])
  lookup={e['key']:e for e in p.result['enemies']};icons={key:icon.cacheKey()for _,key,icon in p.enemy_choices.entries()}
  for item in rows:
   key=item.data(0,Qt.ItemDataRole.UserRole);self.assertEqual([item.text(i)for i in range(3)],overview_cells(lookup[key]));self.assertEqual(item.icon(0).cacheKey(),icons[key]);self.assertIsNone(lookup[key]['expected_stats'])
  self.assertIn('不用白值',p.enemy_overview.notice.text())
  with patch.object(model,'picture_for_enemy',side_effect=AssertionError('reuse verified icons')):p._sync_enemy_grid()
 def test_three_exact_stage_variants_keep_own_prior_full_result_and_each_enemy_player_text(self):
  raw=(ROOT/'research/enemy-overview-review-20261031/before-current-battle-view.py').read_bytes();prior=ModuleType('rouge._before_enemy_overview_review');prior.__package__='rouge';exec(compile(raw,'<own-prior-battle-reader>','exec'),prior.__dict__)
  for sid in ['ro6_n_2_6','ro6_n_5_3','ro6_e_5_3_dlc1']:
   before=prior.CurrentBattlePanel(sid);self.addCleanup(before.close);after=self.panel(sid);self.assertEqual(before.result,after.result)
   for enemy in after.result['enemies']:
    before.enemy_choices.select_value(enemy['key']);after.enemy_choices.select_value(enemy['key']);self.assertEqual(before.enemy_player.toPlainText(),after.enemy_player.toPlainText());self.assertEqual(before.enemy_key,after.enemy_key)
 def test_group_fold_is_independent_and_survives_same_source_refresh_search_and_return(self):
  p=self.panel();tree=p.enemy_overview.tree;group=tree.topLevelItem(0);tier=group.data(0,Qt.ItemDataRole.UserRole+1);group.setExpanded(False)
  self.assertTrue(p.refresh_reference());self.assertFalse(tree.topLevelItem(0).isExpanded())
  p.enemy_search.setText('__no_enemy_9182__');self.assertEqual(tree.topLevelItemCount(),0);p.enemy_search.clear()
  group=next(tree.topLevelItem(i)for i in range(tree.topLevelItemCount())if tree.topLevelItem(i).data(0,Qt.ItemDataRole.UserRole+1)==tier);self.assertFalse(group.isExpanded())
  enemy=p.result['enemies'][0];p.enemy_choices.select_value(enemy['key']);self.assertTrue(p.enemy_player.isVisible());p.enemy_combo.setCurrentIndex(0);self.assertTrue(p.enemy_overview.isVisible());self.assertFalse(group.isExpanded())
 def test_exact_selection_has_full_reader_and_original_branch_filter_limits_overview(self):
  p=self.panel();item=self.rows(p)[0];key=item.data(0,Qt.ItemDataRole.UserRole);p.enemy_overview._select(item);self.assertEqual(p.enemy_key,key);self.assertTrue(p.enemy_player.isVisible());self.assertFalse(p.enemy_overview.isVisible())
  for tier,label in model.TIERS.items():
   if not p.enemy_choices.select_branch(label):continue
   p.enemy_combo.setCurrentIndex(0);self.assertTrue(p.enemy_overview.isVisible());self.assertEqual({r.data(0,Qt.ItemDataRole.UserRole)for r in self.rows(p)},{e['key']for e in p.result['enemies']if e['tier']==tier})
 def test_same_name_references_and_missing_portrait_stay_independent(self):
  p=self.panel();fresh=deepcopy(p.result);e=deepcopy(fresh['enemies'][0]);e['key']='separate-test-reference';e['reference_index']=1000;e['portrait']=None;fresh['enemies'].append(e)
  with patch.object(model,'stage_reference',return_value=fresh):p.refresh_reference()
  rows=[r for r in self.rows(p)if r.text(0)==e['name']];self.assertGreaterEqual(len(rows),2);item=next(r for r in rows if r.data(0,Qt.ItemDataRole.UserRole)==e['key']);self.assertIn('1001',item.toolTip(0));p.enemy_overview._select(item);self.assertEqual(p.enemy_key,e['key'])
 def test_source_loss_clears_table_and_recovery_does_not_restore_old_selection_or_folds(self):
  p=self.panel();p.enemy_overview.tree.topLevelItem(0).setExpanded(False);p.enemy_choices.select_value(p.result['enemies'][0]['key'])
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertEqual(self.rows(p),[]);self.assertFalse(p.enemy_overview.isVisible());self.assertTrue(p.refresh_reference());self.assertEqual(p.tabs.currentIndex(),0);p.tabs.setCurrentIndex(1);self.assertTrue(p.enemy_overview.isVisible());self.assertIsNone(p.enemy_key);self.assertTrue(p.enemy_overview.tree.topLevelItem(0).isExpanded())
 def test_short_summary_is_explicit_and_complete_original_remains_in_tooltip_and_reader(self):
  e={'name':'long','abilities':['甲'*250],'description':'介绍','declared_traits':None};cells=overview_cells(e);self.assertIn('点选查看全文',cells[2]);self.assertNotEqual(cells[2],e['abilities'][0]);self.assertIn('未核对',cells[1])

if __name__=='__main__':unittest.main()
