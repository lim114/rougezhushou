PENDING_PREPARATION = False
if PENDING_PREPARATION:
    raise SystemExit('Pending093 actual root source guard and fresh final source-only review; root alone executes Wine')
"""One Wine process, fresh real MainWindows, public isolated account fixtures."""
import gzip,hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat')
EXPECTED_GUARD_SHA256='0fbfe28e2528ae9987f9f260bfed0068b1e16edf02274ea3349cd6d988aa2180'
GUARD=Path(__file__).with_name('wine-account-window-093-source.json')
assert hashlib.sha256(GUARD.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA256
SOURCE=json.loads(GUARD.read_text(encoding='utf-8'));SOURCE_HASHES=SOURCE['source_sha256_after']
assert SOURCE['passed'] is True and len(SOURCE_HASHES)==732
for rel,digest in SOURCE_HASHES.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,('source before Qt',rel)
PLAN_PATH=Path(__file__).with_name('wine-account-window-093-plan.json')
assert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='6ff61e9d3bf12ee822efecf627b38bbbe9e4a8e608d93eff8b108191c150e5e3'
PLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))
assert hashlib.sha256((ROOT/'rouge/app.py').read_bytes()).hexdigest()==PLAN['candidate_v2_app']['sha256']
assert hashlib.sha256((ROOT/'rouge/account_cache.py').read_bytes()).hexdigest()==PLAN['candidate_v2_helper']['sha256']
RECEIPT=OUT/'wine-account-window-093.json';ARCHIVE=OUT/'wine-account-window-093-records.json.gz'
assert not RECEIPT.exists() and not ARCHIVE.exists(),'Preserve previous evidence; never replay a successful prefix'
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

counts={};all_entries={};signals=[];API=[];CALLS=[];pending={};side_effects=[];qt_exceptions=[];states=[];checks=[]
phase='preparation';request='none';case_id=None;current='before-first-window';explicit_buttons=0;explicit_texts=0
window=None;application=None;active_folder=None;account_path=None;started=time.perf_counter()
previous_profile=sys.getprofile();previous_trace=sys.gettrace();previous_excepthook=sys.excepthook
receipt={'format_version':1,'passed':False,'workflow_complete':False,'source_guard_sha256':EXPECTED_GUARD_SHA256,
    'source_sha256_before':SOURCE_HASHES,'plan_counts':PLAN['counts'],'checks':checks,'private_state_isolated':True,
    'game_capture_requests':0,'chat_requests':0,'native_game_clock_certified':False,'old92_matrix_replayed':False,
    'native_codec':'flat-typed-graph-v1; iterative inverse checked for each snapshot; JSON projection retains values, native retains exact types/key types/order/float hex/aliases',
    'coverage_limits':PLAN['coverage_limits']}

def path_of(frame):return frame.f_code.co_filename.replace('\\','/').lower()
def frame_inputs(frame,key):
    local=frame.f_locals
    if key=='calculate_damage':return {'scenario':local['scenario']}
    if key=='RunState.apply':return {'observed':local['observed'],'captured_at':local['captured_at']}
    if key=='AccountCache.observe':return {'operator':local['operator'],'captured_at':local['captured_at']}
    if key=='account_cache._merged_record':return {name:local[name] for name in ('operator','captured_at','saved')}
    if key=='account_cache._record_issue':return {'op':local['op'],'record':local['record']}
    if key=='account_cache._timestamp':return {'value':local['value']}
    if key in ('AccountCache.view','AccountCache.notice'):return {name:local[name] for name in ('op','run_confirmed') if name in local}
    if key=='MainWindow.apply_operator_observation':return {'operator':local['operator'],'captured_at':local['captured_at']}
    if key=='MainWindow.apply_run_observation':return {'observed':local['observed'],'captured_at':local['captured_at']}
    if key=='MainWindow.sample_received':
        image,observed=local['result']
        return {'observation':observed,'public_image':{'shape':list(image.shape),'dtype':str(image.dtype),'bytes_hex':image.tobytes().hex()}}
    return None

