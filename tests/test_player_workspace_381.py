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
 def test_explicit_developer_dialog_is_current_and_product_navigation_returns(self):
  page,normal=QWidget(),QWidget();self.w.addTab(page,'局外工具');self.w.addTab(normal,'地图预览');self.w.developer_tools=True
  self.w.show();self.assertTrue(self.w.setCurrentWidget(page));self.gui.processEvents()
  self.assertTrue(page.isVisible());self.assertIs(self.w.currentWidget(),page)
  self.w.setCurrentWidget(normal);self.gui.processEvents();self.assertFalse(self.w.developer_dialog.isVisible());self.assertIs(self.w.currentWidget(),normal)
 def test_group_navigation_uses_exact_first_page_without_new_instances(self):
  normal=QWidget();self.w.addTab(normal,'伤害测试');self.assertTrue(self.w.show_group('干员计算'));self.assertIs(self.w.currentWidget(),normal)
  self.assertFalse(self.w.show_group('unknown'))
if __name__=='__main__':unittest.main()
