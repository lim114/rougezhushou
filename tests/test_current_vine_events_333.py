from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_vine_events as model,current_node_readers as bridge,node_catalog
from scripts import build_current_vine_events_333 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
 m=json.loads((ROOT/model.MANIFEST).read_bytes())
 for name in(model.MANIFEST,*m['files']):
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def by_original(r,key):return next(c for c in r['choices'].values()if key in c['variant_ids'])
class CurrentVineEvents333Tests(unittest.TestCase):
 def test_complete_two_tables8_scenes6_choices3_items_reproducible_full_versions(self):
  d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();self.assertEqual(r['data']['counts'],{'events':2,'scenes':8,'document_choices':6,'original_choice_variants':6,'named_battle_choices':0,'required_item_choices':1,'items':3})
  v=model.version.packet()
  for group,rows in r['data']['originals'].items():
   table='choiceScenes'if group=='scenes'else group
   for key,value in rows.items():self.assertEqual(value,v['current']['details'][table][key]);self.assertIs(r['data']['complete_selected_record_comparison_to_baseline'][group][key],v['baseline']['details'][table].get(key)==value)
  self.assertFalse(r['data']['complete_game_option_pool']);self.assertFalse(r['data']['game_parent_script_restored'])
 def test_all14_version_entries_exact_narrative_parent_no_other_event_or_battle(self):
  d=model.packet()['data']
  for sid,s in d['scenes'].items():self.assertEqual(model.locate('scenes',sid),{'event_id':s['event_id'],'scene_id':sid,'choice_id':None})
  for key in d['originals']['choices']:
   t=model.locate('choices',key);r=model.reference(t['event_id']);c=model.choice_reference(r,t['scene_id'],t['choice_id']);self.assertEqual(c['variant_ids'],[key]);self.assertEqual(r['data']['originals']['scenes'][c['next_scene_id']]['title'],t['event_id']);self.assertEqual(c['stage_ids'],[])
  self.assertIsNone(model.locate('choices','choice_ro6_normal2_2'))
 def test_house_alternative_costs_no_controller_requirement_named_part_not_relic_no_quantity_guess(self):
  for gold in(None,0,7,8):
   r=model.reference('沉寂之屋',gold);hp=by_original(r,'choice_ro6_normal1_1');pay=by_original(r,'choice_ro6_normal1_2');leave=by_original(r,'choice_ro6_normal1_3')
   self.assertEqual(hp['target_life_cost_reference'],2);self.assertEqual(pay['gold_cost_reference'],8);self.assertIs(model.choice_reference(r,pay['scene_id'],pay['id'])['listed_condition_match'],None if gold is None else gold>=8)
   for c in(hp,pay):
    self.assertIsNone(c['required_item_id']);self.assertIsNone(c['named_reward_item_id']);self.assertIsNone(c['named_part_quantity']);self.assertEqual(r['data']['originals']['items'][c['named_part_item_id']]['type'],'SCRAP');self.assertIn('不自动补成1件',model.player_text(r,c['scene_id'],c['id']))
   self.assertIsNone(model.choice_reference(r,hp['scene_id'],hp['id'])['listed_condition_match']);self.assertIsNone(model.choice_reference(r,leave['scene_id'],leave['id'])['listed_condition_match']);self.assertIn('不套用黑诞的保底规则',model.player_text(r,hp['scene_id'],hp['id']))
 def test_controller_and_seed_branches_independent30gold_not_added_to_seed_or_current_stats(self):
  for controller in(None,False,True):
   for seeds in(None,0,1,3):
    r=model.reference('呼吸的红苔',controller=controller,seeds=seeds);a=by_original(r,'choice_ro6_normal3_1');b=by_original(r,'choice_ro6_normal3_2');leave=by_original(r,'choice_ro6_normal3_3');ar=model.choice_reference(r,a['scene_id'],a['id']);br=model.choice_reference(r,b['scene_id'],b['id'])
    self.assertIs(ar['listed_condition_match'],controller);self.assertIs(br['listed_condition_match'],None if seeds is None else seeds>=1);self.assertIsNone(model.choice_reference(r,leave['scene_id'],leave['id'])['listed_condition_match']);self.assertEqual(a['resource_reward_reference'],{'quantity':30,'resource':'源石锭'});self.assertIsNone(b['resource_reward_reference']);self.assertEqual(b['seed_cost_reference'],1);self.assertEqual(a['future_region_reference'],b['future_region_reference']);self.assertIsNone(r['actual_future_region']);self.assertFalse(r['run_updated'])
  r=model.reference('呼吸的红苔');a=by_original(r,'choice_ro6_normal3_1');b=by_original(r,'choice_ro6_normal3_2');self.assertIn('持有不等于已经消耗',model.player_text(r,a['scene_id'],a['id']));self.assertIn('不是现在全队获得属性加成',model.player_text(r,b['scene_id'],b['id']));self.assertIn('不是获得1枚种子',model.player_text(r,b['scene_id'],b['id']))
 def test_strict_inputs_and_wrong_operator_specific_controls_rejected(self):
  for key,value in(('gold',False),('gold',-1),('seeds',True),('seeds',-1),('seeds',1.5),('controller',1)):
   with self.assertRaises(ValueError):model.reference('沉寂之屋'if key=='gold'else'呼吸的红苔',**{key:value})
  with self.assertRaises(ValueError):model.reference('沉寂之屋',controller=True)
  with self.assertRaises(ValueError):model.reference('呼吸的红苔',gold=8)
 def test_two_catalogue_admissions_full_objects_exact8_links_warm_drift_and_title_only_rejected(self):
  for key in model.CATALOGUE_IDS:
   row=next(x for x in node_catalog.all_events(include_indirect=True)['rows']if x['id']==key);b=bridge.binding_for(row);self.assertEqual(len(b['exact_scene_links']),4);self.assertIsNotNone(bridge.recheck(b));self.assertFalse(b['actual_node_version_confirmed']);bad=deepcopy(row);bad['title']='same title from another version';self.assertIsNone(bridge.binding_for(bad));bad=deepcopy(node_catalog._event(key));bad['scenes'][0]['description']+='drift'
   with patch.object(node_catalog,'_event',return_value=bad):self.assertIsNone(bridge.binding_for(row))
 def test_every_source_file_damage_and_current_full_record_drift_fails_closed(self):
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
   with patch.object(model,'ROOT',root):
    for name in(model.MANIFEST,*m['files']):
     f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
  r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_normal3_2']['description']='unverified'
  with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
 def test_builder_rejects_changed_next_and_duplicate_scene(self):
  for kind in('next','scene'):
   with TemporaryDirectory()as folder:
    root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
    if kind=='next':d['details']['choices']['choice_ro6_normal3_2']['nextSceneId']='scene_ro6_normal1_2'
    else:d['details']['choiceScenes']['invented']=deepcopy(d['details']['choiceScenes']['scene_ro6_normal3_2'])
    f.write_bytes(builder.encoded(d))
    with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