def trace_local(frame,event,arg):
    if event=='exception' and id(frame) in pending:
        pending[id(frame)].setdefault('exception_events',[]).append({'type':arg[0].__name__,'message':str(arg[1]),'args':snapshot(arg[1].args)})
    return trace_local
def trace(frame,event,arg):
    path=path_of(frame)
    if event=='call' and (path.endswith('/rouge/account_cache.py') or path.endswith('/rouge/damage.py') and frame.f_code.co_name=='calculate_damage'
                         or path.endswith('/rouge/app.py') or path.endswith('/rouge/run_state.py')):return trace_local
    return None

def profile(frame,event,arg):
    path=path_of(frame);name=frame.f_code.co_name
    if event=='call' and account_path is not None and name in ('mkdir','write_text','replace') and path.endswith('/pathlib.py'):
        caller=frame.f_back
        if caller is not None and path_of(caller).endswith('/rouge/account_cache.py'):
            side_effects.append({'case':case_id,'step':current,'phase':phase,'method':'Path.'+name,'path':str(frame.f_locals.get('self')),
                                 'target':str(frame.f_locals.get('target')) if 'target' in frame.f_locals else None})
    if event=='call' and '/rouge/' in path:
        full='rouge/'+path.split('/rouge/',1)[1]+':'+frame.f_code.co_qualname
        all_entries[full]=all_entries.get(full,0)+1;key=None
        if path.endswith('/rouge/damage.py') and name=='calculate_damage':key='calculate_damage'
        elif path.endswith('/rouge/estimate.py') and name=='format_estimate':key='format_estimate'
        elif path.endswith('/rouge/reporting.py') and name=='format_report':key='format_report_technical' if frame.f_locals['technical'] else 'format_report_default'
        elif path.endswith('/rouge/operator_summary.py') and name=='format_operator_observation':key='format_operator_observation'
        elif path.endswith('/rouge/capture.py') and name in ('capture','next_frame'):key='GameCapture.'+name
        elif path.endswith('/rouge/account_cache.py'):
            key=('AccountCache.' if 'self' in frame.f_locals else 'account_cache.')+name
        elif path.endswith('/rouge/run_state.py') and name in ('__init__','apply','save','reset'):key='RunState.'+name
        elif path.endswith('/rouge/app.py') and name in ('__init__','calculate','sample_received','sample_now','send_chat','apply_operator_observation','apply_run_observation','current_operator_state','update_operator','level_changed','show_observed_operator'):key='MainWindow.'+name
        if key:counts[key]=counts.get(key,0)+1
        if key and (key=='calculate_damage' or key.startswith(('AccountCache.','account_cache.','RunState.','MainWindow.'))):
            record={'sequence':len(CALLS)+1,'key':key,'case':case_id,'step':current,'phase':phase,'request':request,'outcome':'pending'}
            inputs=frame_inputs(frame,key)
            if inputs is not None:record['caller_before']=snapshot(inputs)
            if key=='AccountCache.__init__':record['source_bound_catalog_arguments']={'profiles':431,'implemented_ids':32,'path':str(frame.f_locals['path'])}
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
            owner=frame.f_locals['self'];record['outcome']='numerical_result_available' if owner.damage_result else 'no_numerical_result'
            record['visible_status']=owner.damage_text.toPlainText()
        elif arg is not None:
            record['outcome']='returned_value'
            if type(arg) in (dict,list,tuple,bool,int,float,str):record['returned']=snapshot(arg)
        else:record['outcome']='returned_none_with_exception_events' if record.get('exception_events') else 'returned_none'
    return profile

