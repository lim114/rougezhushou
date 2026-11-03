"""Frozen source agreement and usable lowland-road center mapping, not planes."""
import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch

from rouge.battle_preview import battle_data,DATA,spawn_rows
from rouge.fixed_landmark_mapping import landmark_data
from rouge.map_projection import projection_for,projection_data,grid_digest
from scripts import extend_direct_landmark_288 as builder

STAGES=('ro6_t_1','ro6_t_3','ro6_e_t_3')
EXPECTED={
 'ro6_t_1':{(1,2),(1,4),(3,4),(3,5),(3,6),(4,5),(4,6),(4,7)},
 'ro6_t_3':{(1,6),(1,8),(4,6),(4,8)}}

def projected(stage):
    image=stage['image']
    return projection_for(stage,image['sha256'],(image['width'],image['height']))

class DirectRoad288Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output,cls.receipt=builder.build()

    def test_01_new_twelve_centers_keep_all_twenty_eight_prior_centers(self):
        prior=builder.read(builder.BASE/'prior-direct-references.json')
        current=landmark_data()
        for group in ('references','stages'):
            for key,value in prior[group].items():self.assertEqual(self.output[group][key],value)
            for key,value in self.output[group].items():self.assertEqual(current[group][key],value)
        self.assertEqual(set(self.output['stages'])-set(prior['stages']),set(STAGES))
        r=self.receipt
        self.assertEqual((r['new_requested_points'],r['new_accepted_points'],r['new_rejected_points']),(23,12,11))
        self.assertEqual((r['total_partial_images'],r['total_partial_stage_bindings'],r['total_partial_points']),(8,14,40))
        for sid,cells in EXPECTED.items():
            record=self.output['references'][sid]
            self.assertEqual({(p['row'],p['col']) for p in record['points']},cells)
            self.assertTrue(all(p['tile_key'] in ('tile_floor','tile_road') for p in record['points']))

    def test_02_all_pairs_remain_original_and_failed_pairs_never_enter_output(self):
        author=builder.read(builder.BASE/'author-readings-before-fit.json')
        reader=builder.read(builder.BASE/'independent-readings-before-comparison.json')
        sealed=builder.read(builder.BASE/'point-comparison.json')
        self.assertEqual(self.receipt['agreement_comparisons'],sealed['comparisons'])
        for row in self.receipt['agreement_comparisons']:
            sid=row['stage_id'];key=(row['row'],row['col'])
            first=next(p for e in author['observations'] if e['id']==sid for p in e['checks'] if tuple(p[:2])==key)
            second=next(p for p in reader['observations'][sid] if tuple(p[:2])==key)
            self.assertEqual(row['observed_pixel'],first[2:4]);self.assertEqual(row['independent_pixel'],second[2:4])
            self.assertEqual(row['agreement_px'],math.sqrt(sum((a-b)**2 for a,b in zip(first[2:4],second[2:4]))))
            self.assertEqual(row['accepted'],row['agreement_px']<=4)
            actual=next((p for p in self.output['references'][sid]['points'] if (p['row'],p['col'])==key),None)
            if row['accepted']:self.assertEqual(actual['observed_pixel'],first[2:4])
            else:self.assertIsNone(actual)
        near=[r for r in self.receipt['agreement_comparisons'] if r['squared_distance_px2']==17]
        self.assertTrue(near);self.assertTrue(all(not r['accepted'] for r in near))

    def test_03_regular_planes_and_original_failures_do_not_change_scope(self):
        regular=builder.read(builder.BASE/'prior-regular-projections.json')
        self.assertEqual(projection_data(),regular)
        self.assertEqual((len(regular['calibrations']),len(regular['stages'])),(12,24))
        self.assertEqual([r['max_error_px'] for r in self.receipt['rejected_plane_fits']],
            [5.216400541309983,4.958574758473317])
        self.assertTrue(all(not r['accepted_for_runtime'] for r in self.receipt['rejected_plane_fits']))
        self.assertEqual(self.receipt['complete_calibration_added'],0)
        self.assertEqual((self.receipt['remaining_regular_unbound_stages'],self.receipt['remaining_regular_distinct_bitmaps']),(81,59))
        self.assertNotIn('matrix',json.dumps(self.output));self.assertFalse(self.receipt['absolute_position_accuracy_verified'])

    def test_04_readonly_replay_is_deterministic_and_does_not_write_any_source(self):
        files=[p for p in builder.BASE.iterdir() if p.is_file()]+[builder.OUTPUT,DATA/'battle-map-projections.json']
        before={p:builder.sha(p) for p in files}
        self.assertEqual(builder.build(),(self.output,self.receipt))
        self.assertEqual(before,{p:builder.sha(p) for p in files})
        for name in ('game_actions','chat_requests','live_samples'):self.assertEqual(self.receipt[name],0)

    def test_05_every_manifest_and_input_pin_rejects_tampering_and_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            clone=Path(directory)/'public';shutil.copytree(builder.BASE,clone)
            with patch.object(builder,'BASE',clone):
                self.assertEqual(builder.build(),(self.output,self.receipt))
                names=['source-manifest.json',*builder.read(clone/'source-manifest.json')['files']]
                for name in names:
                    path=clone/name;original=path.read_bytes()
                    with self.subTest(name=name,mode='changed'):
                        path.write_bytes(bytes([original[0]^1])+original[1:])
                        with self.assertRaises((ValueError,OSError)):builder.build()
                        path.write_bytes(original)
                    with self.subTest(name=name,mode='missing'):
                        path.unlink()
                        with self.assertRaises((ValueError,OSError)):builder.build()
                        path.write_bytes(original)
                self.assertEqual(builder.build(),(self.output,self.receipt))

    def test_06_explicit_write_is_reviewed_idempotent_and_refuses_unknown_target(self):
        actual_before=builder.sha(builder.OUTPUT)
        with tempfile.TemporaryDirectory() as directory:
            clone=Path(directory)/'public';shutil.copytree(builder.BASE,clone)
            target=Path(directory)/'result.json';target.write_bytes((clone/'prior-direct-references.json').read_bytes())
            with patch.object(builder,'BASE',clone),patch.object(builder,'OUTPUT',target):
                before=target.read_bytes();builder.build();self.assertEqual(target.read_bytes(),before)
                builder.build(write=True);self.assertEqual(json.loads(target.read_text(encoding='utf-8')),self.output)
                written=target.read_bytes();builder.build(write=True);self.assertEqual(target.read_bytes(),written)
                target.write_bytes(b'concurrent unrelated data')
                with self.assertRaises(ValueError):builder.build(write=True)
                self.assertEqual(target.read_bytes(),b'concurrent unrelated data')
        self.assertEqual(builder.sha(builder.OUTPUT),actual_before)

    def test_07_actual_public_resolver_maps_only_registered_integer_centers(self):
        for sid in STAGES:
            stage=battle_data()['stages'][sid];p=projected(stage);self.assertIsNotNone(p,sid)
            record=self.output['references'][self.output['stages'][sid]['reference']]
            expected={(v['row'],v['col']):tuple(v['observed_pixel']) for v in record['points']}
            self.assertEqual(p.mapping_mode,'direct_verified_centers');self.assertFalse(p.supports_segment_reference)
            for r,row in enumerate(stage['map']):
                for c,_ in enumerate(row):self.assertEqual(p.project({'row':r,'col':c}),expected.get((r,c)))
            for r,c in expected:
                self.assertIsNone(p.project({'row':r+.1,'col':c}));self.assertIsNone(p.project({'row':True,'col':c}))
                self.assertIsNone(p.cell_at(*expected[r,c]));self.assertIsNone(p.cell_at(0,0))
            self.assertIsNone(p.project({'row':-1,'col':2}));self.assertIsNone(p.project({'row':float('nan'),'col':2}))

    def test_08_explicit_road_tags_are_required_while_legacy_floor_defaults_remain(self):
        stage=battle_data()['stages']['ro6_t_1']
        for tag in (None,False,1,[],{},'tile_wall','tile_forbidden','LOWLAND','tile_floor'):
            data=copy.deepcopy(self.output);data['references']['ro6_t_1']['points'][0]['tile_key']=tag
            with self.subTest(tag=tag),patch('rouge.fixed_landmark_mapping.landmark_data',return_value=data):
                self.assertIsNone(projected(stage))
        data=copy.deepcopy(self.output);data['references']['ro6_t_1']['points'][0].pop('tile_key')
        with patch('rouge.fixed_landmark_mapping.landmark_data',return_value=data):self.assertIsNone(projected(stage))
        old=next(s for s in builder.read(builder.BASE/'prior-direct-references.json')['stages'])
        self.assertIsNotNone(projected(battle_data()['stages'][old]))

    def test_09_tag_and_real_grid_height_key_must_match_even_after_digest_rebinding(self):
        for height,key in (('HIGHLAND','tile_road'),('LOWLAND','tile_wall'),('LOWLAND','tile_floor'),('LOWLAND','future_ground')):
            stage=copy.deepcopy(battle_data()['stages']['ro6_t_1']);data=copy.deepcopy(self.output)
            point=data['references']['ro6_t_1']['points'][0];r,c=point['row'],point['col']
            tile=stage['tiles'][stage['map'][r][c]];tile['heightType']=height;tile['tileKey']=key
            data['references']['ro6_t_1']['grid_sha256']=grid_digest(stage)
            with self.subTest(height=height,key=key),patch('rouge.fixed_landmark_mapping.landmark_data',return_value=data):
                self.assertIsNone(projected(stage))

    def test_10_original_four_pixel_agreement_boundary_and_finite_pixels(self):
        stage=battle_data()['stages']['ro6_t_1']
        for dx,dy,accepted in ((4,0,True),(4,1,False),(float('nan'),0,False)):
            data=copy.deepcopy(self.output);point=data['references']['ro6_t_1']['points'][0]
            point['independent_pixel']=[point['observed_pixel'][0]+dx,point['observed_pixel'][1]+dy]
            with patch('rouge.fixed_landmark_mapping.landmark_data',return_value=data):
                self.assertEqual(projected(stage) is not None,accepted)

    def test_11_each_alias_keeps_image_filename_level_grid_and_size_guards(self):
        for sid in STAGES:
            original=battle_data()['stages'][sid];self.assertIsNotNone(projected(original))
            for kind in ('id','level','path','image','size','grid'):
                stage=copy.deepcopy(original)
                if kind=='id':stage['id']='same-name-unbound'
                elif kind=='level':stage['level_source']['sha256']='changed'
                elif kind=='path':stage['image']['file']='wrong-file.png'
                elif kind=='image':stage['image']['sha256']='f'*64
                elif kind=='size':stage['image']['width']+=1
                else:stage['tiles'][stage['map'][1][2]]['heightType']='HIGHLAND'
                self.assertIsNone(projected(stage),(sid,kind))
            self.assertIsNone(projection_for(original,'f'*64,(512,286)))
            self.assertIsNone(projection_for(original,original['image']['sha256'],(511,286)))

