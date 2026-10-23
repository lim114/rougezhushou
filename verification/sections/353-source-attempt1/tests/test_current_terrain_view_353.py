from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import current_map_position as model,current_terrain as terrain
from rouge.current_map_position_view import CurrentMapPositionPanel


class CurrentTerrainView353Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self,sid='ro6_n_5_8'):
        panel=CurrentMapPositionPanel(sid);panel.resize(1050,640);panel.show();self.addCleanup(panel.close);self.app.processEvents();return panel
    def test_actual_terrain_branches_exact_cells_and_original_projection_admission(self):
        p=self.panel();keys={p.terrain_kind.itemData(i)for i in range(1,p.terrain_kind.count())}
        self.assertTrue({'tile_healing','tile_bigforce','tile_infection'}.issubset(keys))
        for key in keys:
            p.terrain_kind.setCurrentIndex(p.terrain_kind.findData(key));self.app.processEvents()
            rows=model.terrain_locations(p.result,key);self.assertEqual(p.terrain_cells.count(),len(rows)+1)
            self.assertEqual(p.grid.highlight_cells,{(r['row'],r['col'])for r in rows})
            self.assertIsNone(p.selected);self.assertIsNone(p.original.point)
            p.terrain_cells.setCurrentIndex(1);self.app.processEvents();cell=model.cell_reference(p.result,*p.selected)
            self.assertEqual(cell['tile']['tileKey'],key);self.assertIn(cell['terrain']['name'],p.player.toPlainText())
            self.assertEqual(p.original.point is not None,cell['mapped_to_original'])
    def test_three_actual_special_tiles_use_own_values_and_do_not_modify_result(self):
        p=self.panel();original=json.dumps(p.result,sort_keys=True)
        wanted={'tile_healing':'3%','tile_bigforce':'1个等级','tile_infection':'100点真实伤害'}
        for key,text in wanted.items():
            p.terrain_kind.setCurrentIndex(p.terrain_kind.findData(key));p.terrain_cells.setCurrentIndex(1);self.app.processEvents()
            self.assertIn(text,p.player.toPlainText());self.assertIn('没有将地形效果写入本局计算',p.player.toPlainText())
        self.assertEqual(json.dumps(p.result,sort_keys=True),original)
    def test_refresh_preserves_type_cell_and_both_nonzero_readers(self):
        p=self.panel();p.resize(950,400);p.terrain_kind.setCurrentIndex(p.terrain_kind.findData('tile_infection'));p.terrain_cells.setCurrentIndex(1);self.app.processEvents()
        for widget in(p.player,p.technical):
            p.tabs.setCurrentWidget(widget);self.app.processEvents();cursor=widget.textCursor();cursor.setPosition(2);cursor.setPosition(10,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor);self.assertGreater(widget.verticalScrollBar().maximum(),0);widget.verticalScrollBar().setValue(2)
            before=(p.terrain_kind.currentData(),p.selected,widget.textCursor().selectedText(),widget.verticalScrollBar().value(),p.tabs.currentIndex())
            self.assertTrue(p.refresh_reference());self.app.processEvents();self.assertEqual(before,(p.terrain_kind.currentData(),p.selected,widget.textCursor().selectedText(),widget.verticalScrollBar().value(),p.tabs.currentIndex()))
    def test_evidence_bytes_fail_after_warm_read_clear_and_recover_without_selection(self):
        p=self.panel();p.terrain_kind.setCurrentIndex(p.terrain_kind.findData('tile_healing'));p.terrain_cells.setCurrentIndex(1)
        with TemporaryDirectory()as folder:
            root=Path(folder);manifest=json.loads((terrain.ROOT/terrain.MANIFEST).read_bytes())
            for name in(terrain.MANIFEST,*manifest['files']):
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((terrain.ROOT/name).read_bytes())
            with patch.object(terrain,'ROOT',root):
                self.assertTrue(p.refresh_reference());path=root/terrain.NOTES;raw=path.read_bytes();path.write_bytes(raw+b'x')
                self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.terrain_kind.count(),0);self.assertEqual(p.terrain_cells.count(),0);self.assertFalse(p.grid.highlight_cells);self.assertIsNone(p.original.point)
                path.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected);self.assertIsNone(p.terrain_kind.currentData())
    def test_grid_click_can_leave_filter_without_stale_marker_or_members(self):
        p=self.panel();p.terrain_kind.setCurrentIndex(p.terrain_kind.findData('tile_healing'))
        other=next(r for r in model.terrain_locations(p.result)if r['tile_key']=='tile_infection')
        self.assertTrue(p.select_cell(other['row'],other['col']));self.app.processEvents();self.assertEqual(p.terrain_kind.currentData(),'tile_infection');self.assertEqual(p.selected,(other['row'],other['col']))
        self.assertEqual(model.terrain_locations(None),[])


if __name__=='__main__':unittest.main()
