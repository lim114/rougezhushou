PENDING_PREPARATION = True
if PENDING_PREPARATION:
    raise SystemExit('Pending094: 93 runtime completion, root applied94 actual source guard and fresh final source-only review required; root alone executes Wine')
"""Root-only actual MainWindow workflow; this pending source is never executed."""
import gzip,hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
from contextlib import ExitStack
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat')
EXPECTED_GUARD_SHA256='PENDING_ROOT_ACTUAL_094_SOURCE_GUARD'
GUARD=Path(__file__).with_name('wine-focused-inputs-094-pending-source.json')
assert hashlib.sha256(GUARD.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA256
SOURCE=json.loads(GUARD.read_text(encoding='utf-8'));SOURCE_HASHES=SOURCE['source_sha256_after']
assert SOURCE['passed'] is True and len(SOURCE_HASHES)==732
for rel,digest_value in SOURCE_HASHES.items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest_value,('source before Qt',rel)
assert SOURCE_HASHES['rouge/app.py']=='589b9ac2b846206581c394d037baec0d9e43a165a7bdd5becc0982ab0e09c0fd'
assert SOURCE_HASHES['rouge/account_cache.py']=='17250d93fa3932fc6233bc5b8dd8d1a17d76a283feee5fe694ffebe530ecb5d5'
PLAN_PATH=Path(__file__).with_name('wine-focused-inputs-094-plan.json')
assert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='a61c11b82d35536c0fe9f31e5481aac9ac09cff803b945641763426a73ea5f5b'
PLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))
RECEIPT=OUT/'wine-focused-inputs-094.json';ARCHIVE=OUT/'wine-focused-inputs-094-records.json.gz'
assert not RECEIPT.exists() and not ARCHIVE.exists(),'Preserve previous evidence; never replay a successful prefix'
for name in ('wine-focused-inputs-silver-094.png','wine-focused-inputs-shield-094.png','wine-focused-inputs-charge-error-094.png','wine-focused-inputs-failure-094.png'):
    assert not (OUT/name).exists(),('Preserve existing image',name)
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

counts={};all_entries={};entries_by_scope={};signals=[];API=[];CALLS=[];pending={};qt_exceptions=[];states=[];checks=[];pngs=[]
phase='preparation';request='none';current='before-first-window';group_id=None;window_id=None
window=None;application=None;active_folder=None;account_path=None;run_path=None
explicit_buttons=0;explicit_texts=0;affected_edits=0;fresh_windows=0;checkpoint_pauses=0
started=time.perf_counter();folders=ExitStack();off_gate_reference=None;elapsed_reference=None
previous_profile=sys.getprofile();previous_trace=sys.gettrace();previous_excepthook=sys.excepthook
receipt={'format_version':1,'passed':False,'workflow_complete':False,'source_guard_sha256':EXPECTED_GUARD_SHA256,
    'source_sha256_before':SOURCE_HASHES,'plan_counts':PLAN['counts'],'checks':checks,'private_state_isolated':True,
    'native_codec':'flat-typed-graph-v1; byte-exact source reuse from final093; iterative lossless inverse verified per runtime snapshot',
    'codec_preparation_executed':False,'old92_matrix_replayed':False,'old93_corruption_matrix_replayed':False,
    'native_game_clock_certified':False,'game_capture_requests':0,'chat_requests':0,
    'checkpoint_pause_scope':'Only stdlib json/gzip/hashlib/Path serialization and writes; no UI snapshot/product/API/Qt/processEvents/signal delivery in pause',
    'coverage_limits':PLAN['scope_limits'],'commit_policy':'Collective commit after95 full validation; no invented93 Git/tag prerequisite'}

def path_of(frame):return frame.f_code.co_filename.replace('\\','/').lower()
def frame_inputs(frame,key):
    if key=='calculate_damage':return {'scenario':frame.f_locals['scenario']}
    if key in ('RunState.apply','MainWindow.apply_run_observation'):
        return {name:frame.f_locals[name] for name in ('observed','captured_at')}
    return None
def trace_local(frame,event,arg):
    if event=='exception' and id(frame) in pending:
        pending[id(frame)].setdefault('exception_events',[]).append({'type':arg[0].__name__,'message':str(arg[1]),'args':snapshot(arg[1].args)})
    return trace_local
def trace(frame,event,arg):
    path=path_of(frame)
    if event=='call' and (path.endswith('/rouge/app.py') and frame.f_code.co_name in ('calculate','apply_run_observation')
        or path.endswith('/rouge/damage.py') and frame.f_code.co_name=='calculate_damage'
        or path.endswith('/rouge/run_state.py') and frame.f_code.co_name=='apply'):
        return trace_local
    return None
