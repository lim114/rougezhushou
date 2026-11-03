PENDING_PREPARATION = True
if PENDING_PREPARATION:
    raise SystemExit('Pending096: actual full095 available PASS and commit/push, root-filled actual guards, fresh baseline, independent FINAL source admission and root authorization are required')
import gzip, hashlib, json, sys, tempfile, time, traceback
from pathlib import Path
from contextlib import ExitStack
BINDING_PATH=Path(__file__).with_name('condition096-binding-final.json')
EXPECTED_BINDING_SHA256=None  # Root FINAL substitution, source-review required.
assert type(EXPECTED_BINDING_SHA256) is str and len(EXPECTED_BINDING_SHA256)==64
assert hashlib.sha256(BINDING_PATH.read_bytes()).hexdigest()==EXPECTED_BINDING_SHA256
BINDING=json.loads(BINDING_PATH.read_text(encoding='utf-8'))
assert BINDING['status']=='ROOT_SEALED_CONDITION096_RUNTIME_BINDING'
assert BINDING['root_runtime_authorized'] is True
assert BINDING['actual_full095_validation_receipt'] is not None and BINDING['actual_post_full095_commit_push_proof'] is not None
assert BINDING['actual_FINAL_runner_formal_review'] is not None
ROOT=Path(BINDING['source_root']);OUT=Path(BINDING['fresh_output_directory']);MODE=BINDING['mode']
assert MODE in ('gold','candidate')
def bound_file(row):
    data=Path(row['path']).read_bytes()
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    return data
def pointer(value,path):
    if path=='':return value
    for item in path[1:].split('/'):
        item=item.replace('~1','/').replace('~0','~');value=value[int(item)] if isinstance(value,list) else value[item]
    return value
for row in BINDING['required_actual_prerequisite_gates']:
    actual=json.loads(bound_file(row).decode('utf-8'));assert row['JSON_pointer_gates']
    for gate in row['JSON_pointer_gates']:
        value=pointer(actual,gate['pointer']);assert type(value) is type(gate['expected']) and value==gate['expected']
for key in ('actual_full095_validation_receipt','actual_post_full095_commit_push_proof','candidate_code_manifest','condition096_formal_source_review','actual_FINAL_runner_formal_review'):
    bound_file(BINDING[key])
    assert any(row['path']==BINDING[key]['path'] for row in BINDING['required_actual_prerequisite_gates']),'Every admission reference requires root-bound typed actual gates'
GUARD=json.loads(bound_file(BINDING['actual_source_guard']).decode('utf-8'))
SOURCE_HASHES=GUARD['source_sha256_after'];assert GUARD['passed'] is True
assert len(SOURCE_HASHES)==BINDING['actual_maintained_count']
for rel,sha in SOURCE_HASHES.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha,('Preimport maintained source',rel)
PLAN=json.loads(bound_file(BINDING['validation_plan']).decode('utf-8'))
assert not OUT.exists(),'Every attempt uses a fresh absent directory; preserve successful prefixes and failures'
OUT.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(ROOT))
def flat_native(value):
    nodes=[];todo=[];seen={}
    def reference(v):
        kind=type(v)
        if kind in (dict,list,tuple) and id(v) in seen:return seen[id(v)]
        index=len(nodes);nodes.append(None);todo.append((index,v))
        if kind in (dict,list,tuple):seen[id(v)]=index
        return index
    root=reference(value)
    while todo:
        index,v=todo.pop();kind=type(v)
        if v is None or kind in (bool,int,str):node={'type':kind.__name__,'value':v}
        elif kind is float:node={'type':'float','hex':v.hex()}
        elif kind is bytes:node={'type':'bytes','hex':v.hex()}
        elif kind in (list,tuple):node={'type':kind.__name__,'items':[reference(x) for x in v]}
        elif kind is dict:node={'type':'dict','items':[[reference(k),reference(x)] for k,x in v.items()]}
        else:raise TypeError(('unsupported evidence value',kind.__name__))
        nodes[index]=node
    return {'schema':'flat-typed-graph-v1','root':root,'nodes':nodes}


