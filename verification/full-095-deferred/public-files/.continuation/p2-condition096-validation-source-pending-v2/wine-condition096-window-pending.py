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
if MODE=='candidate':assert SOURCE_HASHES['rouge/app.py']==PLAN['presentation_partition']['candidate_app_sha256'],'Presentation classification applies only to the exact frozen candidate app'
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


BASELINE=None;BASELINE_STATES={};BASELINE_API={};BASELINE_PREPARED={}
if MODE=='candidate':
    BASELINE_RECEIPT=json.loads(bound_file(BINDING['actual_baseline_receipt']).decode('utf-8'));assert BASELINE_RECEIPT['passed'] is True and BASELINE_RECEIPT['workflow_complete'] is True and BASELINE_RECEIPT['source_drift']==[]
    assert BASELINE_RECEIPT['plan_sha256']==BINDING['validation_plan']['sha256']
    assert bound_file(BINDING['actual_baseline_shell_status']) in (b'0\n',b'0\r\n')
    assert BINDING['actual_baseline_saved_review'] is not None
    bound_file(BINDING['actual_baseline_saved_review'])
    assert any(row['path']==BINDING['actual_baseline_saved_review']['path'] for row in BINDING['required_actual_prerequisite_gates'])
    BASELINE=json.loads(gzip.decompress(bound_file(BINDING['actual_baseline_records'])).decode('utf-8'));assert BASELINE['passed'] is True
    assert [r['id'] for r in BASELINE['states']]==[r['id'] for r in PLAN['steps']]
    BASELINE_STATES={r['id']:r for r in BASELINE['states']};BASELINE_API={r['sequence']:r for r in BASELINE['API_entries']};BASELINE_PREPARED={r['sequence']:r for r in BASELINE['prepared_entries']}
counts={};all_entries={};entries_by_scope={};presentation_entries={};constructor_import_entries={};constructor_import_events=[];API=[];PREPARED=[];CALLS=[];pending={};caller_objects={};signals=[];states=[];checks=[];qt_exceptions=[];pngs=[]
phase='before-import';request='none';current='before-first-window';window_id=None
window=None;application=None;active_folder=None;account_path=None;run_path=None
explicit_buttons=0;explicit_texts=0;fresh_windows=0;checkpoint_pauses=0
started=time.perf_counter();folders=ExitStack();previous_profile=sys.getprofile();previous_trace=sys.gettrace();previous_excepthook=sys.excepthook
CONTROL_NAMES=tuple(row['widget'] for row in PLAN['controls'])
RECEIPT=OUT/'wine-condition096-receipt.json';ARCHIVE=OUT/'wine-condition096-records.json.gz'
receipt={'format_version':1,'kind':'ACTUAL_CONDITION096_FOCUSED_WINDOW','mode':MODE,'passed':False,'workflow_complete':False,'completed_section_increment':0,'source_guard_sha256':BINDING['actual_source_guard']['sha256'],'plan_sha256':BINDING['validation_plan']['sha256'],'private_state_isolated':True,'scope_limits':PLAN['scope_limits'],'runner_sha256':digest(Path(__file__).read_bytes())}
def presentation_stack(frame):
    cursor=frame
    while cursor:
        if MODE=='candidate' and path_of(cursor).endswith('/rouge/app.py'):
            for site in (PLAN['presentation_partition']['method'],PLAN['presentation_partition']['new_signal_lambda']):
                if cursor.f_code.co_qualname==site['qualname'] and cursor.f_code.co_firstlineno==site['co_firstlineno']:return True
        cursor=cursor.f_back
    return False
def path_of(frame):return frame.f_code.co_filename.replace('\\','/').lower()
def exact_constructor_import(frame):
    site=PLAN['presentation_partition']['constructor_module_import']
    if MODE!='candidate' or not path_of(frame).endswith('/'+site['relative_path']) or frame.f_code.co_qualname!=site['qualname']:return None
    if phase!=site['phase'] or request!=site['request']:return None
    cursor=frame.f_back
    while cursor:
        if path_of(cursor).endswith('/rouge/app.py') and cursor.f_code.co_qualname==site['caller_qualname'] and cursor.f_lineno==site['caller_lineno']:
            return {'step':current,'window':window_id,'phase':phase,'request':request,'module':site['relative_path'],'module_qualname':frame.f_code.co_qualname,'caller_qualname':cursor.f_code.co_qualname,'caller_lineno':cursor.f_lineno}
        cursor=cursor.f_back
    return None


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


