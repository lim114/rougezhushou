"""Public305 fixed offering/flow checks; no game, chat, Qt or run state."""
import copy
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from rouge import relic_exchange_flow as flow,node_catalog

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_025'
STOP_KEYS=(EVENT+':scene:3:choice:1',EVENT+':scene:7:choice:1')
ORIGINAL_STOP_IDS=('scene_ro6_sacrifice1_10','scene_ro6_sacrifice1_17','scene_ro6_sacrifice2_10','scene_ro6_sacrifice2_17')
ACTUAL=('actual_selectable','actual_consumed','actual_reward','actual_quantity','actual_reward_pool',
 'actual_offered_consumed','actual_eligible','quantity','reward_pool')

class OfferingFlow305(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.primary=json.loads((ROOT/'research/p3-future-region-effects-300/game-topic-complete.json').read_text(encoding='utf8'))['details']['rogue_6']
  cls.catalog=json.loads((ROOT/'rouge/data/node-catalog.json').read_text(encoding='utf8'))
  cls.event=next(e for e in cls.catalog['events']if e['id']==EVENT)
  cls.items={k:v for k,v in cls.primary['items'].items()if v['type']=='RELIC'}
  cls.allowed=next(k for k,v in cls.items.items()if v['canSacrifice'])
  cls.forbidden=next(k for k,v in cls.items.items()if not v['canSacrifice'])
 def assertActualUnknown(self,result):
  for key in ACTUAL:self.assertIsNone(result[key],key)
  for key in('inventory_updated','calculation_applied','run_state_updated'):self.assertIs(result[key],False,key)
 def test_complete272_primary_objects_and_offer_direction(self):
  p=flow.event_reference(EVENT)
  self.assertEqual(len(p['catalogue']),272);self.assertEqual(p['catalogue_scope']['offer_false'],21)
  self.assertFalse(p['catalogue_scope']['current_complete_catalogue'])
  self.assertEqual({x['item_id']:x['item']for x in p['catalogue']},self.items)
  for x in p['catalogue']:
   self.assertEqual([x['name'],x['rarity'],x['canSacrifice']],[x['item']['name'],x['item']['rarity'],x['item']['canSacrifice']])
   self.assertIs(type(x['canSacrifice']),bool)
 def test_all272_offering_flags_do_not_create_rewards_or_actual_eligibility(self):
  for key,item in self.items.items():
   with self.subTest(item_id=key):
    p=flow.relic_offer_reference(key,owned=True)
    self.assertEqual(p['item'],item);self.assertIs(p['can_offer_reference'],item['canSacrifice'])
    self.assertEqual(p['documented_condition_status'],'matched'if item['canSacrifice']else'excluded')
    self.assertFalse(p['offering_flag_used_for_reward_side']);self.assertFalse(p['reward_rarity_inferred'])
    self.assertActualUnknown(p)
 def test_all11_scenes19_choices_keep_complete_source_roles(self):
  p=flow.event_reference(EVENT);self.assertEqual(p['scenes'],self.event['scenes']);self.assertEqual(len(p['choices']),19)
  source={c['key']:c for s in self.event['scenes']for c in s['choices']}
  self.assertEqual([x['choice_key']for x in p['choices']],list(source))
  self.assertTrue(any(c['presentation_role']!='display_option_reference'for c in source.values()))
  for row in p['choices']:
   self.assertEqual(row['catalog_choice'],source[row['choice_key']]);self.assertEqual(row['presentation_role'],source[row['choice_key']]['presentation_role'])
   self.assertEqual(row['reference_id'],row['choice_key']);self.assertIsNone(row['related_stage_reference'])
 def test_choice_details_exactly_same_row_for_all19(self):
  p=flow.event_reference(EVENT)
  for row in p['choices']:
   got=flow.choice_details(EVENT,row['scene_key'],row['choice_key']);self.assertEqual(got['reference'],row);self.assertActualUnknown(got)
 def test_two_stop_relations_remain_independent_and_four_way_ambiguous(self):
  p=flow.event_reference(EVENT);stops=[x for x in p['choices']if x['documented_result_text']is not None]
  self.assertEqual([x['choice_key']for x in stops],list(STOP_KEYS))
  for row in stops:
   self.assertEqual([x['id']for x in row['original_scene_candidates']],list(ORIGINAL_STOP_IDS))
   self.assertTrue(all(x['description']==row['documented_result_text']for x in row['original_scene_candidates']))
   # Preserve the older community navigation; it is not a recovered server edge.
   target=next(s for s in self.event['scenes']if s['key']==EVENT+':scene:5')
   self.assertEqual(row['documented_destinations'],[{'scene_key':target['key'],
    'description':target['description'],'game_scene_ids':target['game_scene_ids'],
    'evidence':'existing_fixed_community_navigation','actual_reached':None}])
   self.assertEqual(row['catalog_choice']['destination_keys'],[target['key']])
   self.assertEqual(row['catalog_choice']['game_match_basis'],'destination_mismatch')
   self.assertNotEqual(target['description'],row['documented_result_text'])
   self.assertFalse(row['source_scene_link_verified']);self.assertEqual(row['original_choice_ids'],[])
   self.assertIsNone(row['current_actual_original_candidate'])
  a=stops[0]['documented_rules'][0]['source_refs'][0];b=stops[1]['documented_rules'][0]['source_refs'][0]
  self.assertNotEqual(a['branch_label'],b['branch_label']);self.assertNotEqual(a['result_row']['byte_start'],b['result_row']['byte_start'])
 def test_all_existing_destinations_preserved_no_new_server_edges(self):
  p=flow.event_reference(EVENT)
  for row in p['choices']:
   destinations=row['catalog_choice']['destination_keys']
   self.assertEqual([x['scene_key']for x in row['documented_destinations']],destinations)
   for x in row['documented_destinations']:
    s=next(v for v in self.event['scenes']if v['key']==x['scene_key'])
    self.assertEqual(x['description'],s['description']);self.assertEqual(x['game_scene_ids'],s['game_scene_ids']);self.assertIsNone(x['actual_reached'])
 def test_ownership_three_states_and_never_quantity(self):
  for owned,expected in [(None,'unknown'),(False,'excluded'),(True,'matched')]:
   p=flow.relic_offer_reference(self.allowed,owned=owned);self.assertEqual(p['documented_condition_status'],expected);self.assertActualUnknown(p)
 def test_second_palm_three_states(self):
  for palm,expected in [(None,'unknown'),(False,'excluded'),(True,'matched')]:
   p=flow.relic_offer_reference(self.allowed,exchange_index=2,first_exchange_item_type='RELIC',palm_unlocked=palm,owned=True)
   self.assertEqual(p['documented_condition_status'],expected);self.assertActualUnknown(p)
 def test_second_first_type_three_states(self):
  for first,expected in [(None,'unknown'),('SCRAP','excluded'),('RELIC','matched')]:
   p=flow.relic_offer_reference(self.allowed,exchange_index=2,first_exchange_item_type=first,palm_unlocked=True,owned=True)
   self.assertEqual(p['documented_condition_status'],expected)
 def test_forbidden_flag_cannot_be_overridden_by_other_matches(self):
  p=flow.relic_offer_reference(self.forbidden,exchange_index=2,first_exchange_item_type='RELIC',palm_unlocked=True,owned=True)
  self.assertEqual(p['documented_condition_status'],'excluded');self.assertIs(p['can_offer_reference'],False);self.assertActualUnknown(p)
 def test_non_target_and_invalid_tuples_are_no_io(self):
  with patch.object(flow,'_packet',side_effect=AssertionError('must not read')):
   for value in(None,False,1,[],{},'community_group_024'):self.assertIsNone(flow.event_reference(value))
   for value in(None,False,1,[],{},'not-an-item'):self.assertIsNone(flow.relic_offer_reference(value))
   self.assertIsNone(flow.choice_details(EVENT,'community_group_031:scene:0',STOP_KEYS[0]))
   self.assertIsNone(flow.choice_details(EVENT,EVENT+':scene:3',EVENT+':scene:3:choice:404'))
   self.assertIsNone(flow.choice_details(False,False,False))
 def test_integer_bool_and_unknown_input_validation_before_io(self):
  with patch.object(flow,'_packet',side_effect=AssertionError('must not read')):
   for value in(False,True,0,3,1.0,'1',None):
    with self.subTest(index=value),self.assertRaises(ValueError):flow.relic_offer_reference(self.allowed,exchange_index=value)
   for key in('owned','palm_unlocked'):
    for value in(0,1,'true',[],{}):
     with self.subTest(key=key,value=value),self.assertRaises(ValueError):flow.relic_offer_reference(self.allowed,**{key:value})
   for first in('SCRAP','RELIC'):
    with self.assertRaises(ValueError):flow.relic_offer_reference(self.allowed,first_exchange_item_type=first)
   for first in(False,1,[],{},'加工品'):
    with self.assertRaises(ValueError):flow.relic_offer_reference(self.allowed,exchange_index=2,first_exchange_item_type=first)
 def test_defensive_copy_and_no_mutable_packet_cache(self):
  p=flow.event_reference(EVENT);p['catalogue'][0]['item']['canSacrifice']='poison';p['choices'][0]['catalog_choice']['title']='poison';p['flow_notices'].clear()
  q=flow.event_reference(EVENT);self.assertEqual(q['catalogue'][0]['item'],self.items[q['catalogue'][0]['item_id']]);self.assertEqual(q['choices'][0]['catalog_choice'],self.event['scenes'][0]['choices'][0]);self.assertTrue(q['flow_notices'])
 def test_legacy_nested_event_cache_pollution_rejected(self):
  e=copy.deepcopy(self.event);e['scenes'][0]['choices'][0]['description']='poison'
  with patch.object(node_catalog,'_event',return_value=e):
   for got in(flow.event_reference(EVENT),flow.choice_details(EVENT,EVENT+':scene:0',EVENT+':scene:0:choice:0'),flow.relic_offer_reference(self.allowed)):
    self.assertEqual(got['status'],'source_unavailable');self.assertEqual(got['choices'],[]);self.assertIsNone(got['source_identity']);self.assertIsNone(got['reference'])
 def test_every_runtime_member_fresh_tamper_delete_and_recovery(self):
  manifest=json.loads((ROOT/flow.MANIFEST).read_text(encoding='utf8'))
  with tempfile.TemporaryDirectory()as td:
   tmp=Path(td)
   for name in[flow.MANIFEST,*manifest['runtime_files']]:
    dst=tmp/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
   with patch.object(flow,'ROOT',tmp):
    self.assertEqual(flow.event_reference(EVENT)['status'],'documented_reference')
    for name in manifest['runtime_files']:
     f=tmp/name;original=f.read_bytes()
     for action in('tamper','delete'):
      if action=='tamper':f.write_bytes(original+b' ')
      else:f.unlink()
      self.assertEqual(flow.event_reference(EVENT)['status'],'source_unavailable')
      self.assertEqual(flow.relic_offer_reference(self.allowed)['status'],'source_unavailable')
      self.assertEqual(flow.choice_details(EVENT,EVENT+':scene:0',EVENT+':scene:0:choice:0')['status'],'source_unavailable')
      f.write_bytes(original);self.assertEqual(flow.event_reference(EVENT)['status'],'documented_reference')
 def test_source_labels_and_actual_vs_declared_boundary(self):
  p=flow.event_reference(EVENT);self.assertEqual(p['rarity_labels'],{'NORMAL':'低稀有度','RARE':'中稀有度','SUPER_RARE':'高稀有度'})
  self.assertIn('固定本体',p['catalogue_scope']['label']);self.assertFalse(p['current_server_verified']);self.assertFalse(p['original_entry_restored']);self.assertActualUnknown(p)
 def test_source_rebuild_from_complete_documents_is_deterministic(self):
  path=ROOT/'scripts/build_relic_exchange_flow_305.py';sp=spec_from_file_location('builder305_deterministic',path);builder=module_from_spec(sp);sp.loader.exec_module(builder)
  with tempfile.TemporaryDirectory()as td:
   temp=Path(td)
   for name in('notrade-corner-433235.html','relic-index-current.html','http-source-records.json','backend-template.py'):
    dest=temp/flow.PACK/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/flow.PACK/name,dest)
   result=builder.build(ROOT,temp)
   for name in result['outputs']:self.assertEqual((temp/name).read_bytes(),(ROOT/name).read_bytes(),name)

if __name__=='__main__':unittest.main()
