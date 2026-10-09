PENDING_PREPARATION = False
if PENDING_PREPARATION:
    raise SystemExit('Pending095: root actual95 applied source guard, fresh actual94 baseline PASS/captured shell status/saved review, actual candidate source review and FINAL independent review required; root alone executes Wine')
"""Focused selected-module report group: same source-bound real window plan as actual94 baseline."""
import gzip,hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
from contextlib import ExitStack
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat\focused095-window-attempt2')
BINDING_PATH=Path(__file__).with_name('wine-module-report-095-binding-final.json')
EXPECTED_BINDING_SHA256='8671efd0f9fa3562143c410e91596aacd3d0c38a6e74ea00f0e9274b64d70245'
assert hashlib.sha256(BINDING_PATH.read_bytes()).hexdigest()==EXPECTED_BINDING_SHA256
BINDING=json.loads(BINDING_PATH.read_text(encoding='utf-8'));assert BINDING['status']=='ROOT_SEALED_ACTUAL95_FOCUSED_BINDING'
def bound_file(row):
    path=Path(row['path']);data=path.read_bytes()
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],('Exact runtime bound file',row['path'])
    return data
def pointer(value,path):
    if path=='':return value
    assert path.startswith('/')
    for item in path[1:].split('/'):
        item=item.replace('~1','/').replace('~0','~');value=value[int(item)] if isinstance(value,list) else value[item]
    return value
def evaluate_gate(row,required):
    value=json.loads(bound_file(row).decode('utf-8'));gates=row['JSON_pointer_gates']
    assert len(gates)==len({g['pointer'] for g in gates}),'No duplicate JSON pointer gate'
    provided={g['pointer']:g['expected'] for g in gates}
    for key,expected in required.items():
        assert key in provided and type(provided[key]) is type(expected) and provided[key]==expected,('Required real success/hash pointer',key)
    for gate in gates:
        actual=pointer(value,gate['pointer']);assert type(actual) is type(gate['expected']) and actual==gate['expected'],('Actual root gate',row['path'],gate['pointer'])
    return value
rows=BINDING['required_gate_files'];assert len(rows)==2 and len({r['role'] for r in rows})==2
roles={r['role']:r for r in rows};assert set(roles)=={'baseline_saved_only_review','actual95_candidate_source_review'}
evaluate_gate(roles['baseline_saved_only_review'],{'/passed':True,'/actual_runtime_receipt_sha256':BINDING['baseline_receipt']['sha256'],'/actual_native_archive_sha256':BINDING['baseline_records']['sha256']})
evaluate_gate(roles['actual95_candidate_source_review'],{'/source_gate_passed':True,'/runtime_pass':False,'/code_manifest_sha256':BINDING['candidate_code_manifest']['sha256'],'/base_source_guard_sha256':'259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211','/interface_sha256':BINDING['candidate_interface_artifact']['sha256']})
evaluate_gate(BINDING['single_test_formal_review'],{'/source_gate_passed':True,'/runtime_pass':False,'/test_manifest_sha256':BINDING['single_test_supplement_manifest']['sha256'],'/before_test_sha256':'cea16b4243c949fd1749c1cab4f323b2f5ea7267ad69928e715ea570ab27e199','/after_test_sha256':'ad4a6381e6ec6f1a6db08cb1df0339b614883c960a1db3865d019ac08b12b554','/baseline95_guard_sha256':'57e80f30aa67384225c49fd16b58bd3289fe9df41e018feca242ce132d105b82'})
for packet_key in ('candidate_code_manifest','candidate_interface_artifact','technical_tail_correction_artifact','single_test_supplement_manifest','single_test_inverse','initial_core095_guard'):bound_file(BINDING[packet_key])
assert bound_file(BINDING['baseline_shell_status']).decode('ascii')=='0\n'
GUARD=Path(__file__).with_name('wine-module-report-095-source.json')
EXPECTED_GUARD_SHA256=BINDING['actual95_guard_sha256'];assert hashlib.sha256(GUARD.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA256
SOURCE=json.loads(GUARD.read_text(encoding='utf-8'));SOURCE_HASHES=SOURCE['source_sha256_after'];assert SOURCE['passed'] is True
assert len(SOURCE_HASHES)==BINDING['actual95_maintained_count']
for rel,h in SOURCE_HASHES.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,('Actual95 source before project import',rel)
PLAN_PATH=Path(__file__).with_name('wine-module-report-shared095-plan.json')
assert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a'
PLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))
BASELINE_RECEIPT=json.loads(bound_file(BINDING['baseline_receipt']).decode('utf-8'))
assert BASELINE_RECEIPT['passed'] is True and BASELINE_RECEIPT['workflow_complete'] is True and BASELINE_RECEIPT['completed_section_increment']==0
assert BASELINE_RECEIPT['source_guard_sha256']=='259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'
assert BASELINE_RECEIPT['plan_sha256']=='ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a'
assert BASELINE_RECEIPT['source_drift']==[]
baseline_raw=gzip.decompress(bound_file(BINDING['baseline_records']))
assert len(baseline_raw)==BASELINE_RECEIPT['records']['decoded_bytes'] and hashlib.sha256(baseline_raw).hexdigest()==BASELINE_RECEIPT['records']['decoded_sha256']
BASELINE=json.loads(baseline_raw.decode('utf-8'));assert BASELINE['passed'] is True and BASELINE['schema']=='focused-module-report-baseline-v1'
assert [s['id'] for s in BASELINE['states']]==[s['id'] for s in PLAN['steps']] and all(s['passed'] is True for s in BASELINE['states'])
BASELINE_STATES={s['id']:s for s in BASELINE['states']};BASELINE_API={r['sequence']:r for r in BASELINE['API_entries']};BASELINE_PREPARED={r['sequence']:r for r in BASELINE['prepared_entries']}
ORIGINAL_BATTLE=json.loads(bound_file(BINDING['original_battle']).decode('utf-8'));ORIGINAL_MODULES=json.loads(bound_file(BINDING['original_modules']).decode('utf-8'))
CATALOG=json.loads((ROOT/'rouge/data/catalog.json').read_text(encoding='utf-8'))
INTERFACE=BINDING['candidate_interface'];REFERENCE_KEY=INTERFACE['report_addition_key'];SECTION_ID=INTERFACE['notes_only_section']['id'];SECTION_TITLE=INTERFACE['notes_only_section']['title'];TECHNICAL_DELIMITER=BINDING['technical_tail_exact_delimiter']
assert REFERENCE_KEY=='selected_module_source_reference' and SECTION_ID=='selected_module_source'
assert TECHNICAL_DELIMITER=='\n\n【所选模组原件追溯】\n'
assert OUT==Path(BINDING['output_directory']) and BINDING['runtime_attempt']==2
assert not OUT.exists(),'Preserve every first-attempt artifact; second attempt requires a fresh absent output directory'
RECEIPT=OUT/'wine-module-report-window-095.json';ARCHIVE=OUT/'wine-module-report-window-095-records.json.gz'
assert not RECEIPT.exists() and not ARCHIVE.exists(),'Preserve prior evidence; never replay a successful prefix'
for name in ('wine-module-report-095-normal-gate.png','wine-module-report-095-normal-dedicated.png','wine-module-report-095-technical-raw.png','wine-module-report-095-failure.png'):assert not (OUT/name).exists(),('Preserve existing screenshot',name)
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

