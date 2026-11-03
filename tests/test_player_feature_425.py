import unittest
from PySide6.QtCore import QRect
from rouge.player_game_map import hit_node
class NodeHitTests(unittest.TestCase):
 def sample(self):return {'rect':QRect(-100,20,640,360),'points':[('one',160,180),('two',480,180)]},{'physical_client':(-150,30,960,540),'cursor':(90,300),'cursor_on_game':True}
 def test_node_hit_uses_physical_to_logical_dpi(self):
  data,s=self.sample();self.assertEqual(hit_node(data,s),'one');s['cursor']=(570,300);self.assertEqual(hit_node(data,s),'two')
 def test_off_game_far_and_ambiguous_hits_refused(self):
  data,s=self.sample();s['cursor_on_game']=False;self.assertIsNone(hit_node(data,s));s['cursor_on_game']=True;s['cursor']=(300,100);self.assertIsNone(hit_node(data,s));s['cursor']=(90,300);data['points'].append(('ambiguous',162,180));self.assertIsNone(hit_node(data,s))

class SavedRecordBoundaryTests(unittest.TestCase):
 def test_malformed_new_history_records_are_ignored_not_repaired(self):
  from rouge.player_shop_memory import qualified
  from rouge.player_floor_resources import snapshots
  self.assertIsNone(qualified({'source':'fresh_shop_exact_names','complete':False,'items':[{'id':[],'name':'x'}]}))
  self.assertEqual(snapshots({'history':[{'kind':'floor_resources_read','source':'same_frame_zone_and_resources','zone_id':[],'values':{}}]}),[])

class SparseShopGridTests(unittest.TestCase):
 def test_whole_unread_middle_row_cannot_borrow_another_row_name(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=shop_fixture();names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  for box,text,score in raw:
   if text in('白模鱼','支援补给站','编队'):
    for p in box:p[1]+=230
  self.assertIsNone(shop_target(raw,names,(245,410),(850,800,3))[0])
 def test_whole_unread_column_cannot_borrow_another_column_name(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=shop_fixture();names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  for box,text,score in raw:
   if text in('活玫瑰','支援补给站'):
    for p in box:p[0]+=200
  self.assertIsNone(shop_target(raw,names,(345,170),(600,1000,3))[0])
 def test_unread_lower_row_is_not_filled_from_last_known_row(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=shop_fixture();names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  for box,text,score in raw:
   if text=='编队':
    for p in box:p[1]+=300
  self.assertIsNone(shop_target(raw,names,(245,640),(950,800,3))[0])
 def test_valid_grid_still_follows_continuous_scale_and_translation(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  names={'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
  for scale in(.7,1.3,1.9):
   raw=[[[[p[0]*scale+25,p[1]*scale+15]for p in box],text,score]for box,text,score in shop_fixture()];item,_=shop_target(raw,names,(245*scale+25,170*scale+15),(int(650*scale+30),int(850*scale+30),3));self.assertEqual(item['id'],'a')

class ShopTextCard425Tests(unittest.TestCase):
 def _names(self):return {'第一法则':['a'],'活玫瑰':['b'],'白模鱼':['c'],'支援补给站':['d']}
 def test_one_partial_card_can_be_read_without_whole_grid(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if r[1] in('购买','当前余额','第一法则') or (r[1]=='价格' and r[0][0]==[240,250])]
  item,shop=shop_target(raw,self._names(),(245,170),(600,800,3));self.assertTrue(shop);self.assertEqual(item['id'],'a');self.assertEqual(item['card_evidence'],'exact_name_and_own_price_text')
 def test_no_price_and_no_calibrated_text_layout_remain_unknown(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if r[1]!='价格'];item,shop=shop_target(raw,self._names(),(245,170),(600,800,3));self.assertTrue(shop);self.assertIsNone(item)
 def test_cursor_covered_price_requires_current_row_and_column_anchors(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if not(r[1]=='价格' and r[0][0]==[440,250])]
  item,_=shop_target(raw,self._names(),(445,170),(600,800,3));self.assertEqual(item['id'],'b');self.assertIsNone(item['price_label_bounds']);self.assertEqual(item['card_evidence'],'exact_name_and_current_text_layout')
 def test_missing_entire_price_column_cannot_borrow_another_column(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if not(r[1]=='价格' and r[0][0][0]==440)]
  self.assertIsNone(shop_target(raw,self._names(),(445,170),(600,800,3))[0])
 def test_missing_entire_price_row_cannot_borrow_another_row(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if not(r[1]=='价格' and r[0][0][1]==250)]
  self.assertIsNone(shop_target(raw,self._names(),(445,170),(600,800,3))[0])
 def test_price_label_changes_invalidate_current_text_layout_cache(self):
  from unittest.mock import patch
  import numpy as np
  from rouge.player_shop_hover import ShopNameReader
  from tests.test_player_feature_417 import shop_fixture
  calls=[]
  def engine(*a,**kw):calls.append(True);return shop_fixture(),None
  packet={'current':{'details':{'items':{v[0]:{'name':k}for k,v in self._names().items()}}}}
  with patch('rouge.player_shop_hover.expansion_reference.packet',return_value=packet):
   image=np.zeros((600,800,3),dtype=np.uint8);reader=ShopNameReader(engine);self.assertIsNotNone(reader.identify(image,(245,170)));reader.identify(image,(245,170));self.assertEqual(len(calls),1)
   image[250,240]=255;reader.identify(image,(245,170));self.assertEqual(len(calls),2)

 def test_direct_name_hover_does_not_require_price(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if r[1]!='价格'];item,shop=shop_target(raw,self._names(),(150,130),(600,800,3));self.assertTrue(shop);self.assertEqual(item['id'],'a');self.assertEqual(item['card_evidence'],'cursor_on_exact_name_text');self.assertIsNone(item['price_label_bounds'])

 def test_no_extrapolated_bottom_padding_for_unread_neighbour(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if r[1] not in('白模鱼','支援补给站')];self.assertIsNone(shop_target(raw,self._names(),(245,300),(600,800,3))[0])
 def test_no_extrapolated_right_padding_for_unread_neighbour(self):
  from rouge.player_shop_hover import shop_target
  from tests.test_player_feature_417 import shop_fixture
  raw=[r for r in shop_fixture() if r[1] not in('活玫瑰','支援补给站')];self.assertIsNone(shop_target(raw,self._names(),(290,170),(600,800,3))[0])
