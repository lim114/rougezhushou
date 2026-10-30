import unittest
from copy import deepcopy
from PySide6.QtWidgets import QApplication
from rouge.player_shop_replay import ShopReplayPage
from rouge.player_replay import event_text
from tests.test_player_feature_426 import observations

class HistoricalShopReading(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def test_reading_uses_detached_state_and_cannot_write_current_run(self):
  current={'id':'current','history':[]};past={'id':'past','history':[observations()]};before=deepcopy(past);p=ShopReplayPage()
  try:
   p.refresh(past);self.assertEqual(p.panel.snapshots.count(),1);self.assertIsNot(p.reading.state,past)
   p.reading.state['history'].clear();self.assertEqual(past,before);self.assertEqual(current,{'id':'current','history':[]})
   self.assertFalse(hasattr(p.reading,'save'))
  finally:p.close()
 def test_exact_record_navigation_does_not_use_timestamp_or_name(self):
  row=observations();p=ShopReplayPage()
  try:
   p.refresh({'id':'past','history':[row,{'kind':'other'},deepcopy(row)]})
   self.assertTrue(p.select_observation(0));self.assertEqual(p.panel.snapshots.currentData(),0)
   self.assertTrue(p.select_observation(2));self.assertEqual(p.panel.snapshots.currentData(),2)
   self.assertFalse(p.select_observation(1))
  finally:p.close()
 def test_lost_archive_clears_the_old_goods(self):
  p=ShopReplayPage()
  try:
   p.refresh({'id':'past','history':[observations()]});p.panel.search.setText('第一');self.assertGreater(p.panel.entries.count(),0)
   p.refresh({'id':None,'history':[]});self.assertEqual(p.panel.entries.count(),0);self.assertEqual(p.panel.search.text(),'')
  finally:p.close()
 def test_read_log_displays_names_with_non_purchase_boundary(self):
  row=observations();text=event_text({'label':'读到商店商品名称','time':'隔离时间','event':row})
  self.assertIn(row['items'][0]['name'],text);self.assertIn('不代表已经买下',text)

if __name__=='__main__':unittest.main()
