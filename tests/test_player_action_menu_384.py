import unittest
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QPushButton
from rouge.player_action_menu import ButtonMenu
class ActionMenuTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def setUp(self):
  self.w=QWidget();l=QVBoxLayout(self.w);self.a=QPushButton('资料甲');self.b=QPushButton('资料乙');l.addWidget(self.a);l.addWidget(self.b);self.a.show();self.b.hide();self.m=ButtonMenu(self.w,[self.a,self.b])
 def tearDown(self):self.w.close();self.w.deleteLater();self.gui.processEvents()
 def test_relevance_not_lost(self):self.assertEqual([a.text()for a in self.m.visible_actions()],['资料甲'])
 def test_enabled_state_and_trigger_forwarded(self):
  seen=[];self.a.clicked.connect(lambda:seen.append(True));act=self.m.visible_actions()[0];act.trigger();self.assertEqual(seen,[True]);self.a.setEnabled(False);self.m.sync();self.assertFalse(act.isEnabled())
 def test_dynamic_visibility_and_original_widget_kept(self):
  self.a.hide();self.b.show();self.assertEqual([a.text()for a in self.m.visible_actions()],['资料乙']);self.assertIs(self.m.actions[1][0],self.b)
 def test_explicit_diagnostic_layout_restores_real_eligible_widgets_only(self):
  self.w.show();self.gui.processEvents();self.assertFalse(self.a.isVisible())
  self.m.expose_original_controls();self.gui.processEvents()
  self.assertTrue(self.a.isVisible());self.assertFalse(self.b.isVisible());self.assertFalse(self.m.isVisible())
  self.assertIs(self.a.parentWidget(),self.w);self.assertIs(self.b.parentWidget(),self.w)
  self.m.expose_original_controls();self.assertEqual(self.w.layout().count(),2)
 def test_diagnostic_flag_is_initialized_before_exposure(self):
  self.assertIs(self.m.diagnostic_controls_exposed,False)
  self.m.expose_original_controls();self.assertIs(self.m.diagnostic_controls_exposed,True)
 def test_missing_menu_layout_entry_rejected_before_moving_buttons(self):
  self.w.layout().removeWidget(self.m)
  with self.assertRaisesRegex(ValueError,'原按钮布局无法核对'):self.m.expose_original_controls()
  self.assertIs(self.a.parentWidget(),self.m.holder);self.assertIs(self.b.parentWidget(),self.m.holder)
  self.assertFalse(self.m.diagnostic_controls_exposed)
if __name__=='__main__':unittest.main()
