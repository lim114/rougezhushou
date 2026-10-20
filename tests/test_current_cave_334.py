from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_cave as model,current_node_readers as bridge,node_catalog
from scripts import build_current_cave_334 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
 m=json.loads((ROOT/model.MANIFEST).read_bytes())
 for name in(model.MANIFEST,*m['files']):
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def choice(r,role):return r['choices']['cave-choice:'+role]
class CurrentCave334Tests(unittest.TestCase):
 def test_complete_table_reproducible46_scenes44_choices10_contexts8_groups(self):
  d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.reference();self.assertEqual(r['data']['counts'],{'document_scenes':10,'document_choice_groups':8,'original_scenes':46,'original_choices':44,'caption_cells':13,'documented_random_outcomes':4,'original_next_divergent_groups':2,'catalogue_exact_scene_links':46})
  v=model.version.packet()
  for group,rows in r['data']['originals'].items():
   table='choiceScenes'if group=='scenes'else group
   for k,value in rows.items():self.assertEqual(value,v['current']['details'][table][k]);self.assertIs(r['data']['complete_selected_record_comparison_to_baseline'][group][k],v['baseline']['details'][table].get(k)==value)
  self.assertFalse(r['data']['complete_game_option_pool']);self.assertFalse(r['data']['game_parent_script_restored'])
 def test_four_document_results_no_default_probability_or_infinite_repeat(self):
  r=model.reference()
  for role in('dig','again'):
   c=choice(r,role);self.assertIsNone(c['next_scene_id']);self.assertEqual([x['scene_id']for x in c['documented_outcomes']],['cave-scene:'+v for v in('crow','squirrel','empty','danger')]);self.assertTrue(all(x['probability']is None and x['actual_outcome']is None for x in c['documented_outcomes']))
   for key in c['variant_ids']:self.assertEqual(r['data']['originals']['choices'][key]['type'],'NEXT_PROB');self.assertIsNone(r['data']['originals']['choices'][key]['nextSceneId'])
   self.assertIn('不能据此假定无限继续',model.player_text(r,c['scene_ids'][0],c['id']))
  self.assertIsNone(r['actual_probability']);self.assertIsNone(r['actual_max_attempts']);self.assertIsNone(r['actual_outcome'])
 def test_same_caption_distinct_targets_not_merged_and_exact_late_record_ends(self):
  for role,early,late,low in [('gold','choice_ro6_bat6_3','choice_ro6_bat6_19','low_gold'),('empty','choice_ro6_bat6_5','choice_ro6_bat6_21','low_empty')]:
   r=model.reference();c=choice(r,role);row=model.choice_reference(r,c['scene_ids'][0],c['id']);self.assertIsNone(row['next_scene_id']);self.assertEqual([x['scene_id']for x in row['reference_followups']],['cave-scene:'+low,'cave-scene:end']);self.assertEqual(len(c['variant_ids']),8)
   for key,target in[(early,'cave-scene:'+low),(late,'cave-scene:end')]:
    r=model.reference(source_request={'category':'choices','key':key});row=model.choice_reference(r,c['scene_ids'][0],c['id']);self.assertEqual(row['source_variant_id'],key);self.assertEqual(row['next_scene_id'],target);self.assertEqual(row['reference_followups'],[]);self.assertIsNone(r['actual_variant']);self.assertFalse(r['run_updated'])
 def test_all90_exact_sources_preserved_shared_low_phases_never_default(self):
  d=model.reference()['data'];total=0
  for category in('scenes','choices'):
   for key in d['originals'][category]:
    t=model.locate(category,key);self.assertEqual(t['source_request'],{'category':category,'key':key});r=model.reference(source_request=t['source_request']);self.assertEqual(r['source_request'],t['source_request']);self.assertEqual(t['scene_id']is None,t['phase_needed']);total+=1
  self.assertEqual(total,90)
  for category,key in[('scenes','scene_ro6_bat6_6'),('choices','choice_ro6_bat6_7'),('choices','choice_ro6_bat6_8')]:
   t=model.locate(category,key);self.assertTrue(t['phase_needed']);self.assertEqual(t['possible_scene_ids'],['cave-scene:low_gold','cave-scene:low_empty'])
  for req in[{'category':'scenes','key':'invented'},{'category':False,'key':'x'},{'category':'choices','key':'choice_ro6_bat6_3','extra':1}]:self.assertIsNone(model.reference(source_request=req))
 def test_rewards_only5gold_or1relic_not_sum_and_generic_battle_not_urgent_map(self):
  r=model.reference();self.assertEqual(choice(r,'gold')['reward_reference'],{'quantity':5,'kind':'源石锭','pool':None});self.assertEqual(choice(r,'relic')['reward_reference'],{'quantity':1,'kind':'收藏品','pool':None});self.assertIsNone(choice(r,'empty')['reward_reference']);c=choice(r,'battle');self.assertEqual(c['stage_ids'],[]);self.assertTrue(c['battle_hint_without_exact_stage']);text=model.player_text(r,c['scene_ids'][0],c['id']);self.assertIn('不凭“艰难”认定紧急',text);self.assertIsNone(r['actual_stage'])
 def test_catalogue_binding46links_strict_full_record_warm_drift_and_forgery(self):
  row=next(x for x in node_catalog.all_events(include_indirect=True)['rows']if x['id']=='community_group_017');b=bridge.binding_for(row);self.assertEqual(len(b['exact_scene_links']),46);self.assertIsNotNone(bridge.recheck(b));bad=deepcopy(b);bad['reader']='invented';self.assertIsNone(bridge.recheck(bad));warm=deepcopy(node_catalog._event(row['id']));warm['scenes'][0]['description']+='drift'
  with patch.object(node_catalog,'_event',return_value=warm):self.assertIsNone(bridge.binding_for(row))
 def test_each_manifest_file_and_full_current_record_drift_fails_closed(self):
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);m=json.loads((ROOT/model.MANIFEST).read_bytes())
   with patch.object(model,'ROOT',root):
    for name in(model.MANIFEST,*m['files']):
     f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
  r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_bat6_19']['nextSceneId']='invented'
  with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
 def test_builder_keeps_whole_variant_scope_rejects_changed_caption_or_extra_scene(self):
  for kind in('caption','scene'):
   with TemporaryDirectory()as folder:
    root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
    if kind=='caption':d['details']['choices']['choice_ro6_bat6_19']['description']='unverified'
    else:d['details']['choiceScenes']['invented']=deepcopy(d['details']['choiceScenes']['scene_ro6_bat6_6'])
    f.write_bytes(builder.encoded(d))
    with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