def profile(frame,event,arg):
    path=path_of(frame);name=frame.f_code.co_name
    if event=='call' and '/rouge/' in path:
        full='rouge/'+path.split('/rouge/',1)[1]+':'+frame.f_code.co_qualname
        all_entries[full]=all_entries.get(full,0)+1
        scope=phase+'/'+request;bucket=entries_by_scope.setdefault(scope,{})
        bucket[full]=bucket.get(full,0)+1;key=None
        if path.endswith('/rouge/damage.py') and name=='calculate_damage':key='calculate_damage'
        elif path.endswith('/rouge/estimate.py') and name=='format_estimate':key='format_estimate'
        elif path.endswith('/rouge/reporting.py') and name=='format_report':
            key='format_report_technical' if frame.f_locals['technical'] else 'format_report_default'
        elif path.endswith('/rouge/operator_summary.py') and name=='format_operator_observation':key='format_operator_observation'
        elif path.endswith('/rouge/account_cache.py'):key=('AccountCache.' if 'self' in frame.f_locals else 'account_cache.')+name
        elif path.endswith('/rouge/run_state.py'):key=('RunState.' if frame.f_code.co_qualname.startswith('RunState.') else 'run_state.')+name
        elif path.endswith('/rouge/capture.py') and name in ('capture','next_frame','connect'):key='GameCapture.'+name
        elif path.endswith('/rouge/app.py'):key=('MainWindow.' if frame.f_code.co_qualname.startswith('MainWindow.') else 'app.')+name
        if key:counts[key]=counts.get(key,0)+1
        if key in ('calculate_damage','MainWindow.calculate','RunState.apply','MainWindow.apply_run_observation'):
            record={'sequence':len(CALLS)+1,'key':key,'window':window_id,'group':group_id,'step':current,'phase':phase,'request':request,'outcome':'pending'}
            inputs=frame_inputs(frame,key)
            if inputs is not None:record['caller_before']=snapshot(inputs)
            if key=='MainWindow.calculate':
                owner=frame.f_locals['self']
                record['all_outputs_and_affected_controls_exist']=all(hasattr(owner,x) for x in CONTROL_NAMES+('damage_text','raw_damage','damage_technical','relic_context','timing_scenario'))
            CALLS.append(record);pending[id(frame)]=record
            if key=='calculate_damage':API.append(record)
    elif event=='return' and id(frame) in pending:
        record=pending.pop(id(frame));key=record['key'];inputs=frame_inputs(frame,key)
        if inputs is not None:
            record['caller_after']=snapshot(inputs)
            record['caller_unchanged']=record['caller_before']['native']==record['caller_after']['native']
        if key=='calculate_damage':
            if type(arg) is dict:record.update(outcome='returned_dict',returned=snapshot(arg))
            elif record.get('exception_events'):record['outcome']='raised_exception'
            else:record['outcome']='returned_non_dict_or_unobserved_unwind'
        elif key=='MainWindow.calculate':
            record['outcome']='returned_none_with_exception_events' if record.get('exception_events') else 'returned_none'
            record['assembled_scenario_at_exit']=snapshot(frame.f_locals.get('scenario'))
            record['numerical_result_available']=type(frame.f_locals['self'].damage_result) is dict
        elif arg is not None:
            record['outcome']='returned_value';record['returned']=snapshot(arg)
        else:record['outcome']='returned_none_with_exception_events' if record.get('exception_events') else 'returned_none'

def checkpoint():
    global checkpoint_pauses
    checkpoint_pauses+=1
    payload={'format_version':1,'native_schema':'flat-typed-graph-v1','current_step':current,'passed':receipt['passed'],
        'states':states,'checks':checks,'signals':signals,'API_entries':API,'targeted_calls':CALLS,
        'actual_python_entries':counts,'all_rouge_main_thread_entries':all_entries,'all_rouge_entries_by_phase_and_request':entries_by_scope,
        'Qt_slot_exceptions':qt_exceptions,'explicit_buttons':explicit_buttons,'explicit_three_text_requests':explicit_texts,
        'affected_value_change_requests':affected_edits,'fresh_windows':fresh_windows,'actual_PNGs':pngs,'stdlib_checkpoint_pauses':checkpoint_pauses}
    saved_profile=sys.getprofile();saved_trace=sys.gettrace()
    sys.setprofile(previous_profile);sys.settrace(previous_trace)
    try:
        raw=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8')
        compressed=gzip.compress(raw,mtime=0);ARCHIVE.write_bytes(compressed)
        receipt['records']={'file':ARCHIVE.name,'bytes':len(compressed),'sha256':hashlib.sha256(compressed).hexdigest(),
            'decoded_bytes':len(raw),'decoded_sha256':hashlib.sha256(raw).hexdigest()}
    finally:
        sys.settrace(saved_trace);sys.setprofile(saved_profile)

