from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt,QPointF
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import current_map_position as model
from rouge.current_map_position_view import CurrentMapPositionPanel
from rouge.current_battle_view import CurrentBattleDialog
from tests import test_current_map_position_319 as source_tests
ROOT=Path(__file__).resolve().parents[1]

class CurrentMapPositionView319Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,sid='ro6_n_6_2'):
        p=CurrentMapPositionPanel(sid);p.resize(1000,560);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def test_original_png_and_whole_grid_initially_have_no_selected_marker(self):
        p=self.panel();self.assertIsNotNone(p.result);self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center());self.assertFalse(p.original.pixmap.isNull());self.assertEqual(p.combo.count(),len(p.result['points'])+1);self.assertEqual(p.image_raw,model.battle.version.image_bytes(p.result['image']))
    def test_real_grid_click_selects_observed_center_and_scales_on_original(self):
        p=self.panel();point=p.result['points'][0];center=p.grid.center(point['row'],point['col']);QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=center.toPoint());self.qt.processEvents();self.assertEqual(p.selected,(point['row'],point['col']));self.assertIn('已标出',p.player.toPlainText());self.assertGreater(p.combo.currentIndex(),0);self.assertIn('第'+str(point['row']+1)+'行',p.combo.currentText())
        for width,height in ((840,510),(1300,850)):
            p.resize(width,height);self.qt.processEvents();rect=p.original.image_rect();actual=p.original.point_center();self.assertAlmostEqual((actual.x()-rect.left())/rect.width(),point['pixel'][0]/p.original.pixmap.width());self.assertAlmostEqual((actual.y()-rect.top())/rect.height(),point['pixel'][1]/p.original.pixmap.height())
    def test_unmapped_cell_and_original_click_never_keep_or_invent_point(self):
        p=self.panel();point=p.result['points'][0];p.select_cell(point['row'],point['col']);known={(r['row'],r['col'])for r in p.result['points']};other=next((r,c)for r in range(p.result['rows'])for c in range(p.result['cols'])if(r,c)not in known);QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.center(*other).toPoint());self.assertEqual(p.selected,other);self.assertIsNone(p.original.point_center());self.assertIn('不在原图上猜位置',p.player.toPlainText());QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=p.original.image_rect().center().toPoint());self.assertEqual(p.selected,other);self.assertFalse(p.select_cell(True,0))
    def test_real_known_cell_choice_and_both_nonzero_readers_retained(self):
        p=self.panel();p.resize(900,410);p.combo.setCurrentIndex(1);self.assertIsNotNone(p.selected);self.assertEqual(p.combo.currentIndex(),1)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected,p.combo.currentIndex());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected,p.combo.currentIndex()))
    def test_unmapped_stage_keeps_grid_and_exact_image_without_point_choices(self):
        p=self.panel('ro6_n_1_2');self.assertEqual(len(p.result['points']),0);self.assertFalse(p.combo.isEnabled());self.assertFalse(p.original.pixmap.isNull());QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.center(0,0).toPoint());self.assertEqual(p.selected,(0,0));self.assertIsNone(p.original.point_center())
    def test_actual_source_damage_clears_every_old_artifact_manual_selection_on_recovery(self):
        p=self.panel();p.combo.setCurrentIndex(1)
        with TemporaryDirectory()as folder:
            root=Path(folder);source_tests.CurrentMapPosition319Tests().clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.grid.result);self.assertTrue(p.original.pixmap.isNull());self.assertIsNone(p.original.point_center());self.assertEqual(p.technical.toPlainText(),'');file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center())
    def test_bad_decoding_cannot_keep_point_or_report_refresh_success(self):
        p=self.panel();p.combo.setCurrentIndex(1)
        with patch.object(model.battle.version,'image_bytes',return_value=b'not a PNG'):self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertTrue(p.original.pixmap.isNull())
    def test_repeat_parent_close_and_parent_source_loss_close_owned_position_dialog(self):
        d=CurrentBattleDialog('ro6_n_6_2');d.show();self.addCleanup(d.close);p=d.panel;self.assertTrue(p.open_map_positions());first=p.position_dialog;self.assertTrue(p.open_map_positions());self.assertIs(p.position_dialog,first);self.assertTrue(first.isVisible());second=p.position_dialog;d.close();self.assertFalse(second.isVisible());d.show();self.assertTrue(p.open_map_positions())
        with patch.object(model.battle,'stage_reference',return_value=None):self.assertFalse(p.open_map_positions());self.assertFalse(p.position_dialog.isVisible());self.assertFalse(p.position_button.isEnabled())

if __name__=='__main__':unittest.main()
