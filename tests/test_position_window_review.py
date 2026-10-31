"""Bounded owned map windows and context-safe reuse without weakening sources."""
from pathlib import Path
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge.current_battle_view import CurrentBattlePanel
from rouge.current_map_position_view import CurrentMapPositionDialog
from rouge.current_action_positions_view import CurrentActionPositionsDialog,CurrentActionPositionsPanel

ROOT=Path(__file__).resolve().parents[1]


class PositionWindowReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

 def panel(self,cls=CurrentBattlePanel):
  p=cls('ro6_n_2_3');p.show();self.addCleanup(p.close);return p

 def prior(self):
  raw=(ROOT/'research/position-window-review-20261031/before-current-battle-view.py').read_bytes()
  self.assertEqual(sha256(raw).hexdigest(),'7085628c97721cea21031b0c04c8f5c224b56e64d7c605ae2252f1bb5429eb72')
  m=ModuleType('rouge._before_position_window_parent');m.__package__='rouge';exec(compile(raw,'<verified-own-prior-parent>','exec'),m.__dict__);return m.CurrentBattlePanel

 def test_three_map_opens_keep_one_instead_of_three_owned_native_dialog_objects(self):
  counts=[]
  for cls in [self.prior(),CurrentBattlePanel]:
   p=self.panel(cls)
   for _ in range(3):self.assertTrue(p.open_map_positions());p.position_dialog.close()
   counts.append(len(p.findChildren(CurrentMapPositionDialog)))
  self.assertEqual(counts,[3,1])

 def test_three_same_action_opens_keep_one_instead_of_three_owned_dialog_objects(self):
  counts=[]
  for cls in [self.prior(),CurrentBattlePanel]:
   p=self.panel(cls);p.action_key='1'
   for _ in range(3):self.assertTrue(p.open_action_positions());p.action_position_dialog.close()
   counts.append(len(p.findChildren(CurrentActionPositionsDialog)))
  self.assertEqual(counts,[3,1])

 def test_same_action_reopen_keeps_point_tab_and_actual_text_selection(self):
  p=self.panel();p.action_key='1';p.open_action_positions();d=p.action_position_dialog;c=d.panel;c.combo.setCurrentIndex(1)
  c.tabs.setCurrentIndex(1);cursor=c.technical.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);c.technical.setTextCursor(cursor)
  prior=(c.entry_key,c.grid.selected,c.tabs.currentIndex(),cursor.selectedText());d.close();p.open_action_positions()
  self.assertIs(p.action_position_dialog,d);cursor=c.technical.textCursor();self.assertEqual(prior,(c.entry_key,c.grid.selected,c.tabs.currentIndex(),cursor.selectedText()))

 def test_same_map_reopen_keeps_selected_cell_and_original_window(self):
  p=self.panel();p.open_map_positions();d=p.position_dialog;c=d.panel;c.select_cell(6,2);selected=c.selected;d.close()
  p.open_map_positions();self.assertIs(p.position_dialog,d);self.assertEqual(c.selected,selected)

 def test_changing_action_with_same_sources_clears_old_point_in_reused_window(self):
  p=self.panel();p.action_key='1';p.open_action_positions();d=p.action_position_dialog;d.panel.combo.setCurrentIndex(1);self.assertIsNotNone(d.panel.entry_key)
  p.action_key='2';p.open_action_positions();self.assertIs(p.action_position_dialog,d)
  self.assertEqual(d.panel.result['action_key'],'2');self.assertIsNone(d.panel.entry_key);self.assertIsNone(d.panel.grid.selected)
  self.assertIsNone(d.panel.original.point_center());self.assertEqual(len(p.findChildren(CurrentActionPositionsDialog)),1)

 def test_direct_action_refresh_does_not_keep_a_point_from_another_action(self):
  c=CurrentActionPositionsPanel('ro6_n_2_3','1');self.addCleanup(c.close);c.combo.setCurrentIndex(1)
  c.action_key='2';self.assertTrue(c.refresh_reference());self.assertIsNone(c.entry_key);self.assertIsNone(c.grid.selected)

 def test_manual_reuse_detaches_old_candidate_and_enemy_window_ownership(self):
  p=self.panel();p.action_key='1';p.open_action_positions();d=p.action_position_dialog
  p.spawn_candidates_position_dialog=d;p.enemy_spawns_position_dialog=d
  p.action_key='2';p.open_action_positions();self.assertIs(p.action_position_dialog,d)
  p._spawn_source_invalidated();p._enemy_spawns_source_invalidated()
  self.assertTrue(d.isVisible());self.assertEqual(d.panel.result['action_key'],'2')

 def test_owned_candidate_and_enemy_source_failure_still_clear_their_active_map(self):
  for origin,selected,invalidate in [('spawn','_spawn_position_requested','_spawn_source_invalidated'),('enemy','_enemy_spawns_position_requested','_enemy_spawns_source_invalidated')]:
   p=self.panel();p.action_key='1';gate='_spawn_action_selected'if origin=='spawn'else'_enemy_spawns_action_selected'
   with patch.object(p,gate,return_value=True):self.assertTrue(getattr(p,selected)('1'))
   d=p.action_position_dialog;self.assertTrue(d.isVisible());getattr(p,invalidate)()
   self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result)


if __name__=='__main__':unittest.main()
