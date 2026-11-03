import unittest,time
from copy import deepcopy
import numpy as np
from PySide6.QtCore import QRect
from rouge.player_game_map import payload
from rouge.run_config import config_data

def fixture():
 target={'hwnd':4,'pid':5};image=np.full((600,1000,3),60,np.uint8);nodes=[{'id':str(i),'center':[.25+i*.25,.5],'visible':True,'observed_type':'未知的诡秘','prediction':{'candidates':['诡意行商']},'distance':2}for i in range(3)]
 graph={'status':'matched','zone_id':'zone_1','template_id':'fixture','nodes':nodes};observation={'page':'exploration','map':graph,'texts':[{'text':config_data()['zones']['zone_1']['name'],'confidence':.99,'box':[[.35,.1],[.65,.1],[.65,.15],[.35,.15]]}]}
 source={'run_id':'one','image':image,'target':target,'captured_at':95,'client_rect':[20,40,980,580],'observation':observation};current={'image':image.copy(),'target':target,'captured_at':100,'client_rect':[20,40,980,580]};snapshot={'active':True,'foreground_on_game':True,'key':(4,5),'physical_client':(-1800,100,960,540),'logical_client':QRect(-1200,67,640,360)};return source,current,snapshot
class OverlayTests(unittest.TestCase):
 def test_source_frame_to_client_and_logical_dpi(self):
  a,b,s=fixture();r=payload(a,b,s,'one',100);self.assertIsNotNone(r);self.assertAlmostEqual(r['points'][0][1],(250-20)*640/960);self.assertAlmostEqual(r['points'][0][2],(300-40)*360/540)
 def test_changed_title_or_visible_node_pixels_hide_overlay(self):
  for x,y in ((400,65),(250,300)):
   a,b,s=fixture();b['image'][y,x]=61;self.assertIsNone(payload(a,b,s,'one',100))
 def test_target_age_geometry_run_and_foreground_boundaries(self):
  for field,value in [('target',{'hwnd':4,'pid':6}),('captured_at',97),('captured_at',101),('client_rect',[0,0,960,540])]:
   a,b,s=fixture();b[field]=value;self.assertIsNone(payload(a,b,s,'one',100))
  a,b,s=fixture();self.assertIsNone(payload(a,b,s,'two',100));s['foreground_on_game']=False;self.assertIsNone(payload(a,b,s,'one',100))
 def test_no_title_or_too_few_visible_anchors_not_displayed(self):
  a,b,s=fixture();a['observation']['texts']=[];self.assertIsNone(payload(a,b,s,'one',100))
  a,b,s=fixture();a['observation']['map']['nodes'][0]['visible']=False;self.assertIsNone(payload(a,b,s,'one',100))
 def test_nonfinite_or_outside_points_not_drawn(self):
  a,b,s=fixture();a['observation']['map']['nodes'].append({'id':'bad','center':[float('nan'),.5]});self.assertEqual(len(payload(a,b,s,'one',100)['points']),3)
