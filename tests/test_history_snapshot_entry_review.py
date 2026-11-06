import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PySide6.QtWidgets import QApplication,QComboBox
from rouge.player_shop_memory import qualified,ShopMemoryPanel,remember,recorded_shops
from rouge.player_floor_resources import snapshots
from tests.test_player_feature_426 import observations

class SnapshotEntryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_qualification_keeps_identity_price_and_duplicate_rules(self):
        items={'x':{'name':'测试商品'}}
        base={'source':'fresh_shop_exact_names','complete':False}
        for price,expected in ((0,0),(7,7),(-1,None),(True,None),('7',None)):
            rows=qualified({**base,'items':[{'id':'x','name':'测试商品','price':price}]},items=items)
            self.assertEqual(rows[0].get('price'),expected)
        for rows in ([{'id':'x','name':'错误名称'}],[{'id':'missing','name':'测试商品'}],
                     [{'id':'x','name':'测试商品'}]*2,[{'id':[],'name':'测试商品'}],[None]):
            self.assertIsNone(qualified({**base,'items':rows},items=items))

    def test_snapshot_invalid_fields_and_capacity_are_not_invented(self):
        base={'kind':'floor_resources_read','source':'same_frame_zone_and_resources','zone_id':'zone_1','values':{'gold':0,'hope':2},'capacities':{'hope':1}}
        rows=snapshots({'history':[base,{**base,'zone_id':[]},{**base,'values':None},None]})
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['values'],{'gold':0,'hope':2});self.assertEqual(rows[0]['capacities'],{})
        rows[0]['values']['gold']=99;self.assertEqual(base['values']['gold'],0)

    def test_write_gate_keeps_exact_two_second_and_run_boundaries(self):
        run=SimpleNamespace(state={'id':'current'},save=Mock(return_value=True))
        with patch('rouge.player_shop_memory.time.time',return_value=100),patch('rouge.player_shop_memory.record_shop',return_value=True)as record:
            for value in (None,True,'100',float('nan'),float('inf'),-float('inf'),97.999,100.001,10**1000,-10**1000):
                self.assertFalse(remember(run,{},'current',value))
            self.assertFalse(remember(run,{},'other',100))
            record.assert_not_called();run.save.assert_not_called()
            for value in (98,100):self.assertTrue(remember(run,{},'current',value))
            self.assertEqual(record.call_count,2);self.assertEqual(run.save.call_count,2)
            record.return_value=False
            self.assertFalse(remember(run,{},'current',100));self.assertEqual(run.save.call_count,2)

    def test_huge_history_times_are_excluded_without_losing_valid_records(self):
        import sys
        valid=observations()
        history=[{**valid,'at':value}for value in (10**1000,-10**1000,float('inf'),float('nan'),-1)]+[valid,{**valid,'at':sys.float_info.max}]
        result=recorded_shops({'history':history})
        self.assertEqual([index for index,_ in result],[5,6])
        self.assertEqual(result[-1][1]['at'],sys.float_info.max)

    def test_open_source_refreshes_source_once(self):
        source=SimpleNamespace(openPoolReference=lambda *a:None,reload_sources=Mock(),source_signature=None,
            source_index=None,version=QComboBox())
        source.version.addItem('当前',None)
        run=SimpleNamespace(state={'id':'test','history':[observations()]},save_issue=None)
        panel=ShopMemoryPanel(run,source);self.addCleanup(panel.close);self.addCleanup(panel.source_card.close)
        panel.entries.setCurrentRow(0);source.reload_sources.reset_mock()
        panel.open_source();self.assertEqual(source.reload_sources.call_count,1)

if __name__=='__main__':unittest.main()