def qt_hook(kind,error,tb):
    qt_exceptions.append({'window':window_id,'group':group_id,'step':current,'phase':phase,'type':kind.__name__,'message':str(error),'traceback':''.join(traceback.format_exception(kind,error,tb))})
CONTROL_NAMES=tuple(row['widget'] for row in PLAN['controls'])
DIRECT_FIELDS={'deployment_elapsed':'deployment_elapsed_seconds','healing_targets':'healing_targets','defense':'enemy_defense',
    'resistance':'enemy_resistance','cooperative':'cooperative','fragile':'preexisting_fragile','charge_count':'charge_count',
    'shield_breaks':'shield_break_count','activation_count':'activation_count','companion_attack':'companion_attack','stacks':'deployment_stacks'}
def widget_value(widget):return widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()
def controls_snapshot():
    result={}
    for row in PLAN['controls']:
        widget=getattr(window,row['widget']);data={'value':snapshot(widget_value(widget)),'enabled':widget.isEnabled(),'visible':widget.isVisible(),'hidden':widget.isHidden()}
        if not isinstance(widget,QCheckBox):
            data.update(minimum=snapshot(widget.minimum()),maximum=snapshot(widget.maximum()))
            if hasattr(widget,'decimals'):data['decimals']=widget.decimals()
        result[row['widget']]=data
    return result
def ui_snapshot():
    if window is None:return None
    return {'owner':window.operator.currentData(),'skill':window.skill.currentData(),'level':window.level.value(),
        'level_override':window.level_override,'use_run_training':window.use_run_training.isChecked(),
        'training_status':window.training_status.text(),'elite':window.elite.text(),'trust':window.trust.text(),'potential':window.potential.text(),
        'module':window.module.text(),'rank':window.rank.text(),'damage_text':window.damage_text.toPlainText(),
        'current_operator_state':snapshot(window.current_operator_state()),'account_records':snapshot(window.account_cache.records),
        'account_issues':snapshot(window.account_cache.issues),'load_issue':window.account_cache.load_issue,'preserve_original':window.account_cache.preserve_original,
        'run_state':snapshot(window.run.state),'damage_result':snapshot(window.damage_result),'controls':controls_snapshot(),
        'selected_target':snapshot(window.target_enemy.currentData()),'frame_timing':window.frame_timing.isChecked(),'limit_window':window.limit_window.isChecked(),
        'window_seconds':window.window_seconds.value(),'auto_relics':window.auto_relics.isChecked(),'raw_damage':window.raw_damage.isChecked(),
        'damage_technical':window.damage_technical.isChecked(),'timing_text':window.timing_scenario.toPlainText(),'relic_context_text':window.relic_context.toPlainText(),
        'visible':window.isVisible()}
def durable_snapshot():
    if window is None:return None
    return {'run':snapshot(window.run.state),'account_records':snapshot(window.account_cache.records),'account_bytes':snapshot(file_bytes(account_path)),
        'files':filesystem(active_folder),'operator_observations_alias_is_records':window.operator_observations is window.account_cache.records}
def unchanged(before,after):
    assert before['run']['native']==after['run']['native'],'Preview must preserve complete real RunState and member/time/history/resource metadata'
    assert before['account_records']['native']==after['account_records']['native'],'Preview must preserve account records'
    assert before['account_bytes']['native']==after['account_bytes']['native'],'Preview must preserve account raw bytes'
    assert before['files']==after['files'],'Preview must preserve every temporary existing file/byte/name'
    assert before['operator_observations_alias_is_records'] and after['operator_observations_alias_is_records']
def signal_record(widget_name,value):
    signals.append({'window':window_id,'group':group_id,'step':current,'phase':phase,'request':request,'widget':widget_name,'value':snapshot(value)})
def attach_signal_observers():
    for row in PLAN['controls']:
        name=row['widget'];getattr(getattr(window,name),row['signal']).connect(lambda value,name=name:signal_record(name,value))
    window.skill.currentIndexChanged.connect(lambda value:signal_record('skill',value))
    window.operator.currentIndexChanged.connect(lambda value:signal_record('operator',value))
    window.timing_scenario.textChanged.connect(lambda:signal_record('timing_scenario',window.timing_scenario.toPlainText()))
    window.relic_context.textChanged.connect(lambda:signal_record('relic_context',window.relic_context.toPlainText()))
def external_idle():
    assert not window.auto.isChecked() and window.capture.target is None
    assert not window.desktop.process and not window.desktop_request_busy and not active_folder.joinpath('chat').exists()
