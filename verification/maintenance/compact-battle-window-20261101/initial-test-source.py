"""Actual compact sizes and reachable content on all original battle pages."""
import unittest
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication,QWidget,QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from rouge.current_battle_view import CurrentBattleDialog
from rouge.player_map_reader import make_reader
from rouge import current_battle_reference as model

class CompactBattleWindowReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,direct=False,sid='ro6_n_2_6'):
  owner=QWidget();self.addCleanup(owner.close);d=CurrentBattleDialog(sid,owner)if direct else make_reader('battle',{'id':sid,'title':'公开资料'},owner);self.addCleanup(d.close);d.show();self.qt.processEvents();QTest.qWait(30);return d
 def reach(self,area,widget):
  area.ensureWidgetVisible(widget);self.qt.processEvents();self.assertTrue(widget.visibleRegion().contains(widget.rect().center()))
 def test_factory_and_direct_routes_have_same_compact_default_theme_and_original_source(self):
  a=self.dialog();b=self.dialog(True);self.assertEqual(a.size(),b.size());self.assertEqual(a.objectName(),b.objectName());self.assertEqual(a.objectName(),'mapReferenceWindow');area=a.screen().availableGeometry();self.assertEqual((a.width(),a.height()),(min(800,area.width()-40),min(340,area.height()-40)));self.assertEqual(a.panel.result,b.panel.result);self.assertEqual(a.panel.tabs.count(),4)
 def test_all_original_pages_keep_real_requested_small_size_through_repeated_transitions(self):
  d=self.dialog();p=d.panel
  for w,h in((640,360),(800,340),(1040,600),(800,340)):
   d.resize(w,h)
   for i in range(4):p.tabs.setCurrentIndex(i);QTest.qWait(30);self.qt.processEvents();self.assertEqual((d.width(),d.height()),(w,h));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()))
 def test_enemy_controls_and_full_reader_are_reachable_inside_native_viewport(self):
  d=self.dialog();p=d.panel;p.tabs.setCurrentIndex(1);p.enemy_choices.select_value(p.result['enemies'][0]['key']);self.qt.processEvents();self.assertTrue(p.enemy_scroll.isAncestorOf(p.enemy_player))
  for button in p.enemy_scroll.findChildren(QPushButton):
   if not button.isHidden():self.reach(p.enemy_scroll,button)
  self.reach(p.enemy_scroll,p.enemy_player);self.assertIn('【介绍与机制】',p.enemy_player.toPlainText());self.assertGreaterEqual(p.enemy_player.viewport().visibleRegion().boundingRect().height(),p.enemy_player.fontMetrics().lineSpacing()*2)
 def test_expanded_settlement_body_is_readable_instead_of_seven_pixels(self):
  d=self.dialog();p=d.panel;p.tabs.setCurrentWidget(p.rewards);p.rewards.sections.setCurrentWidget(p.settlement);p.details_toggle.setChecked(True);self.qt.processEvents();s=p.settlement
  for widget in(s.entry,s.region,s.player):self.reach(s.body_scroll,widget)
  self.assertGreaterEqual(s.player.viewport().visibleRegion().boundingRect().height(),s.player.fontMetrics().lineSpacing()*2);self.assertTrue(s.player.toPlainText());self.assertEqual((d.width(),d.height()),(800,340));s.tabs.setCurrentIndex(1);self.reach(s.body_scroll,s.technical);self.assertTrue(s.technical.toPlainText())
 def test_wave_and_reward_actions_can_be_reached_at_compact_default(self):
  d=self.dialog();p=d.panel;p.tabs.setCurrentIndex(2);self.qt.processEvents()
  for widget in(p.queue_kind,p.action_group,p.actions,p.action_position_button,p.spawn_candidates_button,p.route_itinerary_button):self.reach(p.wave_scroll,widget)
  p.tabs.setCurrentWidget(p.rewards);self.qt.processEvents();self.reach(p.rewards.body_scroll,p.rewards.combo)
 def test_refresh_keeps_user_size_search_exact_enemy_and_reading(self):
  d=self.dialog();p=d.panel;d.resize(640,360);p.tabs.setCurrentIndex(1);enemy=p.result['enemies'][0];p.enemy_search.setText(enemy['name']);p.enemy_choices.select_value(enemy['key']);self.qt.processEvents();self.reach(p.enemy_scroll,p.enemy_player);cursor=p.enemy_player.textCursor();cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor);offset=p.enemy_scroll.verticalScrollBar().value();before=deepcopy(p.result);p.refresh_reference();self.qt.processEvents();self.assertEqual((d.width(),d.height()),(640,360));self.assertEqual(p.enemy_search.text(),enemy['name']);self.assertEqual(p.enemy_key,enemy['key']);self.assertEqual(p.result,before);self.assertEqual((p.enemy_player.textCursor().anchor(),p.enemy_player.textCursor().position()),(3,12));self.assertEqual(p.enemy_scroll.verticalScrollBar().value(),offset)
 def test_source_loss_and_recovery_do_not_restore_old_selection_or_force_default_size(self):
  d=self.dialog();p=d.panel;d.resize(640,360);p.enemy_choices.select_value(p.result['enemies'][0]['key'])
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.enemy_player.toPlainText(),'')
  self.assertTrue(p.refresh_reference());self.qt.processEvents();self.assertIsNone(p.enemy_key);self.assertEqual((d.width(),d.height()),(640,360))

if __name__=='__main__':unittest.main()
