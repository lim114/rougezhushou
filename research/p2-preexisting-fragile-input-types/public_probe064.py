from pathlib import Path
import sys,json,hashlib,itertools,datetime,collections
base=Path(__file__).parent;sys.path.insert(0,str(base/'baseline'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

VALUES=[('absent',None),('bool_false',False),('bool_true',True),('null',None),('int_zero',0),('int_one',1),('float_zero',0.0),('float_one',1.0),('negative_zero',-0.0),('empty_text',''),('false_text','false'),('upper_false_text','False'),('zero_text','0'),('true_text','true'),('one_text','1'),('int_two',2),('int_negative',-1),('empty_list',[]),('nonempty_list',[False]),('empty_object',{}),('nonempty_object',{'enabled':False})]

def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
def flag_request(args,label,value):return dict(args) if label=='absent' else {**args,'preexisting_fragile':value}
records=[];identities=set();groups=collections.Counter()

def add(group,args,label,value):
 request=flag_request(args,label,value); key=canonical(request)
 if key in identities:return
 identities.add(key)
 before=json.loads(canonical(request));public=canonical(catalog())
 try:
  result=calculate_damage(request)
  record={'group':group,'value_label':label,'request':before,'full_result':result,'full_result_sha256':digest(result)}
 except Exception as error:
  record={'group':group,'value_label':label,'request':before,'error':{'type':type(error).__name__,'message':str(error)}}
 assert canonical(request)==canonical(before);assert canonical(catalog())==public
 records.append(record);groups[group]+=1

for mode,rank in itertools.product(('frames','continuous'),(1,7,10)):
 for label,value in VALUES:
  add('active_flag_types',{'operator':'silverash','skill':3,'skill_rank':rank,'timing_mode':mode,'window_seconds':10,'base_attack':1000,'enemy_defense':1000},label,value)
for mode,condition in itertools.product(('frames','continuous'),(
 {'window_seconds':0},{'window_seconds':10,'timing':{'target_disappears_seconds':0}},
 {'window_seconds':10,'timing':{'target_windows':[]}}, {'window_seconds':10,'cooperative':True},
 {'window_seconds':10,'effects':[{'kind':'damage_taken','damage_type':'physical','value':.5}]},
 {'window_seconds':10,'effects':[{'kind':'damage_taken','damage_type':'magic','value':.5}]},
 {'window_seconds':10,'effects':[{'kind':'damage_taken','damage_type':'true','value':.5}]})):
 for label,value in [('bool_false',False),('bool_true',True),('false_text','false')]:
  add('active_boundary_and_existing_effect_math',{'operator':'silverash','skill':3,'timing_mode':mode,'base_attack':1000,'enemy_defense':1000,**condition},label,value)
for elite,skill,mode,potential in itertools.product((0,1),range(1,4),('frames','continuous'),(1,6)):
 for label,value in [('absent',None),('bool_false',False),('bool_true',True),('false_text','false'),('null',None)]:
  add('silverash_early_elite_and_skill_qualification',{'operator':'silverash','skill':skill,'elite':elite,'skill_rank':7,'potential':potential,'timing_mode':mode},label,value)
for op,p in catalog()['operators'].items():
 for skill in range(1,len(p['skills'])+1):
  if op=='silverash' and skill==3:continue
  for mode in ('frames','continuous'):
   for label,value in [('absent',None),('bool_false',False),('false_text','false'),('nonempty_object',{'enabled':False})]:
    add('inactive_whole_output_controls',{'operator':op,'skill':skill,'timing_mode':mode},label,value)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf','public_calculation_calls':len(records),'groups':groups,'records':records}
(base/'public-results064.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# Group flag variants by all other identical inputs and compare entire outputs/errors.
lookup=collections.defaultdict(dict)
for record in records:
 request={k:v for k,v in record['request'].items() if k!='preexisting_fragile'}
 lookup[canonical(request)][record['value_label']]=record
checks=[];mismatches=[];counterexamples=[]
for request,variants in lookup.items():
 def outcome(record):return record.get('full_result_sha256') or canonical(record['error'])
 for label,value in VALUES:
  if label not in variants:continue
  r=variants[label]
  request_obj=json.loads(request);active=request_obj['operator']=='silverash' and request_obj['skill']==3 and request_obj.get('elite',2)==2
  if not active:
   reference=variants.get('absent') or variants.get('bool_false')
   if reference:
    same=outcome(reference)==outcome(r);checks.append({'request':r['request'],'control':'inactive_or_qualification_prior_error','same_full_result_or_error':same})
    if not same:mismatches.append(checks[-1])
  elif label in ('null','int_zero','float_zero','negative_zero','int_one','float_one'):
   reference=variants['bool_true' if bool(value) else 'bool_false'];same=outcome(reference)==outcome(r)
   checks.append({'request':r['request'],'control':'legal_numeric_or_null_existing_behavior','same_full_result':same})
   if not same:mismatches.append(checks[-1])
  elif label in ('false_text','upper_false_text','zero_text','nonempty_list','nonempty_object','int_two','int_negative'):
   reference=variants.get('bool_true');off=variants.get('bool_false')
   if reference and off and outcome(r)==outcome(reference):
    result=r.get('full_result',{});off_result=off.get('full_result',{});
    counterexamples.append({'request':r['request'],'matches_true_full_json':True,'differs_from_false_full_json':outcome(r)!=outcome(off),
       'total_damage':result.get('total_damage'),'false_total_damage':off_result.get('total_damage'),'per_hit':result.get('per_hit'),'false_per_hit':off_result.get('per_hit')})
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'public_calls':len(records),'groups':groups,
 'public_success_calls':sum('full_result' in r for r in records),'existing_qualification_error_calls':sum('error' in r for r in records),
 'checks':checks,'mismatches':mismatches,'truthy_counterexamples':counterexamples,
 'no_source_patch':True,'no_tracked_edits':True,'all_caller_and_catalog_inputs_unchanged':True}
(base/'public-comparison064.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('checks','mismatches','truthy_counterexamples')},ensure_ascii=False));print('mismatches',len(mismatches),'counterexamples',len(counterexamples));assert not mismatches
