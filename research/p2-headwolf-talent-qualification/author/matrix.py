import copy,gzip,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True;p=pathlib.Path(__file__).resolve().parent;tag=sys.argv[1];assert tag in ('baseline','draft');package=p/('frozen70' if tag=='baseline' else 'draft');sys.path.insert(0,str(package))
from rouge.catalog import catalog
from rouge.damage import _prepare_damage,calculate_damage
from rouge.operator_engine import Combat
from rouge.reporting import format_report
from rouge.estimate import format_estimate

def strict(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
cache={};records=[];mutations=[];before_catalog=strict(catalog())
def outcome(kind,args):
 key=strict([kind,args])
 if key in cache:return cache[key]
 given=copy.deepcopy(args);before=strict(given)
 try:
  if kind=='calculate':
   result=calculate_damage(given);value={'accepted':True,'result':result,'formatted_report':format_report(result),'technical_report':format_report(result,technical=True),'formatted_estimate':format_estimate(result)}
  else:
   scenario,attributes,_,_=_prepare_damage(given);result=Combat(scenario,attributes).plan(normal=True,window=given.get('window_seconds',1));value={'accepted':True,'normal_owner_clock_reference':result}
 except Exception as e:value={'accepted':False,'error_type':type(e).__name__,'error':str(e)}
 if strict(given)!=before:mutations.append({'kind':kind,'input':args})
 strict(value);cache[key]=value;return value
def add(group,args,kind='calculate'):
 records.append({'key':str(len(records)),'group':group,'kind':kind,'input':args,'outcome':outcome(kind,args)})
base={'operator':'char_1038_whitw2','base_attack':1000}
for elite in (0,1,2):
 for skill in (1,2,3):
  for rank in range(1,11):
   for mode in ('frames','continuous'):
    for elapsed in (0,60,120):
     for window in (0,1,61):
      add('all_elite_skill_rank_window',dict(base,elite=elite,skill=skill,skill_rank=rank,timing_mode=mode,deployment_elapsed_seconds=elapsed,window_seconds=window))
for elite in (0,1,2):
 for skill in (1,2,3):
  for rank in (1,7,10):
   for mode in ('frames','continuous'):
    for context in ({'timing':{'target_windows':[]}},{'timing':{'target_disappears_seconds':0}},{'timing':{'projectile_travel_seconds':100}}, {'base_attack':0}):
     add('target_boundaries',dict(base,elite=elite,skill=skill,skill_rank=rank,timing_mode=mode,deployment_elapsed_seconds=120,window_seconds=3,**context))
for elite,level in ((0,1),(0,50),(1,1),(1,80),(2,1),(2,59),(2,60),(2,90)):
 for potential in range(1,7):
  for stage in range(4):
   add('qualification_module_potential',dict(base,elite=elite,level=level,potential=potential,skill=1,skill_rank=7,window_seconds=3,deployment_elapsed_seconds=120,module_id='uniequip_002_whitw2' if stage else None,module_level=stage))
for elite,potential,threshold in ((0,1,60),(0,6,60),(1,1,90),(1,6,78),(2,1,60),(2,6,48)):
 for mode in ('frames','continuous'):
  for age in (threshold-.001,threshold,threshold+.001):
   for offset in (0,age):
    for skill in (1,2,3):
     add('inclusive_reference_boundary',dict(base,elite=elite,potential=potential,skill=skill,skill_rank=7,window_seconds=1,timing_mode=mode,deployment_elapsed_seconds=age-offset,_timeline_offset_seconds=offset,drone_warmup_hits=100,timing={'windup_frames':0,'recovery_frames':0}),kind='normal')
for op in ('char_1038_whitw2','char_328_cammou'):
 for elite in (0,1,2):
  for mode in ('frames','continuous'):
   for field in ('deployment_elapsed_seconds','drone_warmup_hits'):
    for raw in (None,False,True,0,1,'60','60.0','false',[],{},-1,3601):
     add('existing_raw_input_contract',dict(base,operator=op,elite=elite,skill=1,skill_rank=7,window_seconds=3,timing_mode=mode,**{field:raw}))
for op in ('char_328_cammou','char_1034_jesca2','char_110_deepcl'):
 for mode in ('frames','continuous'):
  for skill in (1,2):
   add('unrelated_owner_preserved',dict(base,operator=op,skill=skill,skill_rank=7,window_seconds=3,timing_mode=mode,deployment_elapsed_seconds=120))
assert not mutations and strict(catalog())==before_catalog
raw=(json.dumps(records,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();compressed=gzip.compress(raw,mtime=0);(p/(tag+'-whole-outcomes.json.gz')).write_bytes(compressed)
receipt={'tag':tag,'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','cases':len(records),'actual_calls':len(cache),'accepted_calls':sum(v['accepted'] for v in cache.values()),'error_calls':sum(not v['accepted'] for v in cache.values()),'input_mutations':len(mutations),'catalog_mutated':False,'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'gzip_bytes':len(compressed),'gzip_sha256':hashlib.sha256(compressed).hexdigest(),'strict_json_allow_nan_false':True,'whole_result_and_all_formatted_reports_recorded':True,'root_working_tree_used':False}
(p/(tag+'-matrix-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
