import unittest,time
from unittest.mock import patch
import numpy as np,cv2
from rouge.player_game_hover import HoverGate
from rouge.player_hover_match import hover_item,client_image,verify_again
from rouge import relic_recognition as icons
from rouge.player_shop_hover import shop_target,ShopNameReader

def snapshot():return {'key':(4,5),'physical_client':(100,50,960,540),'cursor':(560,300),'active':True,'cursor_on_game':True}
def specimen():
 image=np.full((540,960,3),24,np.uint8);rgba=icons._reference_image('rogue_6_relic_legacy_1');ratio=39/max(rgba.shape[:2]);rgba=cv2.resize(rgba,(round(rgba.shape[1]*ratio),round(rgba.shape[0]*ratio)),interpolation=cv2.INTER_AREA)
 h,w=rgba.shape[:2];alpha=rgba[:,:,3:4]/255;image[240:240+h,450:450+w]=(rgba[:,:,:3]*alpha+image[240:240+h,450:450+w]*(1-alpha)).astype(np.uint8)
 return image,(450+w//2,240+h//2)
class HoverTests(unittest.TestCase):
 def test_shop_text_uses_card_alignment_not_nearest_label(self):
  raw=shop_fixture();names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  found,is_shop=shop_target(raw,names,(245,170),(600,800,3))
  self.assertTrue(is_shop);self.assertEqual(found['id'],'a');self.assertEqual(found['source'],'shop_exact_name_and_current_grid')
 def test_shop_text_adapts_to_position_and_scale(self):
  names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  raw=[[[[p[0]*1.5+30,p[1]*1.5+15]for p in box],s,c]for box,s,c in shop_fixture()]
  found,_=shop_target(raw,names,(245*1.5+30,170*1.5+15),(920,1280,3));self.assertEqual(found['id'],'a')
 def test_shop_ambiguous_or_unread_name_is_not_filled_from_neighbours(self):
  names={'第一法则':['a','variant'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  self.assertIsNone(shop_target(shop_fixture(),names,(245,170),(600,800,3))[0])
  names.pop('第一法则');self.assertIsNone(shop_target(shop_fixture(),names,(245,170),(600,800,3))[0])
 def test_shop_recheck_requires_current_exact_name(self):
  raw=shop_fixture();names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']};item,_=shop_target(raw,names,(245,170),(600,800,3))
  engine=lambda *args,**kw:([['活玫瑰',.99]],None)
  self.assertIsNone(ShopNameReader(engine).verify(np.zeros((600,800,3),np.uint8),item))
 def test_exact_name_pixels_reuse_only_verified_initial_name(self):
  from hashlib import sha256
  image=np.zeros((600,800,3),np.uint8);item,_=shop_target(shop_fixture(),{'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']},(245,170),image.shape)
  x,y,u,v=item['name_bounds'];item['name_pixels_sha256']=sha256(image[y:v,x:u].tobytes()).hexdigest()
  reader=ShopNameReader(lambda *a,**k:([['不相符',.99]],None));self.assertIsNotNone(reader.verify(image,item))
  image[y,x]=255;self.assertIsNone(reader.verify(image,item))
 def test_waits_full_five_seconds_and_fires_once(self):
  g=HoverGate();s=snapshot();self.assertFalse(g.update(s,100));self.assertFalse(g.update(s,104.999));self.assertTrue(g.update(s,105));self.assertFalse(g.update(s,111))
 def test_movement_window_geometry_and_occlusion_restart(self):
  for change in ({'cursor':(567,300)},{'key':(4,6)},{'physical_client':(101,50,960,540)},{'cursor_on_game':False},{'active':False}):
   g=HoverGate();s=snapshot();g.update(s,0);self.assertFalse(g.update({**s,**change},4.9));self.assertFalse(g.update(s,5))
 def test_small_tremor_is_not_new_target(self):
  g=HoverGate();s=snapshot();g.update(s,0);self.assertTrue(g.update({**s,'cursor':(566,300)},5))
 def test_frame_scope_freshness_and_exact_client_geometry(self):
  request=snapshot();frame={'image':np.zeros((550,970,3),np.uint8),'client_rect':[2,5,962,545],'captured_at':10,'target':{'hwnd':4,'pid':5}}
  self.assertEqual(client_image(frame,request,now=11).shape,(540,960,3))
  for patch in ({'captured_at':7},{'captured_at':12},{'captured_at':True},{'target':{'hwnd':4,'pid':6}},{'client_rect':[0,0,960,539]},{'client_rect':None}):self.assertIsNone(client_image({**frame,**patch},request,now=11))
 def test_local_reference_positive_and_negative(self):
  image,point=specimen();item=hover_item(image,point);self.assertIsNotNone(item);self.assertEqual(item['id'],'rogue_6_relic_legacy_1');self.assertTrue(item['confirmed']);self.assertEqual(item['source'],'cursor_local_original_pixels')
  self.assertIsNone(hover_item(image,(20,20)));self.assertIsNone(hover_item(np.zeros_like(image),point))
 def test_current_full_pixel_verification_rejects_changed_icon(self):
  image,point=specimen();item=hover_item(image,point);self.assertIsNotNone(item)
  self.assertIsNone(verify_again(np.full_like(image,24),point,item))
 def test_cancellation_never_produces_result(self):
  image,point=specimen();self.assertIsNone(hover_item(image,point,cancelled=lambda:True))
 def test_cursor_hotspot_near_visual_icon_has_bounded_halo(self):
  image,_=specimen();self.assertIsNotNone(hover_item(image,(487,257)))
  self.assertIsNone(hover_item(image,(535,257)))
 def test_input_pool_and_same_named_node_pools_remain_readable(self):
  from rouge.player_item_sources import ItemSourceIndex
  from rouge.player_source_cards import source_cards
  from tests.test_player_item_sources_394 import fixture
  data=fixture();data['versions']['base'][0]['name']='收藏品'
  result=source_cards(ItemSourceIndex(data),'base','a');self.assertEqual(result['pools'][0]['title'],'收藏品 · 作战')
  result=source_cards(ItemSourceIndex(data),'dlc1','a');self.assertIn('并非奖励池',result['pools'][0]['frequency'])
 def test_shared_artwork_not_silently_unique(self):
  image,point=specimen()
  with patch.object(icons,'artwork_families',return_value={'rogue_6_relic_legacy_1':['rogue_6_relic_legacy_1','unresolved-variant']}):self.assertIsNone(hover_item(image,point))

def shop_fixture():
 def text(name,x,y,w=100):return [[[x,y],[x+w,y],[x+w,y+20],[x,y+20]],name,.99]
 return [text('购买',600,10),text('当前余额',30,40),text('第一法则',100,120),text('活玫瑰',300,120),text('白模鱼',100,350),text('支援补给站',300,350),text('编队',600,550),text('价格',240,250,40),text('价格',440,250,40),text('价格',240,480,40),text('价格',440,480,40)]