pngs=[];baseline_checks=[];live_reference_history=[];live_cached_supplement_baseline_snapshot=None
counts={};all_entries={};entries_by_scope={};API=[];PREPARED=[];CALLS=[];pending={};caller_objects={};signals=[];states=[];checks=[];qt_exceptions=[]
phase='before-import';request='none';current='before-first-window';window_id=None
window=None;application=None;active_folder=None;account_path=None;run_path=None
explicit_buttons=0;explicit_texts=0;fresh_windows=0;checkpoint_pauses=0
started=time.perf_counter();folders=ExitStack()
previous_profile=sys.getprofile();previous_trace=sys.gettrace();previous_excepthook=sys.excepthook
CONTROL_NAMES=tuple(row['widget'] for row in PLAN['controls'])
receipt={'format_version':1,'passed':False,'workflow_complete':False,'completed_section_increment':0,
 'kind':'FOCUSED_ACTUAL95_SELECTED_MODULE_REPORT_GROUP','runtime_attempt':2,'output_directory':str(OUT),'source_guard_sha256':EXPECTED_GUARD_SHA256,
 'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
 'actual94_receipt_sha256':'55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5',
 'actual94_closure_sha256':'613d5956762bd7b0a19d15c15173df698890a8545a8d0e14253086aaf728f806',
 'source_sha256_before':SOURCE_HASHES,'checks':checks,'private_state_isolated':True,'scope_limits':PLAN['scope_limits'],
 'native_codec':'flat-typed-graph-v1; eight functions byte-exact from frozen final094 plus separate raw-file-bytes-evidence-v1',
 'codec_preparation_executed':False,'old94_matrix_replayed':False,'actual94_baseline_receipt_sha256':BINDING['baseline_receipt']['sha256'],'actual94_baseline_records_sha256':BINDING['baseline_records']['sha256'],'candidate_code_manifest_sha256':BINDING['candidate_code_manifest']['sha256'],'single_test_supplement_manifest_sha256':BINDING['single_test_supplement_manifest']['sha256'],'single_test_formal_review_sha256':BINDING['single_test_formal_review']['sha256'],'game_capture_requests':0,'chat_requests':0,
 'checkpoint_pause_scope':'Only stdlib json/gzip/hashlib/Path serialization and writes; no UI/product/API/Qt/processEvents/signals in pause'}
def path_of(frame):return frame.f_code.co_filename.replace('\\','/').lower()
def inputs(frame,key):
 if key in ('calculate_damage','_prepare_damage'):return {'scenario':frame.f_locals['scenario']}
 if key=='RunState.apply':return {k:frame.f_locals[k] for k in ('observed','captured_at')}
 if key=='AccountCache.observe':return {k:frame.f_locals[k] for k in ('operator','captured_at')}
 return None
def trace_local(frame,event,arg):
 if event=='exception' and id(frame) in pending:
  pending[id(frame)].setdefault('exception_events',[]).append({'type':arg[0].__name__,'message':str(arg[1]),'args':snapshot(arg[1].args)})
 return trace_local
def trace(frame,event,arg):
 path=path_of(frame)
 if event=='call' and (path.endswith('/rouge/app.py') and frame.f_code.co_name=='calculate' or path.endswith('/rouge/damage.py') and frame.f_code.co_name in ('calculate_damage','_prepare_damage') or path.endswith('/rouge/run_state.py') and frame.f_code.co_name=='apply' or path.endswith('/rouge/account_cache.py') and frame.f_code.co_name=='observe'):return trace_local
 return None