def native_inverse(graph):
    assert graph['schema']=='flat-typed-graph-v1'
    nodes=graph['nodes'];values={};active=set();stack=[(graph['root'],False)]
    while stack:
        index,finish=stack.pop()
        if index in values:continue
        node=nodes[index];kind=node['type']
        if kind in ('NoneType','bool','int','str'):values[index]=node['value'];continue
        if kind=='float':values[index]=float.fromhex(node['hex']);continue
        if kind=='bytes':values[index]=bytes.fromhex(node['hex']);continue
        if not finish:
            assert index not in active,'Public evidence graph must be acyclic'
            active.add(index);stack.append((index,True))
            children=[x for pair in node['items'] for x in pair] if kind=='dict' else node['items']
            stack.extend((child,False) for child in reversed(children) if child not in values)
        else:
            active.remove(index)
            if kind=='dict':values[index]={values[k]:values[v] for k,v in node['items']}
            elif kind=='list':values[index]=[values[x] for x in node['items']]
            elif kind=='tuple':values[index]=tuple(values[x] for x in node['items'])
            else:raise ValueError(('invalid flat type',kind))
    return values[graph['root']]


def clone(value):return native_inverse(flat_native(value))


def snapshot(value):
    graph=flat_native(value);restored=native_inverse(graph)
    assert flat_native(restored)==graph,'Lossless native inverse must reproduce exact flat graph'
    return {'native':graph,'JSON_projection':restored,'native_inverse_verified':True}


def delta(before,after):return {k:after.get(k,0)-before.get(k,0) for k in sorted(set(before)|set(after))}


def digest(data):return hashlib.sha256(data).hexdigest()


def filesystem(folder):
    rows=[]
    for path in sorted(folder.rglob('*')):
        rel=path.relative_to(folder).as_posix()
        if path.is_dir():rows.append({'path':rel,'kind':'directory'});continue
        data=path.read_bytes();row={'path':rel,'kind':'file','bytes':len(data),'sha256':digest(data),'raw_hex':data.hex()}
        try:row['decoded']=snapshot(json.loads(data.decode('utf-8')))
        except (UnicodeDecodeError,ValueError) as error:row['decode_error']={'type':type(error).__name__,'message':str(error)}
        rows.append(row)
    return rows


def file_bytes(path):return path.read_bytes() if path.exists() else None


def byte_evidence(data):
    assert data is None or type(data) is bytes,'Only an existing raw file byte string or explicit absent file'
    graph=flat_native(data);restored=native_inverse(graph)
    assert type(restored) is type(data) and restored==data and flat_native(restored)==graph,'Lossless raw-byte native inverse must preserve exact original value'
    return {'schema':'raw-file-bytes-evidence-v1','native':graph,'native_inverse_verified':True,
        'JSON_safe_raw_bytes':{'file_exists':data is not None,'raw_hex':data.hex() if data is not None else None,
            'byte_count':len(data) if data is not None else None,'sha256':digest(data) if data is not None else None}}


# This numeric worker never runs the separately written sixteen helper boundary
# tests. Root's independent unittest primary has its own actual argv/log/raw exit.
receipt={'format_version':2,'kind':'CONDITION096_ISOLATED_LINUX_API_PAIRS','mode':MODE,'passed':False,'workflow_complete':False,'completed_section_increment':0,'source_guard_sha256':BINDING['actual_source_guard']['sha256'],'plan_sha256':BINDING['validation_plan']['sha256'],'records':[],'actual_tests_run':0,'written_boundary_tests_executed_by_worker':False,'independent_boundary_unittest_primary_required':True,'actual_API_entries':0,'project_app_imports':0,'private_state_used':False}
counts={};events=[];pending={};callers={};active='before-project-import';previous_profile=sys.getprofile();previous_trace=sys.gettrace()
def path_of(frame):return frame.f_code.co_filename.replace('\\','/').lower()
def trace_local(frame,event,arg):
    if event=='exception' and id(frame) in pending:pending[id(frame)].setdefault('exception_events',[]).append({'type':arg[0].__name__,'message':str(arg[1]),'args':snapshot(arg[1].args)})
    return trace_local
def trace(frame,event,arg):
    if event=='call' and path_of(frame).endswith('/rouge/damage.py') and frame.f_code.co_name in ('calculate_damage','_prepare_damage'):return trace_local
    return None
