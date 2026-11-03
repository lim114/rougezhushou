from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_lone_dog as model,current_node_readers as bridge,node_catalog
from scripts import build_current_lone_dog_335 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
 m=json.loads((ROOT/model.MANIFEST).read_bytes())
 for name in(model.MANIFEST,*m['files']):
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
class CurrentLoneDog335Tests(unittest.TestCase):
 def test_complete_table_reproducible3_scenes4_actions1_relic_and_versions(self):
  d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.reference();self.assertEqual((len(r['scenes']),len(r['choices']),len(r['data']['originals']['items'])),(3,4,1));v=model.version.packet()
  for group,rows in r['data']['originals'].items():
   table='choiceScenes'if group=='scenes'else group
   for k,value in rows.items():self.assertEqual(v['current']['details'][table][k],value);self.assertIs(r['data']['complete_selected_record_comparison_to_baseline'][group][k],v['baseline']['details'][table].get(k)==value)
  self.assertFalse(r['data']['complete_game_option_pool']);self.assertFalse(r['data']['game_parent_script_restored'])
 def test_all7_entries_and_two_later_actions_only_after_approach_not_leave(self):
  r=model.reference();sid=r['choices']['choice_ro6_task2_1']['next_scene_id'];leave=r['choices']['choice_ro6_task2_2']['next_scene_id'];self.assertEqual(r['scenes'][sid]['choice_ids'],['choice_ro6_task2_3','choice_ro6_task2_4']);self.assertEqual(r['scenes'][leave]['choice_ids'],[])
  for key in r['scenes']:self.assertEqual(model.locate('scenes',key),{'event_id':'dog','scene_id':key,'choice_id':None})
  for key,c in r['choices'].items():self.assertEqual(model.locate('choices',key),{'event_id':'dog','scene_id':c['scene_id'],'choice_id':key});self.assertEqual(model.choice_reference(r,c['scene_id'],key)['id'],key)
  self.assertIsNone(model.choice_reference(r,leave,'choice_ro6_task2_3'));self.assertIsNone(model.locate('choices','choice_ro6_task1_1'))
 def test_move_and_mark_different_no_fake_next_coordinates_recruitment_or_actual_state(self):
  r=model.reference()
  for key,kind,role in[('choice_ro6_task2_3','MOVE','move'),('choice_ro6_task2_4','VISION','mark')]:
   c=r['choices'][key];self.assertEqual(r['data']['originals']['choices'][key]['type'],kind);self.assertEqual(c['role'],role);self.assertIsNone(c['next_scene_id']);self.assertEqual(c['target_node_type'],'应急助力');self.assertIsNone(c['actual_target_node_id']);self.assertTrue(all(c[k]is None for k in('actual_moved','actual_marked','actual_recruited','actual_received')))
  self.assertIn('不是只标记位置',model.player_text(r,r['choices']['choice_ro6_task2_3']['scene_id'],'choice_ro6_task2_3'));self.assertIn('不是立即前往',model.player_text(r,r['choices']['choice_ro6_task2_4']['scene_id'],'choice_ro6_task2_4'));self.assertFalse(r['run_updated'])
 def test_named_relic_usage_scope_not_all_team_or_claimed_quantity_and_catalogue3links(self):
  r=model.reference();c=r['choices']['choice_ro6_task2_1'];self.assertIsNone(c['quantity_reference']);text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('同行者',text);self.assertIn('不扩大到所有招募或全队',text);self.assertIn('不补成1件',text);row=next(x for x in node_catalog.all_events(include_indirect=True)['rows']if x['id']=='community_group_020');b=bridge.binding_for(row);self.assertEqual(len(b['exact_scene_links']),3);self.assertIsNotNone(bridge.recheck(b));warm=deepcopy(node_catalog._event(row['id']));warm['scenes'][1]['description']+='changed'
  with patch.object(node_catalog,'_event',return_value=warm):self.assertIsNone(bridge.binding_for(row))
 def test_each_source_file_damage_complete_current_drift_and_builder_bad_action(self):
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);m=json.loads((ROOT/model.MANIFEST).read_bytes())
   with patch.object(model,'ROOT',root):
    for name in(model.MANIFEST,*m['files']):
     f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
   f=root/builder.CURRENT;d=json.loads(f.read_bytes());d['details']['choices']['choice_ro6_task2_4']['type']='MOVE';f.write_bytes(builder.encoded(d))
   with self.assertRaises(ValueError):builder.build(root)
  r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_task2_4']['type']='MOVE'
  with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
if __name__=='__main__':unittest.main()