def qt_hook(kind,error,tb):qt_exceptions.append({'step':current,'phase':phase,'type':kind.__name__,'message':str(error),'traceback':''.join(traceback.format_exception(kind,error,tb))})


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


def signal_record(binding,value,widget):
 signals.append({'window':window_id,'step':current,'phase':phase,'request':request,'binding':clone(binding),'widget_class':type(widget).__name__,'value':snapshot(value),'current_widget_value':snapshot(widget_value(widget))})


def observe_signals():
 for row in PLAN['controls']:
  name=row['widget'];widget=getattr(window,name);signal=getattr(widget,row['signal']);binding={'kind':'common','widget':name,'signal':row['signal']}
  if name=='timing_scenario':signal.connect(lambda widget=widget,binding=binding:signal_record(binding,widget.toPlainText(),widget))
  else:signal.connect(lambda value,widget=widget,binding=binding:signal_record(binding,value,widget))
 condition_bindings=[]
 for index,(owner,key,skills,widget) in enumerate(window.model_option_widgets):
  planned=[r for r in PLAN['condition_controls'] if r['owner']==owner and r['field']==key]
  if not planned:continue
  assert len(planned)==1 and list(skills)==planned[0]['skills'] and type(widget).__name__==planned[0]['widget_class']
  binding={'kind':'condition','owner':owner,'field':key,'skills':list(skills),'model_option_index':index,'signal':planned[0]['signal']}
  condition_bindings.append(binding);getattr(widget,binding['signal']).connect(lambda value,widget=widget,binding=binding:signal_record(binding,value,widget))
 assert len(condition_bindings)==len(PLAN['condition_controls'])==9,'All nine actual original widgets/signals must be bound'


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
 close_window();fresh_windows+=1;window_id='public-condition096-window-'+str(fresh_windows)
 active_folder=Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-condition096-')))
 account_path=active_folder/'account.json';run_path=active_folder/'run.json'
 account_path.write_text(json.dumps(fixture,ensure_ascii=False,allow_nan=False),encoding='utf-8')
 run_path.write_text(json.dumps(PLAN['public_run_initial'],ensure_ascii=False,allow_nan=False),encoding='utf-8')
 module.OPERATOR_STATE=account_path;module.RUN_STATE=run_path;module.SETTINGS=active_folder/'settings.json'
 module.DesktopBackend=lambda _path,callback:original_backend(active_folder/'chat',callback)
 phase='startup';request='real_MainWindow_constructor';before=dict(counts);all_before=dict(all_entries);original_before=dict(entries_by_scope.get(phase+'/'+request,{}));presentation_before=dict(presentation_entries.get(phase+'/'+request,{}));import_before=dict(constructor_import_entries.get(phase+'/'+request,{}));api_start=len(API);prepared_start=len(PREPARED);call_start=len(CALLS)
 window=module.MainWindow();window.show();application.processEvents()
 assert type(window.run) is RunState and window.operator_observations is window.account_cache.records and window.isVisible()
 assert not list_game_windows();external_idle()
 startup={'actual_entries':delta(before,counts),'all_project_entries':delta(all_before,all_entries),'original_project_entries':delta(original_before,entries_by_scope.get(phase+'/'+request,{})),'presentation_project_entries':delta(presentation_before,presentation_entries.get(phase+'/'+request,{})),'constructor_import_project_entries':delta(import_before,constructor_import_entries.get(phase+'/'+request,{})),'API_sequences':[r['sequence'] for r in API[api_start:]],'prepared_sequences':[r['sequence'] for r in PREPARED[prepared_start:]],'targeted_call_sequences':[r['sequence'] for r in CALLS[call_start:]],'UI':ui_snapshot()}
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
 elif what=='condition_value':
  matches=[w for owner,key,skills,w in window.model_option_widgets if owner==step['owner'] and key==step['field'] and window.skill.currentData() in skills];assert len(matches)==1
  widget=matches[0];assert flat_native(widget_value(widget))!=flat_native(step['value']),'Every planned condition set changes the actual typed value'
  signal_start=len(signals);widget.setChecked(step['value']) if isinstance(widget,QCheckBox) else widget.setValue(step['value']);application.processEvents()
  actual=[row for row in signals[signal_start:] if row['binding'].get('owner')==step['owner'] and row['binding'].get('field')==step['field']]
  assert len(actual)==1 and actual[0]['value']['native']==flat_native(step['value']) and actual[0]['current_widget_value']['native']==flat_native(step['value']),'Actual matching owner/field signal and current raw typed value required'
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


