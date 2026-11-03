"""Source-faithful hunt reader checks. No Qt, game, chat or production writes."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from unittest.mock import patch
import json,shutil,sys,tempfile,unittest,subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO=next(parent for parent in(ROOT,*ROOT.parents)if(parent/'rouge/__init__.py').is_file())
sys.path.insert(0,str(REPO))
from rouge import battle_preview,enemy_skills
spec=spec_from_file_location('rouge.boss_hunt_reference',ROOT/'rouge/boss_hunt_reference.py')
model=module_from_spec(spec);spec.loader.exec_module(model)
TARGETS=(('ro6_b_4','enemy_2145_cadejo',0),('ro6_b_4','enemy_2146_cadesd',0),('ro6_b_4','enemy_2137_shsdgo',0))

class BossHunt311Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.battle=deepcopy(battle_preview.battle_data());cls.skills=deepcopy(enemy_skills.skill_data())
  cls.selected=json.loads((ROOT/model.SELECTED).read_bytes())
 def result(self,index=0):return model.hunt_reference(*TARGETS[index])
 def requireCompletePrimaryInputs(self):
  selected=json.loads((ROOT/model.PACK/'selected-original-records.json').read_bytes())
  suffixes=('/enemy_database.json','/level_rogue6_b-4.json','/level_rogue6_b-4-b.json')
  required=[row for row in selected['source_files']if row['file'].endswith(suffixes)]
  self.assertEqual(len(required),3)
  missing=[row['file']for row in required if not(REPO/row['file']).is_file()]
  if missing:self.skipTest('缺少完整固定构建原件：'+'、'.join(missing)+'；重建未执行，不可计为通过。')
  return required
 def assertUnknown(self,result):
  for key in model.ACTUAL_FIELDS:self.assertIsNone(result[key],key)
  for key in model.FALSE_FIELDS:self.assertIs(result[key],False,key)
 def clone(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);root=Path(t.name)
  manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
  for name in(model.MANIFEST,*manifest['runtime_files']):
   dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
  return root,manifest
 def test01_three_exact_normal_entries_have_distinct_names(self):
  self.assertEqual(model.TARGETS,TARGETS)
  for i,name in enumerate(('卡德霍，黑流之源','痛楚化身','猎犬proto')):
   result=self.result(i);self.assertIs(result['source_valid'],True);self.assertEqual(result['status'],'documented_reference')
   self.assertEqual(result['reference']['entry_name'],name)
   self.assertEqual((result['stage_id'],result['enemy_id'],result['level']),TARGETS[i]);self.assertUnknown(result)
 def test02_all_other_versions_custom_entities_and_wrong_types_do_no_source_read(self):
  with patch.object(model,'_packet',side_effect=AssertionError('unrelated source access')):
   for target in[(None,None,None),([],{},0),('ro6_b_4','enemy_2145_cadejo',False),
    ('ro6_b_4','enemy_2145_cadejo',0.0),('ro6_b_4','enemy_2145_cadejo',1),
    ('ro6_b_4_b','enemy_2145_cadejo',0),('ro6_b_4','enemy_2146_cadesd_2',0),
    ('ro6_b_4','enemy_2146_cadesd_3',0),('ro6_b_5','enemy_2145_cadejo',0)]:
    self.assertIsNone(model.hunt_reference(*target),target)
 def test03_four_topics_are_independent_conditions_not_a_phase_timeline(self):
  ref=self.result()['reference'];self.assertIs(ref['not_a_linear_timeline'],True)
  self.assertEqual([t['id']for t in ref['topics']],['condition_flow','cadejo','avatars','hound'])
  for i in range(3):
   text=model.reference_text(self.result(i),'condition_flow')
   for phrase in('不是本局必经时间轴','首次被击倒','回复全部生命','进入休整','无敌与孤立','存疑','由关卡配置生成','技能结束后退场'):
    self.assertIn(phrase,text)
   self.assertUnknown(self.result(i))
 def test04_eight_named_skill_effects_and_three_complete_abilities_are_present(self):
  ref=self.result()['reference'];docs=ref['reviewed_complete_documentation']['documents']
  cards=[c for d in docs.values()for c in d['cards']]
  self.assertEqual(sum(c['kind']=='skill'for c in cards),8);self.assertEqual(sum(c['kind']=='ability'for c in cards),3)
  expected={'卡德霍，黑流之源':4,'痛楚化身':3,'猎犬proto':1}
  for actor,count in expected.items():self.assertEqual(sum(s['actor']==actor for s in ref['skills']),count)
  for topic in('cadejo','avatars','hound'):
   text=model.reference_text(self.result(),topic)
   for skill in ref['skills']:
    if skill['topic_id']==topic:
     self.assertIn('【'+skill['name']+'】',text);self.assertIn(skill['text'],text)
 def test05_full_headers_and_tooltips_survive_only_in_technical_source(self):
  ref=self.result()['reference'];doc=ref['reviewed_complete_documentation']['documents']
  self.assertIn('2020/',doc['卡德霍，黑流之源']['cards'][0]['complete_visible_header'])
  self.assertGreater(sum(len(c['tooltip_nodes'])for d in doc.values()for c in d['cards']),0)
  text=model.reference_text(self.result())
  for raw in('2020/','2040/','450450/','1025/','1540/','complete_DOM','m_defined','enemy_2145','ro6_b_4'):
   self.assertNotIn(raw,text)
 def test06_mode_absence_does_not_assign_initial_state_to_avatar_or_hound(self):
  skills=self.result()['reference']['skills']
  for skill in skills:
   if skill['actor']!='卡德霍，黑流之源':
    self.assertEqual(skill['documented_modes'],[]);self.assertEqual(skill['mode_label'],'文献未限定形态')
  self.assertEqual(next(s for s in skills if s['name']=='感受痛楚')['documented_modes'],['休整形态'])
 def test07_range_branches_and_each_actors_stun_duration_stay_separate(self):
  boss=model.reference_text(self.result(),'cadejo');avatar=model.reference_text(self.result(),'avatars')
  for text in(boss,avatar):
   self.assertIn('若攻击范围内存在我方单位',text);self.assertIn('若攻击范围内不存在我方单位',text)
  self.assertIn('8秒晕眩',boss);self.assertIn('5秒晕眩',avatar);self.assertIn('两种结果不能相加',boss)
 def test08_summary_20s_and_detailed_10s_are_a_visible_source_difference(self):
  result=self.result();text=model.reference_text(result,'cadejo')
  for phrase in('摘要写20秒','写10秒','两种记载都保留','不能据此确认当前对局实际持续时间'):
   self.assertIn(phrase,text)
  self.assertTrue(result['reference']['source_differences']);self.assertIsNone(result['actual_elapsed_time'])
 def test09_configured_spawns_are_not_direct_boss_summons_or_proven_occurrence(self):
  text=model.reference_text(self.result(),'condition_flow')
  self.assertIn('由关卡配置生成，而非卡德霍直接召唤',text);self.assertIn('不证明本局已触发或已经清场',text)
  self.assertIn('从当前波次释放2次（存疑）',text)
 def test10_avatar_exit_scope_and_first_layer_growth_are_not_guessed_current_values(self):
  text=model.reference_text(self.result(),'avatars')
  for phrase in('剩余痛楚化身','当前全场所有敌方单位','退场','最多2层','以第一层数值为基础翻倍',
   '不能擅自把退场只改写为普通击杀','使所有痛楚化身强制发动'):
   self.assertIn(phrase,text)
  self.assertIsNone(self.result()['actual_avatar_form']);self.assertIsNone(self.result()['actual_damage'])
 def test11_hound_nonflight_target_and_attack_lifecycle_do_not_become_tile_or_live_clock(self):
  text=model.reference_text(self.result(),'hound')
  for phrase in('非飞行我方单位','目标所在地块中心','技能开始时自身所在地块中心',
   '不能把“非飞行”自行改成“只可攻击地面部署位”','不会随技能一起被打断',
   '不能简化成所有攻击永远不可打断','30%','1.5秒','最终降低至20%'):
   self.assertIn(phrase,text)
  self.assertUnknown(self.result())
 def test12_player_wording_is_plain_and_raw_original_terms_remain_technical(self):
  result=self.result()
  forbidden=('基础白值','原始冷却字段','实际持续攻击回调','普通版原配置','完整原值与全部限定','字段','回调','预制体','脚本','追猎版')
  for topic in(None,'condition_flow','cadejo','avatars','hound'):
   text=model.reference_text(result,topic)
   for word in forbidden:self.assertNotIn(word,text,(topic,word))
  raw=json.dumps(result['reference'],ensure_ascii=False)
  for word in('基础白值','原始冷却字段','实际持续攻击回调','普通版原配置','完整原值与全部限定'):
   self.assertIn(word,raw)
  self.assertIn('资料中的冷却数值',model.reference_text(result,'avatars'))
  self.assertIn('每次实际造成伤害的时刻',model.reference_text(result,'hound'))
  self.assertIn('痛苦将息关卡的两种自定义化身',model.reference_text(result))
 def test13_pursuit_custom_refs_keep_nonempty_skills_but_cannot_open_entries(self):
  ref=self.result()['reference']['source_differences']
  technical=json.dumps(ref,ensure_ascii=False)
  self.assertIn('enemy_2146_cadesd_2',technical);self.assertIn('enemy_2146_cadesd_3',technical)
  selected=json.loads((ROOT/model.PACK/'selected-original-records.json').read_bytes())
  rows=[r for r in selected['complete_stage_enemyDbRefs']['ro6_b_4_b']if r['id']in('enemy_2146_cadesd_2','enemy_2146_cadesd_3')]
  self.assertEqual(len(rows),2)
  for row in rows:
   self.assertIs(row['useDb'],False);self.assertEqual(len(row['overwrittenData']['skills']),3)
   self.assertIsNone(model.hunt_reference('ro6_b_4_b',row['id'],0))
 def test14_returned_nested_objects_are_independent_and_forged_or_mutated_text_is_refused(self):
  first=self.result();first['reference']['topics'][0]['paragraphs'][0]='注入的玩家文字'
  self.assertNotIn('注入的玩家文字',model.reference_text(first));self.assertIn('暂时无法核对',model.reference_text(first))
  fresh=self.result();self.assertNotEqual(fresh['reference']['topics'][0]['paragraphs'][0],'注入的玩家文字')
  fresh['reference']['reviewed_complete_documentation'].clear()
  self.assertTrue(self.result()['reference']['reviewed_complete_documentation'])
 def test15_all_runtime_files_missing_or_tampered_fail_all_three_entries_and_recover(self):
  root,manifest=self.clone()
  with patch.object(model,'ROOT',root):
   self.assertTrue(self.result()['source_valid'])
   for name in manifest['runtime_files']:
    path=root/name;original=path.read_bytes()
    for action in('tamper','delete'):
     try:
      path.write_bytes(original+b' ')if action=='tamper'else path.unlink()
      for i in range(3):
       result=self.result(i);self.assertFalse(result['source_valid'],(name,action,i))
       self.assertIsNone(result['reference']);self.assertIsNone(result['source_identity']);self.assertUnknown(result)
     finally:path.write_bytes(original)
     self.assertTrue(self.result()['source_valid'],(name,action))
 def test16_data_plus_changed_manifest_never_authorize_new_payload(self):
  root,manifest=self.clone()
  with patch.object(model,'ROOT',root):
   path=root/model.DATA;path.write_bytes(path.read_bytes()+b' ')
   manifest['runtime_files'][model.DATA]={'bytes':path.stat().st_size,'sha256':sha256(path.read_bytes()).hexdigest()}
   manifest['data_sha256']=manifest['runtime_files'][model.DATA]['sha256']
   (root/model.MANIFEST).write_text(json.dumps(manifest),encoding='utf8')
   self.assertFalse(self.result()['source_valid'])
 def test17_held_valid_result_does_not_render_after_source_fault_or_selection_change(self):
  result=self.result();root,_=self.clone()
  with patch.object(model,'ROOT',root):
   (root/model.SELECTED).unlink();text=model.reference_text(result,'cadejo')
   self.assertIn('旧说明与条目选择已清除',text);self.assertNotIn('【痛吼】',text)
  for value in(False,0,[],{},'missing',''):
   self.assertIn('所选资料条目暂时无法核对',model.reference_text(result,value))
  self.assertEqual(model.reference_text(None),'')
 def test18_complete_selected_two_stages_reject_any_warm_mutation_not_unrelated_stage(self):
  for sid in('ro6_b_4','ro6_b_4_b'):
   battle=deepcopy(self.battle);battle['stages'][sid]['map'][0][0]='污染'
   with patch.object(battle_preview,'battle_data',return_value=battle):self.assertFalse(self.result()['source_valid'],sid)
  battle=deepcopy(self.battle);battle['stages']['ro6_t_1']['name']='无关修改'
  with patch.object(battle_preview,'battle_data',return_value=battle):self.assertTrue(self.result()['source_valid'])
 def test19_all_five_definition_and_eight_binding_objects_are_checked_including_empty_custom(self):
  for eid in model.RELATED_ENEMIES:
   skills=deepcopy(self.skills);skills['definitions'][eid]['unexpected']=True
   with patch.object(enemy_skills,'skill_data',return_value=skills):self.assertFalse(self.result()['source_valid'],eid)
  for sid,rows in self.selected['complete_skill_bindings'].items():
   for key in rows:
    skills=deepcopy(self.skills);skills['bindings'][sid][key]['unexpected']=False
    with patch.object(enemy_skills,'skill_data',return_value=skills):self.assertFalse(self.result()['source_valid'],(sid,key))
 def test20_type_strict_source_identity_and_unknown_flags_cannot_be_injected(self):
  battle=deepcopy(self.battle);battle['source']['unexpected']=True
  with patch.object(battle_preview,'battle_data',return_value=battle):self.assertFalse(self.result()['source_valid'])
  skills=deepcopy(self.skills);skills['source']['unexpected']=True
  with patch.object(enemy_skills,'skill_data',return_value=skills):self.assertFalse(self.result()['source_valid'])
  battle=deepcopy(self.battle);battle['stages']['ro6_b_4']['enemies'][0]['level']=False
  with patch.object(battle_preview,'battle_data',return_value=battle):self.assertFalse(self.result()['source_valid'])
  result=self.result();result['actual_damage']=0;self.assertIn('暂时无法核对',model.reference_text(result))
 def test21_query_does_not_call_numerical_prediction_or_mutate_legacy_sources(self):
  before=(deepcopy(battle_preview.battle_data()),deepcopy(enemy_skills.skill_data()))
  with patch.object(battle_preview,'enemy_preview',side_effect=AssertionError('no prediction')):
   for i in range(3):self.assertUnknown(self.result(i))
  self.assertEqual(before,(battle_preview.battle_data(),enemy_skills.skill_data()))
 def test22_path_guards_and_runtime_scope_exclude_whole_database_and_level_files(self):
  for name in('../secret.json','C:/secret.json','/secret.json','research\\file.json',False):
   with self.assertRaises(ValueError):model._file(name)
  manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
  self.assertEqual(set(manifest['runtime_files']),model.RUNTIME_FILES)
  self.assertIs(manifest['runtime_full_database_hashing'],False)
  for name in manifest['runtime_files']:
   self.assertNotIn('enemy_database.json',name);self.assertNotIn('battle-previews.json',name);self.assertNotIn('/levels/',name)
 def test23_builder_recreates_exact_candidate_from_complete_primary_authority(self):
  self.requireCompletePrimaryInputs()
  spec=spec_from_file_location('hunt311_builder',ROOT/'scripts/build_boss_hunt_reference_311.py')
  builder=module_from_spec(spec);spec.loader.exec_module(builder)
  with tempfile.TemporaryDirectory()as directory:
   target=Path(directory);receipt=builder.build(REPO,target,authority_root=ROOT)
   self.assertEqual(receipt['boss_skill_cards'],8);self.assertEqual(receipt['ability_cards'],3)
   for name in receipt['outputs']:self.assertEqual((target/name).read_bytes(),(ROOT/name).read_bytes(),name)
 def test24_builder_refuses_changed_full_source_without_writing_product(self):
  spec=spec_from_file_location('hunt311_bad_builder',ROOT/'scripts/build_boss_hunt_reference_311.py')
  builder=module_from_spec(spec);spec.loader.exec_module(builder)
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);pack=root/model.PACK;pack.mkdir(parents=True)
   handoff=json.loads((ROOT/model.PACK/'HANDOFF.json').read_bytes())
   shutil.copyfile(ROOT/model.PACK/'HANDOFF.json',pack/'HANDOFF.json')
   for name in handoff['source_files']:
    path=pack/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/model.PACK/name,path)
   (pack/'boss-complete.html').write_bytes((pack/'boss-complete.html').read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'Frozen whole member differs'):builder.build(REPO,root/'output',authority_root=root)
   self.assertFalse((root/'output'/model.DATA).exists())
 def test25_cli_three_primary_location_overrides_rebuild_identical_bytes_and_check_without_writes(self):
  self.requireCompletePrimaryInputs()
  selected=json.loads((ROOT/model.PACK/'selected-original-records.json').read_bytes())
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);output=root/'result';shutil.copytree(ROOT/model.PACK,output/model.PACK)
   roles=('--enemy-database','--normal-level','--pursuit-level')
   suffixes=('/enemy_database.json','/level_rogue6_b-4.json','/level_rogue6_b-4-b.json')
   flags=[]
   for i,(role,suffix)in enumerate(zip(roles,suffixes)):
    source=next(row for row in selected['source_files']if row['file'].endswith(suffix))
    target=root/('relocated-primary-'+str(i)+'.json');shutil.copyfile(REPO/source['file'],target);flags += [role,str(target)]
   argv=[sys.executable,'-B',str(ROOT/'scripts/build_boss_hunt_reference_311.py'),'--root',str(REPO),'--output-root',str(output),*flags]
   process=subprocess.run(argv,capture_output=True,cwd=REPO)
   self.assertEqual(process.returncode,0,process.stderr.decode('utf8',errors='replace'))
   receipt=json.loads(process.stdout);self.assertEqual(receipt['explicit_primary_override_roles'],['enemy_database','normal_level','pursuit_level'])
   for name in receipt['outputs']:self.assertEqual((output/name).read_bytes(),(ROOT/name).read_bytes(),name)
   manifest=json.loads((output/model.MANIFEST).read_bytes())
   for target in flags[1::2]:self.assertNotIn(target,json.dumps(manifest))
   before={str(p.relative_to(output)):sha256(p.read_bytes()).hexdigest()for p in output.rglob('*')if p.is_file()}
   process=subprocess.run([*argv,'--check'],capture_output=True,cwd=REPO)
   self.assertEqual(process.returncode,0,process.stderr.decode('utf8',errors='replace'))
   after={str(p.relative_to(output)):sha256(p.read_bytes()).hexdigest()for p in output.rglob('*')if p.is_file()}
   self.assertEqual(before,after)
 def test26_cli_wrong_or_partial_primary_overrides_are_rejected_before_output(self):
  required=self.requireCompletePrimaryInputs()
  selected=json.loads((ROOT/model.PACK/'selected-original-records.json').read_bytes())
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);output=root/'result';shutil.copytree(ROOT/model.PACK,output/model.PACK)
   partial=root/'fragment.json';partial.write_text('{"enemies": []}',encoding='utf8')
   role_suffixes={'--enemy-database':'/enemy_database.json','--normal-level':'/level_rogue6_b-4.json','--pursuit-level':'/level_rogue6_b-4-b.json'}
   valid={};logical={}
   for i,(role,suffix)in enumerate(role_suffixes.items()):
    source=next(row for row in required if row['file'].endswith(suffix));original=REPO/source['file']
    self.assertEqual({'bytes':original.stat().st_size,'sha256':sha256(original.read_bytes()).hexdigest()},
     {key:source[key]for key in('bytes','sha256')},'已存在但错误的构建原件不能跳过或用于其它角色自证')
    relocated=root/('known-valid-'+str(i)+'.json');shutil.copyfile(original,relocated)
    valid[role]=relocated;logical[role]=source['file']
   normal=valid['--normal-level'];pursuit=valid['--pursuit-level']
   for role,path in(('--enemy-database',partial),('--normal-level',partial),('--pursuit-level',partial),('--normal-level',pursuit),('--pursuit-level',normal)):
    chosen={**valid,role:path};flags=[token for name,location in chosen.items()for token in(name,str(location))]
    argv=[sys.executable,'-B',str(ROOT/'scripts/build_boss_hunt_reference_311.py'),'--root',str(REPO),'--output-root',str(output),*flags]
    process=subprocess.run(argv,capture_output=True,cwd=REPO)
    self.assertNotEqual(process.returncode,0,(role,path))
    self.assertIn('Complete build authority differs: '+logical[role],process.stderr.decode('utf8',errors='replace'))
    self.assertFalse((output/model.DATA).exists())

if __name__=='__main__':unittest.main()
