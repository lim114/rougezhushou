import unittest
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_source_cards import source_cards
from rouge.player_item_sources import ItemSourceIndex
from rouge.player_item_hover import ItemHoverCard
from tests.test_player_item_sources_394 import fixture
class SourceCardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_known_counts_stay_per_pool(self):
  data=fixture();second=deepcopy(data['versions']['base'][0]);second['id']='second';second['observedDistribution']['members'][0]['occurrenceCount']=4;second['observedDistribution']['members'][0]['occurrenceRate']=.4;data['versions']['base'].append(second)
  before=deepcopy(data);cards=source_cards(ItemSourceIndex(data),'base','a')
  self.assertEqual(len(cards['nodes']),2);self.assertEqual({r['frequency']for r in cards['nodes']},{'历史候选频率 20.00%','历史候选频率 40.00%'});self.assertEqual(data,before)
 def test_unknown_scope_or_identity_not_borrowed(self):
  index=ItemSourceIndex(fixture());self.assertEqual(source_cards(index,'dlc2','a'),{'pools':[],'nodes':[]});self.assertEqual(source_cards(index,'base','同名藏品'),{'pools':[],'nodes':[]})
 def test_invalid_ratio_and_missing_summary_not_numeric(self):
  data=fixture();data['versions']['base'][0]['observedDistribution']['members'][0]['occurrenceRate']=.8
  self.assertEqual(source_cards(ItemSourceIndex(data),'base','a')['pools'][0]['frequency'],'暂无可核对统计')
 def test_no_source_clears_cards_and_navigation(self):
  owner=QWidget();card=ItemHoverCard(owner)
  try:
   row={'id':'a','name':'同名藏品'};card.install(row,'base',ItemSourceIndex(fixture()),'1');self.assertTrue(card.cards.buttons)
   card.install(row,'base',None,'2')
   self.assertEqual(card.cards.buttons,[])
   self.assertEqual(card.pools.count(),0)
   self.assertEqual(card.map_targets.count(),0)
   self.assertFalse(card.open_button.isEnabled())
   self.assertEqual(card.detail.toPlainText(),'请先更新公开资料。')
  finally:card.close();owner.close()
 def test_pinned_different_identity_and_exact_navigation(self):
  owner=QWidget();card=ItemHoverCard(owner)
  try:
   card.install({'id':'a','name':'同名'},'base',ItemSourceIndex(fixture()),'s');card.pin.setChecked(True)
   self.assertFalse(card.install({'id':'b','name':'同名'},'base',ItemSourceIndex(fixture()),'s'))
   seen=[];card.poolRequested.connect(lambda v,i:seen.append((v,i)));card.cards.buttons[0].click();card.open_button.click()
   self.assertEqual(seen,[('base','pool1')]);self.assertTrue(card.show_conditions.isChecked())
  finally:card.close();owner.close()

 def test_one_pool_lookup_per_selection_and_a_fresh_lookup_after_switch(self):
  data = fixture()
  second = deepcopy(data['versions']['base'][0])
  second.update(id='second', name='第二个池', nodeBindings=[{'nodeType':'BATTLE_ELITE', 'nodeName':'紧急作战'}])
  data['versions']['base'].append(second)
  index = ItemSourceIndex(data)
  owner = QWidget()
  card = ItemHoverCard(owner)
  self.addCleanup(owner.close)
  self.addCleanup(card.close)
  card.install({'id':'a','name':'同名'}, 'base', index, 'fixture')
  with patch.object(index, 'pools', wraps=index.pools) as lookup:
   card.read_pool()
   lookup.assert_called_once_with('base', 'a')
   lookup.reset_mock()
   card.pools.setCurrentIndex(card.pools.findData('second'))
   lookup.assert_called_once_with('base', 'a')
  self.assertIn('第二个池', card.detail.toPlainText())
  self.assertEqual(card.map_targets.currentData(), '紧急作战')

 def test_single_item_statistics_do_not_render_other_members(self):
  index = ItemSourceIndex(fixture())
  with patch('rouge.public_archive.members', side_effect=AssertionError('whole pool rendered')), \
       patch('rouge.public_compendium.resolve', side_effect=AssertionError('unneeded descriptions')):
   cards = source_cards(index, 'base', 'a')
   description = index.describe('base', 'a', 'pool1')
  self.assertIn('20.00%', cards['pools'][0]['frequency'])
  self.assertIn('20.00%', description)