def checkpoint():
    payload={'format_version':1,'native_schema':'flat-typed-graph-v1','current_step':current,'passed':receipt['passed'],
             'states':states,'checks':checks,'signals':signals,'API_entries':API,'all_targeted_calls':CALLS,
             'actual_python_entries':counts,'all_rouge_main_thread_entries':all_entries,'account_file_side_effects':side_effects,
             'Qt_slot_exceptions':qt_exceptions,'explicit_buttons':explicit_buttons,'explicit_three_text_requests':explicit_texts}
    raw=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8');compressed=gzip.compress(raw,mtime=0);ARCHIVE.write_bytes(compressed)
    receipt['records']={'file':ARCHIVE.name,'bytes':len(compressed),'sha256':digest(compressed),'decoded_bytes':len(raw),'decoded_sha256':digest(raw)}
def qt_hook(kind,error,tb):
    qt_exceptions.append({'case':case_id,'step':current,'phase':phase,'type':kind.__name__,'message':str(error),'traceback':''.join(traceback.format_exception(kind,error,tb))})

def ui_snapshot():
    if window is None:return None
    state=window.current_operator_state()
    return {'owner':window.operator.currentData(),'skill':window.skill.currentData(),'level':window.level.value(),
            'level_override':window.level_override,'use_run_training':window.use_run_training.isChecked(),
            'training_status':window.training_status.text(),'elite':window.elite.text(),'trust':window.trust.text(),
            'potential':window.potential.text(),'module':window.module.text(),'rank':window.rank.text(),
            'damage_text':window.damage_text.toPlainText(),'operator_summary':window.operator_summary.toPlainText(),
            'current_operator_state':snapshot(state),'account_records':snapshot(window.account_cache.records),
            'account_issues':snapshot(window.account_cache.issues),'load_issue':window.account_cache.load_issue,
            'preserve_original':window.account_cache.preserve_original,'run_state':snapshot(window.run.state),
            'result':snapshot(window.damage_result),'timing_text':window.timing_scenario.toPlainText(),
            'relic_context_text':window.relic_context.toPlainText(),'visible':window.isVisible()}
def check_chain(value,label):
    for _ in range(500):assert type(value) is dict and list(value)==['next'];value=value['next']
    assert value=={'sentinel':'public-093-'+label,'values':[None,False,0,'原值']}

