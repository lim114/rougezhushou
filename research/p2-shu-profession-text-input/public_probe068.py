from pathlib import Path
import sys,json,hashlib,itertools,collections,datetime
base=Path(__file__).parent;sys.path.insert(0,str(base/'baseline'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

SHU='char_2025_shu';FIELDS=('three_professions','three_same_profession')
VALUES=[('absent',None),('bool_false',False),('bool_true',True),('null',None),('int_zero',0),('int_one',1),('float_zero',0.0),('float_one',1.0),('negative_zero',-0.0),('empty_text',''),('false_text','false'),('upper_false_text','False'),('zero_text','0'),('true_text','true'),('one_text','1'),('int_two',2),('int_negative',-1),('empty_list',[]),('nonempty_list',[False]),('empty_object',{}),('nonempty_object',{'enabled':False})]
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
records=[];seen=set();groups=collections.Counter();catalog_before=canonical(catalog())
def add(group,field,args,label,value):
 request=dict(args) if label=='absent' else {**args,field:value};key=canonical(request)
 if key in seen:return
 seen.add(key);before=json.loads(key)
 try:
  result=calculate_damage(request);row={'group':group,'field':field,'value_label':label,'request':before,'full_result':result,'full_result_sha256':digest(result)}
 except Exception as e:row={'group':group,'field':field,'value_label':label,'request':before,'error':{'type':type(e).__name__,'message':str(e)}}
 assert request==before;records.append(row);groups[group]+=1
for field,mode,skill,rank in itertools.product(FIELDS,('frames','continuous'),(1,2,3),(1,7,10)):
 for label,value in VALUES:
  add('active_original_talent_flag_types',field,{'operator':SHU,'skill':skill,'timing_mode':mode,'skill_rank':rank,'window_seconds':10},label,value)
for field,mode,skill,condition in itertools.product(FIELDS,('frames','continuous'),(1,2,3),(
 {'window_seconds':0},{'window_seconds':10,'timing':{'target_disappears_seconds':0}}, {'window_seconds':10,'timing':{'target_windows':[]}},
 {'window_seconds':10,'four_sui':True}, {'window_seconds':10,'four_sui':1}, {'window_seconds':10,'four_sui':None},
 {'window_seconds':10,'level':59,'module_id':'uniequip_002_shu','module_level':3},
 {'window_seconds':10,'level':60,'potential':6,'module_id':'uniequip_002_shu','module_level':3},
 {'window_seconds':10,'effects':[{'kind':'hp_pct','value':.2},{'kind':'attack_speed','value':18}]})):
 for label,value in [('bool_false',False),('bool_true',True),('false_text','false')]:
  add('active_scope_training_and_independent_effects',field,{'operator':SHU,'skill':skill,'timing_mode':mode,**condition},label,value)
for field,mode,skill,flag in itertools.product(FIELDS,('frames','continuous'),(1,2,3),('', 'false','0')):
 for label,value in [('absent',None),('bool_false',False),('bool_true',True),('false_text','false')]:
  add('preserved_062_four_sui_text_error',field,{'operator':SHU,'skill':skill,'timing_mode':mode,'four_sui':flag},label,value)
for field,elite,skill,mode,potential in itertools.product(FIELDS,(0,1),(1,2,3),('frames','continuous'),(1,6)):
 for label,value in [('absent',None),('bool_false',False),('bool_true',True),('false_text','false'),('null',None)]:
  add('locked_talent_and_qualification_controls',field,{'operator':SHU,'skill':skill,'elite':elite,'skill_rank':7,'potential':potential,'timing_mode':mode},label,value)
for op,p in catalog()['operators'].items():
 if op==SHU:continue
 for skill in range(1,len(p['skills'])+1):
  for mode in ('frames','continuous'):
   args={'operator':op,'skill':skill,'timing_mode':mode}
   add('inactive_owner_whole_output_controls','three_professions',args,'absent',None)
   add('inactive_owner_whole_output_controls','three_professions',args,'bool_false',False)
   add('inactive_owner_whole_output_controls','three_professions',args,'false_text','false')
   add('inactive_owner_whole_output_controls','three_same_profession',args,'false_text','false')
assert canonical(catalog())==catalog_before
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':'0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb','public_calls':len(records),'groups':groups,'records':records}
(base/'public-results068.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# Compare outcomes without dropping inactive raw field controls.
lookup=collections.defaultdict(dict)
for row in records:
 field=row['field'];request={k:v for k,v in row['request'].items() if k!=field};lookup[(field,canonical(request))][row['value_label']]=row
checks=[];counterexamples=[];mismatches=[]
def outcome(r):return r.get('full_result_sha256') or canonical(r['error'])
for (field,raw_request),variants in lookup.items():
 request=json.loads(raw_request);eligible=request['operator']==SHU and request.get('elite',2)==2
 for label,row in variants.items():
  value=row['request'].get(field)
  if 'error' in row or not eligible:
   reference=variants.get('absent') or variants.get('bool_false')
   if reference:
    same=outcome(row)==outcome(reference);checks.append({'request':row['request'],'kind':'inactive_or_original_error','same_full_result_or_error':same})
    if not same:mismatches.append(checks[-1])
  elif label in ('null','int_zero','int_one','float_zero','float_one','negative_zero'):
   reference=variants.get('bool_true' if bool(value) else 'bool_false')
   if reference:
    same=outcome(row)==outcome(reference);checks.append({'request':row['request'],'kind':'numeric_null_compatibility','same_full_result':same})
    if not same:mismatches.append(checks[-1])
  elif label in ('false_text','upper_false_text','zero_text'):
   reference=variants.get('bool_true');off=variants.get('bool_false')
   if reference and off:
    same=outcome(row)==outcome(reference);stats=row['full_result']['estimate']['base_stats'];offstats=off['full_result']['estimate']['base_stats']
    counterexamples.append({'request':row['request'],'text_equals_true_full_json':same,'differs_from_false_full_json':outcome(row)!=outcome(off),'field':field,
      'current_hp':stats['hp'],'false_hp':offstats['hp'],'current_attack_speed_reference':stats['attack_speed_reference'],'false_attack_speed_reference':offstats['attack_speed_reference']})
    if not same:mismatches.append(counterexamples[-1])
summary={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'public_calls':len(records),'groups':groups,'success_calls':sum('full_result'in r for r in records),
 'error_counts':dict(collections.Counter(r['error']['message'] for r in records if 'error'in r)),'checks':checks,'counterexamples':counterexamples,'mismatches':mismatches,
 'caller_and_cached_catalog_preserved':True,'read_only_no_patch':True}
(base/'public-comparison068.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('checks','counterexamples','mismatches')},ensure_ascii=False));print('counterexamples',len(counterexamples),'mismatches',len(mismatches));assert not mismatches
