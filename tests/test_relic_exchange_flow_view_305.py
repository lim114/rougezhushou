from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import relic_exchange_flow as model
from rouge.relic_exchange_flow_view import RelicExchangeFlowPanel
from rouge.node_catalog_view import NodeCatalogPanel
EVENT='community_group_025'

class RelicExchangeView305Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def setUp(self):
  self.panel=RelicExchangeFlowPanel();self.panel.set_reference(EVENT,scope_key='test-node')
  self.addCleanup(self.panel.close)
 def choose(self,control,value):
  i=control.findData(value);self.assertGreaterEqual(i,0);control.setCurrentIndex(i);self.gui.processEvents()
 def test_complete_catalogue_defaults_unselected_and_second_only_inputs_hidden(self):
  self.assertEqual(self.panel.flow.count(),19);self.assertEqual(self.panel.relic.count(),272)
  self.assertEqual(self.panel.flow.currentIndex(),-1);self.assertEqual(self.panel.relic.currentIndex(),-1)
  self.assertTrue(self.panel.palm.isHidden());self.assertTrue(self.panel.first_type.isHidden())
  self.assertIn('固定本体',self.panel.catalogue_count.text())
  self.assertNotIn('旗标',self.panel.flow_reader.toPlainText())
 def test_both_flag_classes_are_offering_only_and_no_reward_inferred(self):
  packet=model.event_reference(EVENT)
  for flag in(True,False):
   row=next(x for x in packet['catalogue']if x['canSacrifice']is flag)
   self.choose(self.panel.relic,row['item_id'])
   text=self.panel.offer_reader.toPlainText()
   self.assertIn('允许作为提供物'if flag else'不能作为提供物',text)
   self.assertIn('不说明能否作为交换奖励得到',text)
   self.assertIn('不从提供物的稀有度推算奖励',text)
   self.assertNotIn('旗标',text)
 def test_flag_filter_has_21_exclusions_and_clears_out_of_scope_selection(self):
  allowed=next(x for x in model.event_reference(EVENT)['catalogue']if x['canSacrifice'])
  self.choose(self.panel.relic,allowed['item_id'])
  self.choose(self.panel.membership,False)
  self.assertEqual(self.panel.relic.count(),21);self.assertEqual(self.panel.relic.currentIndex(),-1)
  self.assertNotIn(allowed['name'],self.panel.offer_reader.toPlainText())
  self.panel.search.setText('不存在的收藏品名字')
  self.assertEqual(self.panel.relic.count(),0)
 def test_second_exchange_checks_do_not_leak_into_first(self):
  allowed=next(x for x in model.event_reference(EVENT)['catalogue']if x['canSacrifice'])
  self.choose(self.panel.relic,allowed['item_id']);self.choose(self.panel.exchange_index,2)
  self.assertFalse(self.panel.palm.isHidden());self.assertFalse(self.panel.first_type.isHidden())
  self.choose(self.panel.first_type,'SCRAP');self.choose(self.panel.palm,True)
  result=model.relic_offer_reference(allowed['item_id'],exchange_index=2,first_exchange_item_type='SCRAP',palm_unlocked=True)
  self.assertFalse(next(c['matches']for c in result['checks']if c['key']=='same_first_type'))
  self.assertIn('不符',self.panel.offer_reader.toPlainText())
  self.choose(self.panel.exchange_index,1)
  self.assertNotIn('与首次同为收藏品',self.panel.offer_reader.toPlainText())
  self.assertTrue(self.panel.first_type.isHidden())
 def test_two_missing_leave_results_are_available_without_inventing_unique_origin(self):
  packet=model.event_reference(EVENT)
  rows=[r for r in packet['choices']if r.get('documented_result_text')]
  self.assertEqual({r['choice_key']for r in rows},{EVENT+':scene:3:choice:1',EVENT+':scene:7:choice:1'})
  for row in rows:
   self.choose(self.panel.flow,row['reference_id'])
   self.assertIn(row['documented_result_text'],self.panel.flow_reader.toPlainText())
   self.assertIn('多个候选',self.panel.flow_reader.toPlainText())
   self.assertIn('两份资料的后续不一致',self.panel.flow_reader.toPlainText())
   self.assertIn('不能确定游戏实际会出现哪一种后续',self.panel.flow_reader.toPlainText())
   for destination in row['documented_destinations']:
    self.assertIn(destination['description'],self.panel.flow_reader.toPlainText())
 def test_refresh_preserves_scope_selection_declarations_scroll_and_cursor(self):
  self.panel.resize(680,360);self.panel.show();self.gui.processEvents()
  packet=model.event_reference(EVENT);row=packet['catalogue'][0]
  self.choose(self.panel.relic,row['item_id']);self.choose(self.panel.exchange_index,2)
  self.choose(self.panel.owned,True);self.choose(self.panel.palm,True);self.choose(self.panel.first_type,'RELIC')
  self.choose(self.panel.flow,packet['choices'][0]['reference_id'])
  self.panel.tabs.setCurrentWidget(self.panel.source_reader);self.gui.processEvents()
  reader=self.panel.source_reader;cursor=reader.textCursor();cursor.setPosition(30);cursor.setPosition(60,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
  reader.verticalScrollBar().setValue(max(1,reader.verticalScrollBar().maximum()//2))
  self.assertGreater(reader.verticalScrollBar().value(),0)
  before=(self.panel.flow.currentData(),self.panel.relic.currentData(),self.panel.tabs.currentIndex(),reader.textCursor().selectionStart(),reader.textCursor().selectionEnd(),reader.verticalScrollBar().value())
  self.panel.set_reference(EVENT,scope_key='test-node');self.gui.processEvents()
  self.assertEqual(before,(self.panel.flow.currentData(),self.panel.relic.currentData(),self.panel.tabs.currentIndex(),reader.textCursor().selectionStart(),reader.textCursor().selectionEnd(),reader.verticalScrollBar().value()))
  self.assertIs(self.panel.owned.currentData(),True);self.assertEqual(self.panel.first_type.currentData(),'RELIC')
 def test_source_failure_clears_and_recovery_does_not_reselect(self):
  self.panel.flow.setCurrentIndex(0);self.panel.relic.setCurrentIndex(0)
  with patch.object(model,'event_reference',return_value={'target':True,'source_valid':False}):
   self.panel.refresh_reference();self.assertIsNone(self.panel.packet)
   for control in(self.panel.flow,self.panel.relic):self.assertEqual(control.count(),0)
   self.assertIn('清除',self.panel.offer_reader.toPlainText())
  self.panel.refresh_reference()
  self.assertEqual(self.panel.flow.currentIndex(),-1);self.assertEqual(self.panel.relic.currentIndex(),-1)
 def test_range_change_resets_only_manual_reading_and_unrelated_entry_stays_hidden(self):
  self.panel.flow.setCurrentIndex(0);self.panel.relic.setCurrentIndex(0)
  self.panel.set_reference(EVENT,scope_key='new-node')
  self.assertEqual(self.panel.flow.currentIndex(),-1);self.assertEqual(self.panel.relic.currentIndex(),-1)
  node=NodeCatalogPanel();self.addCleanup(node.close)
  node.kind.setCurrentIndex(node.kind.findData('event'));node.search.setText('回滚文明');node.refresh()
  node.list.setCurrentRow(next(i for i,r in enumerate(node.entries)if r['kind']=='event'and r['record']['id']==EVENT))
  self.assertFalse(node.relic_exchange_flow_button.isHidden());node.open_relic_exchange_flow()
  dialog=node.relic_exchange_flow_window;self.addCleanup(dialog.close);self.assertIsNotNone(dialog)
  node.search.setText('好奇心与死');node.refresh()
  self.assertTrue(node.relic_exchange_flow_button.isHidden());self.assertIsNone(dialog.packet)

if __name__=='__main__':unittest.main()
