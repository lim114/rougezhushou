import unittest,tempfile,time
from pathlib import Path
from copy import deepcopy
from rouge.player_shop_hover import ShopNameReader
from rouge.player_shop_memory import remember,qualified
from rouge.run_state import RunState
from tests.test_player_feature_417 import shop_fixture
import numpy as np
class ShopMemoryTests(unittest.TestCase):
 def sample(self):
  reader=ShopNameReader(lambda *a,**k:(shop_fixture(),None));image=np.zeros((600,800,3),np.uint8);reader.identify(image,(245,170));return reader,image,reader.snapshot(image)
 def test_name_set_requires_fresh_unchanged_all_headers(self):
  reader,image,snapshot=self.sample();self.assertGreater(len(snapshot['items']),1);self.assertFalse(snapshot['complete']);image[120,300]=255;self.assertIsNone(reader.snapshot(image));self.assertIsNotNone(qualified(snapshot))
 def test_exact_run_and_time_gates_and_duplicate_snapshot(self):
  _,_,snapshot=self.sample()
  with tempfile.TemporaryDirectory()as d:
   run=RunState(Path(d)/'run.json');before=deepcopy(run.state);self.assertFalse(remember(run,snapshot,'other-run',time.time()));self.assertFalse(remember(run,snapshot,run.state['id'],time.time()-3));self.assertEqual(run.state,before)
   self.assertTrue(remember(run,snapshot,run.state['id'],time.time()));self.assertFalse(remember(run,snapshot,run.state['id'],time.time()));self.assertEqual(len([e for e in run.state['history']if e['kind']=='shop_items_read']),1);self.assertEqual(run.state['relics'],before['relics']);self.assertEqual(RunState(Path(d)/'run.json').state['history'],run.state['history'])
 def test_unknown_or_name_mismatch_never_published(self):
  _,_,snapshot=self.sample();snapshot['items'][0]['name']='其他名称';self.assertIsNone(qualified(snapshot));snapshot['complete']=True;self.assertIsNone(qualified(snapshot))
