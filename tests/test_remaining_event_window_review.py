from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.current_sand_view import CurrentSandDialog
from rouge.current_lake_view import CurrentLakeDialog
from rouge.current_ritual_view import CurrentRitualDialog
from rouge.player_window_frame import PlayerDialog


class RemainingEventWindowReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,constructor,*args):
  d=constructor(*args);self.addCleanup(d.close);d.show();self.qt.processEvents();return d
 def test_three_direct_windows_share_frame_theme_and_real_default_geometry(self):
  for constructor in(CurrentSandDialog,CurrentLakeDialog,CurrentRitualDialog):
   d=self.dialog(constructor);area=d.screen().availableGeometry();self.assertIsInstance(d,PlayerDialog);self.assertEqual(d.objectName(),'mapReferenceWindow');self.assertEqual((d.width(),d.height()),(min(760,area.width()-40),min(600,area.height()-40)));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()));self.assertGreater(d.panel.player.viewport().height(),d.panel.player.fontMetrics().lineSpacing()*4)
 def test_sand_conditions_hidden_by_default_all_eight_reachable_after_real_toggle(self):
  d=self.dialog(CurrentSandDialog);p=d.panel;self.assertTrue(p.conditions.isVisible());self.assertFalse(p.conditions.content().isVisible());self.assertFalse(p.gold.isVisible());self.assertFalse(any(x.isVisible()for x in p.controls.values()));height=p.player.height();QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertTrue(p.conditions.content().isVisible());self.assertEqual(len(p.controls),7)
  for widget in[*p.controls.values(),p.gold]:
   p.condition_scroll.ensureWidgetVisible(widget);self.qt.processEvents();self.assertTrue(widget.visibleRegion().contains(widget.rect().center()))
  self.assertGreater(p.player.viewport().height(),p.player.fontMetrics().lineSpacing()*4);QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);self.qt.processEvents();QTest.qWait(30);self.qt.processEvents();self.assertFalse(p.conditions.isExpanded());self.assertFalse(p.conditions.content().isVisible());self.assertGreaterEqual(p.player.height(),height)
 def test_sand_local_controls_and_original_reading_survive_collapse_refresh_and_resize(self):
  d=self.dialog(CurrentSandDialog,'curiosity');p=d.panel;p.controls['scope'].setCurrentIndex(p.controls['scope'].findData('history'));p.gold.setValue(50);p.choices.setCurrentRow(0);c=p.player.textCursor();c.setPosition(3);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);p.player.setTextCursor(c);before=(p.scene_id,p.choice_id,p.player.toPlainText(),deepcopy(p.result['context']),c.anchor(),c.position());p.conditions.expand();self.qt.processEvents();p.conditions.collapse();self.qt.processEvents();d.resize(640,600);self.assertTrue(p.refresh_reference());self.qt.processEvents();c=p.player.textCursor();self.assertEqual(before,(p.scene_id,p.choice_id,p.player.toPlainText(),p.result['context'],c.anchor(),c.position()));self.assertEqual((d.width(),d.height()),(640,600));self.assertFalse(p.conditions.content().isVisible())
 def test_enter_in_gold_field_does_not_toggle_conditions_or_open_unrelated_reader(self):
  d=self.dialog(CurrentSandDialog);p=d.panel;QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);QTest.qWait(30);p.condition_scroll.ensureWidgetVisible(p.gold);self.qt.processEvents();p.gold.setFocus();QTest.keyClick(p.gold,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier);QTest.keyClicks(p.gold,'50');QTest.keyClick(p.gold,Qt.Key.Key_Enter);QTest.qWait(30);self.assertEqual(p.gold.value(),50);self.assertTrue(p.conditions.isExpanded());self.assertTrue(p.gold.isVisible());self.assertIsNone(p.related_dialog)
 def test_sand_actual_source_loss_clears_children_and_recovery_does_not_reuse_old_choice(self):
  d=self.dialog(CurrentSandDialog,'curiosity');p=d.panel;p.choices.setCurrentRow(0);self.assertTrue(p.open_related());child=p.related_dialog
  with patch.object(p.reference_model,'reference',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertIsNone(p.result);self.assertFalse(child.isVisible());self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.refresh_reference());self.assertIsNone(p.choice_id)
 def test_lake_documented_result_buttons_follow_exact_scene_without_game_selection(self):
  d=self.dialog(CurrentLakeDialog);p=d.panel
  for sid,scene in p.result['scenes'].items():
   p.scene.setCurrentIndex(p.scene.findData(sid))
   for i in range(p.choices.count()):
    p.choices.setCurrentRow(i);choice=p.reference_model.choice_reference(p.result,p.scene_id,p.choice_id)
    if choice['documented_outcomes']:
     target=choice['documented_outcomes'][0]['scene_id'];QTest.mouseClick(p.outcome_buttons[0],Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertEqual(p.scene_id,target);return
  self.fail('No documented two-outcome choice found')
 def test_ritual_exact_related_battle_is_closed_with_native_parent_close(self):
  d=self.dialog(CurrentRitualDialog);p=d.panel;self.assertTrue(p.open_related());child=p.battle_dialog;self.assertEqual(child.panel.stage_id,p.result['data']['related_boss_stage_id']);QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(d.isVisible());self.assertFalse(child.isVisible())
