from copy import deepcopy
from unittest.mock import patch
import unittest
import shiboken6
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from rouge.player_window_frame import PlayerDialog
from rouge.current_enemy_spawns_view import CurrentEnemySpawnsDialog
from rouge.current_action_positions_view import CurrentActionPositionsDialog
from rouge.current_event_battles_view import CurrentEventBattlesDialog
from rouge.current_stage_objects_view import CurrentStageObjectsDialog
from rouge.current_battle_view import CurrentBattlePanel


class BattleReferenceChainReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,constructor,*args):
  d=constructor(*args);self.addCleanup(d.close);d.show();QTest.qWait(30);return d
 def assert_frame(self,d,size):
  self.assertIsInstance(d,PlayerDialog);self.assertEqual(d.objectName(),'mapReferenceWindow');area=d.screen().availableGeometry();self.assertEqual((d.width(),d.height()),(min(size[0],area.width()-40),min(size[1],area.height()-40)));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()));self.assertTrue(all(not b.autoDefault()for b in d.findChildren(QPushButton)))
 def test_five_reference_classes_share_native_frame_theme_and_real_sizes(self):
  for ctor,args,size in[(CurrentEnemySpawnsDialog,('ro6_n_1_1','5'),(760,600)),(CurrentActionPositionsDialog,('ro6_n_2_3','1'),(960,640)),(CurrentEventBattlesDialog,('鸭托邦','choice_ro6_bat3_5'),(760,600)),(CurrentStageObjectsDialog,('ro6_n_1_1',),(760,600))]:
   d=self.dialog(ctor,*args);self.assert_frame(d,size);self.assertIsNotNone(d.panel.result)
  p=d.panel;p.entries.setCurrentIndex(1);self.assertTrue(p.open_position());self.assert_frame(p.position_dialog,(960,640));self.assertIsNotNone(p.position_dialog.panel.result)
 def test_enemy_full_and_home_views_hide_only_empty_numeric_columns_and_restore_real_zero(self):
  p=CurrentBattlePanel('ro6_n_2_6');p.show();self.addCleanup(p.close);self.qt.processEvents();key=p.result['enemies'][0]['key'];old=deepcopy(p.result)
  for v in(p.quick_table,p.enemy_overview.tree):self.assertEqual([i for i in range(7)if not v.isColumnHidden(i)],[0,5,6]);self.assertEqual(v.model().columnCount(),7)
  p.enemy_forecasts={key:{'environment_component':{'atk':0,'magicResistance':0},'conditions_label':'公开布局对照，不是实际面板'}};p._sync_enemy_grid();self.qt.processEvents()
  for v in(p.quick_table,p.enemy_overview.tree):self.assertEqual([i for i in range(7)if not v.isColumnHidden(i)],[0,2,4,5,6])
  p.enemy_forecasts={};p._sync_enemy_grid()
  for v in(p.quick_table,p.enemy_overview.tree):self.assertEqual([i for i in range(7)if not v.isColumnHidden(i)],[0,5,6])
  self.assertEqual(p.result,old);self.assertIn('完整',p.enemy_overview.notice.text());self.assertIn('尚未核验',p.enemy_overview.notice.text())
 def test_spawns_close_clears_original_reference_and_refresh_keeps_manual_size(self):
  d=self.dialog(CurrentEnemySpawnsDialog,'ro6_n_1_1','5');p=d.panel;p.entries.setCurrentIndex(1);before=deepcopy(p.result);d.resize(800,650);self.assertTrue(p.refresh_reference());self.assertEqual(p.result,before);self.assertEqual((d.width(),d.height()),(800,650));QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(d.isVisible());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'')
 def test_objects_normal_close_clears_owned_position_source(self):
  d=self.dialog(CurrentStageObjectsDialog,'ro6_n_1_1');p=d.panel;p.entries.setCurrentIndex(1);self.assertTrue(p.open_position());child=p.position_dialog;QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(d.isVisible());self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result)
 def test_exact_event_stage_entry_remains_explicit_and_closes_with_parent(self):
  d=self.dialog(CurrentEventBattlesDialog,'鸭托邦','choice_ro6_bat3_5');p=d.panel;self.assertIsNone(p.stages.currentData());self.assertFalse(p.open_battle());p.stages.setCurrentIndex(1);self.assertTrue(p.open_battle());child=p.battle_dialog;self.assertEqual(child.panel.stage_id,p.stages.currentData());QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertFalse(shiboken6.isValid(child));self.assertIsNone(p.battle_dialog)