def profile(frame,event,arg):
    path=path_of(frame);name=frame.f_code.co_name
    if event=='call' and '/rouge/' in path:
        full='rouge/'+path.split('/rouge/',1)[1]+':'+frame.f_code.co_qualname;all_entries[full]=all_entries.get(full,0)+1
        bucket=entries_by_scope.setdefault(phase+'/'+request,{})
        present=presentation_stack(frame);import_event=None if present else exact_constructor_import(frame)
        if present:
            p=presentation_entries.setdefault(phase+'/'+request,{});p[full]=p.get(full,0)+1
            assert not (path.endswith('/rouge/damage.py') and name in ('calculate_damage','_prepare_damage') or path.endswith('/rouge/app.py') and frame.f_code.co_qualname=='MainWindow.calculate' or path.endswith('/rouge/run_state.py') and frame.f_code.co_qualname=='RunState.apply' or path.endswith('/rouge/account_cache.py') and frame.f_code.co_qualname=='AccountCache.observe'),'Presentation stack/lambda must never calculate or mutate account/run observations'
        elif import_event is not None:
            p=constructor_import_entries.setdefault(phase+'/'+request,{});p[full]=p.get(full,0)+1;constructor_import_events.append(import_event)
        else:bucket[full]=bucket.get(full,0)+1
        if path.endswith('/rouge/condition_cultivation.py'):assert present or import_event is not None,'Only exact presentation sites or one exact constructor module import are admitted; never broad selector/helper exclusion'
        key=None
        if path.endswith('/rouge/damage.py') and name in ('calculate_damage','_prepare_damage'):key=name
        elif path.endswith('/rouge/estimate.py') and name=='format_estimate':key='format_estimate'
        elif path.endswith('/rouge/reporting.py') and name=='format_report':key='format_report_technical' if frame.f_locals['technical'] else 'format_report_default'
        elif path.endswith('/rouge/run_state.py'):key=('RunState.' if frame.f_code.co_qualname.startswith('RunState.') else 'run_state.')+name
        elif path.endswith('/rouge/account_cache.py'):key=('AccountCache.' if 'self' in frame.f_locals else 'account_cache.')+name
        elif path.endswith('/rouge/capture.py') and name in ('capture','next_frame','connect'):key='GameCapture.'+name
        elif path.endswith('/rouge/app.py'):key=('MainWindow.' if frame.f_code.co_qualname.startswith('MainWindow.') else 'app.')+name
        if key and not present and import_event is None:counts[key]=counts.get(key,0)+1
        if key in ('calculate_damage','_prepare_damage','MainWindow.calculate','RunState.apply','AccountCache.observe') and not present and import_event is None:
            row={'sequence':len(CALLS)+1,'key':key,'window':window_id,'step':current,'phase':phase,'request':request,'outcome':'pending','numeric_entry_counts':dict(bucket)}
            actual=inputs(frame,key)
            if actual is not None:row['caller_before']=snapshot(actual);caller_objects[id(frame)]=actual
            if key=='MainWindow.calculate':row['all_outputs_and_affected_controls_exist']=all(hasattr(frame.f_locals['self'],x) for x in CONTROL_NAMES+('damage_text','relic_context'))
            CALLS.append(row);pending[id(frame)]=row
            if key=='calculate_damage':API.append(row)
            elif key=='_prepare_damage':PREPARED.append(row)
    elif event=='return' and id(frame) in pending:
        row=pending.pop(id(frame));key=row['key'];original=caller_objects.pop(id(frame),None)
        if original is not None:row['caller_after']=snapshot(original);row['caller_unchanged']=row['caller_before']['native']==row['caller_after']['native']
        if key in ('calculate_damage','_prepare_damage'):
            if arg is not None:
                row.update(outcome='returned_dict' if type(arg) is dict else 'returned_prepared_tuple' if type(arg) is tuple else 'returned_other',returned=snapshot(arg));row['caller_and_returned_graph']=snapshot({'caller':original,'returned':arg})
            elif row.get('exception_events'):row['outcome']='raised_exception'
            else:row['outcome']='returned_none_or_unobserved_unwind'
            row['original_numeric_subtree_vector']=delta(row.pop('numeric_entry_counts'),entries_by_scope[row['phase']+'/'+row['request']])
            if key=='_prepare_damage':row['local_prepared_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'))
        elif key=='MainWindow.calculate':row['outcome']='returned_none_with_exception_events' if row.get('exception_events') else 'returned_none';row['assembled_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'));row.pop('numeric_entry_counts')
        else:row['outcome']='returned_value' if arg is not None else 'returned_none';row['returned']=snapshot(arg);row.pop('numeric_entry_counts')
        # Bind the entire completed row before ordinary JSON serialization can
        # turn a snapshot JSON_projection tuple into a list. The original tuple,
        # types/order/float/aliases remain exact in this graph, including every
        # caller/result/exit/exception/vector field. No row field is stripped.
        row['complete_row_native']=flat_native(row)
