"""Accepted same-frame snapshots precede only the map rows of that observation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from types import ModuleType
import json,unittest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.map_recognition import map_data
from rouge.player_replay_nodes import node_steps,NodeReplayPage
from rouge.player_history_store import RunHistoryStore

ROOT=Path(__file__).resolve().parents[1];COMPARISON={}

def graph(template=None,position=0,kind='作战'):
 template=template or next(t for t in map_data()['templates']if t['zone_id']=='zone_1')
 g={**deepcopy(template),'status':'matched','template_id':template['id'],'current_node':template['nodes'][position]['id']}
 g['nodes'][position]['observed_type']=kind
 return g

class MapResourceReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.folder=Path(self.enterContext(TemporaryDirectory(prefix='rouge-public-map-resources-')));self.run=RunState(self.folder/'run.json');self.at=self.run.state['started_at']+1
 def observe(self,quantity,*,template=None,position=0,at=None):
  incoming={'map':graph(template,position),'resources':{'gold':{'value':quantity}}};before=deepcopy(incoming);self.assertTrue(self.run.apply(incoming,self.at if at is None else at));self.at+=1;self.assertEqual(incoming,before);return node_steps(self.run.state)
 def test_own_prior_reproduces_missing_same_frame_resources_and_new_code_links_both_rows(self):
  raw=(ROOT/'research/map-resource-review-20261031/before-run-state.py').read_bytes();old=ModuleType('rouge._before_map_resource_review');old.__package__='rouge';exec(compile(raw,'<own-prior-run-state>','exec'),old.__dict__)
  prior=old.RunState(self.folder/'before.json');observation={'map':graph(),'resources':{'gold':{'value':7}}};self.assertTrue(prior.apply(observation,prior.state['started_at']+1));prior_rows=node_steps(prior.state);self.assertTrue(prior_rows);self.assertTrue(all(r['resource_snapshot']is None for r in prior_rows))
  rows=self.observe(7);self.assertEqual(len(rows),len(prior_rows));self.assertTrue(all(r['resource_snapshot']['values']=={'gold':7}for r in rows));COMPARISON.update({'prior_map_rows':len(prior_rows),'prior_snapshot_values':[r['resource_snapshot']for r in prior_rows],'current_map_rows':len(rows),'current_snapshot_values':[r['resource_snapshot']['values']for r in rows]})
 def test_later_resource_and_node_read_cannot_fill_or_replace_earlier_history(self):
  early=self.observe(7);history=deepcopy(self.run.state['history']);later=self.observe(99,position=1);self.assertEqual(self.run.state['history'][:len(history)],history)
  self.assertEqual(later[:len(early)],early);self.assertTrue(all(r['resource_snapshot']['values']=={'gold':99}for r in later[len(early):]))
 def test_equal_timestamps_still_use_only_this_apply_batch_without_reordering_old_events(self):
  at=self.at;early=self.observe(7,at=at);history=deepcopy(self.run.state['history']);later=self.observe(12,position=1,at=at);self.assertEqual(self.run.state['history'][:len(history)],history);self.assertEqual(later[:len(early)],early)
  self.assertTrue(all(r['resource_snapshot']['values']=={'gold':12}for r in later[len(early):]))
 def test_layout_change_keeps_old_rows_and_owns_new_snapshot_after_layout_barrier(self):
  first=next(t for t in map_data()['templates']if t['zone_id']=='zone_1');other=next(t for t in map_data()['templates']if t['zone_id']=='zone_1'and t['id']!=first['id'])
  early=self.observe(7,template=first);later=self.observe(22,template=other);self.assertEqual(later[:len(early)],early)
  for row in later[len(early):]:self.assertEqual(row['template']['id'],other['id']);self.assertEqual(row['resource_snapshot']['template_id'],other['id']);self.assertEqual(row['resource_snapshot']['values'],{'gold':22})
 def test_no_new_resource_read_reuses_prior_snapshot_without_creating_a_fake_current_one(self):
  self.observe(7);snapshots_before=[r for r in self.run.state['history']if r['kind']=='floor_resources_read'];self.assertTrue(self.run.apply({'map':graph(position=1)},self.at))
  self.assertEqual([r for r in self.run.state['history']if r['kind']=='floor_resources_read'],snapshots_before);self.assertEqual(node_steps(self.run.state)[-1]['resource_snapshot']['values'],{'gold':7})
 def test_legacy_history_is_not_rewritten_when_loading_or_processing_an_unrelated_page(self):
  raw=(ROOT/'research/map-resource-review-20261031/before-run-state.py').read_bytes();old=ModuleType('rouge._legacy_map_resource_review');old.__package__='rouge';exec(compile(raw,'<own-prior-run-state>','exec'),old.__dict__);prior=old.RunState(self.folder/'legacy.json');at=prior.state['started_at']+1;prior.apply({'map':graph(),'resources':{'gold':{'value':7}}},at)
  saved_history=deepcopy(prior.state['history']);restored=RunState(prior.file);self.assertEqual(restored.state['history'],saved_history);self.assertTrue(all(r['resource_snapshot']is None for r in node_steps(restored.state)));restored.apply({'resources':{'gold':{'value':100}}},at+1);self.assertEqual(restored.state['history'][:len(saved_history)],saved_history);self.assertTrue(all(r['resource_snapshot']is None for r in node_steps(restored.state)))
 def test_save_reload_and_archive_keep_exact_new_snapshot_ownership(self):
  rows=self.observe(7);history=deepcopy(self.run.state['history']);restored=RunState(self.run.file);self.assertEqual(restored.state['history'],history);self.assertEqual(node_steps(restored.state),rows)
  store=RunHistoryStore(self.folder/'archives');path=store.archive(restored.state);record=store.read(path);self.assertEqual(record['state']['history'],history);self.assertEqual(node_steps(record['state']),rows)
 def test_real_replay_widget_preserves_selected_earlier_value_after_future_append(self):
  self.observe(7);page=NodeReplayPage();self.addCleanup(page.close);page.show();page.refresh(self.run.state);page.entries.setCurrentRow(0);self.qt.processEvents();self.assertIn('源石锭 7',page.resources.text());index=page.entries.currentItem().data(256)
  self.observe(99,position=1);page.refresh(self.run.state);self.assertEqual(page.entries.currentItem().data(256),index);self.assertIn('源石锭 7',page.resources.text());page.entries.setCurrentRow(page.entries.count()-1);self.assertIn('源石锭 99',page.resources.text())

if __name__=='__main__':unittest.main()
