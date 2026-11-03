"""Once-only approved7 tests/12 groups; record actual RunState entries and trees."""
import copy,gzip,hashlib,importlib.util,json,sys,tempfile,unittest
from collections import Counter
from pathlib import Path
OUT=Path(__file__).resolve().parent;REPO=Path('/workspace/rougezhushou')
SOURCE=Path('/workspace/.continuation/p2-crew-count-boolean-089-source')
freeze=json.loads((OUT/'draft-freeze089.json').read_bytes())
for row in freeze['files']:
 p=Path(row['source_path']);b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
assert not (OUT/'new-test-summary089.json').exists()
sys.dont_write_bytecode=True;sys.path.insert(0,str(REPO))
runtime=OUT/'runtime';runtime.mkdir(exist_ok=False);tempfile.tempdir=str(runtime)
PRODUCT=OUT/'draft/rouge/run_state.py'
import rouge
spec=importlib.util.spec_from_file_location('rouge.run_state',PRODUCT)
module=importlib.util.module_from_spec(spec);sys.modules['rouge.run_state']=module;spec.loader.exec_module(module)
test_spec=importlib.util.spec_from_file_location('author_new089',OUT/'draft/tests/test_run_crew_count_boolean_input.py')
tests=importlib.util.module_from_spec(test_spec);test_spec.loader.exec_module(tests)
assert tests.RunState is module.RunState
def native(v):
 if isinstance(v,dict):return {'type':'dict','items':[[native(k),native(x)] for k,x in v.items()]}
 if isinstance(v,(tuple,list)):return {'type':type(v).__name__,'items':[native(x) for x in v]}
 if isinstance(v,float):return {'type':'float','hex':v.hex()}
 return {'type':type(v).__name__,'value':v}
def disk(p):
 if not p.exists():return None
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'UTF8_raw_bytes':b.decode('utf-8'),
  'JSON':json.loads(b),'JSON_typed':native(json.loads(b))}
records=[];pending={};roles=Counter();entries=Counter()
def observe(frame,event,arg):
 if frame.f_code.co_filename!=str(PRODUCT):return
 if event=='call':entries[frame.f_code.co_name]+=1
 if frame.f_code.co_name not in ('__init__','apply'):return
 if event=='call':
  self=frame.f_locals['self'];name=frame.f_code.co_name;caller=frame.f_back.f_code.co_name
  if name=='__init__':
   role='constructor_reload' if caller=='reload_run' else 'constructor_new';assert caller in ('seed_run','reload_run')
   path=Path(frame.f_locals['file'])
  else:
   role='seed_apply' if caller=='seed_run' else 'subject_apply';assert caller in ('seed_run','observe')
   path=self.file
  assert path.resolve().is_relative_to(runtime)
  roles[role]+=1;record={'sequence':len(records)+len(pending)+1,'method':name,'role':role,'file_path':str(path),
    'state_before':copy.deepcopy(getattr(self,'state',None)),
    'state_before_typed':native(getattr(self,'state',None)),'disk_before':disk(path)}
  if name=='apply':
   record.update(observed_before=copy.deepcopy(frame.f_locals['observed']),
    observed_before_typed=native(frame.f_locals['observed']),captured_at=frame.f_locals['captured_at'])
  pending[id(frame)]=record
 elif event=='return':
  self=frame.f_locals['self'];record=pending.pop(id(frame));record.update(return_value=arg,return_value_typed=native(arg),
    state_after=copy.deepcopy(self.state),state_after_typed=native(self.state),disk_after=disk(self.file))
  if frame.f_code.co_name=='apply':
   record.update(observed_after=copy.deepcopy(frame.f_locals['observed']),observed_after_typed=native(frame.f_locals['observed']))
   record['caller_whole_typed_unchanged']=record['observed_before_typed']==record['observed_after_typed']
   assert record['caller_whole_typed_unchanged']
  records.append(record)
def forbid_real_local(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)):
  value=args[0].decode() if isinstance(args[0],bytes) else args[0]
  if '.local' in Path(value).resolve().parts:raise AssertionError('Real.local access forbidden')
sys.addaudithook(forbid_real_local)
suite=unittest.defaultTestLoader.loadTestsFromModule(tests);assert suite.countTestCases()==7
previous=sys.getprofile();sys.setprofile(observe)
try:
 with (OUT/'new-tests-attempt-1.log').open('x',encoding='utf-8') as log:
  result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
finally:sys.setprofile(previous)
proof=json.loads((SOURCE/'fixed-public-source-bindings089.json').read_bytes());loaded=[]
for name,loaded_module in sorted(sys.modules.items()):
 file=getattr(loaded_module,'__file__',None)
 if not name.startswith('rouge') or not file:continue
 p=Path(file).resolve();b=p.read_bytes()
 if name=='rouge.run_state':assert p==PRODUCT;expected=freeze['files'][0]
 else:
  assert p.is_relative_to(REPO);relative=p.relative_to(REPO).as_posix();expected=proof['files'][relative]
 assert len(b)==expected['bytes'] and hashlib.sha256(b).hexdigest()==expected['sha256'],name
 loaded.append({'module':name,'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
actual={'constructor_new':12,'constructor_reload':2,'seed_apply':12,'subject_apply':12}
summary={'status':'PASS' if result.wasSuccessful() else 'FAILED_PRESERVED','tests_run':result.testsRun,
 'errors':len(result.errors),'failures':len(result.failures),'skips':len(result.skipped),'actual_explicit_entry_roles':dict(roles),
 'actual_RunState_file_entries':dict(entries),'records':len(records),'budget_expected':actual,'budget_exact':roles==actual,
 'loaded_project_module_bytes_bound':loaded,'source_base_commit':proof['base_commit'],'product_transport_commit':freeze['transport_root_commit'],
 'clock_scope':'Natural perconstructorUUID/started_at retained; seed+1/subject+2 follows existingprotocol. Reload onlynotice expectedsourcechanges; no normalized crosscase whole equality.',
 'legacy_nonbool_scope':'float0.0/string0 cover old compatibility only; actualrecognition producer stillint/None.',
 'damage_training_app_recognition_API_calls':0,'formatter_calls':0,'Qt':0,'Wine':0,'tests_source5_repeated':False,'real_local_access':0,'tracked_edits':0,
 'internal_nonRunState_helper_entry_counts':'Notinstrumented; do not infer wholeproject totals.'}
raw=json.dumps({'summary':summary,'records':records},ensure_ascii=False,allow_nan=False).encode()
compressed=gzip.compress(raw,mtime=0)
with (OUT/'new-tests-native-records089.json.gz').open('xb') as f:f.write(compressed)
summary.update(saved_gzip_bytes=len(compressed),saved_gzip_sha256=hashlib.sha256(compressed).hexdigest(),
 decoded_bytes=len(raw),decoded_sha256=hashlib.sha256(raw).hexdigest())
with (OUT/'new-test-summary089.json').open('x',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'status':summary['status'],'tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),
 'roles':dict(roles),'records':len(records),'damage_app_API_calls':0}))
assert result.wasSuccessful() and roles==actual and entries['__init__']==14 and entries['apply']==24 and len(records)==38