def old_control_projection(rows):
    projected=clone(rows)
    allowed={(row['owner'],row['field']) for row in PLAN['condition_controls']}
    for row in projected:
        if (row['owner'],row['field']) in allowed:row['tooltip']='EXACT_NINE_SOURCE_BOUND_PRESENTATION_TOOLTIP_DELTA'
    return snapshot(projected)
def condition_probe(ui):
    old_controls=[];op=window.operator.currentData();skill=window.skill.currentData()
    for owner,key,skills,widget in window.model_option_widgets:
        row={'owner':owner,'field':key,'skills':skills,'value':widget_value(widget),'visible':widget.isVisible(),'enabled':widget.isEnabled(),'tooltip':widget.toolTip()}
        if hasattr(widget,'minimum'):row.update(minimum=widget.minimum(),maximum=widget.maximum(),singleStep=widget.singleStep())
        old_controls.append(row)
    if MODE=='gold':
        assert not hasattr(window,'condition_cultivation_explanation') and not hasattr(window,'condition_cultivation_rows')
        return {'old_controls':snapshot(old_controls),'old_controls_comparison':old_control_projection(old_controls),'new_presentation':None}
    rows=window.condition_cultivation_rows;label=window.condition_cultivation_explanation
    expected=[key for owner,key,skills,w in window.model_option_widgets if owner==op and skill in skills and key in PLAN['target_fields']]
    assert [r['field'] for r in rows]==expected
    state=ui['current_operator_state']['JSON_projection'] or {};fields=state.get('fields',{})
    confirmed=state.get('run_confirmed_fields',()) if state.get('scope')=='run' else ()
    provenance={key:('simulated_override' if key=='level' and ui['level_override'] else 'preview_unconfirmed' if key not in fields else 'run_confirmed' if key in confirmed else 'account_reference') for key in ('elite','level','potential','module_id','module_level')}
    expected_effective=None
    if rows:
        expected_effective={'elite':fields.get('elite',PLAN['profile_preview_facts'][op]['maximum_elite']),'level':ui['level'],'potential':fields.get('potential',1),'module_id':fields.get('module_id'),'module_level':fields.get('module_level',0)}
    source_labels={'run_confirmed':'本局确认','account_reference':'账号参考（本局未确认）','preview_unconfirmed':'来源缺失，采用预览','simulated_override':'手动等级预览'}
    for row in rows:
        widget=next(w for owner,key,skills,w in window.model_option_widgets if owner==op and key==row['field'] and skill in skills)
        assert row['operator']==op and row['eligibility_status'] in ('met','unmet','unavailable')
        assert row['eligibility_status']==('unavailable' if row['selection_error'] is not None else 'met' if row['selected_talent'] is not None else 'unmet')
        assert type(row['condition_value']) is type(widget_value(widget)) and row['condition_value']==widget_value(widget)
        assert row['new_arithmetic_applied'] is False and row['actual_activation'] is None and row['native_attachment'] is None and row['account_unlock_verified'] is None
        assert row['training_provenance']==provenance and flat_native(row['effective_training'])==flat_native(expected_effective),'Refresh must reflect current public merged training and manual level without recomputing the helper'
        relevant=('elite','level','potential')+(('module_id','module_level') if expected_effective['module_id'] else ())
        assert row['uses_unconfirmed_preview'] is any(provenance[k] in ('preview_unconfirmed','simulated_override') for k in relevant)
        assert row['uses_account_reference'] is any(provenance[k]=='account_reference' for k in relevant)
        definition=next(d for d in PLAN['field_source_definitions'][op] if d['field']==row['field'])
        for key in ('label','talent_name','talent_index','first_original_gate','modeled_parameter_keys','scope_note'):assert flat_native(row[key])==flat_native(definition[key]),('Complete original field/source definition',key)
        original=row['original_source']
        if original is not None:
            assert PLAN['source_coordinate_owners'][original['path']]==op,'Raw source coordinates belong to the currently selected owner'
            fact=PLAN['source_coordinate_facts'][original['path']]
            for key,value in fact.items():assert key in original and flat_native(original[key])==flat_native(value),('Exact complete raw source coordinate fact',row['field'],key)
            assert row['source_status']=='located'
        elif row['selected_talent'] is not None or row['selection_error'] is not None:assert row['source_status']=='missing'
        else:assert row['source_status']=='not_selected'
        step=next(s for s in PLAN['steps'] if s['id']==current);qualified=step.get('expected_field_qualification',{})
        if row['field'] in qualified:assert row['eligibility_status']==qualified[row['field']],('Pinned original first gate qualification',current,row['field'])
        designated=step.get('expected_presentation')
        if designated:
            for key in ('training_provenance','uses_unconfirmed_preview','uses_account_reference','eligibility_status','source_status','effective_training'):assert flat_native(row[key])==flat_native(designated[key]),('Designated source-bound refresh',current,row['field'],key)
            assert original is not None and original['path']==designated['original_source_path'] and ui['level_override'] is designated['level_override']
            assert designated['source_text_contains'] in widget.toolTip()
        assert widget.toolTip() and row['talent_name'] in widget.toolTip() and row['scope_note'] in widget.toolTip()
        assert '培养资格不确认实际触发、账号任务解锁或原生附着。' in widget.toolTip()
        for key in relevant:assert source_labels[provenance[key]] in widget.toolTip(),('Actual per-field provenance appears in current tooltip',current,key)
    tooltip_text=[next(w for owner,key,skills,w in window.model_option_widgets if owner==op and key==row['field'] and skill in skills).toolTip() for row in rows]
    assert label.text()=='\n\n'.join(tooltip_text) and label.isVisible()==bool(rows)
    if not rows:assert not label.text()
    # Full rows are preserved as evidence, not projected into qualification booleans.
    return {'old_controls':snapshot(old_controls),'old_controls_comparison':old_control_projection(old_controls),'new_presentation':{'rows':snapshot(rows),'text':label.text(),'visible':label.isVisible(),'tooltips':tooltip_text,'current_public_training_and_source_verified':True}}
