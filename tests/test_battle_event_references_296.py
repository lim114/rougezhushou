"""Necessary exact identity, source freshness and manual-token boundaries."""
from copy import deepcopy
from hashlib import sha256
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge import battle_event_references as model

GOLD={
 'ro6_t_1':('community_group_012','思乡心切',[1,2],[(1,0)],[]),
 'ro6_t_2':('community_group_013','划算买卖',[2,3],[(1,0)],[]),
 'ro6_t_3':('community_group_014','鸭托邦',[3,4],[(1,0)],[(2,0)]),
 'ro6_t_4':('community_group_015','传奇团伙',[4,5,6],[(1,0)],[(2,0)]),
 'ro6_t_5':('community_group_016','湖中仙女',[3,4,5],[(3,0)],[(8,0)]),
 'ro6_e_t_3':('community_group_014','鸭托邦',[3,4],[(1,0),(2,0)],[]),
 'ro6_e_t_4':('community_group_015','传奇团伙',[4,5,6],[(1,0),(2,0)],[]),
 'ro6_e_t_5':('community_group_016','湖中仙女',[3,4,5],[(3,0),(8,0)],[])}

class BattleEventReferencesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source_root=model.ROOT
  cls.manifest=json.loads((cls.source_root/model.MANIFEST).read_bytes())
  cls.original_pins={name:sha256((cls.source_root/name).read_bytes()).hexdigest()
   for name in[model.MANIFEST,*cls.manifest['files']]}
  cls.temporary=tempfile.TemporaryDirectory(prefix='rouge-296-public-reference-test-')
  cls.clone=Path(cls.temporary.name)
  for name in cls.original_pins:
   target=cls.clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((cls.source_root/name).read_bytes())
  cls.root_patch=patch.object(model,'ROOT',cls.clone);cls.root_patch.start()
 @classmethod
 def tearDownClass(cls):
  cls.root_patch.stop()
  assert cls.original_pins=={name:sha256((cls.source_root/name).read_bytes()).hexdigest()for name in cls.original_pins}
  cls.temporary.cleanup()
 def reference(self,sid='ro6_t_3'):
  result=model.stage_event_references(sid)
  self.assertEqual(result['status'],'documented_reference');self.assertTrue(result['source_valid']);return result

 def test_eight_exact_stage_ids_fourteen_original_eleven_admitted_three_excluded(self):
  values=[self.reference(sid)for sid in GOLD]
  self.assertEqual(sum(v['raw_edge_count']for v in values),14)
  self.assertEqual(sum(len(v['rows'])for v in values),11)
  self.assertEqual(sum(len(v['excluded_rows'])for v in values),3)
  for value in values:self.assertEqual(value['scope_counts'],{'raw_edges':14,'admitted_edges':11,'explicit_exclusions':3,'events':5,'choices':8,'stage_ids':8})

 def test_complete_event_scene_and_choice_literal_identity_for_all_fourteen_edges(self):
  for sid,(event,title,floors,admitted,excluded)in GOLD.items():
   value=self.reference(sid)
   for name,pairs in(('rows',admitted),('excluded_rows',excluded)):
    self.assertEqual([(r['scene_key'],r['choice_key'])for r in value[name]],
     [(event+':scene:'+str(si),event+':scene:'+str(si)+':choice:'+str(ci))for si,ci in pairs])
    for row in value[name]:
     self.assertEqual((row['stage_id'],row['event_id'],row['event_title'],row['event_documented_main_floors']),(sid,event,title,floors))
     self.assertEqual(row['event_node_types'],['不期而遇'])

 def test_explicit_emergency_choices_cannot_be_normal_stage_navigation_tokens(self):
  for sid in('ro6_t_3','ro6_t_4','ro6_t_5'):
   row=self.reference(sid)['excluded_rows'][0]
   self.assertEqual(row['conditional_text'],'升级为紧急作战')
   self.assertFalse(row['source_difficulty_matches']);self.assertTrue(row['excluded_by_explicit_difficulty'])
   self.assertIsNone(row['token'])

 def test_emergency_alias_retains_both_ordinary_choice_variant_and_emergency_choice(self):
  for sid in('ro6_e_t_3','ro6_e_t_4','ro6_e_t_5'):
   result=self.reference(sid);self.assertEqual(len(result['rows']),2)
   self.assertEqual([r['source_difficulty_matches']for r in result['rows']],[None,True])
   self.assertTrue(all(r['stage_reference']['difficulty']=='FOUR_STAR'for r in result['rows']))
   self.assertFalse(result['excluded_rows'])

 def test_same_level_and_name_do_not_merge_distinct_stage_difficulty_aliases(self):
  normal=self.reference()['rows'][0];emergency=self.reference('ro6_e_t_3')['rows'][0]
  self.assertEqual(normal['stage_reference']['name'],emergency['stage_reference']['name'])
  self.assertEqual(normal['stage_reference']['level_id'],emergency['stage_reference']['level_id'])
  self.assertNotEqual(normal['reference_id'],emergency['reference_id'])
  self.assertNotEqual(normal['token'],emergency['token'])

 def test_event_floor_declarations_never_become_all_stage_origins_or_actual_entry(self):
  for sid in GOLD:
   value=self.reference(sid)
   for item in[value,*value['rows'],*value['excluded_rows']]:
    self.assertIsNone(item['stage_global_floors']);self.assertFalse(item['full_stage_origin_floors_known'])
    for key in('actual_stage_id','actual_choice_eligible','actual_entered'):self.assertIsNone(item[key])
   for row in value['rows']:
    self.assertEqual(row['event_floor_scope'],'event_documented_main_floors_only');self.assertFalse(row['source_scene_link_verified'])

 def test_full_fixed_level_source_and_original_stage_fields_are_not_filename_fallbacks(self):
  value=self.reference();stage=value['stage_reference']
  self.assertEqual(stage['stage_id'],'ro6_t_3');self.assertEqual(stage['name'],'开业剪彩')
  self.assertEqual(stage['code'],'ISW-NO');self.assertEqual(stage['difficulty'],'NORMAL')
  self.assertEqual(stage['level_id'],'Obt/Roguelike/RO6/level_rogue6_t-3')
  self.assertEqual(stage['source_selector'],'$.details.rogue_6.stages.ro6_t_3')
  self.assertEqual(stage['level_source']['sha256'],'2f637de071447b5a1ad8beeb4fbe42493887371d101417712bd109d32e3f57b3')
  self.assertEqual(stage['level_source']['bytes'],76623)
  self.assertIn('/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/',stage['level_source']['url'])

 def test_source_derived_numbers_follow_actual_full_event_scene_and_choice_order(self):
  for sid,(_,_,_,pairs,excluded)in GOLD.items():
   value=self.reference(sid)
   for row,(scene,choice)in zip([*value['rows'],*value['excluded_rows']],[*pairs,*excluded]):
    self.assertEqual((row['scene_number'],row['choice_number']),(scene+1,choice+1))
    if row['token']:
     self.assertEqual(row['token']['scene_number'],scene+1);self.assertEqual(row['token']['choice_number'],choice+1)

 def test_reference_ids_are_stable_and_page_sensitive_across_all_raw_edges(self):
  first=[r['reference_id']for sid in GOLD for r in[*self.reference(sid)['rows'],*self.reference(sid)['excluded_rows']]]
  second=[r['reference_id']for sid in GOLD for r in[*self.reference(sid)['rows'],*self.reference(sid)['excluded_rows']]]
  self.assertEqual(first,second);self.assertEqual(len(first),len(set(first)));self.assertEqual(len(first),14)
  self.assertTrue(all(r.startswith('battle-event:')and len(r)==77 for r in first))

 def test_all_eleven_complete_tokens_resolve_after_a_fresh_source_check(self):
  for sid in GOLD:
   for row in self.reference(sid)['rows']:
    self.assertEqual(model.resolve_stage_event_reference(sid,row['token']),row)
    self.assertEqual(row['reference_id'],row['token']['reference_id'])

 def test_current_stage_must_equal_full_token_stage_even_when_level_is_shared(self):
  token=self.reference()['rows'][0]['token']
  self.assertIsNone(model.resolve_stage_event_reference('ro6_e_t_3',token))
  self.assertIsNone(model.resolve_stage_event_reference('ro6_t_4',token))

 def test_every_top_level_token_key_is_required_and_no_extra_key_is_accepted(self):
  token=self.reference()['rows'][0]['token']
  for key in token:
   changed=deepcopy(token);changed.pop(key);self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed),key)
  changed=deepcopy(token);changed['context']={};self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed))

 def test_nested_full_identity_fields_are_not_ignored(self):
  token=self.reference()['rows'][0]['token']
  for section in('stage_record','stage_page','level_source','source_identity'):
   for key in token[section]:
    changed=deepcopy(token);changed[section].pop(key)
    self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed),(section,key))
  for section,key in(('stage_page','url'),('stage_record','source_selector'),('source_identity','manifest_sha256')):
   changed=deepcopy(token);changed[section][key]+='x';self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed))

 def test_bool_and_subclass_keys_do_not_alias_int_or_builtin_str_fields(self):
  class Text(str):pass
  token=self.reference()['rows'][0]['token']
  for mutate in('boss','scene','level_bytes','key_subclass','value_subclass'):
   changed=deepcopy(token)
   if mutate=='boss':changed['stage_record']['is_boss_parameter']=False
   elif mutate=='scene':changed['scene_number']=True
   elif mutate=='level_bytes':changed['level_source']['bytes']=True
   elif mutate=='key_subclass':changed[Text('event_id')]=changed.pop('event_id')
   else:changed['event_id']=Text(changed['event_id'])
   self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed),mutate)

 def test_titles_or_partial_choice_keys_cannot_replace_exact_reference(self):
  token=self.reference()['rows'][0]['token']
  for key,value in(('event_id','鸭托邦'),('choice_key','区区打手！'),('reference_id',token['choice_key'])):
   changed=deepcopy(token);changed[key]=value;self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',changed))

 def test_explicitly_excluded_normal_edge_cannot_be_forged_from_an_admitted_token(self):
  value=self.reference();excluded=value['excluded_rows'][0];token=deepcopy(value['rows'][0]['token'])
  for key in('reference_id','event_id','scene_key','choice_key','scene_number','choice_number'):token[key]=excluded[key]
  self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',token))

 def test_non_exact_targets_do_not_read_sources_or_forward_queries(self):
  class Text(str):pass
  with patch.object(Path,'read_bytes',side_effect=AssertionError('must not read'))as reads:
   with patch.object(model.event_planning,'event_battle_links',side_effect=AssertionError('must not query'))as query:
    for value in(None,True,1,[],{},Text('ro6_t_3'),'开业剪彩','ro6_t_12','ro6_t_8','ro6_n_1_2','ro6_t_13'):
     self.assertIsNone(model.stage_event_references(value))
     self.assertIsNone(model.resolve_stage_event_reference(value,{}))
   query.assert_not_called()
  reads.assert_not_called()

 def test_source_public_apis_do_not_accept_context_data_or_evaluator_overrides(self):
  self.assertEqual(list(inspect.signature(model.stage_event_references).parameters),['stage_id'])
  self.assertEqual(list(inspect.signature(model.resolve_stage_event_reference).parameters),['stage_id','token'])
  self.assertEqual(list(inspect.signature(model.source_data).parameters),[])
  for name in('context','data','source','evaluator'):
   with self.assertRaises(TypeError):model.stage_event_references('ro6_t_3',**{name:{}})

 def test_public_query_mutation_never_changes_later_rows_or_tokens(self):
  before=self.reference();changed=self.reference();changed['rows'][0]['token']['stage_record']['name']='poison'
  changed['rows'][0]['event_documented_main_floors'].append(6);changed['excluded_rows'].clear()
  self.assertEqual(self.reference(),before)

 def test_source_data_and_resolved_rows_are_defensive_copies(self):
  before=model.source_data();changed=model.source_data();changed['edges'].clear();changed['sources'].clear()
  self.assertEqual(model.source_data(),before)
  row=self.reference()['rows'][0];resolved=model.resolve_stage_event_reference('ro6_t_3',row['token'])
  resolved['token']['source_identity']['documents'].clear();self.assertEqual(model.resolve_stage_event_reference('ro6_t_3',row['token']),row)

 def test_warm_legacy_planning_lru_mutation_is_rejected_even_with_unchanged_disk(self):
  self.reference()
  cached=model.event_planning.reference_data();saved=deepcopy(cached)
  try:
   raw=next(r for r in cached['battle_links']if r['event_id']=='community_group_014')
   raw['stage_page_links'][0]['stage_records'][0]['name']='缓存污染'
   result=model.stage_event_references('ro6_t_3')
   self.assertEqual(result['status'],'unknown');self.assertFalse(result['source_valid'])
   self.assertEqual(result['rows'],[]);self.assertEqual(result['excluded_rows'],[])
  finally:cached.clear();cached.update(saved)
  self.reference()

 def test_warm_legacy_catalog_lru_floor_mutation_is_rejected(self):
  self.reference()
  cached=model.event_planning.catalog._data();saved=deepcopy(cached)
  try:
   next(e for e in cached['events']if e['id']=='community_group_014')['floors']=[1]
   self.assertEqual(model.stage_event_references('ro6_t_3')['status'],'unknown')
  finally:cached.clear();cached.update(saved)
  self.reference()

 def test_forward_api_is_used_without_any_current_inventory_or_context(self):
  original=model.event_planning.event_battle_links
  with patch.object(model.event_planning,'event_battle_links',wraps=original)as query:
   self.reference();query.assert_called_once_with('community_group_014')

 def test_every_bound_file_tamper_and_missing_is_rejected_after_warm_call(self):
  token=self.reference()['rows'][0]['token']
  for name in self.original_pins:
   target=self.clone/name;raw=target.read_bytes()
   for missing in(False,True):
    with self.subTest(name=name,missing=missing):
     self.reference()
     try:
      if missing:target.unlink()
      else:target.write_bytes(raw+b' ')
      self.assertIsNone(model.source_data())
      value=model.stage_event_references('ro6_t_3')
      self.assertEqual(value['status'],'unknown');self.assertFalse(value['source_valid'])
      self.assertEqual(value['rows'],[]);self.assertEqual(value['excluded_rows'],[]);self.assertIsNone(value['stage_reference'])
      self.assertIsNone(value['source_identity']);self.assertIsNone(model.resolve_stage_event_reference('ro6_t_3',token))
     finally:target.write_bytes(raw)
     self.reference()

 def test_source_revision_and_exact_counts_are_reference_only(self):
  data=model.source_data()
  self.assertEqual([d['revision']for d in data['sources']['documents']],['427904','440271'])
  self.assertEqual(data['sources']['original_game']['commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
  self.assertFalse(data['current_server_verified']);self.assertIsNone(data['actual_entered'])
  self.assertIn('不是作战全部入口',self.reference()['notice'])

 def test_warm_catalog_choice_description_and_original_ids_cannot_hide_behind_forward_projection(self):
  self.reference()
  cached=model.event_planning.catalog._data();saved=deepcopy(cached)
  for field,value in(('description','Isolated cached description mismatch'),('game_choice_ids',['forged-original-choice'])):
   try:
    event=next(e for e in cached['events']if e['id']=='community_group_014')
    event['scenes'][1]['choices'][0][field]=value
    result=model.stage_event_references('ro6_t_3')
    self.assertEqual(result['status'],'unknown');self.assertEqual(result['rows'],[]);self.assertEqual(result['excluded_rows'],[])
   finally:cached.clear();cached.update(deepcopy(saved))
   self.reference()

 def test_warm_planning_original_choice_payload_must_also_equal_fresh_current_bytes(self):
  self.reference()
  cached=model.event_planning.reference_data();saved=deepcopy(cached)
  try:
   cached['original_choices']['choice_ro6_bat3_3']['description']='Isolated cached original-choice mismatch'
   self.assertEqual(model.stage_event_references('ro6_t_3')['status'],'unknown')
  finally:cached.clear();cached.update(saved)
  self.reference()

if __name__=='__main__':unittest.main()
