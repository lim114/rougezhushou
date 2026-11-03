"""Exact old reader output, with reference lookups limited to each current frame."""
from pathlib import Path
from types import ModuleType
from contextlib import ExitStack
from copy import deepcopy
from unittest.mock import patch
import unittest
import numpy as np
from rouge import recognition as current

ROOT=Path(__file__).resolve().parents[1]
class InterpretLookupReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.prior=ModuleType('rouge._before_document_recognition');cls.prior.__package__='rouge';cls.prior.__file__=str(ROOT/'rouge/recognition.py');exec(compile((ROOT/'research/battle-document-20261101/before-recognition.py').read_bytes(),'<exact-prior-reader>','exec'),cls.prior.__dict__)
 def run_reader(self,module,labels,catalog):
  image=np.full((300,600,3),32,np.uint8);raw=[[[[20,20+i],[140,20+i],[140,35+i],[20,35+i]],text,confidence]for i,(text,confidence)in enumerate(labels)];reader=module.ScreenReader();reader._engine=lambda image:([],None)
  with ExitStack()as stack:
   for name in('read_operator','read_module_page','read_run','read_node_content','read_map'):stack.enter_context(patch.object(module,name,return_value=None))
   stack.enter_context(patch.object(module,'map_evidence'));stack.enter_context(patch('rouge.player_shop_hover.shop_snapshot',return_value=None));stack.enter_context(patch.object(module,'stage_previews',return_value={}))
   lookup=stack.enter_context(patch.object(module,'catalog',return_value=catalog));result=reader._interpret(image,{'source_size':[600,300]},raw,lambda _:None,{})
  result.pop('observed_at');return result,lookup.call_count
 def test_long_current_text_list_keeps_all_results_and_reduces_repeated_catalog_builds(self):
  ref={'node_types':{'fight':{'name':'作战'}},'stages':{'first':{'name':'目标关卡','difficulty':'NORMAL'},'second':{'name':'目标关卡','difficulty':'FOUR_STAR'}}};labels=[('无关文字'+str(i),.98)for i in range(120)]+[('未知的凶房',.7),('作战',.699),('目标关卡',.9)];before,n=self.run_reader(self.prior,labels,ref);after,m=self.run_reader(current,labels,ref);self.assertEqual(before,after);self.assertEqual(m,2);self.assertGreater(n,120);self.assertEqual(after['nodes'][0]['type'],'未知的凶戾');self.assertIsNone(after['stage']['id']);self.assertEqual([v['id']for v in after['stage']['variants']],['first','second'])
 def test_stage_source_order_and_ocr_confidence_still_control_first_valid_match(self):
  ref={'node_types':{},'stages':{'a':{'name':'同名','difficulty':'NORMAL'},'b':{'name':'另一关','difficulty':'NORMAL'},'c':{'name':'同名','difficulty':'FOUR_STAR'}}}
  for labels in[[('同名',.79),('另一关',.8)],[('同名',.8),('另一关',.99)],[('未匹配',1.)],[]]:
   self.assertEqual(self.run_reader(self.prior,labels,ref)[0],self.run_reader(current,labels,ref)[0])
 def test_reference_changes_between_frames_are_read_without_a_persistent_index(self):
  first={'node_types':{},'stages':{'a':{'name':'关卡','difficulty':'NORMAL'}}};second=deepcopy(first);second['stages']['b']=second['stages'].pop('a');a,_=self.run_reader(current,[('关卡',.9)],first);b,_=self.run_reader(current,[('关卡',.9)],second);self.assertEqual(a['stage']['id'],'a');self.assertEqual(b['stage']['id'],'b')

if __name__=='__main__':unittest.main()
