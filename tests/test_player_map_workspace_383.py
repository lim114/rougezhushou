import unittest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_workspace import PlayerWorkspace
class MapWorkspaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_both_exact_aliases_reach_shared_page(self):
  w=PlayerWorkspace();a,b=QWidget(),QWidget();w.addTab(a,'地图预览');w.addTab(b,'本图节点')
  c=w.combine_map_and_node(a,b)
  for p in (a,b,a):w.setCurrentWidget(p);self.assertIs(w.currentWidget(),p);self.assertIs(w.aliases[p],c)
  self.assertEqual(w.groups['地图与节点'].count(),1);w.close();w.deleteLater()
 def test_children_not_recreated(self):
  w=PlayerWorkspace();a,b=QWidget(),QWidget();b.setObjectName('kept-selection');w.addTab(a,'地图预览');w.addTab(b,'本图节点');w.combine_map_and_node(a,b)
  w.setCurrentWidget(b);w.setCurrentIndex(0);w.setCurrentWidget(b);self.assertEqual(b.objectName(),'kept-selection');w.close();w.deleteLater()
if __name__=='__main__':unittest.main()