def result_capture():
    value=window.damage_result;ui=ui_snapshot()
    return {'damage_result':snapshot(value),'UI':ui,'visible_status':window.damage_text.toPlainText(),'three_texts':three_texts(),'condition_probe':condition_probe(ui)}
def compare_capture(actual,baseline):
    assert actual['damage_result']['native']==baseline['damage_result']['native'],'Entire old95 native report/types/order/alias/float remains exact; no stripping'
    assert actual['UI']==baseline['UI'] and actual['visible_status']==baseline['visible_status']
    assert actual['three_texts']==baseline['three_texts'],'All strings/status and original formatter function metadata exact'
    assert actual['condition_probe']['old_controls_comparison']['native']==baseline['condition_probe']['old_controls_comparison']['native'],'Identical two-sided schema preserves all original values/visibility/enabled/ranges and every non-target tooltip; both full tooltip vectors remain captured'
def compare_entries(seq,oldseq,rows,oldrows):
    assert len(seq)==len(oldseq)
    byseq={r['sequence']:r for r in rows}
    for a,b in zip(seq,oldseq):
        assert set(byseq[a])==set(oldrows[b]) and byseq[a]['complete_row_native']==oldrows[b]['complete_row_native'],'Entire actual completed API/prepared native row exact, including tuple projections before serialization'