try:
    import numpy as np
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton,QScrollArea
    import rouge.app as module
    from rouge.run_state import RunState
    from rouge.capture import list_game_windows
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    from rouge.account_cache import RUN_METADATA
    application=QApplication([]);application.setQuitOnLastWindowClosed(False)
    original_backend=module.DesktopBackend
    sys.setprofile(profile);sys.settrace(trace);sys.excepthook=qt_hook
    for case in PLAN['cases']:
        case_id=case['id'];phase='public_fixture';request='fixture'
        with tempfile.TemporaryDirectory(prefix='public-account093-') as folder:
            active_folder=Path(folder);account_path=active_folder/'account.json';run_path=active_folder/'run.json'
            module.OPERATOR_STATE=account_path;module.RUN_STATE=run_path;module.SETTINGS=active_folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:original_backend(active_folder/'chat',callback)
            if not case.get('disk_missing'):
                raw=case['disk_raw'].encode('utf-8') if case.get('disk_raw') is not None else json.dumps(case['disk_decoded'],ensure_ascii=False,allow_nan=False).encode('utf-8')
                account_path.write_bytes(raw)
            original_account=file_bytes(account_path);original_files=filesystem(active_folder)
            for step in case['steps']:
                current=case_id+'/'+step['id'];before=dict(counts);api_before=len(API);signal_before=len(signals);write_before=len(side_effects);qt_before=len(qt_exceptions)
                phase='probe_before';request='explicit_probe'
                before_files=filesystem(active_folder);before_account=file_bytes(account_path)
                before_run=snapshot(window.run.state) if window is not None else None
                before_record=snapshot(window.account_cache.records) if window is not None else None
                record={'id':current,'planned':snapshot(step),'passed':False,'original_account_hex':original_account.hex() if original_account is not None else None,
                        'original_files':original_files,'files_before':before_files,'actual_entries_before':before,'before_run':before_run,'before_account_records':before_record}
                states.append(record);checkpoint();action=step['action'];phase='startup' if action=='startup' else 'action';request='manual_button' if action=='button' else 'Qt_slot_or_internal'
                if action=='startup':
                    assert window is None
                    window=module.MainWindow();window.show();application.processEvents()
                    assert type(window.run) is RunState
                    assert window.operator_observations is window.account_cache.records
                    assert window.isVisible() and not window.auto.isChecked() and window.capture.target is None and not list_game_windows()
                    assert not window.desktop.process and not window.desktop_request_busy
                    record['startup_actual_entries']=delta(before,counts);phase='probe_startup';request='explicit_probe';record['startup_ui_before_common']=ui_snapshot();checkpoint()
                    window.operator.currentIndexChanged.connect(lambda v:signals.append({'step':current,'signal':'operator.currentIndexChanged','value':snapshot(v)}))
                    window.level.valueChanged.connect(lambda v:signals.append({'step':current,'signal':'level.valueChanged','value':snapshot(v)}))
                    window.use_run_training.toggled.connect(lambda v:signals.append({'step':current,'signal':'use_run_training.toggled','value':snapshot(v)}))
                    window.timing_scenario.textChanged.connect(lambda:signals.append({'step':current,'signal':'timing.textChanged','text':window.timing_scenario.toPlainText()}))
                    window.relic_context.textChanged.connect(lambda:signals.append({'step':current,'signal':'relic_context.textChanged','text':window.relic_context.toPlainText()}))
                    phase='common_controls';request='Qt_slot_or_internal';window.centralWidget().setCurrentIndex(1)
                    window.auto_relics.setChecked(False);window.frame_timing.setChecked(False);window.defense.setValue(0);window.resistance.setValue(0)
                    window.target_enemy.setCurrentIndex(0);window.cooperative.setChecked(False);window.fragile.setChecked(False)
                    window.target_buff_test.setChecked(False);window.raw_damage.setChecked(False);window.damage_technical.setChecked(False)
                    window.timing_scenario.clear();window.relic_context.clear();application.processEvents()
                    record['startup_and_common_actual_entries']=delta(before,counts)
                elif action=='select':assert window.select_operator(step['owner'])
                elif action=='observe':window.apply_operator_observation(step['operator'],step['captured_at'])
                elif action=='sample':
                    captured=max(time.time(),window.run.state['started_at']+1,window.last_sample_at+1)
                    observation={'captured_at':captured,'page':'operator_detail','nodes':[],'operator':step['operator']}
                    record['public_sample_input']=snapshot(observation);window.events.sample.emit((np.zeros((8,8,3),dtype=np.uint8),observation))
                elif action=='run':
                    captured=max(time.time(),window.run.state['started_at']+1,window.run.state.get('last_read') or 0)
                    record['runtime_run_input']=snapshot({'observed':step['observed'],'captured_at':captured})
                    assert window.apply_run_observation(step['observed'],captured)
                elif action=='button':
                    button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估');explicit_buttons+=1;button.click()
                elif action=='restore_level':next(b for b in window.findChildren(QPushButton) if b.text()=='使用读取等级').click()
                elif action=='level':assert window.level.value()!=step['value'];window.level.setValue(step['value'])
                elif action=='run_training':window.use_run_training.setChecked(step['value'])
                elif action=='overview':assert window.operator_choices.select_branch('__overview__')
                elif action=='timing':window.timing_scenario.setPlainText(step['text'])
                elif action=='relic_context':window.relic_context.setPlainText(step['text'])
                elif action=='relic':
                    item=next(window.relic_list.item(i) for i in range(window.relic_list.count()) if window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)==step['rid'])
                    item.setCheckState(Qt.CheckState.Checked if step['checked'] else Qt.CheckState.Unchecked)
                elif action=='view_top':
                    view=window.account_cache.view('kaltsit');check_chain(view['extra_metadata'],step['chain_label']);view['public-view-only-093']=True
                    assert 'public-view-only-093' not in window.account_cache.records['kaltsit']
                else:raise AssertionError(('unknown public action',action))
                application.processEvents();phase='probe_after';request='explicit_probe'
                record['actual_ui']=ui_snapshot();record['files_after']=filesystem(active_folder)
                record['signals']=clone(signals[signal_before:]);record['account_side_effects']=clone(side_effects[write_before:]);checkpoint()
                assert len(qt_exceptions)==qt_before,('Qt slot exception',qt_exceptions[qt_before:])
                assert window.operator_observations is window.account_cache.records
                if 'preserve' in step:assert window.account_cache.preserve_original is step['preserve']
                if case.get('protect_original_all_steps') or window.account_cache.preserve_original:
                    assert file_bytes(account_path)==original_account
                    assert not side_effects[write_before:],'Protected account save must skip mkdir/write/replace entirely'
                    assert not account_path.with_suffix('.tmp').exists()
                if step.get('issue'):
                    assert window.account_cache.issues[step['issue_owner']]==step['issue']
                if step.get('load_issue'):assert window.account_cache.load_issue==step['load_issue']
                if step.get('cleared_issue'):assert step['cleared_issue'] not in window.account_cache.issues
                if window.account_cache.preserve_original:assert '原账号档案文件已保留' in window.training_status.text()
                if 'expected_owner' in step:assert window.operator.currentData()==step['expected_owner']
                if action=='select':assert window.operator.currentData()==step['owner']
                if 'expected_level' in step:assert window.level.value()==step['expected_level']
                if 'expected_override' in step:assert window.level_override is step['expected_override']
                if 'expected_fields' in step:assert flat_native(window.current_operator_state().get('fields',{}))==flat_native(step['expected_fields'])
                if before_run is not None and not step.get('run_update'):
                    assert flat_native(window.run.state)==before_run['native'],'Account/browse/preview must leave real RunState unchanged'
                    assert next((r for r in before_files if r['path']=='run.json'),None)==next((r for r in record['files_after'] if r['path']=='run.json'),None)
                if step.get('unchanged_account'):
                    assert flat_native(window.account_cache.records)==before_record['native'] and file_bytes(account_path)==before_account
                if step.get('unchanged_account_file'):assert file_bytes(account_path)==before_account
                if step.get('expect_account_changed'):assert file_bytes(account_path)!=before_account
                if step.get('expect_account_created'):assert before_account is None and account_path.exists()
                if case.get('unknown_id'):assert flat_native(window.account_cache.records[case['unknown_id']])==flat_native(case['disk_decoded'][case['unknown_id']])
                if step.get('merge')=='clean-first':
                    saved=window.account_cache.records['silverash']
                    assert saved['fields']=={**case['disk_decoded']['silverash']['fields'],'level':65,'trust':55}
                    assert saved['skill_ranks']=={'1':7,'3':10} and saved['captured_at']==120
                    assert saved['sources']=={'level':'public-synthetic-old-093','trust':'public-new-093'}
                    assert saved['field_times']=={'level':120,'elite':90,'trust':120} and saved['skill_times']=={'1':100,'3':120}
                    assert 'old_extra' not in saved
                if step.get('incoming_only'):
                    saved=window.account_cache.records['silverash']
                    assert saved['fields']=={'elite':2} and saved['skill_ranks']=={} and saved['captured_at']==200
                    assert saved['sources']=={'elite':'new-public'} and saved['field_times']=={'elite':200} and saved['skill_times']=={}
                    assert 'old_extra' not in saved and 'invalid_skill_ranks' not in saved
                    assert '未确认' in window.trust.text() and '未确认' in window.rank.text()
                if step.get('chain_label'):
                    check_chain(window.account_cache.records['kaltsit']['extra_metadata'],step['chain_label'])
                    check_chain(window.account_cache.view('kaltsit')['extra_metadata'],step['chain_label'])
                if step.get('deep_merge'):
                    saved=window.account_cache.records['kaltsit'];check_chain(saved['sources']['opaque'],'source-old')
                    assert saved['sources']['new']=='public' and 'old_extra' not in saved
                    stored=json.loads(account_path.read_text());check_chain(stored['kaltsit']['extra_metadata'],'new');check_chain(stored['kaltsit']['sources']['opaque'],'source-old')
                if step.get('sanitized'):
                    assert not (set(window.account_cache.view('kaltsit')) & RUN_METADATA)
                    assert '应急雇佣' not in window.operator_summary.toPlainText() and '本局进阶' not in window.operator_summary.toPlainText()
                    assert not window.run.state['operators']
                if step.get('run_precedence'):
                    state=window.current_operator_state();member=window.run.state['operators']['silverash']
                    assert state['scope']=='run' and state['fields']==member['fields'] and state['skill_ranks']==member['skill_ranks']
                    assert state['captured_at']==member['captured_at'] and state['public_metadata']==member['public_metadata']
                    assert '本局已确认培养' in window.training_status.text()
                shape=step.get('shape')
                if shape:
                    assert window.damage_result is None and len(API)==api_before,'Natural early return must not fabricate a numerical result'
                    record['three_texts']='inapplicable: natural existing early return, numerical API not called'
                    if shape=='overview':assert window.operator.currentData() is None and '本局总览暂无已确认招募干员' in window.damage_text.toPlainText()
                    else:
                        assert '技能伤害规则尚未实现' in window.damage_text.toPlainText()
                        if shape=='unimplemented-no-skill':assert window.skill.currentData() is None and window.rank.text()=='无可用技能' and '无技能' in window.damage_text.toPlainText()
                elif step.get('error'):
                    assert window.damage_result is None and window.damage_text.toPlainText()==step['error']
                    if step['numeric_error']:assert len(API)>api_before and API[-1]['outcome']=='raised_exception'
                    else:assert len(API)==api_before
                    record['three_texts']='inapplicable: existing JSON error before numerical API';record['visible_error']=window.damage_text.toPlainText()
                else:
                    assert window.damage_result,window.damage_text.toPlainText()
                    raw=window.damage_result['scenario'];result=window.damage_result['result'];raw_native=flat_native(raw);result_native=flat_native(result)
                    phase='explicit_three_texts';request='explicit_formatter';record['three_texts']={'estimate':format_estimate(result),'default':format_report(result),'technical':format_report(result,technical=True)};explicit_texts+=3;checkpoint()
                    assert record['three_texts']['estimate']==record['three_texts']['default']
                    assert window.damage_text.toPlainText()==record['three_texts']['default'].replace(chr(160),' ')
                    phase='technical_view_signals';request='Qt_slot_or_internal';window.damage_technical.setChecked(True);application.processEvents()
                    assert window.damage_text.toPlainText()==record['three_texts']['technical'].replace(chr(160),' ')
                    window.damage_technical.setChecked(False);application.processEvents()
                    assert window.damage_text.toPlainText()==record['three_texts']['default'].replace(chr(160),' ')
                    assert flat_native(raw)==raw_native and flat_native(result)==result_native
                    if step.get('sanitized'):assert raw['recruitment_kind'] is None and raw['char_buff_ids']==[] and raw['char_buffs_complete'] is False
                    if 'expected_relic_context' in step:assert raw['relic_context']==step['expected_relic_context']
                    if step.get('run_precedence'):assert raw['skill_rank']==7 and raw['level']==window.level.value() and raw['elite']==1
                if step.get('screenshot'):
                    label=window.training_status;parent=label.parentWidget()
                    while parent is not None and not isinstance(parent,QScrollArea):parent=parent.parentWidget()
                    if parent is not None:parent.ensureWidgetVisible(label)
                    application.processEvents();path=OUT/step['screenshot'];assert window.grab().save(str(path))
                    record['actual_screenshot']={'file':path.name,'bytes':path.stat().st_size,'sha256':digest(path.read_bytes()),'training_status_visible':label.isVisible(),'training_status':label.text()}
                record['actual_entries']=delta(before,counts);record['API_outcomes']={outcome:sum(r['outcome']==outcome for r in API[api_before:]) for outcome in ('returned_dict','raised_exception','returned_non_dict_or_unobserved_unwind')}
                record['passed']=True;checks.append({'id':current,'passed':True,'outcome':'natural_early_return' if shape else 'existing_error' if step.get('error') else 'numerical_result'})
                checkpoint()
            phase='close';request='window_close';before_close=filesystem(active_folder)
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process and not active_folder.joinpath('chat').exists()
            window.close();application.processEvents();window.deleteLater();application.processEvents();window=None
            assert filesystem(active_folder)==before_close
    assert len(checks)==PLAN['counts']['planned_states'] and explicit_buttons==PLAN['counts']['manual_button_requests']
    assert not pending and not qt_exceptions
    assert all(counts.get(key,0)==0 for key in ('GameCapture.capture','GameCapture.next_frame','MainWindow.sample_now','MainWindow.send_chat'))
    receipt['game_capture_requests']=counts.get('GameCapture.capture',0)
    receipt['chat_requests']=counts.get('MainWindow.send_chat',0)
    assert all(record.get('caller_unchanged',True) for record in CALLS if record['key'] in ('calculate_damage','AccountCache.observe','MainWindow.apply_operator_observation','MainWindow.apply_run_observation','RunState.apply','MainWindow.sample_received'))
    receipt['actual_API_outcomes']={outcome:sum(r['outcome']==outcome for r in API) for outcome in ('returned_dict','raised_exception','returned_non_dict_or_unobserved_unwind')}
    receipt['actual_API_by_phase_and_request']={key:sum(r['phase']+'/'+r['request']==key for r in API) for key in sorted({r['phase']+'/'+r['request'] for r in API})}
    receipt['numeric_state_success_count']=sum(c['outcome']=='numerical_result' for c in checks)
    receipt['actual_existing_error_count']=sum(c['outcome']=='existing_error' for c in checks)
    receipt['actual_natural_early_return_count']=sum(c['outcome']=='natural_early_return' for c in checks)
    receipt['passed']=True;receipt['workflow_complete']=True