def profile(frame,event,arg):
 path=path_of(frame);name=frame.f_code.co_name
 if event=='call' and '/rouge/' in path:
  full='rouge/'+path.split('/rouge/',1)[1]+':'+frame.f_code.co_qualname
  all_entries[full]=all_entries.get(full,0)+1
  scope=phase+'/'+request;bucket=entries_by_scope.setdefault(scope,{})
  bucket[full]=bucket.get(full,0)+1;key=None
  if path.endswith('/rouge/damage.py') and name in ('calculate_damage','_prepare_damage'):key=name
  elif path.endswith('/rouge/estimate.py') and name=='format_estimate':key='format_estimate'
  elif path.endswith('/rouge/reporting.py') and name=='format_report':key='format_report_technical' if frame.f_locals['technical'] else 'format_report_default'
  elif path.endswith('/rouge/run_state.py'):key=('RunState.' if frame.f_code.co_qualname.startswith('RunState.') else 'run_state.')+name
  elif path.endswith('/rouge/account_cache.py'):key=('AccountCache.' if 'self' in frame.f_locals else 'account_cache.')+name
  elif path.endswith('/rouge/capture.py') and name in ('capture','next_frame','connect'):key='GameCapture.'+name
  elif path.endswith('/rouge/app.py'):key=('MainWindow.' if frame.f_code.co_qualname.startswith('MainWindow.') else 'app.')+name
  if key:counts[key]=counts.get(key,0)+1
  if key in ('calculate_damage','_prepare_damage','MainWindow.calculate','RunState.apply','AccountCache.observe'):
   row={'sequence':len(CALLS)+1,'key':key,'window':window_id,'step':current,'phase':phase,'request':request,'outcome':'pending'}
   actual=inputs(frame,key)
   if actual is not None:row['caller_before']=snapshot(actual);caller_objects[id(frame)]=actual
   if key=='MainWindow.calculate':row['all_outputs_and_affected_controls_exist']=all(hasattr(frame.f_locals['self'],x) for x in CONTROL_NAMES+('damage_text','relic_context'))
   CALLS.append(row);pending[id(frame)]=row
   if key=='calculate_damage':API.append(row)
   elif key=='_prepare_damage':PREPARED.append(row)
 elif event=='return' and id(frame) in pending:
  row=pending.pop(id(frame));key=row['key']
  original=caller_objects.pop(id(frame),None)
  if original is not None:
   row['caller_after']=snapshot(original);row['caller_unchanged']=row['caller_before']['native']==row['caller_after']['native']
  if key in ('calculate_damage','_prepare_damage'):
   if arg is not None:row.update(outcome='returned_dict' if type(arg) is dict else 'returned_prepared_tuple' if type(arg) is tuple else 'returned_other',returned=snapshot(arg))
   elif row.get('exception_events'):row['outcome']='raised_exception'
   else:row['outcome']='returned_none_or_unobserved_unwind'
   if key=='_prepare_damage':row['local_prepared_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'))
  elif key=='MainWindow.calculate':
   row['outcome']='returned_none_with_exception_events' if row.get('exception_events') else 'returned_none'
   row['assembled_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'))
  else:row['outcome']='returned_value' if arg is not None else 'returned_none';row['returned']=snapshot(arg)
def qt_hook(kind,error,tb):qt_exceptions.append({'step':current,'phase':phase,'type':kind.__name__,'message':str(error),'traceback':''.join(traceback.format_exception(kind,error,tb))})
def checkpoint():
 global checkpoint_pauses
 checkpoint_pauses+=1
 payload={'format_version':1,'schema':'focused-module-report-095-v1','native_schema':'flat-typed-graph-v1','current_step':current,'passed':receipt['passed'],'states':states,'checks':checks,'signals':signals,'API_entries':API,'prepared_entries':PREPARED,'targeted_calls':CALLS,'actual_python_entries':counts,'all_rouge_main_thread_entries':all_entries,'all_rouge_entries_by_phase_and_request':entries_by_scope,'Qt_slot_exceptions':qt_exceptions,'baseline_equivalence_checks':baseline_checks,'actual_PNGs':pngs,'live_cached_supplement_baseline_snapshot':live_cached_supplement_baseline_snapshot,'explicit_buttons':explicit_buttons,'explicit_three_text_requests':explicit_texts,'fresh_windows':fresh_windows,'stdlib_checkpoint_pauses':checkpoint_pauses}
 saved_profile=sys.getprofile();saved_trace=sys.gettrace();sys.setprofile(previous_profile);sys.settrace(previous_trace)
 try:
  raw=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8');compressed=gzip.compress(raw,mtime=0);ARCHIVE.write_bytes(compressed)
  receipt['records']={'file':ARCHIVE.name,'bytes':len(compressed),'sha256':digest(compressed),'decoded_bytes':len(raw),'decoded_sha256':digest(raw)}
 finally:sys.settrace(saved_trace);sys.setprofile(saved_profile)
def widget_value(widget):
 if isinstance(widget,QCheckBox):return widget.isChecked()
 if hasattr(widget,'currentData'):return widget.currentData()
 if hasattr(widget,'toPlainText'):return widget.toPlainText()
 return widget.value()
def ui_snapshot():
 if window is None:return None
 return {'owner':window.operator.currentData(),'skill':window.skill.currentData(),'level':window.level.value(),'level_override':window.level_override,'use_run_training':window.use_run_training.isChecked(),'elite':window.elite.text(),'trust':window.trust.text(),'potential':window.potential.text(),'module':window.module.text(),'rank':window.rank.text(),'training_status':window.training_status.text(),'current_operator_state':snapshot(window.current_operator_state()),'damage_result':snapshot(window.damage_result),'visible_text':window.damage_text.toPlainText(),'raw_damage':window.raw_damage.isChecked(),'technical':window.damage_technical.isChecked(),'frame_timing':window.frame_timing.isChecked(),'timing_text':window.timing_scenario.toPlainText(),'relic_context':window.relic_context.toPlainText(),'visible':window.isVisible()}
def durable_snapshot():
 if window is None:return None
 return {'run':snapshot(window.run.state),'account_records':snapshot(window.account_cache.records),'account_issues':snapshot(window.account_cache.issues),'preserve_original':window.account_cache.preserve_original,'account_bytes':byte_evidence(file_bytes(account_path)),'files':filesystem(active_folder),'operator_observations_alias_is_records':window.operator_observations is window.account_cache.records}
def assert_unchanged(before,after):
 assert before==after,'Preview/manual/render must preserve complete public RunState/account/files/raw bytes and helper alias'
 assert after['operator_observations_alias_is_records'] is True
def external_idle():
 assert not window.auto.isChecked() and window.capture.target is None
 assert not window.desktop.process and not window.desktop_request_busy and not (active_folder/'chat').exists()
def signal_record(name,value):signals.append({'window':window_id,'step':current,'phase':phase,'request':request,'widget':name,'value':snapshot(value)})
def observe_signals():
 for row in PLAN['controls']:
  name=row['widget'];signal=getattr(getattr(window,name),row['signal'])
  if name=='timing_scenario':signal.connect(lambda name=name:signal_record(name,window.timing_scenario.toPlainText()))
  else:signal.connect(lambda value,name=name:signal_record(name,value))