def three_texts():
    global explicit_texts,phase,request
    if window.damage_result is None:return {'applicable':False,'reason':'Actual error or natural early return; no numerical result','visible_status':window.damage_text.toPlainText()}
    phase='explicit_three_texts';request='explicit_formatter';before=dict(counts);all_before=dict(all_entries)
    raw=window.damage_result['scenario'];result=window.damage_result['result'];raw_before=flat_native(raw);result_before=flat_native(result)
    texts={'estimate':format_estimate(result),'default':format_report(result),'technical':format_report(result,technical=True)};explicit_texts+=3
    assert texts['estimate']==texts['default']
    assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
    assert flat_native(raw)==raw_before and flat_native(result)==result_before,'Formatter must preserve complete native caller/result'
    return {'applicable':True,'strings':texts,'requests':3,'actual_entries':delta(before,counts),'all_project_entries':delta(all_before,all_entries),'native_preserved':True}
def assert_raw_assembly(raw):
    expected={field:widget_value(getattr(window,name)) for name,field in DIRECT_FIELDS.items()}
    for owner,key,skills,widget in window.model_option_widgets:
        if owner==window.operator.currentData() and window.skill.currentData() in skills:expected[key]=widget_value(widget)
    for field,value in expected.items():
        assert flat_native(raw[field])==flat_native(value),('Existing raw assembly incl hidden/enabled/OPTIONS',field,raw[field],value)
    include=window.operator.currentData()=='mechanist' and window.skill.currentData()==2 and window.shield_duration_known.isChecked()
    assert ('skill_duration_seconds' in raw)==include
    if include:assert type(raw['skill_duration_seconds']) is float and raw['skill_duration_seconds']==window.shield_duration.value()
    assert ('window_seconds' in raw)==window.limit_window.isChecked()
    assert raw['operator']==window.operator.currentData() and raw['skill']==window.skill.currentData()
    target=window.target_enemy.currentData()
    if target:assert flat_native(raw['target_enemy'])==flat_native(target)
    else:assert 'target_enemy' not in raw
def validate_outcome(step,api_start,entries):
    expected=step.get('expected',{});kind=expected.get('kind','numerical_result');rows=API[api_start:]
    assert entries.get('MainWindow.calculate',0)>0,'Actual MainWindow.calculate must enter after the affected signal/button'
    if kind=='JSON_error_before_numerical_API':
        assert not rows and window.damage_result is None and window.damage_text.toPlainText()==expected['message']
    elif kind=='numerical_API_exception':
        assert rows and all(row['outcome']=='raised_exception' for row in rows)
        assert window.damage_result is None and window.damage_text.toPlainText()==expected['message']
        assert all(any(event['type']==expected['type'] and event['message']==expected['message'] for event in row.get('exception_events',[])) for row in rows)
    elif kind=='natural_early_return':
        assert not rows and window.damage_result is None and expected['text_contains'] in window.damage_text.toPlainText()
    else:
        assert rows and all(row['outcome']=='returned_dict' for row in rows) and type(window.damage_result) is dict,window.damage_text.toPlainText()
        assert_raw_assembly(window.damage_result['scenario'])
    assert all(row.get('caller_unchanged') is True for row in rows)
    return kind
def API_outcomes(rows):
    return {name:sum(row['outcome']==name for row in rows) for name in ('returned_dict','raised_exception','returned_non_dict_or_unobserved_unwind')}
def selected_snapshot():
    return {'damage_result':snapshot(window.damage_result),'visible_status':window.damage_text.toPlainText(),'UI':ui_snapshot()}
def begin_record(step,suffix=''):
    global phase,request,current
    current=group_id+'/'+step['_source_step_id']+suffix;phase='probe_before';request='explicit_probe'
    before_probe=dict(counts)
    record={'id':current,'window':window_id,'group':group_id,'planned':snapshot({key:value for key,value in step.items() if not key.startswith('_')}),
        'passed':False,'before':ui_snapshot(),'durable_before':durable_snapshot(),'counter_before_probe':before_probe}
    states.append(record);return record
def finish_record(record,preserve=True):
    global phase,request
    phase='probe_after';request='explicit_probe';record['window_after']=window_id;record['after']=ui_snapshot();record['durable_after']=durable_snapshot()
    if preserve and record['durable_before'] is not None:unchanged(record['durable_before'],record['durable_after'])
    external_idle();record['actual_entries_including_probes_and_formatters']=delta(record['counter_before_probe'],counts)
    record['passed']=True;checks.append({'id':record['id'],'group':group_id,'passed':True,'kind':record['planned']['JSON_projection']['kind']})
    checkpoint()
def select_owner_skill(owner,skill=None):
    assert window.select_operator(owner),('Select lawful source-qualified owner',owner)
    if skill is not None:
        index=window.skill.findData(skill);assert index>=0,('Legal open skill',owner,skill);window.skill.setCurrentIndex(index)
    application.processEvents();assert window.operator.currentData()==owner
    if skill is not None:assert window.skill.currentData()==skill
