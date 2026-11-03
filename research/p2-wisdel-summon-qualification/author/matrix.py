import copy,gzip,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True;p=pathlib.Path(__file__).resolve().parent;tag=sys.argv[1];assert tag in ('baseline','draft');sys.path.insert(0,str(p/('frozen70' if tag=='baseline' else 'draft')))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.estimate import format_estimate
strict=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
cache={};records=[];mutations=[];catalog_before=strict(catalog())
if tag=='draft':
 from rouge.wisdel_summon_qualification import _source
 source_before=strict(_source())
def outcome(args):
 key=strict(args)
 if key in cache:return cache[key]
 given=copy.deepcopy(args);before=strict(given)
 try:
  result=calculate_damage(given);value={'accepted':True,'result':result,'formatted_report':format_report(result),'technical_report':format_report(result,technical=True),'formatted_estimate':format_estimate(result)}
  if tag=='draft':
   stripped=copy.deepcopy(result);stripped.pop('wisdel_summon_qualification_reference',None);stripped['report']['sections']=[s for s in stripped['report']['sections'] if s['id']!='wisdel_summon_qualification']
   value['stripped_old_outcome']={'accepted':True,'result':stripped,'formatted_report':format_report(stripped),'technical_report':format_report(stripped,technical=True),'formatted_estimate':format_estimate(stripped)}
 except Exception as e:value={'accepted':False,'error_type':type(e).__name__,'error':str(e)}
 if strict(given)!=before:mutations.append(args)
 strict(value);cache[key]=value;return value
def add(group,args):records.append({'key':str(len(records)),'group':group,'input':args,'outcome':outcome(args)})
base={'operator':'char_1035_wisdel','base_attack':1000,'window_seconds':3}
for elite in (0,1,2):
 for skill in (1,2,3):
  for rank in range(1,11):
   for mode in ('frames','continuous'):
    for potential in (1,6):
     for ghosts,casts in ((0,0),(1,0),(1,2),(3,2)):
      add('all_elite_skill_rank_declarations',dict(base,elite=elite,skill=skill,skill_rank=rank,potential=potential,timing_mode=mode,ghost_count=ghosts,ghost_casts=casts))
for elite,level in ((0,1),(0,50),(1,1),(1,80),(2,1),(2,59),(2,60),(2,90)):
 for stage in range(4):
  for skill in (1,2,3):
   for mode in ('frames','continuous'):
    add('module_culture_boundaries',dict(base,elite=elite,level=level,skill=skill,skill_rank=7,timing_mode=mode,module_id='uniequip_002_wisdel' if stage else None,module_level=stage,ghost_count=1,ghost_casts=2))
for elite in (0,1,2):
 for skill in (1,2,3):
  for mode in ('frames','continuous'):
   for ghosts,casts in ((0,0),(1,0),(1,2)):
    for context in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}},{'timing':{'projectile_travel_seconds':100}}):
     add('window_source_contract',dict(base,elite=elite,skill=skill,skill_rank=7,timing_mode=mode,ghost_count=ghosts,ghost_casts=casts,**context))
for mode in ('frames','continuous'):
 for elite in (0,1,2):
  for field in ('ghost_count','ghost_casts'):
   for value in (None,False,True,0,1,3,'0','0.0','2','2.0','false',[],{},-1,3.5,1001):
    for active in (0,1):
     args=dict(base,elite=elite,skill=1,skill_rank=7,timing_mode=mode,ghost_count=active,ghost_casts=0);args[field]=value;add('old66_type_and_idle_gate',args)
for op in ('char_328_cammou','char_110_deepcl','char_2025_shu'):
 for mode in ('frames','continuous'):
  add('unrelated_owner',dict(base,operator=op,skill=1,skill_rank=7,timing_mode=mode,ghost_count=1,ghost_casts=2))
assert not mutations and strict(catalog())==catalog_before
if tag=='draft':assert strict(_source())==source_before
raw=(json.dumps(records,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();blob=gzip.compress(raw,mtime=0);(p/(tag+'-whole-outcomes.json.gz')).write_bytes(blob)
receipt={'tag':tag,'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','cases':len(records),'actual_public_calculate_calls':len(cache),'accepted_calls':sum(v['accepted'] for v in cache.values()),'error_calls':sum(not v['accepted'] for v in cache.values()),'input_mutations':0,'source_or_catalog_mutated':False,'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'gzip_bytes':len(blob),'gzip_sha256':hashlib.sha256(blob).hexdigest(),'all_public_results_and_formatted_report_texts_recorded':True,'root_working_tree_used':False}
(p/(tag+'-matrix-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt))