def three_texts():
 global explicit_texts,phase,request
 if window.damage_result is None:return {'applicable':False,'reason':'Existing error or natural early return','visible_status':window.damage_text.toPlainText()}
 phase='three_texts';request='explicit_formatter';before=dict(counts);all_before=dict(all_entries)
 raw=window.damage_result['scenario'];result=window.damage_result['result'];raw_before=flat_native(raw);result_before=flat_native(result)
 strings={'estimate':format_estimate(result),'default':format_report(result),'technical':format_report(result,technical=True)};explicit_texts+=3
 assert strings['estimate']==strings['default']
 displayed=json.dumps(window.damage_result,ensure_ascii=False,indent=2) if window.raw_damage.isChecked() else strings['technical' if window.damage_technical.isChecked() else 'default']
 assert window.damage_text.toPlainText()==displayed.replace(chr(160),' ')
 assert flat_native(raw)==raw_before and flat_native(result)==result_before
 return {'applicable':True,'strings':strings,'requests':3,'actual_entries':delta(before,counts),'all_project_entries':delta(all_before,all_entries),'full_native_preserved':True}
def result_capture():return {'live_reference_alias_check':actual_live_alias_probe(),'damage_result':snapshot(window.damage_result),'UI':ui_snapshot(),'visible_status':window.damage_text.toPlainText(),'three_texts':three_texts()}
def outcomes(rows):return {key:sum(row['outcome']==key for row in rows) for key in ('returned_dict','raised_exception','returned_none_or_unobserved_unwind')}
def validate(step,rows,entered,require_callback=True):
 expected=step.get('expected',{});kind=expected.get('kind','numerical_result')
 if require_callback:assert entered.get('MainWindow.calculate',0)>0,('No actual MainWindow.calculate callback',step['id'])
 if kind=='JSON_error_before_numerical_API':assert not rows and window.damage_result is None and window.damage_text.toPlainText()==expected['message']
 elif kind=='natural_early_return':assert not rows and window.damage_result is None and expected['text_contains'] in window.damage_text.toPlainText()
 else:
  assert type(window.damage_result) is dict and (not rows or all(row['outcome']=='returned_dict' for row in rows)),window.damage_text.toPlainText()
 for row in rows:assert row['caller_unchanged'] is True
 return kind
def close_window():
 global window,phase,request
 if window is None:return
 phase='close';request='real_window_close';external_idle();before=filesystem(active_folder)
 window.close();application.processEvents();window.deleteLater();application.processEvents();window=None
 assert filesystem(active_folder)==before

def fresh_window(fixture):
 global window,active_folder,account_path,run_path,window_id,fresh_windows,phase,request
 close_window();fresh_windows+=1;window_id='public-focused095-window-'+str(fresh_windows)
 active_folder=Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-focused095-')))
 account_path=active_folder/'account.json';run_path=active_folder/'run.json'
 account_path.write_text(json.dumps(fixture,ensure_ascii=False,allow_nan=False),encoding='utf-8')
 run_path.write_text(json.dumps(PLAN['public_run_initial'],ensure_ascii=False,allow_nan=False),encoding='utf-8')
 module.OPERATOR_STATE=account_path;module.RUN_STATE=run_path;module.SETTINGS=active_folder/'settings.json'
 module.DesktopBackend=lambda _path,callback:original_backend(active_folder/'chat',callback)
 phase='startup';request='real_MainWindow_constructor';before=dict(counts);all_before=dict(all_entries);api_start=len(API);prepared_start=len(PREPARED);call_start=len(CALLS)
 window=module.MainWindow();window.show();application.processEvents()
 assert type(window.run) is RunState and window.operator_observations is window.account_cache.records and window.isVisible()
 assert not list_game_windows();external_idle()
 startup={'actual_entries':delta(before,counts),'all_project_entries':delta(all_before,all_entries),'API_sequences':[r['sequence'] for r in API[api_start:]],'prepared_sequences':[r['sequence'] for r in PREPARED[prepared_start:]],'UI':ui_snapshot()}
 phase='common_controls';request='actual_existing_controls'
 window.centralWidget().setCurrentIndex(1);window.auto_relics.setChecked(False);window.frame_timing.setChecked(False);window.limit_window.setChecked(False);window.target_enemy.setCurrentIndex(0);window.target_buff_test.setChecked(False);window.raw_damage.setChecked(False);window.damage_technical.setChecked(False);window.timing_scenario.clear();window.relic_context.clear();application.processEvents()
 assert all(row['all_outputs_and_affected_controls_exist'] for row in CALLS[call_start:] if row['key']=='MainWindow.calculate')
 observe_signals();return startup

def action(step):
 global phase,request
 what=step['action'];phase='automatic_action';request=what
 if what=='account_observation':
  data=clone(step['observation']);window.apply_operator_observation(data,data['captured_at']);application.processEvents()
  assert window.operator.currentData()==data['id'] and window.skill.currentData()==step['skill']
  assert all(flat_native(window.account_cache.records[data['id']]['fields'].get(k))==flat_native(v) for k,v in data['fields'].items())
 elif what=='run_observation':
  data=clone(step['observation']);assert window.apply_run_observation(data,step['captured_at']);application.processEvents()
  assert window.current_operator_state()['scope']=='run'
 elif what=='level':assert window.level.value()!=step['value'];window.level.setValue(step['value'])
 elif what=='technical':assert window.damage_technical.isChecked()!=step['value'];window.damage_technical.setChecked(step['value'])
 elif what=='raw':assert window.raw_damage.isChecked()!=step['value'];window.raw_damage.setChecked(step['value'])
 elif what=='use_run_training':assert window.use_run_training.isChecked()!=step['value'];window.use_run_training.setChecked(step['value'])
 elif what=='timing_text':assert window.timing_scenario.toPlainText()!=step['value'];window.timing_scenario.setPlainText(step['value'])
 elif what=='overview':assert window.operator_choices.select_branch('__overview__')
 elif what=='select':
  assert window.select_operator(step['owner']);index=window.skill.findData(step['skill']);assert index>=0;window.skill.setCurrentIndex(index)
 else:raise AssertionError(('Unknown fixed source-supported action',what))
 application.processEvents()


def mutable_ids(value):
 found=set();todo=[value];seen=set()
 while todo:
  item=todo.pop();kind=type(item)
  if kind not in (dict,list,tuple) or id(item) in seen:continue
  seen.add(id(item))
  if kind in (dict,list):found.add(id(item))
  todo.extend(list(item.keys())+list(item.values()) if kind is dict else item)
 return found

