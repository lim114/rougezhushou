from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_map_markers as model
from rouge.current_map_position_view import CurrentMapPositionDialog
from rouge.current_action_positions_view import CurrentActionPositionsDialog
from tests.test_current_map_markers_337 import clone

class CurrentMapMarkersView337Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,sid='ro6_b_7'):
        d=CurrentMapPositionDialog(sid);d.show();self.addCleanup(d.close);self.qt.processEvents();return d
    def test_all16_symbols_scale_to_actual_original_without_inverse_or_unmeasured_markers(self):
        for sid in model.STAGES:
            d=self.dialog(sid);p=d.panel;self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center());self.assertEqual(p.combo.count(),9)
            for w,h in[(850,440),(1300,900)]:
                d.resize(w,h);self.qt.processEvents()
                for point in p.result['points']:
                    self.assertTrue(p.select_cell(point['row'],point['col']));center=p.original.point_center();rect=p.original.image_rect();self.assertAlmostEqual(center.x(),rect.left()+point['pixel'][0]*rect.width()/512);self.assertAlmostEqual(center.y(),rect.top()+point['pixel'][1]*rect.height()/286);self.assertIn('标志',p.player.toPlainText());self.assertIn('标志',p.combo.currentText())
            self.assertTrue(p.select_cell(1,1));self.assertIsNone(p.original.point_center());self.assertIn('尚未核对',p.player.toPlainText())
    def test_same_source_refresh_keeps_two_nonzero_readers_and_symbol_selection(self):
        d=self.dialog();d.resize(850,440);p=d.panel;p.select_cell(7,6)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));prior=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected);self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(prior,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.selected))
    def test_source_failure_clears_grid_and_symbol_then_manual_recovery_and_action_reader(self):
        p=self.dialog().panel;p.select_cell(7,6)
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.grid.result);self.assertTrue(p.original.pixmap.isNull());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected);self.assertIsNone(p.original.point_center())
        d=CurrentActionPositionsDialog('ro6_b_7','0');d.show();self.addCleanup(d.close);self.qt.processEvents();a=d.panel;key=next(e['key']for e in a.result['entries']if e['label']=='终点参考格');a.combo.setCurrentIndex(a.combo.findData(key));self.qt.processEvents();self.assertIsNotNone(a.original.point_center());self.assertIn('原图可见标志位置',a.player.toPlainText())
if __name__=='__main__':unittest.main()