def profile(frame,event,arg):
    path=path_of(frame)
    if event=='call' and '/rouge/' in path:
        key='rouge/'+path.split('/rouge/',1)[1]+':'+frame.f_code.co_qualname;counts[key]=counts.get(key,0)+1
        if path.endswith('/rouge/app.py'):raise AssertionError('Linux worker must not import or execute app')
        if path.endswith('/rouge/condition_cultivation.py'):raise AssertionError('Numeric API must add no presentation helper call')
        if path.endswith('/rouge/damage.py') and frame.f_code.co_name in ('calculate_damage','_prepare_damage'):
            caller={'scenario':frame.f_locals['scenario']};row={'key':frame.f_code.co_name,'case':active,'caller_before':snapshot(caller),'outcome':'pending'}
            events.append(row);pending[id(frame)]=row;callers[id(frame)]=caller
    elif event=='return' and id(frame) in pending:
        row=pending.pop(id(frame));caller=callers.pop(id(frame));row['caller_after']=snapshot(caller);row['caller_unchanged']=row['caller_before']['native']==row['caller_after']['native']
        if arg is not None:
            row['outcome']='returned_'+type(arg).__name__;row['returned']=snapshot(arg);row['caller_and_returned_graph']=snapshot({'caller':caller,'returned':arg})
        elif row.get('exception_events'):row['outcome']='raised_exception'
        else:row['outcome']='returned_none_or_unobserved_unwind'
        if row['key']=='_prepare_damage':row['local_prepared_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'))
def save_record(row):
    sequence=len(receipt['records'])+1;path=OUT/('%06d.json.gz'%sequence);raw=json.dumps(row,ensure_ascii=False,allow_nan=False).encode('utf-8');compressed=gzip.compress(raw,mtime=0);path.write_bytes(compressed)
    receipt['records'].append({'id':row['id'],'path':str(path),'bytes':len(compressed),'sha256':digest(compressed),'decoded_bytes':len(raw),'decoded_sha256':digest(raw)})
    (OUT/'linux-condition096-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
try:
    sys.setprofile(profile);sys.settrace(trace)
    from rouge.damage import calculate_damage
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    for case in PLAN['Linux_cases']:
        active=case['id'];scenario=clone(case['scenario']);before=snapshot(scenario);start=dict(counts);event_start=len(events)
        try:
            value=calculate_damage(scenario);outcome={'kind':'returned','value':snapshot(value),'caller_and_result':snapshot({'caller':scenario,'result':value})}
        except Exception as error:outcome={'kind':'raised','type':type(error).__name__,'message':str(error),'args':snapshot(error.args)};value=None
        numeric_vector=delta(start,counts);assert flat_native(scenario)==before['native'];format_start=dict(counts)
        texts=None
        if outcome['kind']=='returned':
            result_before=flat_native(value);texts={'estimate':format_estimate(value),'default':format_report(value),'technical':format_report(value,technical=True)};assert flat_native(value)==result_before
        row={'id':active,'planned':snapshot(case),'caller_before':before,'caller_after':snapshot(scenario),'outcome':outcome,'actual_API_and_prepare_entries':clone(events[event_start:]),'original_numeric_function_vector':numeric_vector,'actual_formatter_function_vector':delta(format_start,counts),'all_three_texts':texts,'passed':True}
        assert all(e['caller_unchanged'] for e in row['actual_API_and_prepare_entries'])
        receipt['actual_API_entries']+=sum(e['key']=='calculate_damage' for e in row['actual_API_and_prepare_entries'])
        # Pause only for stdlib serialization; never execute product code with profiling disabled.
        sys.setprofile(previous_profile);sys.settrace(previous_trace)
        try:save_record(row)
        finally:sys.setprofile(profile);sys.settrace(trace)
    assert len(receipt['records'])==PLAN['counts']['Linux_API_cases_planned'] and receipt['actual_API_entries']==len(receipt['records'])
    assert not pending and not callers;receipt['passed']=True;receipt['workflow_complete']=True
except BaseException as error:receipt['failure']={'type':type(error).__name__,'message':str(error),'case':active,'traceback':traceback.format_exc()}
finally:
    sys.setprofile(previous_profile);sys.settrace(previous_trace)
    after={rel:digest((ROOT/rel).read_bytes()) for rel in SOURCE_HASHES};receipt['source_sha256_after']=after;receipt['source_drift']=[r for r in SOURCE_HASHES if after[r]!=SOURCE_HASHES[r]]
    if receipt['source_drift']:receipt['passed']=False;receipt['workflow_complete']=False
    receipt['all_project_function_entries']=counts;(OUT/'linux-condition096-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':receipt['passed'],'records':len(receipt['records']),'failure':receipt.get('failure')},ensure_ascii=False));sys.exit(0 if receipt['passed'] else 1)
