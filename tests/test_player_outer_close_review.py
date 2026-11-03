"""Video outer close remains part of the original, natively resizable dialog."""
import sys,unittest
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QEvent
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel
from PySide6.QtTest import QTest
from rouge.player_compact import ToolPopover
from rouge.player_theme import apply_theme

class PlayerOuterCloseReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def make(self,theme='light',extra=''):
  owner=QWidget();self.addCleanup(owner.close);body=QWidget();QVBoxLayout(body).addWidget(QLabel('公开窗口资料'));d=ToolPopover('节点资料',body,owner,theme=theme,extra_style=extra,object_name='outerCloseTest');d.resize(900,500);d.show();self.addCleanup(d.close);self.qt.processEvents();self.qt.sendPostedEvents(None,QEvent.Type.DeferredDelete);return d,body
 def test_close_is_outside_body_but_has_the_same_original_window_and_native_button(self):
  from third_party.qframelesswindow.titlebar.title_bar_buttons import CloseButton
  d,body=self.make();b=d.titleBar.closeBtn;self.assertIsInstance(b,CloseButton);self.assertIs(b.parentWidget(),d);self.assertIs(b.window(),d);self.assertTrue(b.isVisible());self.assertLessEqual(body.geometry().right(),d.width()-d.CLOSE_GUTTER);self.assertGreater(b.x(),d.width()-d.CLOSE_GUTTER);self.assertFalse(d.titleBar.geometry().intersects(b.geometry()));self.assertEqual(len(d.findChildren(CloseButton)),1)
 def test_actual_translucent_pixels_leave_only_the_circle_and_panel_opaque(self):
  for theme,color in [('light','#f5f5f7'),('dark','#1b2928')]:
   d,_=self.make(theme);b=d.titleBar.closeBtn;image=d.grab().toImage();scale=image.width()/d.width();at=lambda x,y:image.pixelColor(round(x*scale),round(y*scale));self.assertEqual(at(d.width()-9,d.height()/2).alpha(),0);self.assertEqual(at(20,d.height()-3).name(),color);self.assertEqual(at(0,0).alpha(),0);self.assertEqual(at(b.x()+3,b.y()+9).name(),'#353b3c');self.assertGreater(at(b.x()+9,b.y()+9).alpha(),0)
 def test_resize_keeps_close_visible_outside_and_content_inside_the_painted_panel(self):
  d,body=self.make()
  for width in (480,640,900,1200):
   d.resize(width,500);QTest.qWait(20);self.qt.processEvents();b=d.titleBar.closeBtn;self.assertTrue(d.rect().contains(b.geometry()));self.assertGreater(b.x(),body.geometry().right());self.assertFalse(d.titleBar.geometry().intersects(b.geometry()));self.assertGreater(body.height(),200);self.assertTrue(b.mask().contains(b.rect().center()));self.assertFalse(b.mask().contains(QPoint(0,0)))
 def test_original_mouse_close_and_refused_close_have_no_second_window_to_orphan(self):
  d,_=self.make();QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(d.isVisible());self.assertFalse(d.titleBar.closeBtn.isVisible())
  class Veto(ToolPopover):
   def closeEvent(self,e):e.ignore()
  owner=QWidget();self.addCleanup(owner.close);v=Veto('公开手动草稿',QWidget(),owner);v.show();self.qt.processEvents();QTest.mouseClick(v.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.assertTrue(v.isVisible());self.assertTrue(v.titleBar.closeBtn.isVisible());v.hide()
 def test_repeated_hide_and_show_preserves_layout_margins_without_duplicating_close(self):
  d,body=self.make();before=(d.layout().contentsMargins(),d.layout().count(),body)
  for _ in range(4):d.hide();d.show();self.qt.processEvents();self.assertEqual((d.layout().contentsMargins(),d.layout().count(),body),before);self.assertEqual(d.titleBar.closeBtn.parentWidget(),d);self.assertTrue(d.titleBar.closeBtn.isVisible())
 def test_theme_extra_cannot_paint_over_the_transparent_outside_gutter(self):
  d,_=self.make(extra='QDialog#outerCloseTest{background:#f5f5f7;border:1px solid red;}');before=(d.layout().count(),d.titleBar.titleLabel.text());apply_theme(d,'dark');self.qt.processEvents();self.assertEqual((d.layout().count(),d.titleBar.titleLabel.text()),before);image=d.grab().toImage();scale=image.width()/d.width();self.assertEqual(image.pixelColor(round((d.width()-9)*scale),round(d.height()/2*scale)).alpha(),0);self.assertEqual(d.titleBar.closeBtn.getNormalColor().name(),'#ededed')
 def test_existing_custom_panel_background_is_preserved_instead_of_becoming_theme_default(self):
  for selector,color in [('QDialog#outerCloseTest','#262528'),('#outerCloseTest','#1e1e20')]:
   d,_=self.make('dark',selector+'{background:'+color+';border:1px solid #585858;border-radius:12px;}');image=d.grab().toImage();scale=image.width()/d.width();self.assertEqual(image.pixelColor(round(20*scale),round((d.height()-3)*scale)).name(),color);self.assertEqual(image.pixelColor(round((d.width()-9)*scale),round(d.height()/2*scale)).alpha(),0)
 def test_owned_move_translates_circle_with_the_dialog_without_any_sibling_window(self):
  d,_=self.make();b=d.titleBar.closeBtn;before=b.mapToGlobal(b.rect().center());d.move(d.pos()+QPoint(19,17));self.qt.processEvents();self.assertEqual(b.mapToGlobal(b.rect().center())-before,QPoint(19,17));self.assertIs(b.window(),d)
 def test_native_visible_panel_right_edges_keep_resizing_after_gutter_is_reserved(self):
  if sys.platform!='win32':self.skipTest('Actual Win32 dispatch only.')
  import win32gui,win32api,win32con
  d,_=self.make();h=int(d.winId());_,_,width,height=win32gui.GetClientRect(h);right=width-round(d.CLOSE_GUTTER*d.devicePixelRatioF())
  for pos,expected in [((right-1,1),win32con.HTTOPRIGHT),((right-1,height//2),win32con.HTRIGHT),((right-1,height-1),win32con.HTBOTTOMRIGHT)]:
   with patch.object(win32api,'GetCursorPos',return_value=win32gui.ClientToScreen(h,pos)):self.assertEqual(win32gui.SendMessage(h,win32con.WM_NCHITTEST,0,0),expected)
if __name__=='__main__':unittest.main()
