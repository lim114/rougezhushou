import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.player_recent_scene import event_candidates,event_excerpt,RecentScenePanel
from rouge import current_event_directory as events

class RecentEventCandidates(unittest.TestCase):
 def test_exact_title_is_required_not_substring_or_reward_text(self):
  reference=events.reference();row=reference['rows'][0]
  self.assertEqual([r['id']for r in event_candidates({'kind':'event','title':row['title']},reference)],[row['id']])
  self.assertEqual(event_candidates({'kind':'event','title':row['title'][:2]},reference),[])
  self.assertEqual(event_candidates({'kind':'battle','title':row['title']},reference),[])
 def test_bad_explicit_identity_does_not_fall_back_to_title(self):
  reference=events.reference();row=reference['rows'][0]
  for value in('',False,[],{},0,'not-a-source-id'):
   self.assertEqual(event_candidates({'kind':'event','title':row['title'],'event_id':value},reference),[])
 def test_explicit_scene_has_exact_parent_candidate(self):
  reference=events.reference();row=reference['rows'][0]
  self.assertIn(row['id'],[r['id']for r in event_candidates({'kind':'event','event_id':row['event']['entry_scene_id']},reference)])
 def test_duplicate_titles_remain_separate_candidates(self):
  row=deepcopy(events.reference()['rows'][0]);other=deepcopy(row);other['id']='distinct-reference-fixture'
  self.assertEqual(len(event_candidates({'kind':'event','title':row['title']},{'rows':[row,other]})),2)
 def test_default_excerpt_leads_with_selected_content_and_keeps_limits(self):
  result=events.reference(events.reference()['rows'][0]['id']);entry=result['selected']['entries'][0];text=event_excerpt(result,entry['key'])
  self.assertLess(text.index(entry['title']),text.index('这是固定资料'))
  self.assertIn(entry['description'],text);self.assertIn('可选资格',text);self.assertNotIn(result['selected']['id'],text)

class RecentEventWindow(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def make(self):
  run=SimpleNamespace(state={'id':'fixture-run','last_node_content':{'kind':'event','title':'桑尼的邀请'}})
  return run,RecentScenePanel(run)
 def test_refresh_preserves_exact_selected_entry_and_scroll_until_source_changes(self):
  run,p=self.make()
  try:
   self.assertIsNone(p.event_choices.currentData());p.event_choices.setCurrentIndex(1);p.event_entries.setCurrentIndex(1)
   before=p.event_entries.currentData();text=p.event_text.toPlainText();run.state['last_node_content']['captured_at']=2;p.refresh()
   self.assertEqual(p.event_entries.currentData(),before);self.assertEqual(p.event_text.toPlainText(),text)
   with patch('rouge.player_recent_scene.events.reference',return_value=None):
    self.assertFalse(p.open_event());self.assertIsNone(p.event_result);self.assertFalse(p.event_open.isEnabled())
   p.refresh();self.assertIsNone(p.event_choices.currentData())
  finally:p.close()
 def test_new_run_does_not_reuse_prior_stage_or_event_selection(self):
  run,p=self.make()
  try:
   p.event_choices.setCurrentIndex(1);run.state['id']='new-fixture-run';p.refresh();self.assertIsNone(p.event_choices.currentData())
   run.state['last_node_content']={'kind':'battle','title':'遗忘时间'};p.refresh();p.stages.setCurrentIndex(1);self.assertIsNotNone(p.result)
   run.state['id']='another-fixture-run';p.refresh();self.assertIsNone(p.stages.currentData())
  finally:p.close()
 def test_note_emits_exact_fixed_scene_not_unverified_live_phase(self):
  run,p=self.make();sent=[];p.noteRequested.connect(sent.append)
  try:
   p.event_choices.setCurrentIndex(1);p.event_entries.setCurrentIndex(1);target=p._target();p.write_event_note()
   self.assertEqual(len(sent),1);self.assertEqual(sent[0]['kind'],'reference-scene');self.assertEqual(sent[0]['event_id'],target['scene_id'])
  finally:p.close()

if __name__=='__main__':unittest.main()
