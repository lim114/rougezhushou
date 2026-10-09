"""Root-only fresh actual94 baseline for source-qualified focused095 UI changes.
Source preparation executes zero project imports, codecs, Qt, APIs or tests.
"""
import gzip,hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
from contextlib import ExitStack
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat')
EXPECTED_GUARD_SHA256='259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'
GUARD=Path(__file__).with_name('wine-module-report-baseline094-source.json')
assert hashlib.sha256(GUARD.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA256
SOURCE=json.loads(GUARD.read_text(encoding='utf-8'));SOURCE_HASHES=SOURCE['source_sha256_after']
assert SOURCE['passed'] is True and len(SOURCE_HASHES)==732
for rel,expected_hash in SOURCE_HASHES.items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected_hash,('actual94 source before project import',rel)
COMPLETED94=ROOT/'verification/sections/094.json'
assert hashlib.sha256(COMPLETED94.read_bytes()).hexdigest()=='55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5'
completed94=json.loads(COMPLETED94.read_text(encoding='utf-8'))
assert completed94['passed'] is True and completed94['workflow_complete'] is True
CLOSURE94=Path(r'Z:\workspace\.continuation\section094-archived-working-tree-closure.json')
assert hashlib.sha256(CLOSURE94.read_bytes()).hexdigest()=='613d5956762bd7b0a19d15c15173df698890a8545a8d0e14253086aaf728f806'
PLAN_PATH=Path(__file__).with_name('wine-module-report-shared095-plan.json')
assert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a'
PLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))
RECEIPT=OUT/'wine-module-report-baseline-094-for095.json';ARCHIVE=OUT/'wine-module-report-baseline-094-for095-records.json.gz'
assert not RECEIPT.exists() and not ARCHIVE.exists(),'Preserve prior evidence; never replay a successful prefix'
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

counts={};all_entries={};entries_by_scope={};API=[];PREPARED=[];CALLS=[];pending={};caller_objects={};signals=[];states=[];checks=[];qt_exceptions=[]
phase='before-import';request='none';current='before-first-window';window_id=None
window=None;application=None;active_folder=None;account_path=None;run_path=None
explicit_buttons=0;explicit_texts=0;fresh_windows=0;checkpoint_pauses=0
started=time.perf_counter();folders=ExitStack()
previous_profile=sys.getprofile();previous_trace=sys.gettrace();previous_excepthook=sys.excepthook
CONTROL_NAMES=tuple(row['widget'] for row in PLAN['controls'])
receipt={'format_version':1,'passed':False,'workflow_complete':False,'completed_section_increment':0,
 'kind':'FRESH_ACTUAL94_FOCUSED095_BASELINE_NOT_SECTION_COMPLETION','source_guard_sha256':EXPECTED_GUARD_SHA256,
 'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
 'actual94_receipt_sha256':'55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5',
 'actual94_closure_sha256':'613d5956762bd7b0a19d15c15173df698890a8545a8d0e14253086aaf728f806',
 'source_sha256_before':SOURCE_HASHES,'checks':checks,'private_state_isolated':True,'scope_limits':PLAN['scope_limits'],
 'native_codec':'flat-typed-graph-v1; eight functions byte-exact from frozen final094 plus separate raw-file-bytes-evidence-v1',
 'codec_preparation_executed':False,'old94_matrix_replayed':False,'game_capture_requests':0,'chat_requests':0,
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
 payload={'format_version':1,'schema':'focused-module-report-baseline-v1','native_schema':'flat-typed-graph-v1','current_step':current,'passed':receipt['passed'],'states':states,'checks':checks,'signals':signals,'API_entries':API,'prepared_entries':PREPARED,'targeted_calls':CALLS,'actual_python_entries':counts,'all_rouge_main_thread_entries':all_entries,'all_rouge_entries_by_phase_and_request':entries_by_scope,'Qt_slot_exceptions':qt_exceptions,'explicit_buttons':explicit_buttons,'explicit_three_text_requests':explicit_texts,'fresh_windows':fresh_windows,'stdlib_checkpoint_pauses':checkpoint_pauses}
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
def result_capture():return {'damage_result':snapshot(window.damage_result),'UI':ui_snapshot(),'visible_status':window.damage_text.toPlainText(),'three_texts':three_texts()}
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
 assert len(states)==PLAN['counts']['states_planned'] and fresh_windows==2 and explicit_buttons==PLAN['counts']['manual_button_requests_planned']
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
 receipt.update(actual_function_entries=counts,all_rouge_main_thread_entries=all_entries,all_rouge_entries_by_phase_and_request=entries_by_scope,states=len(states),fresh_windows=fresh_windows,explicit_button_requests=explicit_buttons,explicit_three_text_requests=explicit_texts,actual_API_outcomes=outcomes(API),prepared_entries=len(PREPARED),elapsed_seconds=round(time.perf_counter()-started,3))
 checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');folders.close()
 print(json.dumps({'passed':receipt['passed'],'states':len(states),'records':receipt['records'],'failure':receipt.get('failure')},ensure_ascii=False));sys.exit(0 if receipt['passed'] else 1)
