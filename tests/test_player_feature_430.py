import unittest
from copy import deepcopy
from rouge.player_recorded_scene import recorded_context

def scene_state():
 content={'kind':'event','title':'桑尼的邀请','captured_at':100.0,'location':None}
 return {'id':'past','history':[{'kind':'node_content_seen','title':content['title'],'at':100.0,'location':None}],
     'node_contents':[content],'last_node_content':{'kind':'battle','title':'遗忘时间'}}

class RecordedSceneBinding(unittest.TestCase):
 def test_unique_saved_read_is_used_not_current_scene(self):
  state=scene_state();before=deepcopy(state);self.assertEqual(recorded_context(state,0),{'kind':'event','title':'桑尼的邀请'});self.assertEqual(state,before)
 def test_old_title_only_or_missing_details_do_not_borrow_present(self):
  state=scene_state();state['node_contents']=[];self.assertIsNone(recorded_context(state,0))
 def test_timestamp_or_location_mismatch_does_not_bind(self):
  for field,value in(('captured_at',101),('location',{'node_id':'elsewhere'})):
   state=scene_state();state['node_contents'][0][field]=value;self.assertIsNone(recorded_context(state,0))
 def test_same_name_ambiguous_contexts_refuse_unique_link(self):
  state=scene_state();other=deepcopy(state['node_contents'][0]);other['event_id']='another-context';state['node_contents'].append(other);self.assertIsNone(recorded_context(state,0))
 def test_repeated_identical_context_does_not_invent_a_new_variant(self):
  state=scene_state();state['node_contents'].append(deepcopy(state['node_contents'][0]));self.assertIsNotNone(recorded_context(state,0))
 def test_direct_map_confirmation_preserves_explicit_stage(self):
  state={'history':[{'kind':'map_node_content_confirmed','content':{'kind':'battle','title':'遗忘时间','stage_id':'source-stage','source':'same_frame_selected_node'}}]}
  self.assertEqual(recorded_context(state,0)['stage_id'],'source-stage')
  state['history'][0]['content']['source']='guessed';self.assertIsNone(recorded_context(state,0))
 def test_malformed_fields_never_return_an_unrelated_context(self):
  state=scene_state()
  for index in(None,-1,True,'0',1):self.assertIsNone(recorded_context(state,index))
  for value in('',False,[]):
   state=scene_state();state['node_contents'][0]['event_id']=value;self.assertIsNone(recorded_context(state,0))

if __name__=='__main__':unittest.main()
