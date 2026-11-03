import unittest,tempfile
from pathlib import Path
from copy import deepcopy
from rouge.run_state import RunState
from rouge.run_config import config_data
from rouge.player_floor_resources import snapshots,snapshot_text,record_snapshot
class FloorSnapshotTests(unittest.TestCase):
 def test_actual_apply_records_same_frame_zone_not_reused_old_zone(self):
  with tempfile.TemporaryDirectory()as d:
   run=RunState(Path(d)/'run.json');zone=config_data()['zones']['zone_1'];t=run.state['started_at']+1
   observation={'config':{'zone':{'id':'zone_1','name':zone['name']}},'resources':{'gold':{'value':7}}};self.assertTrue(run.apply(observation,t));self.assertEqual(snapshots(run.state)[0]['values'],{'gold':7})
   run.apply(observation,t+1);self.assertEqual(len(snapshots(run.state)),1)
   run.apply({'resources':{'gold':{'value':12}}},t+2);self.assertEqual(len(snapshots(run.state)),1)
   run.apply({'config':{'zone':{'id':'zone_1','name':zone['name'],'reused_from_run':True}},'resources':{'gold':{'value':15}}},t+3);self.assertEqual(len(snapshots(run.state)),1)
   restored=RunState(Path(d)/'run.json');self.assertEqual(snapshots(restored.state),snapshots(run.state))
 def test_partial_snapshot_does_not_carry_missing_resource_and_no_reward_claim(self):
  state={'maps':{},'config':{'zone':{'captured_at':10}},'resources':{'gold':{'value':8,'captured_at':10},'parts_count':{'value':2,'captured_at':9}},'history':[]}
  observed={'config':{'zone':{'id':'zone_1'}},'resources':{'gold':{'value':8}}};self.assertTrue(record_snapshot(state,observed,10));row=snapshots(state)[0];self.assertEqual(row['values'],{'gold':8});self.assertIn('不是入层',snapshot_text(row));self.assertIn('不使用当前资源',snapshot_text(None))
  before=deepcopy(state);snapshot_text(row);self.assertEqual(state,before)
 def test_invalid_quantity_or_missing_same_frame_zone_is_not_snapshot(self):
  for value in(True,-1,float('inf'),'7'):
   state={'config':{'zone':{'captured_at':5}},'resources':{'gold':{'value':value,'captured_at':5}},'history':[]}
   self.assertFalse(record_snapshot(state,{'config':{'zone':{'id':'zone_1'}},'resources':{'gold':{'value':value}}},5))
