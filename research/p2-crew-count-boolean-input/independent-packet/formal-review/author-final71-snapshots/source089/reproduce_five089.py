"""Exactly five authorized isolated RunState groups; no other public APIs."""
import copy,hashlib,json,sys,traceback
from collections import Counter
from pathlib import Path
OUT=Path(__file__).resolve().parent
proof=json.loads((OUT/'fixed-public-source-bindings089.json').read_bytes());REPO=Path(proof['repo'])
plan=json.loads((OUT/'authorized-five-case-plan089.json').read_bytes())
sys.dont_write_bytecode=True
sys.path.insert(0,str(REPO))
for row in proof['frozen_named_sources']:
 data=(REPO/row['path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
def native(v):
 if isinstance(v,dict):return {'type':'dict','items':[[native(k),native(x)] for k,x in v.items()]}
 if isinstance(v,(tuple,list)):return {'type':type(v).__name__,'items':[native(x) for x in v]}
 if isinstance(v,float):return {'type':'float','hex':v.hex()}
 return {'type':type(v).__name__,'value':v}
def save(name,obj):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
from rouge.run_state import RunState
import rouge.run_state as module
assert Path(module.__file__).resolve()==REPO/'rouge/run_state.py'
METHODS=Counter();STAGE=Counter();stage='setup';rows=[];explicit=Counter()
def observe(frame,event,arg):
 if event=='call' and frame.f_code.co_filename==str(REPO/'rouge/run_state.py'):
  METHODS[frame.f_code.co_name]+=1;STAGE[(stage,frame.f_code.co_name)]+=1
def forbid_real_local(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)):
  p=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
  if '.local' in p.parts:raise AssertionError('Actual .local access is forbidden')
sys.addaudithook(forbid_real_local)
previous_profile=sys.getprofile();sys.setprofile(observe)
try:
 for index,case in enumerate(plan['groups'],1):
  directory=OUT/'runtime'/case['id'];directory.mkdir(parents=True,exist_ok=False);path=directory/'run.json'
  assert not path.exists() and path.resolve().is_relative_to(OUT/'runtime')
  stage='constructor';explicit['RunState_constructor']+=1;run=RunState(path)
  initial=copy.deepcopy(run.state);initial_tree=native(initial)
  seed={'operators':[{'id':oid,'scope':'run','fields':{},'skill_ranks':{}} for oid in case['seed_ids']],
        'crew_count':case['seed_crew']}
  before_seed=copy.deepcopy(seed);seed_tree=native(seed);seed_at=run.state['started_at']+1
  stage='seed';explicit['seed_apply']+=1;seed_return=run.apply(seed,seed_at)
  assert seed_return is True and native(seed)==seed_tree
  before=copy.deepcopy(run.state);before_tree=native(before);before_bytes=path.read_bytes();before_disk=json.loads(before_bytes)
  assert native(before_disk)==before_tree
  (directory/'seed-persisted.json').write_bytes(before_bytes)
  observed={'operators':[{'id':oid,'scope':'run','fields':{},'skill_ranks':{}} for oid in case['subject_ids']],
            'crew_count':case['crew_count']}
  caller_before=copy.deepcopy(observed);caller_tree=native(observed);at=run.state['started_at']+2
  stage='subject';explicit['subject_apply']+=1;returned=run.apply(observed,at)
  after=copy.deepcopy(run.state);after_tree=native(after);after_bytes=path.read_bytes();after_disk=json.loads(after_bytes)
  assert returned is True and native(observed)==caller_tree and native(after_disk)==after_tree
  departures=[oid for oid,member in after['operators'].items() if not member['present']]
  assert departures==case['expected_source_departures']
  row={'case':case,'file_path':str(path),'initial_state':initial,'initial_state_typed':initial_tree,
   'seed_observed_before':before_seed,'seed_observed_after':seed,'seed_caller_typed_before':seed_tree,'seed_caller_typed_after':native(seed),
   'seed_captured_at':seed_at,'seed_return':seed_return,'before_state':before,'before_state_typed':before_tree,
   'before_persisted_JSON_bytes_sha256':hashlib.sha256(before_bytes).hexdigest(),'before_persisted_JSON':before_disk,
   'observed_before':caller_before,'observed_after':observed,'caller_typed_before':caller_tree,'caller_typed_after':native(observed),
   'subject_captured_at':at,'subject_return':returned,'after_state':after,'after_state_typed':after_tree,
   'after_history':copy.deepcopy(after['history']),'after_persisted_JSON':after_disk,
   'after_persisted_JSON_bytes_sha256':hashlib.sha256(after_bytes).hexdigest(),'source_expected_departures_confirmed':departures,
   'full_caller_unchanged':True,'full_persisted_state_matches_inmemory_native':True}
  save('case-'+str(index)+'.json',row);rows.append(row)
finally:sys.setprofile(previous_profile)
assert explicit=={'RunState_constructor':5,'seed_apply':5,'subject_apply':5}
assert METHODS['__init__']==5 and METHODS['apply']==10
loaded=[]
for name,loaded_module in sorted(sys.modules.items()):
 path=getattr(loaded_module,'__file__',None)
 if not name.startswith('rouge') or not path:continue
 p=Path(path).resolve();assert p.is_relative_to(REPO)
 relative=p.relative_to(REPO).as_posix();data=p.read_bytes();expected=proof['files'][relative]
 assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256'],relative
 loaded.append({'module':name,'path':relative,**expected})
summary={'status':'PASS_FIVE_SOURCE_REPRODUCTIONS','base_commit':proof['base_commit'],'groups':5,
 'explicit_method_calls':dict(explicit),'actual_RunState_file_function_entries':dict(METHODS),
 'actual_RunState_file_function_entries_by_stage':[{'stage':a,'function':b,'count':v} for (a,b),v in STAGE.items()],
 'loaded_project_source_hashes_exact':loaded,'source_bug_confirmed':{'False_with_empty_roster_departs':'mechanist','True_with_one_roster_departs':'char_151_myrtle'},
 'valid_int_controls':'int0 andint1 retain the old departure behavior; None retains membership.',
 'natural_clock_scope':'Each constructor generated natural UUID/started_at. Existing055/063 captured_at started_at+1/+2 is retained as actualfloat. No crossgroup full-tree equality, clock freezing or normalization is claimed.',
 'caller_native_and_disk_checks':'All10observed dicts unchanged; all5before/5after persisted JSON fullnative equals in-memory state.',
 'damage_training_app_recognition_API_calls':0,'formatter_calls':0,'Qt':0,'Wine':0,'tests':0,'tracked_edits':0,
 'real_local_access':0,'P1_buff_or_departure_game_mechanism_validated':False,'product_draft_created':False}
save('five-reproduction-summary.json',summary)
print(json.dumps({'status':summary['status'],'groups':5,'explicit_method_calls':dict(explicit),'actual_apply_entries':METHODS['apply'],'damage_training_app_API_calls':0}))
