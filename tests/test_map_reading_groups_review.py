from types import SimpleNamespace
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QTreeWidget,QTreeWidgetItem,QLineEdit,QPlainTextEdit
from rouge.player_map import MapPanel


class ReadingGroupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def owner(self,key=('zone_1','template','node')):
        entries=QTreeWidget();search=QLineEdit('公开查询');detail=QPlainTextEdit()
        for widget in (entries,search,detail):self.addCleanup(widget.close)
        return SimpleNamespace(reading_key=key,entries=entries,entry_search=search,
            selected_reference=('事件候选','event','public-id'),detail=detail,entry_readings={})

    def test_records_all_generated_group_labels_and_keeps_hidden_groups(self):
        owner=self.owner();owner.entry_readings[owner.reading_key]={'expanded':{'历史隐藏组':True}}
        labels=('事件候选','作战预览','功能说明','已读历史事件','已读历史作战','已列条件排除的事件（不是候选）')
        expected={'历史隐藏组':True}
        for index,label in enumerate(labels):
            root=QTreeWidgetItem([label]);root.setData(0,257,label);owner.entries.addTopLevelItem(root)
            root.setExpanded(index%2==0);expected[label]=index%2==0
        MapPanel.remember_entry_reading(owner)
        stored=owner.entry_readings[owner.reading_key]
        self.assertEqual(stored['expanded'],expected)
        self.assertEqual(stored['query'],'公开查询')
        self.assertEqual(stored['selected'],owner.selected_reference)

    def test_unselected_or_incomplete_identity_does_not_save(self):
        for key in (None,('zone_1',None,None),('', 'template','node'),('zone_1',False,'node'),('zone_1','template',42)):
            with self.subTest(key=key):
                owner=self.owner(key);MapPanel.remember_entry_reading(owner)
                self.assertEqual(owner.entry_readings,{})