def common_controls():
    window.centralWidget().setCurrentIndex(1);window.auto_relics.setChecked(False);window.frame_timing.setChecked(False)
    window.limit_window.setChecked(False);window.target_enemy.setCurrentIndex(0)
    window.target_buff_test.setChecked(False);window.raw_damage.setChecked(False);window.damage_technical.setChecked(False)
    window.timing_scenario.clear();window.relic_context.clear();application.processEvents()
def close_window():
    global window,phase,request
    if window is None:return
    phase='close';request='window_close';external_idle();before=filesystem(active_folder)
    window.close();application.processEvents();window.deleteLater();application.processEvents();window=None
    assert filesystem(active_folder)==before,'Closing cannot alter public fixture files'
def fresh_window(account_fixture):
    global window,active_folder,account_path,run_path,window_id,fresh_windows,phase,request
    assert window is None;fresh_windows+=1;window_id='public-focused094-window-'+str(fresh_windows)
    phase='public_fixture';request='stdlib_public_fixture'
    active_folder=Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-focused094-')))
    account_path=active_folder/'account.json';run_path=active_folder/'run.json'
    module.OPERATOR_STATE=account_path;module.RUN_STATE=run_path;module.SETTINGS=active_folder/'settings.json'
    module.DesktopBackend=lambda _path,callback:original_backend(active_folder/'chat',callback)
    account_path.write_bytes(json.dumps(account_fixture,ensure_ascii=False,allow_nan=False).encode('utf-8'))
    public_files=filesystem(active_folder);phase='startup';request='real_MainWindow_constructor';before=dict(counts);api_start=len(API);call_start=len(CALLS);qt_start=len(qt_exceptions)
    window=module.MainWindow();window.show();application.processEvents()
    startup_entries=delta(before,counts);startup_outcomes=API_outcomes(API[api_start:])
    phase='probe_startup';request='explicit_probe'
    assert type(window.run) is RunState and window.operator_observations is window.account_cache.records
    assert window.isVisible() and not list_game_windows();external_idle();assert len(qt_exceptions)==qt_start
    assert all(record['all_outputs_and_affected_controls_exist'] for record in CALLS[call_start:] if record['key']=='MainWindow.calculate')
    actual_ui=ui_snapshot()
    for row in PLAN['controls']:
        name=row['widget'];widget=getattr(window,name);bounds=row['numeric_bounds_default_decimals']
        if bounds:
            minimum,maximum,default,decimals=bounds
            assert widget.minimum()==minimum
            if name=='healing_targets':assert 1<=widget.maximum()<=maximum
            else:assert widget.maximum()==maximum
            assert widget.value()==default,('Original startup default',name,widget.value(),default)
            if hasattr(widget,'decimals'):assert widget.decimals()==decimals
        else:assert widget.isChecked() is row['boolean_default']
    assert not window.shield_duration.isEnabled()
    attach_signal_observers()
    return {'window':window_id,'original_public_files':public_files,'actual_startup_entries':startup_entries,
        'startup_API_outcomes':startup_outcomes,'actual_UI_after_startup':actual_ui,'startup_includes_existing_outer_callbacks':True}
def capture_png(name):
    global phase,request
    phase='PNG_UI_probe';request='actual_Qt_screenshot';focus=window.shield_duration_known if 'shield' in name else window.activation_count if 'silver' in name else window.charge_count
    parent=focus.parentWidget()
    while parent is not None and not isinstance(parent,QScrollArea):parent=parent.parentWidget()
    if parent is not None:parent.ensureWidgetVisible(focus)
    application.processEvents();path=OUT/name;assert window.grab().save(str(path))
    record={'file':name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes()),'window':window_id,'step':current,
        'focus_visible':focus.isVisible(),'visible_status':window.damage_text.toPlainText(),'actual_controls':controls_snapshot(),'actual_view_by_root_pending':True}
    pngs.append(record);return record