def actual_live_alias_probe():
 global phase,request,live_cached_supplement_baseline_snapshot
 value=window.damage_result
 if value is None or REFERENCE_KEY not in value['result']['report']:return {'applicable':False}
 saved_phase,saved_request=phase,request;phase='live_module_reference_alias_probe';request='actual_cache_and_independent_prepared_report_rebuild'
 before_counts=dict(counts);before_all=dict(all_entries);api_before=len(API);prepared_before=len(PREPARED)
 try:
  from rouge.module_source_reference import _reference_data
  from rouge.reporting import build_report
  result=value['result'];reference=result['report'][REFERENCE_KEY];raw=value['scenario']
  public_before=flat_native(value);durable_before=durable_snapshot()
  catalog_live=module.catalog();supplement_live=_reference_data();supplement_before=flat_native(supplement_live)
  if live_cached_supplement_baseline_snapshot is None:live_cached_supplement_baseline_snapshot=snapshot(supplement_live)
  assert supplement_before==live_cached_supplement_baseline_snapshot['native']
  supplement_native_sha256=digest(json.dumps(supplement_before,ensure_ascii=False,allow_nan=False).encode('utf-8'))
  old_values=[raw]+[v for key,v in result.items() if key!='report']+[v for key,v in result['report'].items() if key not in (REFERENCE_KEY,'sections')]+[b for b in result['report']['sections'] if b['id']!=SECTION_ID]
  current_ids=mutable_ids(reference);catalog_ids=mutable_ids(catalog_live);supplement_ids=mutable_ids(supplement_live)
  assert not current_ids.intersection(mutable_ids(old_values)) and not current_ids.intersection(catalog_ids) and not current_ids.intersection(supplement_ids),'Actual live reference cannot alias caller/old native/catalog/live cached supplement'
  prior_checks=0;cached_same_result=0
  for earlier in live_reference_history:
   if earlier['kind']=='live_window_reference' and earlier['live_owner'] is value:
    cached_same_result+=1;continue
   assert not current_ids.intersection(mutable_ids(earlier['reference'])),'Distinct previously held live/fresh report cannot share new mutable reference records'
   prior_checks+=1
  assert PREPARED and PREPARED[-1]['outcome']=='returned_prepared_tuple' and PREPARED[-1]['window']==window_id
  prepared_record=PREPARED[-1]
  assert prepared_record['caller_before']['native']==flat_native({'scenario':raw}),'Use actual matching API original caller; no hand-built prepared scenario'
  prepared=native_inverse(prepared_record['returned']['native']);assert type(prepared) is tuple and len(prepared)==4
  actual_prepared_scenario=prepared[0];prepared_before_graph=flat_native(prepared)
  fresh_report=build_report(actual_prepared_scenario,result);fresh_reference=fresh_report[REFERENCE_KEY]
  assert flat_native(fresh_reference)==flat_native(reference),'Independently rebuilt source reference must retain exact current selection/source/qualification/links'
  fresh_ids=mutable_ids(fresh_reference)
  fresh_old=[v for key,v in fresh_report.items() if key not in (REFERENCE_KEY,'sections')]+[b for b in fresh_report['sections'] if b['id']!=SECTION_ID]
  assert not fresh_ids.intersection(current_ids|catalog_ids|supplement_ids|mutable_ids(old_values)|mutable_ids(fresh_old)|mutable_ids(prepared)), 'Fresh report reference must be detached from live/current/cache/prepared/old objects'
  for earlier in live_reference_history:assert not fresh_ids.intersection(mutable_ids(earlier['reference']))
  assert flat_native(value)==public_before and flat_native(supplement_live)==supplement_before and flat_native(prepared)==prepared_before_graph
  assert_unchanged(durable_before,durable_snapshot())
  assert len(API)==api_before and len(PREPARED)==prepared_before,'Read-only report rebuild must add zero numerical/preparation API entries'
  live_reference_history.extend([{'kind':'live_window_reference','live_owner':value,'reference':reference},{'kind':'independent_fresh_report_reference','live_owner':fresh_report,'reference':fresh_reference}])
  return {'applicable':True,'actual_live_reference_caller_old_native_catalog_mutable_id_sets_disjoint':True,'actual_live_cached_supplement_mutable_id_set_disjoint':True,'independent_fresh_report_reference_detached_and_exact':True,'independent_fresh_reference':snapshot(fresh_reference),'live_cached_supplement_native_before_sha256':supplement_native_sha256,'live_cached_supplement_native_after_sha256':supplement_native_sha256,'prior_distinct_live_or_fresh_references_checked':prior_checks,'same_cached_live_result_references_retained':cached_same_result,'prepared_call_sequence':prepared_record['sequence'],'actual_additional_API_entries':len(API)-api_before,'actual_additional_prepared_entries':len(PREPARED)-prepared_before,'live_value_cached_supplement_prepared_and_durable_unchanged':True,'actual_entries':delta(before_counts,counts),'all_project_entries':delta(before_all,all_entries),'phase':phase,'request':request}
 finally:phase,request=saved_phase,saved_request

