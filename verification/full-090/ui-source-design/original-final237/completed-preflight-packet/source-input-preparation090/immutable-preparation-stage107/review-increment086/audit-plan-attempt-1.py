"""Static UI086 plan/production-source review; no project imports or calls."""
import ast,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
BASE='0f27027e7e1f49c08f298706b599e310e299238b'
PLAN=OUT.parent/'small-explicit-pair-plan090.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,obj):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def bind(p):
 d=p.read_bytes();return {'source_path':str(p),'bytes':len(d),'sha256':sha(d)}
def main():
 data=PLAN.read_bytes();snapshot=OUT/'plan-snapshot090.json'
 with snapshot.open('xb') as f:f.write(data)
 plan=json.loads(data);sources={};texts={}
 for name in ('rouge/app.py','rouge/operator_options.py','rouge/operator_engine.py','rouge/damage.py','rouge/reporting.py','rouge/estimate.py'):
  raw=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+name])
  assert raw==(REPO/name).read_bytes()
  sources[name]={'commit':BASE,'bytes':len(raw),'sha256':sha(raw)};texts[name]=raw.decode('utf-8')
 assert sources['rouge/operator_engine.py']['sha256']=='c6a7b5e5cd444480f3579a8174246a31f891cb7a2b1c93bbf0826aa4a7765c68'
 assert sources['rouge/damage.py']['sha256']=='6cc15cf93eb52fc42120fff6b795e2cbbf2903cf0af8d7d293ffea9f73f121c6'
 tree=ast.parse(texts['rouge/operator_options.py'])
 options=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets)))
 groups=plan['active_pairs']+plan['qualification_and_coveredmodule_pairs']+plan['hidden_key_omission_pairs']
 assert (len(plan['active_pairs']),len(plan['qualification_and_coveredmodule_pairs']),len(plan['hidden_key_omission_pairs']))==(12,2,8)
 assert len(groups)==plan['pair_groups']==22 and plan['planned_UI_states']==44
 rows=[]
 for group in groups:
  entry=next(e for e in options[group['owner']] if e[0]==group['field'])
  hidden=group['id'].startswith('hidden:');assert (group['skill'] in entry[4]) is (not hidden)
  assert type(entry[2]) is bool
  assert group.get('states',group.get('hidden_widget_checked_states'))==[False,True]
  if hidden:assert group['requested_scenario_key']=='OMITTED'
  for key,value in group.get('option_defaults_before_toggle',{}).items():
   assert value==next(e[2] for e in options[group['owner']] if e[0]==key)
  rows.append({'id':group['id'],'owner':group['owner'],'field':group['field'],'skill':group['skill'],
   'widget_default':entry[2],'allowed_skills':entry[4],'serialized_only_if_owner_and_skill':not hidden,
   'hidden_field_omitted':hidden,'future_runtime_pending':True})
 app=texts['rouge/app.py'];engine=texts['rouge/operator_engine.py'];damage=texts['rouge/damage.py']
 for expression in ('if type(default) is bool:','scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()',
  'if owner==op and self.skill.currentData() in skills:',"'continuous_attacks':self.continuous_attacks.isChecked()"):
  assert expression in app
 assert 'self.continuous_attacks.setChecked(True)' in app
 assert "normal=self.plan(normal=True,window=recharge) if cycle is not None and not (" in engine
 assert "sp['sp_type']=='INCREASE_WHEN_ATTACK' and not self.s.get('continuous_attacks',True)) else None" in engine
 assert 'self.ranged_attack_condition_consumed=False' in engine
 assert 'self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None' in engine
 assert "if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)" in damage
 contexts=[]
 for name,ranges in {'rouge/app.py':[(661,677),(1026,1037)],'rouge/operator_engine.py':[(13,30),(1297,1302),(1471,1475),(1520,1542)],'rouge/damage.py':[(335,357)]}.items():
  lines=texts[name].splitlines()
  contexts.append({'path':name,'binding':sources[name],'ranges':[{'start':a,'end':b,'lines':lines[a-1:b]} for a,b in ranges]})
 receipt=write('static-plan-review086.json',{'status':'PASS_STATIC_PLAN_ONLY_RUNTIME_PENDING','base_commit':BASE,
  'plan_original':{'source_path':str(PLAN),'bytes':len(data),'sha256':sha(data)},'immutable_plan_snapshot':bind(snapshot),
  'production_source_bindings':sources,'groups':rows,'group_count':22,'future_UI_states':44,
  'qualification':'Mizuki E1 lacks actual selected 反移情; E2 has it. Oblvns module3 E2level60 qualifies existing max_cnt12 skill override; actual normal remains gated and must be observed in the authorized call, not inferred from finalcycle or streams.',
  'global_widget_reset_requirement':'Explicitly reset/read continuous_attacks True and other option defaults per group; actual app serializes this real bool regardless of its visibility.',
  'required_result_shape':'Extended public result has components,timing,estimate.base_stats,estimate.skill,report. Preserve complete typed tree and three texts. Conditional references/nullable totals are source-specific; do not require totals to differ or invent absent references.',
  'normal_observation_proposal':'Optional read-only trace during each already-authorized public call may capture plan(normal=True) and current Combat marker; no extra helper call or marker added to scenario/publicresult.',
  'historical_plan_pending_flags':'source86_product_final=False/later87–90unknown are preserved in the snapshot as historical pending metadata; current binding is actual root0f, no runtime pass is claimed.',
  'source_contexts':contexts,'application_API_calls':0,'production_helper_calls':0,'formatter_calls':0,'Qt_calls':0,'Wine_calls':0,'tests_run':0,'tracked_edits':0,
  'original_immutable_source_packets_modified':False,'next':'UI author supplies actual44 saved receipt; reviewer only compares saved44, with0newAPI.'})
 checkpoint=OUT/'CHECKPOINT.md'
 with checkpoint.open('x',encoding='utf-8') as f:f.write('第86增量静态计划核验通过：固定root0f27027，22组44状态；所有API/helper/formatter/Qt/Wine/tests均0。原计划按字节快照保存，未改原封存源包。实际44调用、真实窗口和87–90尚待UI作者/root授权。moduleS3 actualnormal必须依原赋值或同次只读trace观察，不能从最终cycle推断。收到完整saved44后仅静态比较，不重API。\n')
 paths=[Path(__file__),snapshot,receipt,checkpoint]
 files=[{**bind(p),'archive_path':p.name} for p in paths]
 manifest=write('manifest.json',{'version':1,'status':'FINAL_STATIC_SEALED_RUNTIME_PENDING','files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)})
 print(json.dumps({'status':'FINAL_STATIC_SEALED_RUNTIME_PENDING','manifest':bind(manifest),'files':len(files),'bytes':sum(r['bytes'] for r in files),'new_API_calls':0}))
if __name__=='__main__':main()
