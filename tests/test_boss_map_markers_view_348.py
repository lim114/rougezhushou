from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge import boss_map_markers as model,current_action_positions as actions,current_battle_reference as battle
from rouge.current_map_position_view import CurrentMapPositionDialog
from rouge.current_action_positions_view import CurrentActionPositionsDialog
from rouge.current_battle_view import CurrentBattleDialog
from tests.test_boss_map_markers_348 import clone
class BossMapMarkersView348Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,sid='ro6_b_4'):
        d=CurrentMapPositionDialog(sid);d.show();self.addCleanup(d.close);self.qt.processEvents();return d
    def test_all75_symbol_points_scale_with_two_window_sizes_and_other_cells_clear(self):
        for sid in model.STAGES:
            d=self.dialog(sid);p=d.panel;self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center());self.assertEqual(p.combo.count(),len(p.result['points'])+1)
            for w,h in[(850,440),(1300,900)]:
                d.resize(w,h);self.qt.processEvents()
                for q in p.result['points']:
                    p.select_cell(q['row'],q['col']);actual=p.original.point_center();rect=p.original.image_rect();self.assertAlmostEqual(actual.x(),rect.left()+q['pixel'][0]*rect.width()/512);self.assertAlmostEqual(actual.y(),rect.top()+q['pixel'][1]*rect.height()/286);self.assertIn('不是敌人实际脚点',p.player.toPlainText());self.assertIn('标志',p.combo.currentText())
            unknown=next((r,c)for r in range(p.result['rows'])for c in range(p.result['cols'])if not any(q['row']==r and q['col']==c for q in p.result['points']));self.assertTrue(p.select_cell(*unknown));self.assertIsNone(p.original.point_center());QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=p.original.image_rect().center().toPoint());self.assertEqual(p.selected,unknown);d.close()
    def test_same_parent_refresh_keeps_two_nonzero_readers_and_visible_marker(self):
        d=CurrentBattleDialog('ro6_b_4');self.addCleanup(d.close);d.show();self.qt.processEvents();self.assertTrue(d.panel.open_map_positions());child=d.panel.position_dialog;child.resize(850,440);p=child.panel;p.select_cell(6,0);p.player.setFixedHeight(52);p.technical.setFixedHeight(52);self.qt.processEvents()
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected);self.assertTrue(d.panel.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected))
        self.assertIsNotNone(p.original.point_center());d.close();self.assertFalse(child.isVisible())
    def test_new_source_loss_clears_map_and_selection_then_manual_recovery(self):
        p=self.dialog().panel;p.select_cell(6,0)
        with TemporaryDirectory()as f:
            root=Path(f);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.grid.result);self.assertTrue(p.original.pixmap.isNull());self.assertEqual(p.technical.toPlainText(),'');file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center())
    def test_action_position_target_symbol_own_scope_and_repeated_window_close(self):
        sid='ro6_b_1';a=next(a for a in battle.stage_reference(sid)['actions']if a['raw']['actionType']=='SPAWN'and a['queue']['kind']=='main');d=CurrentActionPositionsDialog(sid,a['key']);self.addCleanup(d.close);d.show();self.qt.processEvents();p=d.panel;entry=next(e for e in p.result['entries']if e['label']=='终点参考格');p.combo.setCurrentIndex(p.combo.findData(entry['key']));self.assertIsNotNone(p.original.point_center());self.assertIn('原图可见标志位置',p.player.toPlainText());self.assertIsNone(p.result['actual_path'])
        parent=CurrentBattleDialog(sid);self.addCleanup(parent.close);parent.show();self.qt.processEvents();parent.panel.open_map_positions();old=parent.panel.position_dialog;parent.panel.open_map_positions();self.assertFalse(old.isVisible());child=parent.panel.position_dialog;parent.close();self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