def original_reference_checks(raw,result,reference,block):
 assert list(reference)==['schema_version','operator_id','module_id','module_name','module_type','module_level','source','raw_metadata','raw_owner','raw_phase','cultivation_qualification','candidate_qualifications','existing_coverage']
 profile_data=CATALOG['operators'][raw['operator']];selected=next(m for m in profile_data['modules'] if m['id']==raw['module_id'])
 assert reference['operator_id']==profile_data['id'] and reference['module_name']==selected['name'] and reference['module_type']==selected['type']
 ref_ids=mutable_ids(result['report'][REFERENCE_KEY]);old_values=[raw]+[v for key,v in result.items() if key!='report']+[v for key,v in result['report'].items() if key not in (REFERENCE_KEY,'sections')]+[b for b in result['report']['sections'] if b['id']!=SECTION_ID]
 assert not ref_ids.intersection(mutable_ids(old_values)),'Native graph must preserve separation from caller and old native fields/sections'
 mid=raw.get('module_id');stage=result['estimate']['training']['module_level'];training=result['estimate']['training']
 assert reference['module_id']==mid and reference['module_level']==stage and reference['schema_version']==1
 metadata=ORIGINAL_MODULES['equipDict'][mid];raw_metadata={key:value for key,value in metadata.items() if key in INTERFACE['raw_metadata_keys_in_original_order']}
 assert flat_native(reference['raw_metadata'])==flat_native(raw_metadata),'Full ordered raw metadata including nulls'
 original=ORIGINAL_BATTLE[mid]['phases'][stage-1]
 expected_phase={key:original[key] for key in INTERFACE['raw_phase_key_order']}
 assert flat_native(reference['raw_phase'])==flat_native(expected_phase),'Full ordered parts/candidates/attributes/tokenBB/valueStr/overrideDescripton exact original'
 owner=reference['raw_owner'];owner_id=owner['charEquip_owner_id'];membership=ORIGINAL_MODULES['charEquip'][owner_id]
 assert flat_native(owner['charEquip'])==flat_native(membership) and membership[owner['membership_index']]==mid
 assert owner_id==(metadata['tmplId'] or metadata['charId']),'Lawful raw tmplId/charEquip owner, not forced shared charId'
 assert reference['source']['commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
 assert reference['source']['files']['battle_equip_table']['sha256']==BINDING['original_battle']['sha256'] and reference['source']['files']['uniequip_table']['sha256']==BINDING['original_modules']['sha256']
 assert reference['source']['selectors']['phase']==f'battle_equip_table.{mid}.phases[{stage-1}]'
 qualification=reference['cultivation_qualification']
 assert flat_native(qualification['effective_training'])==flat_native({key:training[key] for key in ('elite','level','potential')})
 assert qualification['uses_unconfirmed_preview_conditions']==bool(raw.get('unconfirmed_training')) and qualification['scope']=='supplied_cultivation_only'
 assert all(qualification[key] is None for key in ('account_mission_unlock','actual_equipment','mode_or_map_applicability','native_attachment')) and qualification['new_reference_adds_arithmetic'] is False
 module_gate=training['elite']>=int(metadata['unlockEvolvePhase'][-1]) and training['level']>=metadata['unlockLevel']
 assert qualification['module_cultivation_gate_met'] is module_gate
 selector=reference['source']['selectors']['phase'];candidate_keys=[]
 for i,part in enumerate(original['parts']):
  for bundle in ('addOrOverrideTalentDataBundle','overrideTraitDataBundle'):
   for j,candidate in enumerate((part.get(bundle) or {}).get('candidates') or ()):
    key=f'{selector}.parts[{i}].{bundle}.candidates[{j}]';candidate_keys.append(key);actual=reference['candidate_qualifications'][key]
    condition=candidate['unlockCondition'];phase=int(condition['phase'][-1]);elite=training['elite'];level=training['level']
    phase_met=phase<=elite;level_met=phase<elite or condition['level']<=level;potential_met=candidate.get('requiredPotentialRank',0)<=training['potential']-1;candidate_gate=phase_met and level_met and potential_met
    assert flat_native(actual)==flat_native({'phase_gate_met':phase_met,'level_gate_met':level_met,'potential_gate_met':potential_met,'candidate_cultivation_gate_met':candidate_gate,'module_cultivation_gate_met':module_gate,'eligible_under_supplied_cultivation':module_gate and candidate_gate,'actual_activation':None})
 assert list(reference['candidate_qualifications'])==candidate_keys
 for link in reference['existing_coverage']['report_sections']:
  target=pointer(result,link['path']);assert target['id']==link['section_id'] and target['title']==link['title'] and target['id']!=SECTION_ID
 for path in reference['existing_coverage']['native_paths']:assert isinstance(path,str) and pointer(result,path)
 assert block['title']==SECTION_TITLE and block['metrics']==[] and len(block['notes'])>=5
 assert any(reference['module_name'] in note for note in block['notes']) and any('原件培养门槛' in note for note in block['notes'])
 return {'raw_original_metadata_phase_owner_exact':True,'full_candidates_unfiltered':len(candidate_keys),'qualification_scope':'supplied_cultivation_only','unknown_equipment_attachment_preserved':True,'existing_coverage_paths_valid':True}

def remove_only_additions(raw,result,check_reference=True):
 # Callers supply independent native_inverse graphs, never live UI/product data.
 # Mutate only this decoded report; keep scenario/result and internal shared aliases.
 report=result['report'];matches=[(i,b) for i,b in enumerate(report['sections']) if b['id']==SECTION_ID]
 if not raw.get('module_id'):
  assert REFERENCE_KEY not in report and not matches;return result,None,None
 assert REFERENCE_KEY in report and len(matches)==1 and matches[0][0]==len(report['sections'])-1
 reference=report[REFERENCE_KEY];block=report['sections'][-1]
 assert len({b['id'] for b in report['sections']})==len(report['sections']) and block['metrics']==[]
 source_check=original_reference_checks(raw,result,reference,block) if check_reference else None
 # Qualification and alias/coverage checks run on the complete decoded graph first.
 report.pop(REFERENCE_KEY);report['sections'].pop()
 return result,reference,source_check

def strip_exact_text_addition(full,old,reference,technical):
 if reference is None:assert full==old;return {'added':False,'full_old_text_exact':True}
 without_tail=full;tail=None
 if technical:
  tail=TECHNICAL_DELIMITER+json.dumps(reference,ensure_ascii=False,indent=2)
  assert full.endswith(tail) and full.count(TECHNICAL_DELIMITER)==1,'Exact final raw JSON bypasses phrase; no normalized source strings'
  without_tail=full[:-len(tail)]
 else:assert TECHNICAL_DELIMITER not in full
 marker='\n\n【'+SECTION_TITLE+'】\n';assert without_tail.count(marker)==1
 start=without_tail.index(marker);extra=len(without_tail)-len(old);assert extra>len(marker)
 block=without_tail[start:start+extra];assert block.startswith(marker) and '\n• ' in block
 assert without_tail[:start]+without_tail[start+extra:]==old,'Only one exact notes-only source block may differ; every old character stays exact'
 return {'added':True,'exact_new_block':block,'exact_technical_tail':tail,'full_old_text_exact':True}

def compare_capture(actual,baseline,label):
 global phase,request
 actual_value=native_inverse(actual['damage_result']['native']);old_value=native_inverse(baseline['damage_result']['native'])
 if actual_value is None or old_value is None:
  assert actual_value is old_value is None and actual['visible_status']==baseline['visible_status'] and actual['three_texts']==baseline['three_texts']
  proof={'full_native_exact':True,'applicable_texts':False}
 else:
  raw=actual_value['scenario'];result=actual_value['result'];reduced,reference,source_check=remove_only_additions(raw,result)
  assert reduced is result and flat_native(actual_value)==flat_native(old_value),'Every old native type/key/order/alias/float and old report section exact'
  source_text_checks={key:strip_exact_text_addition(actual['three_texts']['strings'][key],baseline['three_texts']['strings'][key],reference,key=='technical') for key in ('estimate','default','technical')}
  phase='baseline_existing_formatter_equivalence';request='precisely_reduced_report_formatter';before=dict(counts);before_all=dict(all_entries)
  untouched={'estimate':format_estimate(reduced),'default':format_report(reduced),'technical':format_report(reduced,technical=True)}
  assert untouched==baseline['three_texts']['strings']
  proof={'full_native_except_exact_report_additions':True,'raw_original_source_checks':source_check,'text_additions':source_text_checks,'actual_reduced_formatter_entries':delta(before,counts),'actual_reduced_all_project_entries':delta(before_all,all_entries)}
 actual_UI={k:v for k,v in actual['UI'].items() if k not in ('damage_result','visible_text')};old_UI={k:v for k,v in baseline['UI'].items() if k not in ('damage_result','visible_text')}
 assert flat_native(actual_UI)==flat_native(old_UI),'All UI selection/actual cultivation/preview labels/source priority exact'
 baseline_checks.append({'step':current,'label':label,**proof});return proof

def compare_actual_entries(actual_sequences,old_sequences,collection,old_collection):
 assert len(actual_sequences)==len(old_sequences),'Actual API/prepared phase count must match fresh baseline; no click-count inference'
 current_rows={row['sequence']:row for row in collection}
 for sequence,old_sequence in zip(actual_sequences,old_sequences):
  actual=current_rows[sequence];old=old_collection[old_sequence]
  assert actual['key']==old['key'] and actual['step']==old['step'] and actual['phase']==old['phase'] and actual['request']==old['request'] and actual['outcome']==old['outcome']
  assert actual['caller_before']['native']==old['caller_before']['native'] and actual['caller_after']['native']==old['caller_after']['native']
  assert actual.get('exception_events')==old.get('exception_events')
  if actual.get('returned'):
   value=native_inverse(actual['returned']['native']);old_value=native_inverse(old['returned']['native'])
   if actual['key']=='calculate_damage':
    raw=native_inverse(actual['caller_before']['native'])['scenario'];reduced,ref,source_check=remove_only_additions(raw,value)
    assert flat_native(reduced)==flat_native(old_value)
   else:assert actual['returned']['native']==old['returned']['native'],'Exact prepared scenario/attributes/relic/run resolution and aliases'

def compare_state(record):
 baseline=BASELINE_STATES[record['id']];assert record['planned']['native']==baseline['planned']['native'] and record['window_after']==baseline['window_after']
 record['baseline_equivalence']={'automatic':compare_capture(record['automatic'],baseline['automatic'],'automatic')}
 for key in ('automatic','manual'):
  if key not in record:continue
  if key=='manual':record['baseline_equivalence'][key]=compare_capture(record[key],baseline[key],key)
  compare_actual_entries(record[key].get('API_sequences',[]),baseline[key].get('API_sequences',[]),API,BASELINE_API)
  compare_actual_entries(record[key].get('prepared_sequences',[]),baseline[key].get('prepared_sequences',[]),PREPARED,BASELINE_PREPARED)
 if 'startup' in record:
  compare_actual_entries(record['startup']['API_sequences'],baseline['startup']['API_sequences'],API,BASELINE_API)
  compare_actual_entries(record['startup']['prepared_sequences'],baseline['startup']['prepared_sequences'],PREPARED,BASELINE_PREPARED)
 assert record['durable_after']==baseline['durable_after'],'Cross-version complete deterministic public state/file bytes exact'

def capture_png(name):
 global phase,request
 phase='actual_PNG_probe';request='root_actual_Qt_screenshot';before=snapshot(window.damage_result)
 window.resize(1260,980)
 anchor='【所选模组原件追溯】' if 'technical' in name else '【'+SECTION_TITLE+'】'
 cursor=window.damage_text.document().find(anchor);assert not cursor.isNull();window.damage_text.setTextCursor(cursor);window.damage_text.ensureCursorVisible();application.processEvents()
 path=OUT/name;assert window.grab().save(str(path))
 assert snapshot(window.damage_result)['native']==before['native'],'Visibility probe preserves complete result'
 row={'file':name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes()),'window':window_id,'step':current,'anchor':anchor,'raw_damage':window.raw_damage.isChecked(),'technical':window.damage_technical.isChecked(),'visible_status':window.damage_text.toPlainText(),'UI':ui_snapshot(),'actual_view_by_root_pending':True};pngs.append(row);return row

