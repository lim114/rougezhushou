"""Source-qualified first-floor symbols, with base-map fallback on data loss."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt,QPointF
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import observed_map_symbols as extra,current_map_position as model
from rouge.current_map_position_view import CurrentMapPositionPanel


class FloorMapSymbolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([]);cls.base=model.packet()

    def test_eight_exact_configurations_cover_every_declared_entrance_and_goal(self):
        raw=(extra.ROOT/extra.DATA).read_bytes();self.assertEqual(sha256(raw).hexdigest(),extra.DATA_SHA256);data=json.loads(raw)
        self.assertEqual(tuple(data['bindings']),extra.STAGES);self.assertEqual(len(extra.STAGES),8)
        totals=[]
        for sid in extra.STAGES:
            row=data['bindings'][sid];result=model.stage_reference(sid);self.assertIsNotNone(result)
            self.assertEqual(row['expected_stage'],self.base['current']['version']['current']['details']['stages'][sid]);self.assertEqual(result['points'],row['points']);self.assertEqual(result['is_elite'],row['expected_stage']['isElite'])
            expected={(r,c,t['tileKey'])for r,grid in enumerate(result['map'])for c,i in enumerate(grid)for t in [result['tiles'][i]]if t['tileKey']in('tile_start','tile_end')}
            self.assertEqual({(p['row'],p['col'],p['tile_key'])for p in result['points']},expected)
            self.assertTrue(all(p['kind']=='visible_map_symbol'for p in result['points']));self.assertFalse(result['supports_inverse']);self.assertFalse(result['supports_segments']);totals.append(len(result['points']))
        self.assertEqual(totals,[3,3,3,3,2,2,3,3])

    def test_measurements_match_original_images_and_bounded_visible_regions(self):
        observations=json.loads((extra.ROOT/'research/floor-map-472/observations.json').read_bytes())['observations'];self.assertEqual(len(observations),11)
        for o in observations:
            path=extra.ROOT/'rouge/data/battle-maps'/(o['stage']+'.png');self.assertEqual(sha256(path.read_bytes()).hexdigest(),o['image_sha256'])
            x,y,w,h=o['largest_component_box'];self.assertEqual(o['pixel'],[x+(w-1)/2,y+(h-1)/2]);self.assertGreater(o['component_pixels'],0)
            x0,y0,x1,y1=o['manual_roi'];self.assertTrue(x0<=o['pixel'][0]<x1 and y0<=o['pixel'][1]<y1)
            r=model.stage_reference(o['stage']);point=next(p for p in r['points']if(p['row'],p['col'])==(o['row'],o['col']));self.assertEqual(point['pixel'],o['pixel'])

    def test_corrupt_or_missing_supplement_removes_points_keeps_qualified_bitmap(self):
        original=model.stage_reference(extra.STAGES[0]);self.assertTrue(original['points'])
        with TemporaryDirectory()as folder:
            root=Path(folder);p=root/extra.DATA;p.parent.mkdir(parents=True);p.write_bytes((extra.ROOT/extra.DATA).read_bytes()+b' ')
            with patch.object(extra,'ROOT',root):
                fresh=model.stage_reference(extra.STAGES[0]);self.assertEqual(fresh['points'],[]);self.assertEqual(fresh['image'],original['image']);self.assertNotEqual(fresh['source_identity'],original['source_identity'])
                p.unlink();self.assertEqual(model.stage_reference(extra.STAGES[0])['points'],[])

    def test_changed_stage_identity_or_geometry_cannot_keep_old_positions(self):
        sid=extra.STAGES[0];fresh=deepcopy(self.base);fresh['current']['version']['current']['details']['stages'][sid]['name']='synthetic changed name'
        with patch.object(model,'packet',return_value=fresh):self.assertEqual(model.stage_reference(sid)['points'],[])
        fresh=deepcopy(self.base);key='levels/'+fresh['current']['version']['current']['details']['stages'][sid]['levelId'].lower()+'.json';fresh['current']['inputs']['levels'][key]['cameraPlugin']='synthetic changed camera'
        with patch.object(model,'packet',return_value=fresh):self.assertIsNone(model.stage_reference(sid))

    def test_original_marker_click_selects_source_tile_in_ordinary_and_emergency(self):
        for sid in('ro6_n_1_2','ro6_e_1_2'):
            p=CurrentMapPositionPanel(sid);p.resize(1000,700);p.show();self.qt.processEvents();self.addCleanup(p.close);point=p.result['points'][0];rect=p.original.image_rect()
            pos=QPointF(rect.left()+rect.width()*point['pixel'][0]/p.original.pixmap.width(),rect.top()+rect.height()*point['pixel'][1]/p.original.pixmap.height()).toPoint()
            QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=pos);self.qt.processEvents();self.assertEqual(p.selected,(point['row'],point['col']));self.assertEqual(p.combo.currentIndex(),1)

    def test_warm_ui_clears_old_marker_after_supplement_loss(self):
        p=CurrentMapPositionPanel(extra.STAGES[0]);p.show();self.addCleanup(p.close);self.assertIn('点选原图编号',p.player.toPlainText());self.assertNotIn('不插值',p.player.toPlainText());self.assertIn('不插值',json.loads(p.technical.toPlainText())['完整说明']);p.combo.setCurrentIndex(1);self.assertIsNotNone(p.selected)
        with patch.object(extra,'mapping_for',return_value=None):self.assertTrue(p.refresh_reference())
        self.assertIsNone(p.selected);self.assertEqual(p.original.markers,[]);self.assertIsNone(p.original.point_center());self.assertFalse(p.original.pixmap.isNull())


if __name__=='__main__':unittest.main()