def existing_context(step):
    global phase,request
    action=step['action'];signal_start=len(signals);before=dict(counts);all_before=dict(all_entries);api_start=len(API);qt_start=len(qt_exceptions)
    phase='existing_context_setup';request='existing_Qt_controls'
    if action in ('select-owner-and-skill','return-to-supported-public-preview','select-natural-unimplemented-with-skill','select-natural-no-skill-profile'):
        select_owner_skill(step['owner'],step.get('skill'))
    elif action=='common-controls':common_controls()
    elif action=='select-source-bound-stage-and-enemy':
        assert window.target_stage_choices.select_value(step['stage_id']);assert window.target_enemy_choices.select_value(step['target'])
        application.processEvents();assert window.target_enemy.currentData()==step['target']
        assert not window.defense.isEnabled() and not window.resistance.isEnabled() and not window.defense.isVisible() and not window.resistance.isVisible()
    elif action=='return-manual-target':
        window.target_enemy.setCurrentIndex(0);application.processEvents();assert window.target_enemy.currentData() is None
        assert window.defense.value()==3333 and window.resistance.value()==44.4 and window.defense.isEnabled() and window.resistance.isEnabled()
    elif action=='positive-observation-reference':window.window_seconds.setValue(step['window_seconds']);window.limit_window.setChecked(True)
    elif action=='existing-zero-window-context':window.window_seconds.setValue(step['window_seconds'])
    elif action=='restore-context':window.window_seconds.setValue(step['window_seconds']);window.limit_window.setChecked(step['limit_window'])
    elif action in ('switch-to-S3-existing-clamp','switch-to-S1-existing-clamp'):
        index=window.skill.findData(step['skill']);assert index>=0;window.skill.setCurrentIndex(index)
    elif action in ('existing-invalid-timing-text','restore-timing-JSON'):window.timing_scenario.setPlainText(step['timing_text'])
    elif action=='needed-public-relic-context':
        item=next(window.relic_list.item(i) for i in range(window.relic_list.count()) if window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)==step['rid'])
        item.setCheckState(Qt.CheckState.Checked if step['checked'] else Qt.CheckState.Unchecked);window.relic_context.setPlainText(step['relic_context_text'])
    elif action=='restore-needed-JSON':window.relic_context.setPlainText(step['relic_context_text'])
    elif action=='natural-empty-overview':assert window.operator_choices.select_branch('__overview__')
    else:raise AssertionError(('Unknown source-qualified existing context',action))
    application.processEvents();assert len(qt_exceptions)==qt_start
    if 'expected_maximum' in step:assert window.healing_targets.maximum()==step['expected_maximum']
    if 'expected_value' in step:
        assert window.healing_targets.value()==step['expected_value']
        assert not any(row['widget']=='healing_targets' for row in signals[signal_start:]),'Original clamp blocks only its own existing signal'
    if action=='select-natural-no-skill-profile':assert window.skill.currentData() is None and window.rank.text()=='无可用技能'
    return {'actual_action_entries':delta(before,counts),'actual_all_project_action_entries':delta(all_before,all_entries),
        'action_API_outcomes':API_outcomes(API[api_start:]),'signals':clone(signals[signal_start:]),'affected_input_callback_credit':False}
def existing_result_boundaries(raw,result):
    owner=raw['operator'];skill=raw['skill']
    if raw.get('target_enemy'):
        enemy=result['run_resolution']['enemy'];target=raw['target_enemy']
        assert all(enemy[key]==target[key] for key in ('stage_id','enemy_id','level'))
        assert enemy['reference_stats']['def']==100 and enemy['reference_stats']['magicResistance']==20.0
        assert enemy['stats']['def']==100 and enemy['stats']['magicResistance']==20.0
    if owner=='mechanist' and skill==2:
        reference=result['shield_break_reference']
        assert reference['hits_requested']==raw['shield_break_count']
        assert reference['manual_duration_parameter_seconds']==raw.get('skill_duration_seconds')
        assert all(reference[key] is None for key in ('actual_break_times_seconds','actual_collision_times_seconds','actual_end_seconds','actual_ammunition_consumption_times_seconds'))
        assert reference['events_scheduled'] is False and reference['owner_and_structure_count_mapping_verified'] is False
    if owner=='mechanist' and skill==3:
        if raw['charge_count']:
            reference=result['charge_reference'];assert reference['hits_requested']==raw['charge_count']
            assert reference['collision_times_seconds'] is None and reference['events_scheduled'] is False and reference['full_cast_count_verified'] is False
            assert all(result['estimate']['skill'][key] is None for key in ('total_damage','phase_damage','cycle_damage','cycle_dps'))
        else:assert 'charge_reference' not in result
    if owner=='kaltsit':
        assert result['estimate']['skill']['healing_targets']==raw['healing_targets']
        if skill==2:
            assert any('治疗量为满额潜在治疗' in note for note in result['estimate']['notes'])
        elif skill in (1,3):
            assert any('真实友方获取时钟未核验' in note for note in result['timing']['target_scope_notes'])