def run_step(step):
 global phase,request,current,explicit_buttons
 current=step['id'];phase='before_probe';request='explicit_probe';before_all=dict(counts)
 record={'id':current,'planned':snapshot(step),'passed':False,'window_before':window_id,'before_UI':ui_snapshot(),'durable_before':durable_snapshot()};states.append(record)
 if step['action']=='fresh_window':
  record['startup']=fresh_window(step['fixture']);record['automatic']=result_capture();record['window_after']=window_id;record['durable_after']=durable_snapshot();record['passed']=True
 else:
  auto_before=dict(counts);auto_all=dict(all_entries);api_start=len(API);prepared_start=len(PREPARED);signal_start=len(signals);qt_start=len(qt_exceptions)
  action(step);auto_entries=delta(auto_before,counts);auto_all_entries=delta(auto_all,all_entries);auto_rows=API[api_start:]
  assert len(qt_exceptions)==qt_start
  render_only=step['action'] in ('technical','raw')
  if render_only:assert not auto_rows and auto_entries.get('MainWindow.calculate',0)==0 and auto_entries.get('MainWindow.render_damage',0)>0
  outcome=validate(step,auto_rows,auto_entries,not render_only)
  if not render_only and outcome=='numerical_result':assert auto_rows,'Numerical automatic callback must actually enter API'
  automatic=result_capture();automatic.update(actual_entries=auto_entries,all_project_entries=auto_all_entries,API_sequences=[r['sequence'] for r in auto_rows],prepared_sequences=[r['sequence'] for r in PREPARED[prepared_start:]],signals=clone(signals[signal_start:]),outcome=outcome)
  record['automatic']=automatic;baseline_durable=durable_snapshot();record['durable_after_automatic']=baseline_durable
  if step['action'] not in ('account_observation','run_observation'):assert_unchanged(record['durable_before'],baseline_durable)
  phase='manual_button';request='actual_compute_button';manual_before=dict(counts);manual_all=dict(all_entries);manual_api_start=len(API);manual_prepared_start=len(PREPARED);explicit_buttons+=1
  button=next(x for x in window.findChildren(QPushButton) if x.text()=='计算属性与技能预估');button.click();application.processEvents()
  manual_entries=delta(manual_before,counts);manual_rows=API[manual_api_start:]
  assert len(qt_exceptions)==qt_start and validate(step,manual_rows,manual_entries)==outcome
  manual=result_capture();manual.update(actual_entries=manual_entries,all_project_entries=delta(manual_all,all_entries),API_sequences=[r['sequence'] for r in manual_rows],prepared_sequences=[r['sequence'] for r in PREPARED[manual_prepared_start:]],outcome=outcome)
  record['manual']=manual
  assert automatic['damage_result']['native']==manual['damage_result']['native'] and automatic['visible_status']==manual['visible_status'] and automatic['three_texts'].get('strings')==manual['three_texts'].get('strings')
  if auto_rows and manual_rows:
   assert auto_rows[-1]['caller_before']['native']==manual_rows[-1]['caller_before']['native']
   assert auto_rows[-1].get('returned',{}).get('native')==manual_rows[-1].get('returned',{}).get('native')
  record['full_native_and_three_texts_equal']=True;record['actual_outcome']=outcome;record['window_after']=window_id;record['durable_after']=durable_snapshot();assert_unchanged(baseline_durable,record['durable_after']);record['passed']=True
 compare_state(record)
 if step.get('PNG'):record['actual_PNG']=capture_png(step['PNG'])
 external_idle();record['actual_entries_including_probes_and_formatters']=delta(before_all,counts);checks.append({'id':current,'passed':True,'action':step['action']})
 if len(states)%5==0 or step['action']=='fresh_window':checkpoint()