def checkpoint():
    global checkpoint_pauses
    checkpoint_pauses+=1;payload={'format_version':2,'schema':'condition096-focused-native-v2','passed':receipt['passed'],'states':states,'API_entries':API,'prepared_entries':PREPARED,'targeted_calls':CALLS,'signals':signals,'Qt_slot_exceptions':qt_exceptions,'original_entries_by_phase':entries_by_scope,'presentation_entries_by_actual_UI_stack':presentation_entries,'constructor_import_entries_by_exact_source_site':constructor_import_entries,'constructor_import_events':constructor_import_events,'all_rouge_entries':all_entries,'checks':checks,'actual_PNGs':pngs}
    saved_profile=sys.getprofile();saved_trace=sys.gettrace();sys.setprofile(previous_profile);sys.settrace(previous_trace)
    try:
        raw=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8');compressed=gzip.compress(raw,mtime=0);ARCHIVE.write_bytes(compressed);receipt['records']={'file':ARCHIVE.name,'bytes':len(compressed),'sha256':digest(compressed),'decoded_bytes':len(raw),'decoded_sha256':digest(raw)}
    finally:sys.settrace(saved_trace);sys.setprofile(saved_profile)
def run_step(step):
    global phase,request,current,explicit_buttons
    current=step['id'];phase='before_probe';request='explicit_probe';record={'id':current,'planned':snapshot(step),'passed':False,'window_before':window_id,'durable_before':durable_snapshot()};states.append(record)
    if step['action']=='fresh_window':record['startup']=fresh_window(step['fixture']);record['automatic']=result_capture()
    else:
        api_start=len(API);prep_start=len(PREPARED);before=dict(counts);all_before=dict(entries_by_scope.get('automatic_action/'+step['action'],{}));qt_start=len(qt_exceptions)
        action(step);entered=delta(before,counts);rows=API[api_start:];render_only=step['action'] in ('technical','raw')
        if render_only:assert not rows and entered.get('MainWindow.calculate',0)==0
        outcome=validate(step,rows,entered,not render_only);automatic=result_capture();automatic.update(API_sequences=[r['sequence'] for r in rows],prepared_sequences=[r['sequence'] for r in PREPARED[prep_start:]],actual_entries=entered,outcome=outcome);record['automatic']=automatic
        durable=durable_snapshot();record['durable_after_automatic']=durable
        if step['action'] not in ('account_observation','run_observation'):assert_unchanged(record['durable_before'],durable)
        phase='manual_button';request='actual_compute_button';before=dict(counts);api_start=len(API);prep_start=len(PREPARED);explicit_buttons+=1
        next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估').click();application.processEvents();entered=delta(before,counts)
        assert validate(step,API[api_start:],entered)==outcome and len(qt_exceptions)==qt_start
        manual=result_capture();manual.update(API_sequences=[r['sequence'] for r in API[api_start:]],prepared_sequences=[r['sequence'] for r in PREPARED[prep_start:]],actual_entries=entered,outcome=outcome);record['manual']=manual
        assert automatic['damage_result']['native']==manual['damage_result']['native'] and automatic['three_texts']['strings']==manual['three_texts']['strings'] if automatic['three_texts']['applicable'] else automatic['three_texts']==manual['three_texts']
        assert_unchanged(durable,durable_snapshot())
    record['window_after']=window_id;record['durable_after']=durable_snapshot();record['passed']=True
    if MODE=='candidate':
        baseline=BASELINE_STATES[current];assert record['planned']['native']==baseline['planned']['native'] and record['durable_after']==baseline['durable_after']
        for key in ('automatic','manual'):
            if key not in record:continue
            compare_capture(record[key],baseline[key]);assert record[key].get('actual_entries')==baseline[key].get('actual_entries')
            compare_entries(record[key].get('API_sequences',[]),baseline[key].get('API_sequences',[]),API,BASELINE_API);compare_entries(record[key].get('prepared_sequences',[]),baseline[key].get('prepared_sequences',[]),PREPARED,BASELINE_PREPARED)
        if 'startup' in record:
            for key in ('actual_entries','original_project_entries','API_sequences','prepared_sequences','targeted_call_sequences','UI'):assert record['startup'][key]==baseline['startup'][key],('Constructor original calls/native/outputs remain exact; full added presentation/import vector preserved separately',key)
    if MODE=='candidate' and step.get('PNG'):
        path=OUT/step['PNG'];assert window.grab().save(str(path));pngs.append({'file':path.name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes()),'actual_view_by_root_pending':True})
    external_idle();checks.append({'id':current,'passed':True})
    if len(states)%5==0 or step['action']=='fresh_window':checkpoint()
