import copy,json,unittest
from unittest.mock import patch
from rouge import current_guest_knights as model

class GuestBoss377Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=model.packet();assert cls.packet is not None,'Install the candidate before execution'
  cls.refs={sid:model.reference(sid)for sid in model.STAGES};assert all(cls.refs.values())
 def test_all_actual_stage_aliases_and_exact_reference_pairs(self):
  self.assertEqual(tuple(self.packet['data']['bindings']),model.STAGES)
  actual=set()
  for sid,result in self.refs.items():
   parent=model.battle.stage_reference(sid)
   for row in result['rows']:
    original=next(r for r in parent['enemies']if r['key']==row['key'])
    self.assertEqual(row['enemy'],original);self.assertEqual(row['raw_binding'],original['raw_binding'])
    actual.add((sid,row['key']))
  self.assertEqual(len(actual),sum(len(v['rows'])for v in self.packet['data']['bindings'].values()))
 def test_exact_level_specific_complete_card_selected(self):
  for result in self.refs.values():
   for row in result['rows']:
    profile=result['data']['profiles'][row['actor']]
    for topic,label in model.topics(result,row['key']):
     source=next(t for t in profile['topics']if t['key']==topic)
     index=source['card_by_level'][str(row['level'])]
     card=model.selected_card(result,row['key'],topic)
     self.assertEqual(card,result['data']['materials'][row['actor']]['cards'][index])
     self.assertTrue(card['complete_DOM'].startswith('<div'));self.assertTrue(card['complete_DOM'].endswith('</div>'))
 def test_all_source_levels_and_original_cards_retained(self):
  d=self.packet['data']
  for actor,material in d['materials'].items():
   self.assertTrue(material['revision']>0)
   self.assertTrue(all(c['body']and c['visible_text']for c in material['cards']))
   self.assertTrue(any(row['actor']==actor for b in d['bindings'].values()for row in b['rows']))
 def test_subject_conditions_not_actual_numeric_result(self):
  for result in self.refs.values():
   for row in result['rows']:
    for topic,_ in model.topics(result,row['key']):
     value=model.player_text(result,row['key'],topic)
     self.assertIn('本局',value);self.assertIn('最终预测值仍未知',value)
     for k in('actual_present','actual_form','actual_skill_time','actual_partner_retired','actual_shield','expected_stats'):self.assertIsNone(result[k])
     self.assertFalse(result['numeric_model_added']);self.assertFalse(result['run_updated'])
 def test_unsupported_or_mistyped_exact_identity_fails_closed(self):
  for sid,key in((True,None),('old_same_name',None),(model.STAGES[0],True),(model.STAGES[0],'999')):self.assertIsNone(model.reference(sid,key))
  result=self.refs[model.STAGES[0]];self.assertIsNone(model.entity(result,0))
  self.assertEqual(model.topics(result,'999'),[]);self.assertIsNone(model.selected_card(result,'999','skill'))
 def test_related_request_whole_result_and_identity_guards(self):
  result=self.refs[model.STAGES[0]];key=result['rows'][0]['key'];requests=model.related_entities(result,key)
  with patch.object(model,'reference',return_value=copy.deepcopy(result)):
   for request in requests:
    self.assertEqual(model.resolve_related(result,key,request)['enemy_key'],request['enemy_key'])
    self.assertIsNone(model.resolve_related(result,key,request|{'entity_id':'foreign'}))
   broken=copy.deepcopy(result);broken['stage_name']='foreign'
   self.assertIsNone(model.resolve_related(broken,key,requests[0]if requests else{}))
 def test_mutable_result_does_not_poison_next_reference(self):
  first=model.reference(model.STAGES[0]);first['rows'][0]['raw_binding']['id']='foreign'
  fresh=model.reference(model.STAGES[0]);self.assertNotEqual(first['rows'][0]['raw_binding'],fresh['rows'][0]['raw_binding'])
 def test_manifest_and_each_actual_member_corruption_fails_closed(self):
  real=model.battle.version._file
  manifest=json.loads(real(model.MANIFEST).read_bytes())
  class Bad:
   def read_bytes(self):return b'{}'
  for damaged in(model.MANIFEST,*manifest['files']):
   with self.subTest(damaged=damaged),patch.object(model.battle.version,'_file',side_effect=lambda name:Bad()if name==damaged else real(name)):
    self.assertIsNone(model.packet())
 def test_changed_original_level_database_and_handbook_are_rejected(self):
  current=model.battle.packet()
  for table in('levels','enemy_definitions','handbook'):
   damaged=copy.deepcopy(current);name=next(iter(self.packet['data']['originals'][table]));damaged['inputs'][table][name]={'foreign':True}
   with patch.object(model.battle,'packet',return_value=damaged):self.assertIsNone(model.packet())
 def test_fixed_map_request_requires_whole_current_reference(self):
  result=self.refs[model.STAGES[0]];request=model.map_target(result)
  self.assertIsNotNone(request);self.assertEqual(request['stage_id'],model.STAGES[0]);self.assertFalse(request['run_updated'])
  forged=copy.deepcopy(result);forged['stage_name']='foreign';self.assertIsNone(model.map_target(forged))
 def test_source_specific_condition_boundaries(self):
  text='\n'.join(model.player_text(r,x['key'],t)for r in self.refs.values()for x in r['rows']for t,_ in model.topics(r,x['key']))
  if 377==377:
   self.assertIn('进入终点',text);self.assertIn('22秒',text);self.assertIn('2.5秒',text)
   self.assertTrue(all(x['level']==1 for r in self.refs.values()for x in r['rows']))
  elif 377==379:
   self.assertIn('60层',text);self.assertIn('最多80层',text);self.assertIn('半径0.5',text)
   self.assertIn('生息演算',text);self.assertIn('不把',text);self.assertIn('恰好50%',text)
  else:
   self.assertIn('80秒',text);self.assertIn('40秒',text);self.assertIn('3333',text);self.assertIn('9999',text)
   self.assertIn('最多',text);self.assertIn('最少',text);self.assertIn('斯第奇',text)
   self.assertTrue(all(x['level']==0 for r in self.refs.values()for x in r['rows']))
if __name__=='__main__':unittest.main()
