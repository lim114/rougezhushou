import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QListWidgetItem
from PySide6.QtCore import Qt
from rouge.player_resource_facts import inventory_summary
from rouge.player_resource_history import ResourceHistoryPage,resource_rows

class ResourceEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_inventory_classifies_each_presence_once_for_count_and_unknown(self):
        class Record(dict):
            def __getitem__(self,key):
                if key=='held':self.reads+=1
                return super().__getitem__(key)
        records=[Record(held=x)for x in (True,False,None)]
        for record in records:record.reads=0
        state={'relics':{'a':records[0],'b':records[1]},'tactical_tools':{'c':records[2]},
               'relic_count':1,'inventory_verified':True}
        result=inventory_summary(state)
        self.assertEqual(result,{'relics':1,'tools':0,'total':1,'complete':False,'expected_relics':None})
        self.assertEqual([r.reads for r in records],[1,1,1])

    def test_history_filter_is_read_once_for_the_current_list(self):
        page=ResourceHistoryPage();self.addCleanup(page.close)
        events=[{'kind':'resource_updated','resource':key,'value':i,'at':i+1}
                for i,key in enumerate(('gold','hope','gold','hope'))]
        page.refresh({'id':'review','history':events})
        page.filter.setCurrentIndex(page.filter.findData('gold'))
        with patch.object(page.filter,'currentData',wraps=page.filter.currentData)as selected:
            page.show_rows();self.assertEqual(selected.call_count,1)
        self.assertEqual([page.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(page.entries.count())],[0,2])

    def test_selected_record_identity_is_read_once_and_old_detail_survives(self):
        class Item(QListWidgetItem):
            reads=0
            def data(self,role):
                if role==Qt.ItemDataRole.UserRole:self.reads+=1
                return super().data(role)
        page=ResourceHistoryPage();self.addCleanup(page.close)
        page.rows=resource_rows({'history':[{'kind':'resource_updated','resource':'hope','value':i,'at':i+1}for i in range(4)]})
        item=Item('旧条目');item.setData(Qt.ItemDataRole.UserRole,3);page.entries.addItem(item);page.entries.setCurrentItem(item);item.reads=0
        page.selected()
        self.assertEqual(item.reads,1)
        self.assertIn('读到数量：3',page.detail.toPlainText())

if __name__=='__main__':unittest.main()