try:
    sys.setprofile(profile);sys.settrace(trace);sys.excepthook=qt_hook
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QCheckBox,QPushButton
    import rouge.app as module
    from rouge.run_state import RunState
    from rouge.capture import list_game_windows
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    application=QApplication([]);application.setQuitOnLastWindowClosed(False);original_backend=module.DesktopBackend
    for step in PLAN['steps']:run_step(step)
    close_window();assert len(states)==PLAN['counts']['states_planned'] and fresh_windows==2 and explicit_buttons==PLAN['counts']['manual_button_requests_planned']
    assert not pending and not caller_objects and not qt_exceptions
    assert all(counts.get(k,0)==0 for k in ('GameCapture.capture','GameCapture.next_frame','GameCapture.connect','MainWindow.connect_game','MainWindow.sample_now','MainWindow.sample_received','MainWindow.send_chat','MainWindow.desktop_request','MainWindow.bind_desktop'))
    if MODE=='candidate':
        assert entries_by_scope==BASELINE['original_entries_by_phase'],'Entire old project function vector preserved after exactly stack-proven presentation separation'
        assert len(API)==len(BASELINE['API_entries']) and len(PREPARED)==len(BASELINE['prepared_entries'])
        assert len(CALLS)==len(BASELINE['targeted_calls'])
        for actual,old in zip(CALLS,BASELINE['targeted_calls']):
            assert set(actual)==set(old) and actual['complete_row_native']==old['complete_row_native'],'Strict complete targeted native row pairs calculate exit scenario, RunState.apply and AccountCache.observe callers/results/errors as well as API/prepared entries'
        assert flat_native(signals)==flat_native(BASELINE['signals']),'Complete common plus nine original condition-widget signal/value/identity vector exact'
        assert len(constructor_import_events)==1,'One exact first constructor import, never arbitrary helper calls'
        assert len(pngs)==PLAN['counts']['PNG_planned']
    else:assert not presentation_entries and not constructor_import_entries and not constructor_import_events
    partitioned={}
    for groups in (entries_by_scope,presentation_entries,constructor_import_entries):
        for group in groups.values():
            for key,value in group.items():partitioned[key]=partitioned.get(key,0)+value
    assert partitioned==all_entries,'Every actual project entry classified once; no broad filtering or omitted selector calls'
    for row in CALLS:assert row['complete_row_native']==flat_native({key:value for key,value in row.items() if key!='complete_row_native'}),'Every saved complete row graph must match its actual still-live row before serialization'
    receipt['passed']=True;receipt['workflow_complete']=True
except BaseException as error:receipt['failure']={'type':type(error).__name__,'message':str(error),'step':current,'traceback':traceback.format_exc()}
finally:
    try:close_window()
    except Exception as error:receipt['passed']=False;receipt['workflow_complete']=False;receipt['close_error']={'type':type(error).__name__,'message':str(error)}
    sys.setprofile(previous_profile);sys.settrace(previous_trace);sys.excepthook=previous_excepthook
    after={rel:digest((ROOT/rel).read_bytes()) for rel in SOURCE_HASHES};receipt['source_sha256_after']=after;receipt['source_drift']=[r for r in SOURCE_HASHES if after[r]!=SOURCE_HASHES[r]]
    if receipt['source_drift']:receipt['passed']=False;receipt['workflow_complete']=False
    receipt.update(states=len(states),fresh_windows=fresh_windows,explicit_button_requests=explicit_buttons,explicit_three_text_requests=explicit_texts,actual_API_entries=len(API),prepared_entries=len(PREPARED),actual_targeted_calls=len(CALLS),actual_signals=len(signals),all_project_function_entries=all_entries,presentation_entries_by_actual_UI_stack=presentation_entries,constructor_import_entries_by_exact_source_site=constructor_import_entries,constructor_import_events=constructor_import_events,actual_PNGs=pngs,elapsed_seconds=round(time.perf_counter()-started,3))
    checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');folders.close();print(json.dumps({'passed':receipt['passed'],'states':len(states),'failure':receipt.get('failure')},ensure_ascii=False));sys.exit(0 if receipt['passed'] else 1)
