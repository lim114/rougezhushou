"""Frozen direct nominal centers: exact mapping boundaries and real Qt actions."""
import copy,hashlib,json,math,unittest
from unittest.mock import patch
from rouge.battle_preview import battle_data,spawn_rows,DATA
from rouge.map_projection import projection_for,projection_data
from rouge.fixed_landmark_mapping import landmark_data
from scripts.build_fixed_landmark_references import build,BASE,OUTPUT
STAGES=('ro6_n_6_2','ro6_e_6_2','ro6_n_4_4','ro6_e_4_4')
def projection(stage):
 image=stage['image'];return projection_for(stage,image['sha256'],(image['width'],image['height']))
class DirectLandmarkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.output,cls.receipt=build()
 def test_frozen_eight_acceptances_and_eight_rejections_with_no_pixel_changes(self):
  current=landmark_data()
  for group in ('references','stages'):
   for key,value in self.output[group].items():self.assertEqual(current[group][key],value)
  r=self.receipt
  self.assertEqual((r['requested_points'],r['accepted_points'],r['rejected_points']),(16,8,8))
  self.assertEqual([len(v['points']) for v in self.output['references'].values()],[5,3])
  author=json.loads((BASE/'author-direct-readings-frozen.json').read_text(encoding='utf8'))
  peer=json.loads((BASE/'independent-reader-frozen.json').read_text(encoding='utf8'));self.assertIs(peer['author_pixel_values_or_fits_read'],False)
  for v in r['agreement_comparisons']:
   a=next(p for p in author[v['reference']] if (p['row'],p['col'])==(v['row'],v['col']))
   b=next(p for p in peer['maps'][v['reference']]['points'] if (p['row'],p['col'])==(v['row'],v['col']))
   self.assertEqual(v['observed_pixel'],a['pixel']);self.assertEqual(v['independent_pixel'],b['pixel'])
   self.assertEqual(v['agreement_px'],math.dist(a['pixel'],b['pixel']));self.assertEqual(v['accepted_for_runtime'],v['agreement_px']<=4)
  near=next(v for v in r['agreement_comparisons'] if v['reference']==STAGES[0] and (v['row'],v['col'])==(1,11))
  self.assertEqual(near['agreement_px'],math.sqrt(17));self.assertFalse(near['accepted_for_runtime'])
 def test_rejected_planes_stay_rejected_and_regular_calibration_data_unchanged(self):
  prior=json.loads((BASE/'prior-regular-projections.json').read_text(encoding='utf8'));current=projection_data()
  for group in ('calibrations','stages'):
   for k,v in prior[group].items():self.assertEqual(current[group][k],v)
  self.assertEqual((len(prior['calibrations']),len(prior['stages'])),(12,24))
  for v in self.receipt['rejected_plane_fits']:self.assertGreater(v['max_error_px'],4);self.assertFalse(v['accepted_for_runtime'])
  self.assertEqual(self.receipt['complete_calibration_added'],0)
  self.assertEqual((self.receipt['remaining_regular_unbound_stages'],self.receipt['remaining_regular_distinct_bitmaps']),(81,59))
  for sid in STAGES:self.assertNotIn(sid,prior['stages'])
  self.assertNotIn('matrix',json.dumps(self.output));self.assertFalse(self.receipt['absolute_position_accuracy_verified'])
 def test_only_registered_integer_cells_project_and_no_source_pixel_inverts(self):
  for sid in STAGES:
   stage=battle_data()['stages'][sid];p=projection(stage);record=self.output['references'][self.output['stages'][sid]['reference']]
   known={(v['row'],v['col']):v['observed_pixel'] for v in record['points']}
   self.assertEqual(p.mapping_mode,'direct_verified_centers');self.assertFalse(p.supports_segment_reference)
   for row,line in enumerate(stage['map']):
    for col,_ in enumerate(line):self.assertEqual(p.project({'row':row,'col':col}),tuple(known[(row,col)]) if (row,col) in known else None)
   for bad in (None,{}, {'row':True,'col':5},{'row':1.1,'col':5},{'row':-1,'col':5},{'row':float('nan'),'col':5},{'row':'1','col':5}):self.assertIsNone(p.project(bad))
   for x,y in known.values():
    for dx,dy in ((0,0),(.1,.1),(4,0),(99,99)):self.assertIsNone(p.cell_at(x+dx,y+dy))
 def test_all_exact_stage_level_bitmap_path_size_grid_guards_and_alias_files(self):
  for sid in STAGES:
   original=battle_data()['stages'][sid];self.assertIsNotNone(projection(original));self.assertEqual(hashlib.sha256((DATA/original['image']['file']).read_bytes()).hexdigest(),original['image']['sha256'])
   for kind in ('id','level','path','image','size','grid'):
    stage=copy.deepcopy(original)
    if kind=='id':stage['id']='unbound'
    elif kind=='level':stage['level_source']['sha256']='changed'
    elif kind=='path':stage['image']['file']='other.png'
    elif kind=='image':stage['image']['sha256']='f'*64
    elif kind=='size':stage['image']['width']+=1
    else:stage['tiles'][stage['map'][1][5]]['heightType']='HIGHLAND'
    self.assertIsNone(projection(stage),(sid,kind))
   self.assertIsNone(projection_for(original,'f'*64,(512,286)));self.assertIsNone(projection_for(original,original['image']['sha256'],(511,286)))
 def test_runtime_denies_corrupt_independent_agreement_and_nonfinite_pixels(self):
  stage=battle_data()['stages'][STAGES[0]]
  for kind in ('disagreement','nonfinite'):
   data=copy.deepcopy(self.output);v=data['references'][STAGES[0]]['points'][0]
   if kind=='disagreement':v['independent_pixel'][0]+=100
   else:v['observed_pixel'][0]=float('nan')
   with patch('rouge.fixed_landmark_mapping.landmark_data',return_value=data):self.assertIsNone(projection(stage))
 def test_rebuild_readonly_sources_production_and_no_private_interactions(self):
  paths=[p for p in BASE.iterdir() if p.is_file()]+[OUTPUT,DATA/'battle-map-projections.json'];before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
  self.assertEqual(build(),(self.output,self.receipt));self.assertEqual({p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},before)
  for k in ('game_actions','chat_requests','live_samples'):self.assertEqual(self.receipt[k],0)
class DirectLandmarkWidgetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from PySide6.QtWidgets import QApplication
  cls.app=QApplication.instance() or QApplication([])
 def test_all_four_originals_only_registered_points_scale_at_three_aspect_ratios(self):
  from rouge.battle_view import MapOriginal
  for sid in STAGES:
   stage=battle_data()['stages'][sid];view=MapOriginal();view.set_file(DATA/stage['image']['file']);view.set_reference(stage,spawn_rows(sid))
   self.assertFalse(view.pixmap.isNull());self.assertIsNotNone(view.projection)
   for size in ((1024,572),(640,720),(1600,500)):
    view.resize(*size);view.show();self.app.processEvents();rect=view.image_rect()
    for r,c,x,y in view.projection.points:
     point=view.cell_center({'row':r,'col':c});self.assertAlmostEqual(point.x(),rect.left()+x*rect.width()/512);self.assertAlmostEqual(point.y(),rect.top()+y*rect.height()/286);self.assertIsNone(view.cell_at(point))
    self.assertIsNone(view.cell_center({'row':0,'col':0}));self.assertFalse(view.grab().isNull())
   self.assertTrue(set(view.marker_cells())<={(r,c) for r,c,*_ in view.projection.points});view.close()
 def test_partial_bitmap_never_connects_registered_ends_across_unknown_cells(self):
  from PySide6.QtGui import QPainter
  from rouge.battle_view import MapOriginal
  calls=[]
  class Recorder(QPainter):
   def drawLine(self,*args):calls.append(args);return super().drawLine(*args)
  for sid,cells,expected in ((STAGES[0],[{'row':1,'col':5},{'row':1,'col':7}],0),('ro6_n_1_2',[{'row':2,'col':1},{'row':2,'col':3}],1)):
   stage=battle_data()['stages'][sid];v=MapOriginal();v.resize(1024,572);v.set_file(DATA/stage['image']['file']);v.set_reference(stage,[]);v.selected={'route':{'start':None,'points':cells,'continuous_reference':True}};calls.clear()
   with patch('rouge.battle_view.QPainter',Recorder):v.grab()
   self.assertEqual(len(calls),expected,sid);v.close()
 def test_real_grid_click_maps_known_cell_and_refresh_preserves_selection(self):
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  from rouge.battle_view import BattlePreviewPanel
  for sid in STAGES:
   p=BattlePreviewPanel();p.resize(1450,1000);p._load_stage(sid);p.show();self.app.processEvents();cell={'row':3 if sid.endswith('6_2') else 1,'col':5}
   QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.cell_center(cell).toPoint());self.app.processEvents()
   self.assertEqual(p._tile_cell,cell);self.assertEqual(p.grid.reference_cell,cell);self.assertEqual(p.original.reference_cell,cell)
   self.assertIn('已标出',p.spawn_detail.toPlainText());self.assertIn('其他位置尚未核对，不据此猜测或延伸路线',p.map_caption.text());self.assertNotIn('其他列为外推',p.map_caption.text())
   text=p.spawn_detail.toPlainText();p.render_rows();self.app.processEvents();self.assertEqual(p._tile_cell,cell);self.assertEqual(p.original.reference_cell,cell);self.assertEqual(p.spawn_detail.toPlainText(),text)
   p.set_context({'security_level':1});self.app.processEvents();self.assertEqual(p.original.reference_cell,cell);p.close()
 def test_rejected_cell_clears_old_point_and_never_gets_a_pixel(self):
  from rouge.battle_view import BattlePreviewPanel
  p=BattlePreviewPanel();p._load_stage(STAGES[0]);p._cell_selected({'row':3,'col':5});self.assertIsNotNone(p.original.reference_cell);p._cell_selected({'row':1,'col':11})
  self.assertIsNone(p.original.reference_cell);self.assertEqual(p.grid.reference_cell,{'row':1,'col':11});self.assertIn('位置尚未核对',p.spawn_detail.toPlainText());self.assertIsNone(p.original.cell_center({'row':1,'col':11}));p.close()
 def test_known_spawn_grid_selection_keeps_real_source_row_and_maps_its_nominal_start(self):
  from rouge.battle_view import BattlePreviewPanel
  p=BattlePreviewPanel();p._load_stage(STAGES[0]);cell={'row':1,'col':5};p._cell_selected(cell)
  self.assertIsNone(p._tile_cell);self.assertEqual(p.original.selected['route']['start'],cell)
  self.assertIsNotNone(p.original.cell_center(cell));self.assertIn((1,5),p.original.marker_cells())
  self.assertIn('本格共有2个资料条目',p.spawn_detail.toPlainText());selected=p.original.selected['id'];p.render_rows()
  self.assertEqual(p.original.selected['id'],selected);self.assertIsNotNone(p.original.cell_center(cell));p.close()
 def test_original_click_on_registered_pixel_does_not_emit_inferred_grid_cell(self):
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  from rouge.battle_view import MapOriginal
  stage=battle_data()['stages'][STAGES[0]];v=MapOriginal();v.resize(1024,572);v.set_file(DATA/stage['image']['file']);v.set_reference(stage,[]);v.show();self.app.processEvents();got=[];v.cellSelected.connect(got.append)
  QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=v.cell_center({'row':1,'col':5}).toPoint());self.app.processEvents();self.assertEqual(got,[]);v.close()
if __name__=='__main__':unittest.main()
