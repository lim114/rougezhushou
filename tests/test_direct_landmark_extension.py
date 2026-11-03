"""New fixed-map coverage with old references kept and uncertain pixels denied."""
import copy,hashlib,json,math,unittest
from unittest.mock import patch
from rouge.battle_preview import battle_data,spawn_rows,DATA
from rouge.fixed_landmark_mapping import landmark_data
from rouge.map_projection import projection_for,projection_data
from scripts.extend_direct_landmark_references import build,BASE,OUTPUT
NEW=('ro6_n_3_3','ro6_e_3_3','ro6_n_6_1')
def projection(stage):
 image=stage['image'];return projection_for(stage,image['sha256'],(image['width'],image['height']))
class DirectLandmarkExtensionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.output,cls.receipt=build()
 def test_two_new_originals_three_stage_bindings_and_prior_eight_centers_kept(self):
  prior=json.loads((BASE/'prior-landmark-references.json').read_text(encoding='utf8'));current=landmark_data()
  for group in ('references','stages'):
   for key,value in prior[group].items():self.assertEqual(self.output[group][key],value)
   for key,value in self.output[group].items():self.assertEqual(current[group][key],value)
  self.assertEqual(set(self.output['stages'])-set(prior['stages']),set(NEW))
  self.assertEqual((self.receipt['new_partial_images'],self.receipt['new_partial_stage_bindings']),(2,3));self.assertEqual(self.receipt['prior_partial_points'],8)
  for group in ('calibrations','stages'):
   for key,value in json.loads((BASE/'prior-regular-projections.json').read_text(encoding='utf8'))[group].items():self.assertEqual(projection_data()[group][key],value)
  self.assertEqual(self.receipt['complete_calibration_added'],0);self.assertFalse(self.receipt['absolute_position_accuracy_verified'])
  self.assertEqual(self.receipt['new_accepted_points'],9);self.assertEqual(self.receipt['new_rejected_or_unknown_points'],6)
  self.assertEqual(self.receipt['total_partial_points'],17)
  self.assertEqual([v['id'] for v in self.receipt['excluded_aliases']],['ro6_e_6_1'])
  self.assertIsNone(projection(battle_data()['stages']['ro6_e_6_1']))
  self.assertNotEqual(battle_data()['stages']['ro6_e_6_1']['image']['sha256'],battle_data()['stages']['ro6_n_6_1']['image']['sha256'])
 def test_each_new_requested_reading_is_original_and_agreement_gate_never_relaxed(self):
  author=json.loads((BASE/'author-readings-frozen.json').read_text(encoding='utf8'))
  reader=json.loads((BASE/'independent-reader-frozen.json').read_text(encoding='utf8'));self.assertIs(reader['author_pixel_values_or_fits_read'],False)
  self.assertEqual(self.receipt['new_requested_points'],15)
  for result in self.receipt['new_agreement_comparisons']:
   sid=result['reference'];key=(result['row'],result['col']);first=next(p for p in author['maps'][sid]['points'] if (p['row'],p['col'])==key);peer=next(p for p in reader['maps'][sid]['points'] if (p['row'],p['col'])==key)
   self.assertEqual(result['observed_pixel'],first['pixel']);self.assertEqual(result['independent_pixel'],peer['pixel'])
   if result['agreement_px'] is not None:self.assertEqual(result['agreement_px'],math.dist(first['pixel'],peer['pixel']))
   p=projection(battle_data()['stages'][sid]);actual=p.project(dict(zip(('row','col'),key)))
   self.assertEqual(actual,tuple(first['pixel']) if result['accepted_for_runtime'] else None)
   self.assertEqual(result['accepted_for_runtime'],result['agreement_px'] is not None and result['agreement_px']<=4)
 def test_every_new_stage_denies_unknown_fractional_cells_and_all_inverse_pixels(self):
  for sid in NEW:
   stage=battle_data()['stages'][sid];p=projection(stage);known={(r,c):(x,y) for r,c,x,y in p.points}
   self.assertFalse(p.supports_segment_reference)
   for r,row in enumerate(stage['map']):
    for c,_ in enumerate(row):self.assertEqual(p.project({'row':r,'col':c}),known.get((r,c)))
   for r,c,x,y in p.points:
    self.assertIsNone(p.cell_at(x,y));self.assertIsNone(p.cell_at(x+.1,y));self.assertIsNone(p.project({'row':r+.1,'col':c}));self.assertIsNone(p.project({'row':True,'col':c}))
 def test_exact_source_bytes_grid_alias_file_size_and_level_identity(self):
  for sid in NEW:
   stage=battle_data()['stages'][sid];p=projection(stage);self.assertIsNotNone(p)
   self.assertEqual(hashlib.sha256((DATA/stage['image']['file']).read_bytes()).hexdigest(),stage['image']['sha256'])
   for kind in ('id','path','level','image','size','tile'):
    bad=copy.deepcopy(stage)
    if kind=='id':bad['id']='unsupported-similar-map'
    elif kind=='path':bad['image']['file']='wrong-path.png'
    elif kind=='level':bad['level_source']['sha256']='changed'
    elif kind=='image':bad['image']['sha256']='f'*64
    elif kind=='size':bad['image']['width']+=1
    else:bad['tiles'][bad['map'][p.points[0][0]][p.points[0][1]]]['heightType']='HIGHLAND'
    self.assertIsNone(projection(bad),(sid,kind))
   self.assertIsNone(projection_for(stage,'f'*64,(512,286)));self.assertIsNone(projection_for(stage,stage['image']['sha256'],(511,286)))
 def test_unchanged_source_build_is_readonly_and_uses_no_actual_game_or_chat(self):
  paths=[p for p in BASE.iterdir() if p.is_file()]+[OUTPUT,DATA/'battle-map-projections.json'];before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
  self.assertEqual(build(),(self.output,self.receipt));self.assertEqual({p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},before)
  for key in ('game_actions','chat_requests','live_samples'):self.assertEqual(self.receipt[key],0)
class DirectLandmarkExtensionWidgetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from PySide6.QtWidgets import QApplication
  cls.app=QApplication.instance() or QApplication([])
 def test_new_points_scale_without_unknown_markers_at_three_aspect_ratios(self):
  from rouge.battle_view import MapOriginal
  for sid in NEW:
   stage=battle_data()['stages'][sid];v=MapOriginal();v.set_file(DATA/stage['image']['file']);v.set_reference(stage,spawn_rows(sid));self.assertFalse(v.pixmap.isNull())
   for size in ((1024,572),(640,720),(1600,500)):
    v.resize(*size);v.show();self.app.processEvents();rect=v.image_rect()
    for r,c,x,y in v.projection.points:
     point=v.cell_center({'row':r,'col':c});self.assertAlmostEqual(point.x(),rect.left()+x*rect.width()/512);self.assertAlmostEqual(point.y(),rect.top()+y*rect.height()/286);self.assertIsNone(v.cell_at(point))
    self.assertTrue(set(v.marker_cells())<={(r,c) for r,c,*_ in v.projection.points});self.assertFalse(v.grab().isNull())
   v.close()
 def test_real_grid_selection_maps_source_or_tile_cell_and_refresh_preserves_it(self):
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  from rouge.battle_view import BattlePreviewPanel
  for sid in NEW:
   p=BattlePreviewPanel();p.resize(1450,1000);p._load_stage(sid);p.show();self.app.processEvents()
   cells=[{'row':r,'col':c} for r,c,*_ in p.original.projection.points]
   ordinary=[cell for cell in cells if not any(row['route']['start']==cell for row in p.rows)]
   cell=ordinary[0] if ordinary else cells[0]
   QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.cell_center(cell).toPoint());self.app.processEvents()
   self.assertIsNotNone(p.original.cell_center(cell));self.assertIn('其他位置尚未核对，不据此猜测或延伸路线',p.map_caption.text())
   if ordinary:
    self.assertEqual(p._tile_cell,cell);self.assertEqual(p.original.reference_cell,cell);text=p.spawn_detail.toPlainText();p.render_rows()
    self.assertEqual(p._tile_cell,cell);self.assertEqual(p.original.reference_cell,cell);self.assertEqual(p.spawn_detail.toPlainText(),text)
   else:
    self.assertIsNone(p._tile_cell);self.assertEqual(p.original.selected['route']['start'],cell)
    selected=p.original.selected['id'];self.assertIn((cell['row'],cell['col']),p.original.marker_cells());p.render_rows()
    self.assertEqual(p.original.selected['id'],selected);self.assertIsNotNone(p.original.cell_center(cell))
   unknown=next({'row':r,'col':c} for r,line in enumerate(battle_data()['stages'][sid]['map']) for c,_ in enumerate(line) if p.original.cell_center({'row':r,'col':c}) is None and not any(row['route']['start']=={'row':r,'col':c} for row in p.rows))
   p._cell_selected(unknown);self.assertIsNone(p.original.reference_cell);self.assertIn('位置尚未核对',p.spawn_detail.toPlainText());p.close()
 def test_new_center_reference_cannot_connect_even_directly_observed_ends(self):
  from PySide6.QtGui import QPainter
  from rouge.battle_view import MapOriginal
  calls=[]
  class Recorder(QPainter):
   def drawLine(self,*args):calls.append(args);return super().drawLine(*args)
  for sid in NEW:
   stage=battle_data()['stages'][sid];v=MapOriginal();v.set_file(DATA/stage['image']['file']);v.set_reference(stage,[]);points=[{'row':r,'col':c} for r,c,*_ in v.projection.points[:2]];v.selected={'route':{'start':None,'points':points,'continuous_reference':True}};calls.clear()
   with patch('rouge.battle_view.QPainter',Recorder):v.grab()
   self.assertEqual(calls,[]);v.close()
if __name__=='__main__':unittest.main()
