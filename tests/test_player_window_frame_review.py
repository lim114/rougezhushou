"""Actual Qt frame adoption, original source and editor-close contracts."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch
import json,sys,tomllib,unittest
from PySide6.QtCore import Qt,QPoint,QEvent,QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel
from rouge.player_compact import ToolPopover
from rouge.player_window_frame import PlayerDialog

R=Path(__file__).resolve().parents[1]
class PlayerWindowFrameReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def popover(self,theme='light'):
  owner=QWidget();self.addCleanup(owner.close);body=QWidget();QVBoxLayout(body).addWidget(QLabel('公开资料'));d=ToolPopover('公开窗口',body,owner,theme=theme);d.resize(640,400);d.show();self.addCleanup(d.close);self.qt.processEvents();return d,body
 def event(self):
  from rouge.current_vine_events_view import CurrentVineEventsDialog
  d=CurrentVineEventsDialog('呼吸的红苔');d.show();self.addCleanup(d.close);self.qt.processEvents();return d
 def test_upstream_sources_keep_declared_bytes_with_one_exact_owned_window_adaptation(self):
  m=json.loads((R/'research/shared-player-frame-20261101/upstream.json').read_bytes());self.assertEqual(m['commit'],'fc00919f4915c91a2b6320a8ae7eb1d977ca4f57');self.assertEqual(len(m['files']),19)
  for name,row in m['files'].items():
   raw=(R/'third_party/qframelesswindow'/name).read_bytes()
   if name=='windows/__init__.py':
    original=(R/'research/shared-player-frame-20261101/upstream-windows-init.py').read_bytes();self.assertEqual(sha256(original).hexdigest(),row['sha256']);self.assertEqual(sha256(raw).hexdigest(),m['local_adaptations'][name]['sha256'])
    current=raw.decode('utf8').replace('win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED |\r\n                              win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)','win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)').replace('    # rouge adaptation, 2026-11-01: refresh our frame without activation or Z-order changes.\r\n','');self.assertEqual(current,original.decode('utf8'))
   else:self.assertEqual(sha256(raw).hexdigest(),row['sha256']);self.assertEqual(len(raw),row['bytes'])
  self.assertIn('GNU LESSER GENERAL PUBLIC LICENSE',(R/'third_party/qframelesswindow/LICENSE').read_text('utf8'));self.assertIn('GNU GENERAL PUBLIC LICENSE',(R/'third_party/qframelesswindow/COPYING').read_text('utf8'))
 def test_distribution_includes_library_namespace_and_both_licenses(self):
  cfg=tomllib.loads((R/'pyproject.toml').read_text('utf8'));self.assertIn('third_party.qframelesswindow*',cfg['tool']['setuptools']['packages']['find']['include']);self.assertEqual(set(cfg['tool']['setuptools']['package-data']['third_party.qframelesswindow']),{'LICENSE','COPYING','NOTICE.md','_rc/*.qrc','_rc/title_bar/*.svg'})
  from third_party.qframelesswindow import FramelessDialog
  self.assertTrue(issubclass(PlayerDialog,FramelessDialog))
 def test_popover_has_one_same_header_no_system_title_and_original_body(self):
  d,body=self.popover();self.assertTrue(d.windowFlags()&Qt.WindowType.FramelessWindowHint);self.assertEqual(d.windowFlags()&Qt.WindowType.WindowType_Mask,Qt.WindowType.Tool);self.assertIs(d.layout().itemAt(0).widget(),d.titleBar);self.assertIs(d.layout().itemAt(1).widget(),body);self.assertIs(d.header_bar,d.titleBar.hBoxLayout);self.assertIs(d.title_label,d.titleBar.titleLabel);self.assertFalse(d.titleBar.minBtn.isVisible());self.assertFalse(d.titleBar.maxBtn.isVisible());self.assertFalse(d.titleBar.iconLabel.isVisible());self.assertTrue(d.titleBar.closeBtn.isVisible())
 def test_title_changes_and_dark_light_close_colors_follow_each_window(self):
  for theme,color in [('light','#ededed'),('dark','#ededed')]:
   d,_=self.popover(theme);d.setWindowTitle('新标题');self.assertEqual(d.titleBar.titleLabel.text(),'新标题');self.assertEqual(d.titleBar.closeBtn.getNormalColor().name(),color);self.assertEqual(d.titleBar.closeBtn.accessibleName(),'关闭此窗口')
 def test_show_restore_does_not_add_another_header_or_reset_choice(self):
  d=self.event();p=d.panel;p.choices.setCurrentRow(0);before=(p.scene_id,p.choice_id,p.player.toPlainText());count=d.layout().count();d.hide();d.show();self.qt.processEvents();self.assertEqual(d.layout().count(),count);self.assertEqual(sum(d.layout().itemAt(i).widget()is d.titleBar for i in range(count)),1);self.assertEqual((p.scene_id,p.choice_id,p.player.toPlainText()),before)
 def test_actual_close_button_preserves_normal_close_and_veto(self):
  d,_=self.popover();QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(d.isVisible())
  class Veto(ToolPopover):
   def closeEvent(self,e):e.ignore()
  owner=QWidget();self.addCleanup(owner.close);v=Veto('未保存',QWidget(),owner);v.show();self.qt.processEvents();QTest.mouseClick(v.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.assertTrue(v.isVisible());v.hide()
 def test_title_drag_routes_to_upstream_for_this_exact_window(self):
  d,_=self.popover();bar=d.titleBar
  with patch('third_party.qframelesswindow.titlebar.startSystemMove')as move:
   e=QMouseEvent(QEvent.Type.MouseMove,QPointF(80,12),QPointF(bar.mapToGlobal(QPoint(80,12))),Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier);QApplication.sendEvent(bar,e);self.assertEqual(move.call_count,1);self.assertIs(move.call_args.args[0],d)
 def test_title_double_click_does_not_maximize_reference_window(self):
  d,_=self.popover();before=d.size();QTest.mouseDClick(d.titleBar,Qt.MouseButton.LeftButton,pos=QPoint(80,12));self.qt.processEvents();self.assertFalse(d.isMaximized());self.assertEqual(d.size(),before)
 def test_native_eight_resize_edges_are_accepted_only_for_owned_window(self):
  if sys.platform!='win32':self.skipTest('Actual Win32 dispatch only; portable geometry tests still run.')
  import win32gui,win32api,win32con
  d,_=self.popover();h=int(d.winId());_,_,w,height=win32gui.GetClientRect(h)
  rows=[((1,1),win32con.HTTOPLEFT),((w-1,1),win32con.HTTOPRIGHT),((1,height-1),win32con.HTBOTTOMLEFT),((w-1,height-1),win32con.HTBOTTOMRIGHT),((w//2,1),win32con.HTTOP),((w//2,height-1),win32con.HTBOTTOM),((1,height//2),win32con.HTLEFT),((w-1,height//2),win32con.HTRIGHT)]
  for pos,expected in rows:
   with patch.object(win32api,'GetCursorPos',return_value=win32gui.ClientToScreen(h,pos)):self.assertEqual(win32gui.SendMessage(h,win32con.WM_NCHITTEST,0,0),expected)
 def test_layout_keeps_header_close_and_reading_inside_actual_sizes(self):
  d=self.event()
  for size in[(760,600),(900,650),(1000,720)]:
   d.resize(*size);self.qt.processEvents();self.assertEqual((d.width(),d.height()),size);self.assertTrue(d.rect().contains(d.titleBar.geometry()));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()));self.assertGreater(d.titleBar.closeBtn.x(),d.titleBar.geometry().right());self.assertLess(d.titleBar.geometry().bottom(),d.panel.geometry().top());self.assertGreater(d.panel.player.height(),80)
 def test_seven_families_and_direct_battle_share_actual_external_frame(self):
  from rouge.current_encounters_view import CurrentEncountersDialog
  from rouge.current_resource_events_view import CurrentResourceEventsDialog
  from rouge.current_exit_view import CurrentExitDialog
  from rouge.current_memory_tree_view import CurrentMemoryTreeDialog
  from rouge.box_event_view import BoxEventDialog
  from rouge.documented_event_flow_view import DocumentedEventFlowDialog
  from rouge.current_battle_view import CurrentBattleDialog
  from rouge import current_resource_events,documented_event_flows
  factories=[lambda:CurrentEncountersDialog('黑诞'),lambda:CurrentResourceEventsDialog(current_resource_events.GOLD_EVENTS[0]),CurrentExitDialog,CurrentMemoryTreeDialog,BoxEventDialog,lambda:DocumentedEventFlowDialog(next(iter(documented_event_flows.packet()['data']['events']))),lambda:CurrentBattleDialog('ro6_n_1_2')]
  for factory in factories:
   d=factory();self.addCleanup(d.close);d.show();self.qt.processEvents();self.assertIsInstance(d,PlayerDialog);self.assertIs(d.layout().itemAt(0).widget(),d.titleBar);self.assertGreater(d.panel.height(),0);self.assertTrue(d.titleBar.closeBtn.isVisible());d.close()
 def test_owned_screen_change_refresh_does_not_activate_or_restack(self):
  if sys.platform!='win32':self.skipTest('Actual Win32 screen handler only.')
  import win32gui,win32con
  d,_=self.popover()
  with patch.object(win32gui,'SetWindowPos')as call:
   d._WindowsFramelessWindowBase__onScreenChanged();self.assertEqual(call.call_count,1);args=call.call_args.args;self.assertEqual(args[0],int(d.winId()));self.assertTrue(args[-1]&win32con.SWP_NOACTIVATE);self.assertTrue(args[-1]&win32con.SWP_NOZORDER);self.assertTrue(args[-1]&win32con.SWP_FRAMECHANGED)
 def test_header_resources_wrap_without_clipping_or_losing_navigation(self):
  from PySide6.QtWidgets import QTabBar,QPushButton
  from rouge.player_resource_strip import ResourceStrip
  d,_=self.popover('dark');nav=QTabBar()
  for name in ['收藏品 123','道具 5','零件箱 17/17','商店记录']:nav.addTab(name)
  res=ResourceStrip({},dark=True,leading=(nav,QPushButton('干员 49')));d.title_label.hide();d.header_bar.insertWidget(0,res,1)
  for width in [480,640,900,1200]:
   d.resize(width,540);QTest.qWait(20);self.qt.processEvents();self.assertGreaterEqual(res.height(),res.flow.heightForWidth(res.width()));self.assertTrue(d.rect().contains(d.titleBar.geometry()));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()));self.assertGreater(d.titleBar.closeBtn.x(),d.titleBar.geometry().right());self.assertEqual(nav.count(),4)
 def test_pin_flag_changes_keep_native_resizing_style(self):
  if sys.platform!='win32':self.skipTest('Actual Win32 style only.')
  import win32gui,win32con
  d,_=self.popover()
  for value in [True,False,True]:
   d.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,value);d.show();self.qt.processEvents();self.assertTrue(win32gui.GetWindowLong(int(d.winId()),win32con.GWL_STYLE)&win32con.WS_THICKFRAME)
if __name__=='__main__':unittest.main()