try:
 phase='runtime_project_imports';request='root_sole_Wine_imports';sys.setprofile(profile);sys.settrace(trace);sys.excepthook=qt_hook
 from PySide6.QtCore import Qt
 from PySide6.QtWidgets import QApplication,QCheckBox,QPushButton
 import rouge.app as module
 from rouge.run_state import RunState
 from rouge.capture import list_game_windows
 from rouge.estimate import format_estimate
 from rouge.reporting import format_report
 application=QApplication([]);application.setQuitOnLastWindowClosed(False);original_backend=module.DesktopBackend
 for step in PLAN['steps']:run_step(step)
 close_window()
 assert len(states)==PLAN['counts']['states_planned'] and fresh_windows==2 and explicit_buttons==PLAN['counts']['manual_button_requests_planned'] and len(pngs)==3
 assert len(API)==len(BASELINE['API_entries']) and len(PREPARED)==len(BASELINE['prepared_entries'])
 compare_actual_entries([r['sequence'] for r in API],[r['sequence'] for r in BASELINE['API_entries']],API,BASELINE_API)
 compare_actual_entries([r['sequence'] for r in PREPARED],[r['sequence'] for r in BASELINE['prepared_entries']],PREPARED,BASELINE_PREPARED)
 assert not pending and not caller_objects and not qt_exceptions
 assert all(counts.get(key,0)==0 for key in ('GameCapture.capture','GameCapture.next_frame','GameCapture.connect','MainWindow.connect_game','MainWindow.sample_now','MainWindow.sample_received','MainWindow.send_chat','MainWindow.desktop_request','MainWindow.bind_desktop'))
 receipt['passed']=True;receipt['workflow_complete']=True
except BaseException as error:
 receipt['failure']={'type':type(error).__name__,'message':str(error),'step':current,'traceback':traceback.format_exc()}
 if window is not None:
  try:receipt['failure_UI']=ui_snapshot()
  except Exception as evidence_error:receipt['failure_UI_error']=str(evidence_error)
finally:
 try:close_window()
 except Exception as error:receipt['passed']=False;receipt['workflow_complete']=False;receipt['close_error']={'type':type(error).__name__,'message':str(error)}
 sys.setprofile(previous_profile);sys.settrace(previous_trace);sys.excepthook=previous_excepthook
 after={rel:digest((ROOT/rel).read_bytes()) for rel in SOURCE_HASHES};receipt['source_sha256_after']=after;receipt['source_drift']=[rel for rel in SOURCE_HASHES if after[rel]!=SOURCE_HASHES[rel]]
 if receipt['source_drift']:receipt['passed']=False;receipt['workflow_complete']=False
 receipt.update(actual_PNGs=pngs,baseline_equivalence_checks=len(baseline_checks),actual_function_entries=counts,all_rouge_main_thread_entries=all_entries,all_rouge_entries_by_phase_and_request=entries_by_scope,states=len(states),fresh_windows=fresh_windows,explicit_button_requests=explicit_buttons,explicit_three_text_requests=explicit_texts,actual_API_outcomes=outcomes(API),prepared_entries=len(PREPARED),elapsed_seconds=round(time.perf_counter()-started,3))
 checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');folders.close()
 print(json.dumps({'passed':receipt['passed'],'states':len(states),'records':receipt['records'],'failure':receipt.get('failure')},ensure_ascii=False));sys.exit(0 if receipt['passed'] else 1)
