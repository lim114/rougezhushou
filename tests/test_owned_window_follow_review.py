from types import SimpleNamespace
import unittest
from PySide6.QtCore import Qt,QPoint,QRect,QEvent
from PySide6.QtWidgets import QApplication,QWidget,QDialog
from PySide6.QtTest import QTest
from shiboken6 import isValid
from rouge.player_game_binding import GameWindowBinding,retained_window
from rouge.player_compact import CompactAssistant

class CloseWindow(QDialog):
 def __init__(self,parent):super().__init__(parent);self.keep=False;self.close_calls=0
 def closeEvent(self,event):
  self.close_calls+=1
  if self.keep:event.ignore()
  else:super().closeEvent(event)

class OwnedWindowFollowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def make(self):
  owner=QWidget();owner.closing=False;owner.capture=SimpleNamespace(target={'hwnd':1,'pid':1});owner.player_notes=None;owner.public_archive=None;owner.public_statistics=None
  c=QDialog(owner);c.owner=owner;c.active_popup=None;c.hidden_windows=None;c.map_popup=None;c.game_hover=SimpleNamespace(invalidate=lambda:None);c._dock_positioned=False;c._move_dock=c.move;c.resize(120,40);c.show()
  api=SimpleNamespace(read=lambda target:None);b=GameWindowBinding(c,owner,api=api);b.timer.stop();c.game_binding=b
  def clean():
   b.close();owner.close();owner.deleteLater();self.qt.sendPostedEvents(None,QEvent.Type.DeferredDelete)
  self.addCleanup(clean);self.qt.processEvents();return owner,c,b
 def snap(self,x=100,y=100):return {'key':(123,456),'active':True,'logical_client':QRect(x,y,1000,600),'screen':self.qt.primaryScreen()}
 def child(self,parent):
  w=CloseWindow(parent);w.resize(200,100);w.show();self.qt.processEvents();return w
 def toggle(self,c):CompactAssistant.toggle_visibility(c);self.qt.processEvents()
 def test_dynamic_descendant_discovered_and_parent_first_without_registering_class(self):
  owner,c,b=self.make();p=self.child(c);d=self.child(p);other=self.child(owner);windows=b.surfaces();self.assertIn(d,windows);self.assertLess(windows.index(c),windows.index(p));self.assertLess(windows.index(p),windows.index(d));self.assertNotIn(other,windows);self.assertNotIn(owner,windows);self.assertEqual(len(windows),len(set(windows)))
 def test_owned_auxiliary_moves_by_the_same_delta_but_full_workspace_does_not(self):
  owner,c,b=self.make();d=self.child(c);outside=self.child(owner);b.apply(self.snap());d.move(200,200);outside.move(400,200);b.apply(self.snap(117,111));self.assertEqual(d.pos(),QPoint(217,211));self.assertEqual(outside.pos(),QPoint(400,200))
 def test_visible_descendants_are_captured_before_parent_hides_and_restored(self):
  owner,c,b=self.make();p=self.child(c);d=self.child(p);b.apply(self.snap());b.apply(None);self.assertEqual(set(b.suspended),{c,p,d});self.assertFalse(any(w.isVisible()for w in[c,p,d]));b.apply(self.snap());self.assertTrue(all(w.isVisible()for w in[c,p,d]));self.assertFalse(b.suspended)
 def test_accepted_close_while_already_hidden_is_not_resurrected(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());b.apply(None);self.assertTrue(d.close());self.assertEqual(d.close_calls,1);self.assertNotIn(d,b.suspended);b.apply(self.snap());self.assertFalse(d.isVisible());self.assertTrue(c.isVisible())
 def test_ignored_unsaved_close_is_dispatched_once_and_still_restores(self):
  owner,c,b=self.make();d=self.child(c);d.keep=True;b.apply(self.snap());b.apply(None);self.assertFalse(d.close());self.assertEqual(d.close_calls,1);self.assertIn(d,b.suspended);b.apply(self.snap());self.assertTrue(d.isVisible());d.keep=False
 def test_deleted_pending_window_is_skipped_without_blanket_catch(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());b.apply(None);d.deleteLater();self.qt.sendPostedEvents(None,QEvent.Type.DeferredDelete);self.assertFalse(isValid(d));b.apply(self.snap());self.assertTrue(c.isVisible());self.assertFalse(b.suspended)
 def test_parent_show_refresh_can_close_a_still_pending_child(self):
  owner,c,b=self.make()
  class Parent(QDialog):
   closing_child=False
   def showEvent(self,event):
    super().showEvent(event)
    if self.closing_child:self.child_window.close()
  p=Parent(c);p.show();d=self.child(p);p.child_window=d;b.apply(self.snap());b.apply(None);p.closing_child=True;b.apply(self.snap());self.assertTrue(p.isVisible());self.assertFalse(d.isVisible());self.assertFalse(b.suspended)
 def test_modal_operation_defers_movement_and_auto_hide_until_it_finishes(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());before=c.pos();modal=QDialog(c);modal.setModal(True);modal.show();self.qt.processEvents();self.assertIs(self.qt.activeModalWidget(),modal);b.apply(self.snap(117,111));self.assertEqual(c.pos(),before);b.apply(None);self.assertTrue(c.isVisible());self.assertTrue(modal.isVisible());modal.close();self.qt.processEvents();b.apply(None);self.assertFalse(c.isVisible());self.assertFalse(d.isVisible())
 def test_unbound_standalone_hotkey_roundtrip_keeps_visible_reader(self):
  owner,c,b=self.make();d=self.child(c);self.toggle(c);self.assertFalse(c.isVisible());self.assertFalse(d.isVisible());self.toggle(c);self.assertTrue(c.isVisible());self.assertTrue(d.isVisible())
 def test_game_hidden_memory_survives_manual_hide_and_game_return(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());b.apply(None);self.toggle(c);self.assertIsNotNone(c.hidden_windows);self.assertEqual(set(b.suspended),{c,d});b.apply(self.snap());self.assertFalse(d.isVisible());self.toggle(c);self.assertTrue(c.isVisible());self.assertTrue(d.isVisible())
 def test_manual_restore_does_not_override_unavailable_game_or_forget_pending_reader(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());self.toggle(c);b.apply(None);self.toggle(c);self.assertFalse(c.isVisible());self.assertFalse(d.isVisible());self.assertIn(d,b.suspended);b.apply(self.snap());self.assertTrue(d.isVisible())
 def test_disabling_follow_while_manually_hidden_does_not_leak_windows(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());self.toggle(c);b.set_enabled(False);self.assertFalse(c.isVisible());self.assertFalse(d.isVisible());self.toggle(c);self.assertTrue(c.isVisible());self.assertTrue(d.isVisible())
 def test_global_auxiliary_closed_while_hidden_is_not_restored(self):
  owner,c,b=self.make();owner.show();extra=self.child(owner);self.toggle(c);self.assertIn(extra,c.hidden_windows);self.assertTrue(extra.close());self.assertNotIn(extra,c.hidden_windows);self.toggle(c);self.assertFalse(extra.isVisible());self.assertTrue(owner.isVisible())
 def test_transient_hover_never_reappears_just_because_parent_restores(self):
  owner,c,b=self.make();hint=self.child(c);hint.setProperty('playerVisibility','hover');hint.pinned=False;b.apply(self.snap());b.apply(None);self.assertFalse(hint.isVisible());self.assertNotIn(hint,b.suspended);b.apply(self.snap());self.assertFalse(hint.isVisible())
 def test_pinned_reference_restores_but_an_invalidated_pin_does_not(self):
  owner,c,b=self.make();hint=self.child(c);hint.setProperty('playerVisibility','hover');hint.pinned=True;b.apply(self.snap());b.apply(None);self.assertIn(hint,b.suspended);b.apply(self.snap());self.assertTrue(hint.isVisible());b.apply(None);hint.pinned=False;b.apply(self.snap());self.assertFalse(hint.isVisible())
 def test_ephemeral_overlay_and_game_hover_are_not_replayed_by_hotkey(self):
  owner,c,b=self.make();hint=self.child(c);hint.setProperty('playerVisibility','ephemeral');hint.pinned=True;overlay=QWidget(c,Qt.WindowType.Tool);overlay.setProperty('playerVisibility','ephemeral');overlay.show();self.qt.processEvents();self.assertFalse(retained_window(hint));self.assertFalse(retained_window(overlay));self.toggle(c);self.toggle(c);self.assertFalse(hint.isVisible());self.assertFalse(overlay.isVisible());self.assertTrue(c.isVisible())
 def test_explicit_hidden_parent_close_discards_its_whole_pending_tree(self):
  owner,c,b=self.make();p=self.child(c);d=self.child(p);b.apply(self.snap());b.apply(None);self.assertTrue(p.property('playerSuspended'));self.assertTrue(d.property('playerSuspended'));self.assertTrue(p.close());self.assertNotIn(p,b.suspended);self.assertNotIn(d,b.suspended);self.assertFalse(p.property('playerSuspended'));self.assertFalse(d.property('playerSuspended'));b.apply(self.snap());self.assertFalse(p.isVisible());self.assertFalse(d.isVisible())
 def test_suspend_tags_exist_before_any_parent_hide_and_clear_on_restore(self):
  owner,c,b=self.make();p=self.child(c);d=self.child(p);b.apply(self.snap());b.apply(None);self.assertTrue(all(w.property('playerSuspended')for w in[c,p,d]));b.apply(self.snap());self.assertTrue(all(not w.property('playerSuspended')for w in[c,p,d]))
 def test_unpinned_dropped_reader_does_not_keep_a_stale_suspend_tag(self):
  owner,c,b=self.make();d=self.child(c);d.setProperty('playerVisibility','hover');d.pinned=True;b.apply(self.snap());b.apply(None);d.pinned=False;b.apply(self.snap());self.assertFalse(d.isVisible());self.assertFalse(d.property('playerSuspended'))
 def test_real_recent_event_reader_survives_temporary_hide_but_not_ordinary_hide(self):
  from rouge.player_recent_scene import RecentScenePanel
  p=RecentScenePanel(SimpleNamespace(state={'id':'public-hide-case','last_node_content':{'kind':'event','title':'呼吸的红苔'}}));self.addCleanup(p.close);p.show();p.event_choices.setCurrentIndex(1);self.assertTrue(p.open_event());d=p.event_dialog;old=d.panel.result;p.setProperty('playerSuspended',True);p.hide();self.assertIs(d.panel.result,old);self.assertIs(p.event_dialog,d);p.setProperty('playerSuspended',False);p.show();p.hide();self.assertIsNone(d.panel.result);self.assertFalse(d.isVisible())
 def test_map_reference_check_keeps_temporary_hidden_source_but_clears_manual_close(self):
  from unittest.mock import Mock
  from rouge.player_map import MapPanel
  d=QDialog();self.addCleanup(d.close);refresh=Mock(return_value=True);d.panel=SimpleNamespace(refresh_reference=refresh);d.setProperty('playerSuspended',True);owner=SimpleNamespace(reference_popup=d,reference_binding='public-source',reader_binding=lambda:'public-source',selected_reference=('fixed','event','public-event'),close_reference=Mock());MapPanel.check_reference(owner);owner.close_reference.assert_not_called();refresh.assert_called_once();d.setProperty('playerSuspended',False);MapPanel.check_reference(owner);owner.close_reference.assert_called_once()
 def test_game_move_while_unavailable_uses_last_applied_rect_without_old_frame_freshness(self):
  owner,c,b=self.make();d=self.child(c);b.apply(self.snap());d.move(200,200);b.apply(None);self.assertIsNone(b.snapshot);self.assertIsNotNone(b.previous);b.apply(self.snap(117,111));self.assertEqual(d.pos(),QPoint(217,211));self.assertTrue(d.isVisible())
if __name__=='__main__':unittest.main()
