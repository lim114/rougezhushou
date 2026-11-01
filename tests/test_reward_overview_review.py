"""Reward overview keeps actual quantities conditional and routes exact records."""
from pathlib import Path
from types import ModuleType
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QHeaderView
from rouge import current_reward_reference as model
from rouge.current_reward_view import CurrentRewardPanel
from rouge.current_battle_view import CurrentBattlePanel
from rouge.player_map_reader import make_reader

ROOT=Path(__file__).resolve().parents[1]
class RewardOverviewReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([]);cls.prior=ModuleType('rouge._before_reward_overview_reference');cls.prior.__package__='rouge';cls.prior.__file__=str(ROOT/'rouge/current_reward_reference.py');exec(compile((ROOT/'research/reward-overview-20261101/before-current_reward_reference.py').read_bytes(),'<exact-own-prior-reward-text>','exec'),cls.prior.__dict__)
 def panel(self,sid='ro6_n_2_6'):
  p=CurrentRewardPanel(sid);p.resize(900,600);p.show();self.qt.processEvents();self.addCleanup(p.close);return p
 def rows(self,p):return[p.overview.topLevelItem(i).child(j)for i in range(p.overview.topLevelItemCount())for j in range(p.overview.topLevelItem(i).childCount())]
 def test_all184_fixed_stage_texts_remain_exactly_equal_to_actual_prior_model(self):
  ref=model.packet();ids=ref['current']['version']['current']['details']['stages'];self.assertEqual(len(ids),184);count=0
  with patch.object(model,'packet',return_value=ref):
   for sid in ids:
    result=model.stage_rewards(sid);self.assertEqual(model.summary_text(result),self.prior.summary_text(result))
    for row in result['rows']:self.assertEqual(model.row_text(row),self.prior.row_text(row),(sid,row['id']));count+=1
  self.assertGreater(count,1000)
 def test_default_real_overview_contains_all_exact_source_ids_outcomes_and_groups(self):
  p=self.panel();self.assertTrue(p.overview.isVisible());self.assertTrue(p.overview_section.isExpanded());self.assertIsNone(p.row_id);self.assertFalse(p.source_button.isVisible());self.assertFalse(p.source_combo.isVisible());lookup={r['id']:r for r in p.result['rows']};rows=self.rows(p);self.assertEqual([r.data(0,Qt.ItemDataRole.UserRole)for r in rows],[key for _,key,_ in p.choices.entries()]);self.assertEqual({p.overview.topLevelItem(i).text(0)for i in range(p.overview.topLevelItemCount())},{'宝箱与装置','移动恶笼草','稀有敌人'})
  for item in rows:self.assertEqual(item.text(1),'\n'.join(model.outcome_lines(lookup[item.data(0,Qt.ItemDataRole.UserRole)]['rule'])))
  self.assertIn('不能相加',p.overview_notice.text());self.assertIsNone(p.result['all_actual_rewards']);self.assertFalse(p.result['mutated_run'])
 def test_branch_with_placeholder_unchanged_really_filters_visible_rows(self):
  p=self.panel()
  for kind,label in(('device','宝箱与装置'),('moving','移动恶笼草'),('rare','稀有敌人')):
   self.assertTrue(p.choices.select_branch(label));self.qt.processEvents();self.assertIsNone(p.row_id);self.assertEqual({i.data(0,Qt.ItemDataRole.UserRole)for i in self.rows(p)},{r['id']for r in p.result['rows']if r['kind']==kind});self.assertTrue(p.overview.isVisible())
 def test_actual_click_opens_exact_existing_detail_and_conditions_without_sending_anything(self):
  p=self.panel();item=self.rows(p)[0];key=item.data(0,Qt.ItemDataRole.UserRole);QTest.mouseClick(p.overview.viewport(),Qt.MouseButton.LeftButton,pos=p.overview.visualItemRect(item).center());self.qt.processEvents();row=next(r for r in p.result['rows']if r['id']==key);self.assertEqual(p.row_id,key);self.assertEqual(p.player.toPlainText(),self.prior.row_text(row));self.assertFalse(p.overview_section.isExpanded());self.assertTrue(p.source_button.isVisible());self.assertEqual([p.source_combo.itemData(i)for i in range(1,p.source_combo.count())],row['source_action_keys']);self.assertFalse(p.source_button.isEnabled())
 def test_keyboard_browse_does_not_open_until_return_and_keeps_same_named_rows_distinct(self):
  p=self.panel();t=p.overview;item=self.rows(p)[1];t.setCurrentItem(item);t.setFocus();self.qt.processEvents();self.assertIsNone(p.row_id);key=item.data(0,Qt.ItemDataRole.UserRole);QTest.keyClick(t,Qt.Key.Key_Return);self.qt.processEvents();self.assertEqual(p.row_id,key)
 def test_images_reuse_verified_branch_icons_without_extra_reads_on_table_rebuild(self):
  p=self.panel();icons={key:icon.cacheKey()for _,key,icon in p.choices.entries()}
  for item in self.rows(p):self.assertEqual(item.icon(0).cacheKey(),icons[item.data(0,Qt.ItemDataRole.UserRole)])
  rare=next(r for r in p.result['rows']if r['kind']=='rare');self.assertFalse(p.reward_icons[rare['id']].isNull())
  with patch.object(model.battle,'picture_bytes',side_effect=AssertionError('no image read for table rebuild')):p._sync_overview()
 def test_full_amount_unknown_zero_range_and_deployment_cost_are_not_reformatted_as_totals(self):
  p=self.panel();row=next(r for r in p.result['rows']if r['entity_id']=='trap_320_shtlbx');text='\n'.join(model.outcome_lines(row['rule']));self.assertIn('50点部署费用',text);self.assertIn('不是源石锭',text)
  for lo,hi in((0,0),(1,2),(None,None)):
   fresh=deepcopy(row);fresh['rule']['outcomes'][0].update(minimum=lo,maximum=hi);self.assertIn('\n'.join(model.outcome_lines(fresh['rule'])),self.prior.row_text(fresh));self.assertEqual(model.row_text(fresh),self.prior.row_text(fresh))
 def test_same_source_keeps_real_two_way_scroll_width_fold_and_detail_reading(self):
  p=self.panel();t=p.overview;t.setColumnWidth(1,500);t.verticalScrollBar().setValue(30);t.horizontalScrollBar().setValue(20);self.qt.processEvents();before=(t.verticalScrollBar().value(),t.horizontalScrollBar().value(),t.columnWidth(1));self.assertGreater(before[0],0);self.assertGreater(before[1],0);self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertEqual((t.verticalScrollBar().value(),t.horizontalScrollBar().value(),t.columnWidth(1)),before)
  p.overview_section.collapse(animate=False);self.assertTrue(p.refresh_reference());self.assertFalse(p.overview_section.isExpanded())
 def test_group_fold_and_branch_filter_retain_same_source_memory(self):
  p=self.panel();g=p.overview.topLevelItem(0);kind=g.data(0,Qt.ItemDataRole.UserRole+1);g.setExpanded(False);p.choices.select_branch('稀有敌人');p.choices.select_branch('__overview__');self.qt.processEvents();g=next(p.overview.topLevelItem(i)for i in range(p.overview.topLevelItemCount())if p.overview.topLevelItem(i).data(0,Qt.ItemDataRole.UserRole+1)==kind);self.assertFalse(g.isExpanded());self.assertTrue(p.refresh_reference());g=next(p.overview.topLevelItem(i)for i in range(p.overview.topLevelItemCount())if p.overview.topLevelItem(i).data(0,Qt.ItemDataRole.UserRole+1)==kind);self.assertFalse(g.isExpanded())
 def test_invalid_source_clears_all_old_rows_images_quantities_and_recovers_without_selection(self):
  p=self.panel();p.choices.select_value(p.result['rows'][0]['id'])
  with patch.object(model,'stage_rewards',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertEqual(self.rows(p),[]);self.assertEqual(p.reward_icons,{});self.assertFalse(p.overview_section.isExpanded());self.assertEqual(p.player.toPlainText(),model.UNAVAILABLE);self.assertTrue(p.refresh_reference());self.assertTrue(p.overview_section.isExpanded());self.assertIsNone(p.row_id);self.assertIsNone(p.source_combo.currentData())
 def test_empty_fixed_stage_does_not_claim_no_drop_or_borrow_another_stage(self):
  p=self.panel('ro6_b_5');self.assertEqual(self.rows(p),[]);self.assertIn('0条奖励来源候选',p.overview_notice.text());self.assertIn('不能解释为不会掉落',p.player.toPlainText());self.assertIsNone(p.result['all_actual_rewards'])
 def test_reward_table_row_heights_reflow_and_parent_main_categories_are_unchanged(self):
  p=CurrentBattlePanel('ro6_n_2_6');self.addCleanup(p.close);self.assertEqual([p.tabs.tabText(i)for i in range(4)],['地图与关卡','敌人和机制','出怪与条件','奖励与条件']);r=p.rewards;t=r.overview;item=max(self.rows(r),key=lambda i:len(i.text(1)));idx=t.indexFromItem(item,1);heights=[]
  for w in(120,450):t.setColumnWidth(1,w);t.doItemsLayout();self.qt.processEvents();heights.append(t.visualRect(idx).height())
  self.assertGreater(heights[0],heights[1]);self.assertEqual(r.tabs.count(),2);self.assertEqual(r.sections.count(),2)
 def test_sequential_actual_dialog_sizes_do_not_promote_page_preferred_height_to_window_minimum(self):
  d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);self.addCleanup(d.close);d.show();d.panel.tabs.setCurrentWidget(d.panel.rewards)
  for width,height in[(640,650),(760,720),(1250,720),(640,650)]:d.resize(width,height);QTest.qWait(60);self.assertEqual((d.width(),d.height()),(width,height));self.assertTrue(d.panel.rewards.overview.isVisible());self.assertTrue(d.panel.rewards.player.isVisible())
 def test_outer_scroll_preserves_real_reading_on_same_source_and_resets_on_loss(self):
  p=self.panel();p.resize(600,260);self.qt.processEvents();bar=p.body_scroll.verticalScrollBar();self.assertGreater(bar.maximum(),20);bar.setValue(20);self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertEqual(bar.value(),20)
  with patch.object(model,'stage_rewards',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertEqual(bar.value(),0);self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertEqual(bar.value(),0)

if __name__=='__main__':unittest.main()
