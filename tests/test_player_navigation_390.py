import unittest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_workspace import PlayerWorkspace
class BackNavigation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_exact_leaf_back_preserves_instances(self):
  ws=PlayerWorkspace();a,b=QWidget(),QWidget();ws.addTab(a,'采样测试');ws.addTab(b,'节点事件');ws.setCurrentWidget(b)
  self.assertTrue(ws.go_back());self.assertIs(ws.currentWidget(),a);self.assertFalse(ws.go_back());ws.close()
 def test_combined_map_alias_back(self):
  ws=PlayerWorkspace();a,b,c=QWidget(),QWidget(),QWidget();ws.addTab(a,'地图预览');ws.addTab(b,'本图节点');ws.combine_map_and_node(a,b);ws.addTab(c,'节点事件')
  ws.setCurrentWidget(b);ws.setCurrentWidget(c);self.assertTrue(ws.go_back());self.assertIs(ws.currentWidget(),b);ws.close()
