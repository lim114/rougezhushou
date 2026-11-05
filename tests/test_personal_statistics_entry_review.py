from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge import player_cohort_ui as ui
from rouge.player_personal_statistics import PersonalStatisticsPage,complete_inventory
from rouge.catalog import catalog

class PersonalStatisticsEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_complete_inventory_reads_each_presence_once(self):
        class Record(dict):
            reads=0
            def __getitem__(self,key):
                if key=='held':self.reads+=1
                return super().__getitem__(key)
        identity=next(x for x in catalog()['relics']if x!='rogue_6_relic_legacy_1')
        record=Record(held=True)
        state={'relics':{identity:record},'inventory_verified':True,'relic_count':1}
        self.assertTrue(complete_inventory(state));self.assertEqual(record.reads,1)

    def test_statistics_details_reuse_selected_relic_and_visible_scope(self):
        page=PersonalStatisticsPage(SimpleNamespace(records=lambda:([],[])));self.addCleanup(page.close)
        page.details_open=True
        with patch.object(page.relic,'currentData',wraps=page.relic.currentData)as relic,patch.object(ui,'filter_text',wraps=ui.filter_text)as scope:
            page.render();self.assertEqual((relic.call_count,scope.call_count),(1,2))
        text=page.detail.toPlainText()
        self.assertIn('全部保密等级 · 全部分队类型',text)
        self.assertIn('不表示效果完全相同',text)
        self.assertIn('筛选不改变原记录',text)
        self.assertEqual(page.result['archive_count'],0)
        self.assertIsNone(page.samples.relic_id)

if __name__=='__main__':unittest.main()
