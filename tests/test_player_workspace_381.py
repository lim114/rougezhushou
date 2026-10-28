import unittest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_workspace import PlayerWorkspace,GROUPS

class WorkspaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def setUp(self):self.w=PlayerWorkspace()
 def tearDown(self):self.w.close_developer_tools();self.w.close();self.w.deleteLater();self.gui.processEvents()
 def test_five_player_groups(self):self.assertEqual(tuple(self.w.tabText(i)for i in range(self.w.count())),GROUPS)
 def test_exact_reader_routes_and_keeps_instances(self):
  a,b=QWidget(),QWidget();self.w.addTab(a,'地图预览');self.w.addTab(b,'节点事件')
  self.assertTrue(self.w.setCurrentWidget(b));self.assertIs(self.w.currentWidget(),b)
  self.w.setCurrentWidget(a);self.assertIs(self.w.currentWidget(),a)
 def test_development_is_not_default_navigation(self):
  p=QWidget();self.w.addTab(p,'HP原值资格')
  self.assertFalse(self.w.setCurrentWidget(p));self.assertFalse(self.w.developer_dialog.isVisible())
 def test_leaf_changes_emit_and_unknown_target_is_safe(self):
  events=[];self.w.activePageChanged.connect(events.append);a,b=QWidget(),QWidget()
  self.w.addTab(a,'地图预览');self.w.addTab(b,'本图节点');self.w.setCurrentWidget(a);self.w.setCurrentWidget(b)
  self.assertIs(events[-1],b);self.assertFalse(self.w.setCurrentWidget(QWidget()))
if __name__=='__main__':unittest.main()