except BaseException as error:
    receipt['failure']={'type':type(error).__name__,'message':str(error),'step':current,'traceback':traceback.format_exc()}
    if window is not None:
        try:receipt['failure_ui']=ui_snapshot()
        except Exception as snapshot_error:receipt['failure_ui_error']={'type':type(snapshot_error).__name__,'message':str(snapshot_error)}
        try:
            path=OUT/'wine-account-window-failure-093.png'
            if window.grab().save(str(path)):receipt['failure_screenshot']=path.name
        except Exception as screenshot_error:receipt['failure_screenshot_error']=str(screenshot_error)
finally:
    sys.setprofile(previous_profile);sys.settrace(previous_trace);sys.excepthook=previous_excepthook
    if window is not None:
        window.close()
        if application is not None:application.processEvents()
    after={rel:digest((ROOT/rel).read_bytes()) for rel in SOURCE_HASHES};receipt['source_sha256_after']=after
    receipt['source_drift']=[rel for rel in SOURCE_HASHES if after[rel]!=SOURCE_HASHES[rel]]
    if receipt['source_drift']:receipt['passed']=False;receipt['workflow_complete']=False
    receipt['actual_function_entries']=counts;receipt['all_rouge_main_thread_entries']=all_entries
    receipt['explicit_button_requests']=explicit_buttons;receipt['explicit_three_text_requests']=explicit_texts
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'passed':receipt['passed'],'states':len(states),'checks':len(checks),'records':receipt['records'],'failure':receipt.get('failure')},ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