class DirectRoad288WidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_12_source_pixels_scale_at_three_sizes_without_unknown_markers(self):
        from rouge.battle_view import MapOriginal
        for sid in STAGES:
            stage=battle_data()['stages'][sid];view=MapOriginal()
            try:
                view.set_file(DATA/stage['image']['file']);view.set_reference(stage,spawn_rows(sid))
                self.assertIsNotNone(view.projection)
                for size in ((1024,572),(640,720),(1600,500)):
                    view.resize(*size);view.show();self.app.processEvents();rect=view.image_rect()
                    for r,c,x,y in view.projection.points:
                        point=view.cell_center({'row':r,'col':c})
                        self.assertAlmostEqual(point.x(),rect.left()+x*rect.width()/512)
                        self.assertAlmostEqual(point.y(),rect.top()+y*rect.height()/286)
                        self.assertIsNone(view.cell_at(point))
                    self.assertIsNone(view.cell_center({'row':0,'col':0}))
                    self.assertFalse(view.grab().isNull())
                    self.assertTrue(set(view.marker_cells())<={(r,c) for r,c,*_ in view.projection.points})
            finally:view.close()

    def test_13_real_grid_selection_refreshes_same_center_and_unknown_clears_it(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.battle_view import BattlePreviewPanel
        for sid in STAGES:
            panel=BattlePreviewPanel()
            try:
                panel.resize(1450,1000);panel._load_stage(sid);panel.show();self.app.processEvents()
                self.assertIsNotNone(panel.original.projection)
                cell=next({'row':r,'col':c} for r,c,*_ in panel.original.projection.points
                    if not any(row['route']['start']=={'row':r,'col':c} for row in panel.rows))
                QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.cell_center(cell).toPoint())
                self.app.processEvents();self.assertEqual(panel._tile_cell,cell);self.assertEqual(panel.original.reference_cell,cell)
                text=panel.spawn_detail.toPlainText();self.assertIn('已标出',text)
                panel.render_rows();self.app.processEvents()
                self.assertEqual(panel.original.reference_cell,cell);self.assertEqual(panel.spawn_detail.toPlainText(),text)
                panel.set_context({'security_level':1});self.assertEqual(panel.original.reference_cell,cell)
                unknown={'row':0,'col':0};panel._cell_selected(unknown)
                self.assertIsNone(panel.original.reference_cell);self.assertIsNone(panel.original.cell_center(unknown))
                self.assertIn('位置尚未核对',panel.spawn_detail.toPlainText())
            finally:panel.close()

    def test_14_direct_known_ends_never_draw_a_segment_or_infer_original_clicks(self):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPainter
        from PySide6.QtTest import QTest
        from rouge.battle_view import MapOriginal
        calls=[]
        class Recorder(QPainter):
            def drawLine(self,*args):calls.append(args);return super().drawLine(*args)
        for sid in STAGES:
            stage=battle_data()['stages'][sid];view=MapOriginal()
            try:
                view.resize(1024,572);view.set_file(DATA/stage['image']['file']);view.set_reference(stage,[])
                self.assertIsNotNone(view.projection)
                cells=[{'row':r,'col':c} for r,c,*_ in view.projection.points[:2]]
                view.selected={'route':{'start':None,'points':cells,'continuous_reference':True}}
                calls.clear()
                with patch('rouge.battle_view.QPainter',Recorder):view.grab()
                self.assertEqual(calls,[])
                view.show();self.app.processEvents();clicked=[];view.cellSelected.connect(clicked.append)
                QTest.mouseClick(view,Qt.MouseButton.LeftButton,pos=view.cell_center(cells[0]).toPoint())
                self.app.processEvents();self.assertEqual(clicked,[])
            finally:view.close()

if __name__=='__main__':unittest.main()
