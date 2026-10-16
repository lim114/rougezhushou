"""Real candidate, eligibility and player consumers of the literal source rules."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge import node_catalog as catalog, event_planning as planning
from rouge import event_node_requirements as model
from rouge.player_node_information import node_information_text

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'verification/sections/298-preparation/before-output.json'
FORBIDDEN={'community_group_024':{1,5,6},'community_group_025':{1,6},
 'community_group_027':{1,2,6},'community_group_028':{1,2,6},
 'community_group_029':{1,2,6},'community_group_037':{1}}
KEY='documented_node_natural_main_floor'
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def check(row):return next((c for c in row['checks'] if c['key']==KEY),None)
def graph(kind='先行一步',**extra):
 return {'template_id':'public-fixture','zone_id':'main6','nodes':[
  {'id':'target','row':0,'col':0,'observed_type':kind,**extra}],'edges':[]}

class EventNodeRequirementsIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.saved=model._parsed_packet;model._parsed_packet=None
  self.addCleanup(setattr,model,'_parsed_packet',self.saved)

 def test_real_candidates_and_eligibility_complete_36_contexts(self):
  for identity,forbidden in FORBIDDEN.items():
   event=catalog._event(identity);kind=event['node_types'][0]
   for floor in range(1,7):
    with self.subTest(event=identity,floor=floor):
     r=catalog.event_candidates(kind,floor);rows={x['id']for x in r['rows']};excluded={x['id']for x in r['excluded']}
     self.assertEqual(identity in excluded,floor in forbidden);self.assertEqual(identity in rows,floor not in forbidden)
     qualification=planning.event_eligibility(identity,{'node_type':kind,'floor':floor,'entry_mode':'natural'})
     self.assertIs(check(qualification)['matches'],floor not in forbidden)
     self.assertEqual(qualification['status'],'excluded'if floor in forbidden else 'unknown')
     self.assertIsNone(qualification['actual_server_eligible'])
     if floor in forbidden:self.assertIn('不会',next(x for x in r['excluded']if x['id']==identity)['reason'])

 def test_content_unknown_processed_history_and_special_do_not_borrow_natural_ban(self):
  for identity in FORBIDDEN:
   kind=catalog._event(identity)['node_types'][0]
   for context in ({'entry_mode':'content'},{'entry_mode':'unknown'},{'entry_mode':'processed_item'},
                   {'entry_mode':'history'},{'historical':True},{'special_region':True}):
    with self.subTest(event=identity,context=context):
     self.assertIn(identity,{e['id']for e in catalog.event_candidates(kind,1,**context)['rows']})
   for context in ({'entry_mode':'content'},{'entry_mode':'unknown'},{'entry_mode':'processed_item'},
      {'entry_mode':'natural','special_region':True},
      {'entry_mode':'natural','reference_context_scope':'historical_title_reference_only'}):
    self.assertIsNone(check(planning.event_eligibility(identity,{'floor':1,**context})))

 def test_unknown_floor_does_not_use_an_arbitrary_main_floor(self):
  for identity in FORBIDDEN:
   kind=catalog._event(identity)['node_types'][0]
   self.assertIn(identity,{e['id']for e in catalog.event_candidates(kind)['rows']})
   self.assertIsNone(check(planning.event_eligibility(identity,{'entry_mode':'natural'})))

 def test_new_content_and_history_candidate_modes_preserve_old_positive_floor_references_too(self):
  identity=next(e['id']for e in catalog.all_events()['rows']if e['title']=='桑尼的邀请')
  self.assertNotIn(identity,{e['id']for e in catalog.event_candidates('不期而遇',6)['rows']})
  for context in ({'entry_mode':'content'},{'entry_mode':'unknown'},{'entry_mode':'history'},{'historical':True}):
   self.assertIn(identity,{e['id']for e in catalog.event_candidates('不期而遇',6,**context)['rows']})

 def test_inapplicable_default_eligibility_never_reads_unneeded_new_source_packet(self):
  with patch.object(model,'_verified_packet',side_effect=AssertionError('unneeded new source read')):
   for identity in FORBIDDEN:
    self.assertIsNone(check(planning.event_eligibility(identity)))
    self.assertIsNone(check(planning.event_eligibility(identity,{'entry_mode':'natural'})))

 def test_unknown_type_union_only_excludes_proven_specific_events(self):
  node={'id':'unknown','observed_type':'未知的诡秘','prediction':{'candidates':['先行一步','不期而遇','失与得']}}
  original=deepcopy(node);r=catalog.node_events(node,6)
  self.assertEqual({e['id']for e in r['excluded']if e['id']in FORBIDDEN},{'community_group_024','community_group_025'})
  self.assertTrue(any('不期而遇'in e['node_types']for e in r['rows']));self.assertEqual(node,original)
  self.assertFalse(any(e['id']in ('community_group_024','community_group_025')for e in r['rows']))

 def test_node_dossier_keeps_excluded_manual_reference_but_not_as_candidate(self):
  g=graph();original=deepcopy(g);r=catalog.node_dossier(g,'target',6)
  self.assertFalse(r['rows']);self.assertFalse(r['generic_event_candidates'])
  self.assertEqual([e['id']for e in r['excluded_event_candidates']],['community_group_024'])
  self.assertEqual(g,original);self.assertEqual(len(catalog.event_details('community_group_024')['rows']),4)

 def test_observed_title_conflict_survives_with_original_content_and_not_false_new_exclusion(self):
  g=graph(content={'kind':'event','title':'未涉足之树'});old=deepcopy(g)
  r=catalog.node_dossier(g,'target',6)
  self.assertEqual([e['id']for e in r['rows']],['community_group_024']);self.assertFalse(r['excluded_event_candidates'])
  self.assertEqual(r['current_content'],g['nodes'][0]['content']);self.assertEqual(g,old)
  result=planning.event_eligibility('community_group_024',{'floor':6,'entry_mode':'content'})
  self.assertIsNone(check(result));self.assertNotEqual(result['status'],'excluded')

 def test_passed_clearing_keeps_previous_event_in_history_without_natural_filter(self):
  g=graph('林间空地',remembered_type='先行一步',remembered_content={'kind':'event','title':'未涉足之树'})
  old=deepcopy(g);r=catalog.node_dossier(g,'target',6)
  self.assertFalse(r['rows']);self.assertFalse(r['excluded_event_candidates'])
  self.assertEqual([e['id']for e in r['history_observed_event_rows']],['community_group_024']);self.assertEqual(g,old)

 def test_all_default_190_resource_and_38_player_outputs_remain_exact_parent_bytes(self):
  before=json.loads(BASELINE.read_bytes());self.assertEqual(sha256(BASELINE.read_bytes()).hexdigest(),'68f0d3cd7d116ced58046fb4d40570620b066e6c6303c771db687f53d123ca7b')
  resources={};players={}
  for event in catalog.all_events(include_indirect=True)['rows']:
   players[event['id']]=sha256(node_information_text({'kind':'event','record':event}).encode()).hexdigest()
   for scene in catalog.event_details(event['id'])['rows']:
    resources[scene['key']]=sha256(canon(planning.choice_resources(event['id'],scene['key']))).hexdigest()
  self.assertEqual(len(players),38);self.assertEqual(len(resources),190)
  self.assertEqual(players,before['default_player_events']);self.assertEqual(resources,before['default_choice_resources_scenes'])

 def test_other_32_natural_context_player_outputs_are_unchanged(self):
  before=json.loads(BASELINE.read_bytes());actual={}
  for e in catalog.all_events(include_indirect=True)['rows']:
   if e['id']in FORBIDDEN:continue
   context={'node_type':e['node_types'][0]if e['node_types']else None,'floor':3,'entry_mode':'natural'}
   actual[e['id']]=sha256(node_information_text({'kind':'event','record':e},context=context).encode()).hexdigest()
  self.assertEqual(len(actual),32);self.assertEqual(actual,before['non_target_natural_floor3_player_events'])

 def test_explicit_target_resources_only_add_one_documented_check_and_derived_status(self):
  before=json.loads(BASELINE.read_bytes())['target_natural_floor6_resources'];seen=0
  for identity in FORBIDDEN:
   event=catalog._event(identity);context={'node_type':event['node_types'][0],'floor':6,'entry_mode':'natural'}
   for scene in event['scenes']:
    result=planning.choice_resources(identity,scene['key'],context);expected=before[scene['key']]
    self.assertEqual(len(result['rows']),len(expected['rows']))
    for actual,old in zip(result['rows'],expected['rows']):
     q=actual['choice_eligibility'];oldq=old['choice_eligibility']
     added=[c for c in q['checks']if c['key']==KEY];self.assertEqual(len(added),1)
     self.assertIs(added[0]['matches'],6 not in FORBIDDEN[identity])
     q['checks']=[c for c in q['checks']if c['key']!=KEY];q['status']=oldq['status']
    self.assertEqual(result,expected);seen+=1
  self.assertEqual(seen,32)

 def test_player_explains_main_floor_exclusion_in_game_terms_and_nonexclusive_technology(self):
  e=catalog._summary(catalog._event('community_group_024'));entry={'kind':'event','record':e}
  text=node_information_text(entry,context={'floor':6,'entry_mode':'natural'})
  self.assertIn('【自然出现的已知条件】',text);self.assertIn('第1层、第5层、第6层',text)
  self.assertIn('下方仍可查阅完整事件资料',text);self.assertIn('生命游戏中的“眼睛”',text)
  self.assertIn('不能据未点亮就认定绝不出现',text)
  content=node_information_text(entry,context={'floor':6,'entry_mode':'content'})
  self.assertIn('不据此删除内容或判定不能进入',content)
  for technical in ('rogue_6_outbuff','source_node_floor_requirement','False','None'):self.assertNotIn(technical,text)

 def test_technology_false_is_not_injected_as_a_necessary_negative_gate(self):
  for identity,tech in (('community_group_024','rogue_6_outbuff_9'),('community_group_027','rogue_6_outbuff_7')):
   q=planning.event_eligibility(identity,{'floor':3,'entry_mode':'natural','technology_active':{tech:False}})
   self.assertTrue(check(q)['matches']);self.assertEqual(q['status'],'unknown')

 def test_warm_source_failure_returns_unknown_and_restoration_never_writes_inventory(self):
  identity='community_group_024';context={'floor':6,'entry_mode':'natural'}
  self.assertEqual(planning.event_eligibility(identity,context)['status'],'excluded')
  with patch.object(model,'MANIFEST_SHA256','0'*64):
   q=planning.event_eligibility(identity,context);self.assertEqual(q['status'],'unknown');self.assertIsNone(check(q)['matches'])
   self.assertIn(identity,{e['id']for e in catalog.event_candidates('先行一步',6)['rows']})
   text=node_information_text({'kind':'event','record':catalog._summary(catalog._event(identity))},context=context)
   self.assertIn('不沿用旧限制',text);self.assertNotIn('第1层、第5层、第6层',text);self.assertNotIn('已知开启途径',text)
  q=planning.event_eligibility(identity,context);self.assertEqual(q['status'],'excluded');self.assertFalse(q['inventory_updated'])

 def test_actual_cached_event_mutation_cannot_borrow_rules_even_if_disk_is_intact(self):
  identity='community_group_024';raw=deepcopy(catalog._data());original=catalog._event(identity)
  changed=next(e for e in raw['events']if e['id']==identity);changed['scenes'][0]['description']+='changed'
  with patch.object(catalog,'_data',return_value=raw):
   q=planning.event_eligibility(identity,{'floor':6,'entry_mode':'natural'})
   self.assertEqual(q['status'],'unknown');self.assertIsNone(check(q)['matches'])
   self.assertIn(identity,{e['id']for e in catalog.event_candidates('先行一步',6)['rows']})
  self.assertNotEqual(original,changed)

 def test_history_context_with_accidental_natural_mode_still_never_applies_new_negative(self):
  context={'floor':6,'entry_mode':'natural','reference_context_scope':'historical_title_reference_only'}
  self.assertIsNone(check(planning.event_eligibility('community_group_024',context)))