def control_edit(step,value,index):
    global phase,request,explicit_buttons,affected_edits,off_gate_reference,elapsed_reference
    record=begin_record(step,'/value-'+str(index));name=step['widget'];widget=getattr(window,name);old=widget_value(widget)
    assert old!=value,('Each affected stimulus must actually change value',name,old,value)
    record['actual_old_value']=snapshot(old);record['requested_value']=snapshot(value)
    record['constructed_compatibility_stimulus']=not widget.isEnabled() or not widget.isVisible()
    before=dict(counts);all_before=dict(all_entries);api_start=len(API);signal_start=len(signals);qt_start=len(qt_exceptions)
    phase='control_automatic';request='affected_control_signal';affected_edits+=1
    if isinstance(widget,QCheckBox):widget.setChecked(value)
    else:widget.setValue(value)
    application.processEvents();auto_entries=delta(before,counts);auto_all=delta(all_before,all_entries);auto_rows=API[api_start:]
    assert len(qt_exceptions)==qt_start and widget_value(widget)==value
    assert any(row['widget']==name and row['value']['native']==flat_native(widget_value(widget)) for row in signals[signal_start:]),('Actual affected signal missing',name)
    kind=validate_outcome(step,api_start,auto_entries)
    phase='automatic_result_probe';request='explicit_probe';auto=selected_snapshot();auto['three_texts']=three_texts()
    auto.update(actual_entries=auto_entries,actual_all_project_entries=auto_all,API_sequences=[row['sequence'] for row in auto_rows],API_outcomes=API_outcomes(auto_rows),signals=clone(signals[signal_start:]))
    record['automatic_before_any_manual']=auto;checkpoint()
    if window.damage_result is not None:
        result=window.damage_result['result'];existing_result_boundaries(window.damage_result['scenario'],result)
        if name=='deployment_elapsed' and value==14.99:elapsed_reference=result['estimate']['base_stats']['defense']
        if name=='deployment_elapsed' and value==15:
            assert elapsed_reference is not None and result['estimate']['base_stats']['defense']==elapsed_reference+60
            record['source_existing_15_second_defense_increment']=60
        if name=='shield_duration_known' and value is False and window.operator.currentData()=='mechanist' and window.skill.currentData()==2:
            off_gate_reference=auto['damage_result']['native']
        if name=='shield_duration' and not window.shield_duration_known.isChecked():
            assert off_gate_reference is not None and auto['damage_result']['native']==off_gate_reference,'Disabled duration edit retains value but omitted scenario/result remain identical'
    before_manual=dict(counts);all_before_manual=dict(all_entries);manual_api_start=len(API);manual_signal_start=len(signals)
    phase='manual_button';request='actual_compute_button';explicit_buttons+=1
    button=next(item for item in window.findChildren(QPushButton) if item.text()=='计算属性与技能预估');button.click();application.processEvents()
    manual_entries=delta(before_manual,counts);manual_all=delta(all_before_manual,all_entries);manual_rows=API[manual_api_start:]
    assert len(qt_exceptions)==qt_start;assert validate_outcome(step,manual_api_start,manual_entries)==kind
    phase='manual_result_probe';request='explicit_probe';manual=selected_snapshot();manual['three_texts']=three_texts()
    manual.update(actual_entries=manual_entries,actual_all_project_entries=manual_all,API_sequences=[row['sequence'] for row in manual_rows],API_outcomes=API_outcomes(manual_rows),signals=clone(signals[manual_signal_start:]))
    record['explicit_manual_after_automatic']=manual
    assert auto['damage_result']['native']==manual['damage_result']['native'],'Complete typed-native scenario and post-app result must match auto/manual'
    assert auto['visible_status']==manual['visible_status'] and auto['three_texts'].get('strings')==manual['three_texts'].get('strings')
    assert auto['three_texts']['applicable'] is manual['three_texts']['applicable']
    if auto_rows:
        assert auto_rows[-1]['caller_before']['native']==manual_rows[-1]['caller_before']['native'],'Complete typed-native API caller must match auto/manual'
        if kind=='numerical_result':assert auto_rows[-1]['returned']['native']==manual_rows[-1]['returned']['native'],'Complete typed-native numerical API result must match auto/manual'
    record['complete_native_and_three_texts_equal']=True;record['actual_outcome']=kind;finish_record(record)

try:
    phase='runtime_project_imports';request='root_sole_Wine_imports'
    sys.setprofile(profile);sys.settrace(trace);sys.excepthook=qt_hook
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QCheckBox,QPushButton,QScrollArea
    import rouge.app as module
    from rouge.run_state import RunState
    from rouge.capture import list_game_windows
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    application=QApplication([]);application.setQuitOnLastWindowClosed(False);original_backend=module.DesktopBackend
    for group in PLAN['planned_workflow_groups']:
        group_id=group['id']
        for source_index,original_step in enumerate(group['steps'],1):
            step=dict(original_step);step['_source_step_id']=str(source_index);kind=step['kind']
            if kind=='affected_control_edit':
                for index,value in enumerate(step['values_in_order'],1):control_edit(step,value,index)
                continue
            record=begin_record(step)
            if kind=='startup':
                record['startup']=fresh_window(PLAN['fixtures']['lawful_account_owners']);record['context_three_texts']=three_texts();finish_record(record,preserve=False)
            elif kind=='public_real_RunState_setup':
                phase='real_RunState_setup';request='actual_apply_run_observation';before=dict(counts);api_start=len(API)
                members=[]
                for owner in step['account_fixture_owners']:
                    member=clone(PLAN['fixtures']['lawful_account_owners'][owner]);member['scope']='run';members.append(member)
                captured=max(time.time(),window.run.state['started_at']+1,window.run.state.get('last_read') or 0)
                observed={'operators':members,'selected_operator':'silverash','crew_count':None}
                record['real_apply_input']=snapshot({'observed':observed,'captured_at':captured})
                assert window.apply_run_observation(observed,captured);application.processEvents()
                assert set(window.run.state['operators'])==set(step['account_fixture_owners'])
                assert all(window.run.state['operators'][owner]['scope']=='run' for owner in step['account_fixture_owners'])
                record['actual_setup_entries']=delta(before,counts);record['setup_API_outcomes']=API_outcomes(API[api_start:]);record['context_three_texts']=three_texts();finish_record(record,preserve=False)
            elif kind=='existing_context_setup' and step['action']=='fresh-independent-public-window':
                close_window();record['startup']=fresh_window({});phase='common_controls';request='existing_context_setup';common_controls()
                record['context_three_texts']=three_texts();finish_record(record,preserve=False)
            elif kind=='existing_context_setup':
                record['context_actual']=existing_context(step);record['context_three_texts']=three_texts();finish_record(record)
            elif kind in ('planned_success_PNG','planned_error_PNG'):
                record['actual_screenshot']=capture_png(step['name']);record['context_three_texts']=three_texts();finish_record(record)
            else:raise AssertionError(('Unknown source-plan step kind',kind))
    close_window()
    assert affected_edits==PLAN['counts']['affected_value_change_requests']==62 and explicit_buttons==affected_edits
    assert fresh_windows==PLAN['counts']['fresh_windows_planned']==2 and len(pngs)==3
    assert not pending and not qt_exceptions
    assert all(row.get('caller_unchanged',True) for row in CALLS)
    assert all(row['all_outputs_and_affected_controls_exist'] for row in CALLS if row['key']=='MainWindow.calculate')
    assert all(counts.get(key,0)==0 for key in ('GameCapture.capture','GameCapture.next_frame','GameCapture.connect','MainWindow.connect_game','MainWindow.sample_now','MainWindow.sample_received','MainWindow.send_chat','MainWindow.desktop_request','MainWindow.bind_desktop'))
    receipt['passed']=True;receipt['workflow_complete']=True
except BaseException as error:
    receipt['failure']={'type':type(error).__name__,'message':str(error),'step':current,'traceback':traceback.format_exc()}
    if window is not None:
        try:
            phase='failure_UI_probe';request='explicit_probe';receipt['failure_ui']=ui_snapshot()
        except Exception as snapshot_error:receipt['failure_ui_error']={'type':type(snapshot_error).__name__,'message':str(snapshot_error)}
        try:
            path=OUT/'wine-focused-inputs-failure-094.png'
            if window.grab().save(str(path)):receipt['failure_screenshot']={'file':path.name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())}
        except Exception as screenshot_error:receipt['failure_screenshot_error']=str(screenshot_error)
finally:
    try:close_window()
    except Exception as close_error:
        receipt['passed']=False;receipt['workflow_complete']=False;receipt['close_error']={'type':type(close_error).__name__,'message':str(close_error)}
    sys.setprofile(previous_profile);sys.settrace(previous_trace);sys.excepthook=previous_excepthook
    after={rel:digest((ROOT/rel).read_bytes()) for rel in SOURCE_HASHES};receipt['source_sha256_after']=after
    receipt['source_drift']=[rel for rel in SOURCE_HASHES if after[rel]!=SOURCE_HASHES[rel]]
    if receipt['source_drift']:receipt['passed']=False;receipt['workflow_complete']=False
    receipt['actual_function_entries']=counts;receipt['all_rouge_main_thread_entries']=all_entries;receipt['all_rouge_entries_by_phase_and_request']=entries_by_scope
    receipt['explicit_button_requests']=explicit_buttons;receipt['explicit_three_text_requests']=explicit_texts
    receipt['affected_value_change_requests']=affected_edits;receipt['fresh_windows']=fresh_windows;receipt['actual_API_outcomes']=API_outcomes(API)
    receipt['actual_API_by_phase_and_request']={key:sum(row['phase']+'/'+row['request']==key for row in API) for key in sorted({row['phase']+'/'+row['request'] for row in API})}
    receipt['actual_PNGs']=pngs;receipt['stdlib_checkpoint_pauses']=checkpoint_pauses+1;receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    folders.close()
    print(json.dumps({'passed':receipt['passed'],'states':len(states),'checks':len(checks),'affected_value_changes':affected_edits,'records':receipt['records'],'failure':receipt.get('failure')},ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
