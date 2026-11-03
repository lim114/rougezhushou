PENDING_PREPARATION = True
if PENDING_PREPARATION:
    raise SystemExit('Pending focused92 actual root source guard and sole static formal; root alone executes final runner')
"""Focused actual MainWindow workflow, no old91/full90 matrix replay."""
import copy,gzip,hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat')
EXPECTED_GUARD_SHA256='PENDING_ACTUAL_ROOT_SOURCE_SHA256'
GUARD=Path(__file__).with_name('wine-focused-window-092-source.json')
assert hashlib.sha256(GUARD.read_bytes()).hexdigest()==EXPECTED_GUARD_SHA256
SOURCE=json.loads(GUARD.read_text(encoding='utf-8'))
SOURCE_HASHES=SOURCE['source_sha256_after']
assert len(SOURCE_HASHES)==730
for rel,digest in SOURCE_HASHES.items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,('source before Qt',rel)
PLAN=json.loads(Path(__file__).with_name('wine-focused-window-092-plan.json').read_text(encoding='utf-8'))
assert len(PLAN['rows'])==19
RECEIPT=OUT/'wine-focused-window-092.json';ARCHIVE=OUT/'wine-focused-window-092-records.json.gz'
assert not RECEIPT.exists() and not ARCHIVE.exists(),'Preserve previous outputs; do not replay successful states'
sys.path.insert(0,str(ROOT))
counts={};library_counts={};signals=[];API=[];MAIN=[];pending_api={};pending_main={}
states=[];checks=[];current='startup';explicit_buttons=0;explicit_texts=0
window=None;application=None;started=time.perf_counter()
receipt={'format_version':1,'passed':False,'focused_window_complete':False,'native_game_clock_certified':False,
    'source_guard_sha256':EXPECTED_GUARD_SHA256,'source_sha256_before':SOURCE_HASHES,
    'planned_states':19,'planned_numeric_states':15,'planned_error_states':4,'checks':checks,
    'private_state_isolated':True,'game_capture_requests':0,'chat_requests':0,'old91_or_full90_replayed':False}

def native(v):
    if v is None or type(v) in (bool,int,str):return {'type':type(v).__name__,'value':v}
    if type(v) is float:return {'type':'float','hex':v.hex()}
    if type(v) in (list,tuple):return {'type':type(v).__name__,'items':[native(x) for x in v]}
    if type(v) is dict:return {'type':'dict','items':[[native(k),native(x)] for k,x in v.items()]}
    raise TypeError(('unsupported native transport',type(v).__name__))

def delta(before,after):return {k:after.get(k,0)-before.get(k,0) for k in sorted(set(before)|set(after))}

def trace_local(frame,event,arg):
    if event=='exception':
        record=pending_api.get(id(frame)) or pending_main.get(id(frame))
        if record is not None:
            record.setdefault('exception_events',[]).append({'type':arg[0].__name__,'message':str(arg[1]),'args_native':native(arg[1].args)})
    return trace_local

def trace(frame,event,arg):
    path=frame.f_code.co_filename.replace('\\','/').lower()
    if event=='call' and ((path.endswith('/rouge/damage.py') and frame.f_code.co_name=='calculate_damage') or
                         (path.endswith('/rouge/app.py') and frame.f_code.co_name=='calculate')):
        return trace_local
    return None

def profile(frame,event,arg):
    path=frame.f_code.co_filename.replace('\\','/').lower();name=frame.f_code.co_name
    if event=='call' and '/rouge/' in path:
        key='rouge/'+path.split('/rouge/',1)[1]+':'+name
        library_counts[key]=library_counts.get(key,0)+1
        key=None
        if path.endswith('/rouge/app.py') and name=='calculate':key='MainWindow.calculate'
        elif path.endswith('/rouge/damage.py') and name=='calculate_damage':key='calculate_damage'
        elif path.endswith('/rouge/estimate.py') and name=='format_estimate':key='format_estimate'
        elif path.endswith('/rouge/reporting.py') and name=='format_report':key='format_report_technical' if frame.f_locals['technical'] else 'format_report_default'
        elif path.endswith('/rouge/run_state.py') and name in ('__init__','apply','load'):key='RunState.'+name
        if key:counts[key]=counts.get(key,0)+1
        if key=='calculate_damage':
            rec={'sequence':len(API)+1,'step':current,'scenario':copy.deepcopy(frame.f_locals['scenario']),
                'caller_native_before':native(frame.f_locals['scenario']),'outcome':'pending'}
            API.append(rec);pending_api[id(frame)]=rec
        elif key=='MainWindow.calculate':
            rec={'sequence':len(MAIN)+1,'step':current,'API_entries_before':counts.get('calculate_damage',0),'outcome':'pending'}
            MAIN.append(rec);pending_main[id(frame)]=rec
    elif event=='return' and id(frame) in pending_api:
        rec=pending_api.pop(id(frame));rec['caller_native_after']=native(frame.f_locals['scenario'])
        rec['caller_native_unchanged']=rec['caller_native_before']==rec['caller_native_after']
        if type(arg) is dict:
            rec.update(outcome='returned_dict',result=copy.deepcopy(arg),result_native=native(arg))
        elif rec.get('exception_events'):rec['outcome']='raised_exception'
        else:rec['outcome']='returned_non_dict_or_unobserved_unwind'
    elif event=='return' and id(frame) in pending_main:
        rec=pending_main.pop(id(frame));owner=frame.f_locals['self']
        rec['numeric_entries']=counts.get('calculate_damage',0)-rec['API_entries_before']
        if getattr(owner,'damage_result',None):rec['outcome']='numerical_result_available'
        else:
            rec['outcome']='no_numerical_result'
            rec['visible_status']=owner.damage_text.toPlainText() if hasattr(owner,'damage_text') else None
    return profile

def checkpoint():
    data=json.dumps({'format_version':1,'current_step':current,'passed':receipt['passed'],'states':states,'checks':checks,
        'signals':signals,'API_entries':API,'MainWindow_calculate_entries':MAIN,'actual_python_entries':counts,
        'all_rouge_main_thread_entries':library_counts,'explicit_buttons':explicit_buttons,'explicit_three_text_requests':explicit_texts},
        ensure_ascii=False,allow_nan=False).encode('utf-8')
    compressed=gzip.compress(data,mtime=0);ARCHIVE.write_bytes(compressed)
    receipt['lossless_records']={'file':ARCHIVE.name,'states':len(states),'bytes':len(compressed),'sha256':hashlib.sha256(compressed).hexdigest(),
        'decoded_bytes':len(data),'decoded_sha256':hashlib.sha256(data).hexdigest()}

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton,QCheckBox
    from PySide6.QtGui import QTextCursor
    import rouge.app as module
    from rouge.reporting import format_report
    from rouge.estimate import format_estimate
    from rouge.operator_options import OPTIONS
    from rouge.capture import list_game_windows
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        original_backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:original_backend(isolated/'chat',callback)
        previous_profile=sys.getprofile();previous_trace=sys.gettrace()
        sys.setprofile(profile);sys.settrace(trace)
        application=QApplication([]);window=module.MainWindow();window.show();application.processEvents()
        assert window.isVisible() and window.limit_window.isChecked() is False and window.window_seconds.value()==40
        assert window.continuous_attacks.isChecked() is True
        assert window.damage_form.labelForField(window.continuous_attacks).text()=='普攻回技力条件'
        assert window.limit_window.text()=='使用指定观察窗口（秒）'
        tooltip='只改变当前技能模型的观察范围，不把输入秒数当作技能持续时间；实际已计窗口见报告。已计窗口为0秒时不计算窗口平均DPS/HPS，未定位来源与未知回转仍保持原说明。'
        assert window.limit_window.toolTip()==window.window_seconds.toolTip()==tooltip
        assert '区间按30Hz模拟帧换算，换算后结束须晚于开始' in window.timing_scenario.toolTip()
        assert '常规连续攻击参考不按供靶/移动/中断区间逐帧调度' in window.timing_scenario.toolTip()
        assert not window.auto.isChecked() and window.capture.target is None and not list_game_windows()
        assert not window.desktop.process and not window.desktop_request_busy
        receipt['startup_actual_entries']=dict(counts)
        window.limit_window.toggled.connect(lambda v:signals.append({'step':current,'signal':'limit_window.toggled','value_native':native(v)}))
        window.window_seconds.valueChanged.connect(lambda v:signals.append({'step':current,'signal':'window_seconds.valueChanged','value_native':native(v)}))
        window.frame_timing.toggled.connect(lambda v:signals.append({'step':current,'signal':'frame_timing.toggled','value_native':native(v)}))
        window.timing_scenario.textChanged.connect(lambda:signals.append({'step':current,'signal':'timing_scenario.textChanged','text':window.timing_scenario.toPlainText()}))
        window.centralWidget().setCurrentIndex(1);application.processEvents()
        button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估')
        widgets={(owner,key):widget for owner,key,_skills,widget in window.model_option_widgets}
        window.use_run_training.setChecked(False);window.auto_relics.setChecked(False)
        window.run.state={**window.run.state,'operators':{},'config':{}}
        window.target_enemy.setCurrentIndex(0);window.defense.setValue(0);window.resistance.setValue(0)
        window.cooperative.setChecked(False);window.fragile.setChecked(False)
        window.deployment_elapsed.setValue(0);window.healing_targets.setValue(1)
        window.frame_timing.setChecked(False);window.timing_scenario.clear();window.relic_context.clear()
        window.target_buff_test.setChecked(False);window.raw_damage.setChecked(False);window.damage_technical.setChecked(False)
        for i in range(window.relic_list.count()):
            item=window.relic_list.item(i)
            if item.checkState()!=Qt.CheckState.Unchecked:item.setCheckState(Qt.CheckState.Unchecked)
        receipt['startup_and_common_actual_entries']=dict(counts)
        phase_before=dict(counts);results={};raws={};components={}

        def train(row):
            owner=row['owner']
            for key,_label,default,_maximum,_skills in OPTIONS.get(owner,[]):
                widget=widgets[(owner,key)]
                widget.setChecked(default) if isinstance(widget,QCheckBox) else widget.setValue(default)
            fields={key:PLAN['common'][key] for key in ('elite','level','trust','potential','module_id','module_level')}
            window.operator_observations[owner]={'id':owner,'fields':fields,'skill_ranks':{str(row['skill']):10}}
            window.skill_override=False;window.level_override=False;window.display_operator=None
            assert window.select_operator(owner)
            window.update_operator(preserve_level=False)
            assert window.skill.findData(row['skill'])>=0
            window.skill.setCurrentIndex(window.skill.findData(row['skill']))
            window.timing_scenario.setPlainText(json.dumps(row['timing'],ensure_ascii=False))

        for row in PLAN['rows']:
            current=row['id'];before=dict(counts);api_before=len(API);signal_before=len(signals)
            rec={'id':current,'planned':copy.deepcopy(row),'passed':False,'actual_entries_before':before}
            states.append(rec);checkpoint()
            action=row['action']
            if action=='train':train(row)
            elif action=='limit':
                assert window.limit_window.isChecked() is not row['value'];window.limit_window.setChecked(row['value'])
            elif action=='seconds':
                assert window.window_seconds.value()!=row['value'];window.window_seconds.setValue(row['value'])
            elif action=='frame':
                assert window.frame_timing.isChecked() is not row['value'];window.frame_timing.setChecked(row['value'])
            elif action=='ranges_frames':
                window.frame_timing.setChecked(True);window.timing_scenario.setPlainText(json.dumps(row['timing']))
            elif action=='timing_error_frames':
                window.frame_timing.setChecked(True);window.timing_scenario.setPlainText(row['text'])
            elif action in ('timing_error','timing'):window.timing_scenario.setPlainText(row['text'])
            elif action in ('train_window','train_friendly'):
                train(row);window.window_seconds.setValue(row['seconds'])
            else:raise AssertionError(('unknown focused action',action))
            application.processEvents()
            if row.get('button'):
                previous=dict(counts);button.click();application.processEvents();explicit_buttons+=1
                assert delta(previous,counts).get('calculate_damage',0)==1
            assert window.operator.currentData()==row['owner'] and window.skill.currentData()==row['skill']
            assert window.limit_window.isChecked() is row['limit'] and window.window_seconds.value()==row['seconds']
            assert window.frame_timing.isChecked() is (row['mode']=='frames')
            assert window.continuous_attacks.isChecked() is True
            rec['actual_controls']={'limit_native':native(window.limit_window.isChecked()),'seconds_native':native(window.window_seconds.value()),
                'timing_text':window.timing_scenario.toPlainText(),'continuous_native':native(window.continuous_attacks.isChecked()),
                'frame_native':native(window.frame_timing.isChecked()),'signals':copy.deepcopy(signals[signal_before:]),
                'rank_label':window.rank.text(),'level':window.level.value()}
            if action in ('limit','seconds'):
                assert counts.get('MainWindow.calculate',0)>before.get('MainWindow.calculate',0)
                assert counts.get('calculate_damage',0)>before.get('calculate_damage',0)
                assert rec['actual_controls']['signals']
            if row.get('error'):
                assert window.damage_result is None and window.damage_text.toPlainText()==row['error']
                rec['visible_error']=window.damage_text.toPlainText();rec['result']=None;rec['three_texts']='inapplicable: existing error has no numerical result'
                if row['numeric_error']:
                    assert len(API)>api_before
                    last=API[-1]
                    assert last['step']==current and last['outcome']=='raised_exception'
                    assert last['exception_events'][-1]['type']=='ValueError' and last['exception_events'][-1]['message']==row['error']
                else:assert len(API)==api_before
            else:
                assert window.damage_result,window.damage_text.toPlainText()
                raw=window.damage_result['scenario'];result=window.damage_result['result']
                rec.update(scenario=copy.deepcopy(raw),scenario_native=native(raw),result=copy.deepcopy(result),result_native=native(result))
                checkpoint()
                assert raw['operator']==row['owner'] and raw['skill']==row['skill'] and raw['skill_rank']==10
                assert all(raw[key]==PLAN['common'][key] for key in ('elite','level','trust','potential','module_id','module_level','healing_targets','continuous_attacks','relic_ids'))
                assert type(raw['continuous_attacks']) is bool and raw['timing_mode']==row['mode'] and raw.get('timing',{})==row['timing']
                assert 'base_attack' not in raw
                assert ('window_seconds' in raw) is row['limit']
                if row['limit']:assert type(raw['window_seconds']) is float and raw['window_seconds']==row['seconds']
                texts={'estimate':format_estimate(result),'default':format_report(result),'technical':format_report(result,technical=True)}
                explicit_texts+=3;rec['reports']=texts;checkpoint()
                assert texts['estimate']==texts['default']
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                window.damage_technical.setChecked(True);application.processEvents()
                assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                window.damage_technical.setChecked(False);application.processEvents()
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                assert native(raw)==rec['scenario_native'] and native(result)==rec['result_native']
                sections={s['id']:s for s in result['report']['sections']}
                if 'effective' in row:
                    assert result['estimate']['skill']['window_seconds']==row['effective']
                    for name in ('damage','healing'):
                        section=sections.get(name)
                        if section is None:continue
                        metrics={m['key']:m['value'] for m in section['metrics']}
                        assert metrics['window_seconds']==row['effective']
                        average='window_dps' if name=='damage' else 'window_hps'
                        assert (average in metrics) is bool(row['effective'])
                if row.get('zero_damage'):assert result['total_damage']==0
                if row.get('zero_healing'):assert result['total_healing']==0 and result['estimate']['skill']['window_healing']==0
                if row.get('positive_damage'):assert result['total_damage']>0
                if row.get('positive_healing'):assert result['total_healing']>0 and result['estimate']['skill']['window_healing']>0
                if row.get('same_native_result_as'):
                    assert native(raw)==raws[row['same_native_result_as']]
                    assert native(result)==results[row['same_native_result_as']]
                if row.get('same_components_as'):
                    assert native(result['components'])==components[row['same_components_as']]
                if current=='silver-frames-target-move-interrupt':
                    streams=result['timing']['streams'];assert streams and result['timing']['fps']==30
                    assert any(stream['start_frames'] for stream in streams)
                    for stream in streams:
                        assert stream['target_scope']=='enemy'
                        for start in stream['start_frames']:
                            assert 0<=start<90 or 240<=start<360
                            assert not (60<=start<120 or 180<=start<240)
                    rec['scope']='Actual reference acquisition starts constrained; range exit does not universally cancel locked impacts or prove native game clock.'
                if current.startswith('kaltsit-S3-friendly'):
                    assert result['total_damage']==0
                    if row['mode']=='frames':
                        assert any(s['target_scope']=='friendly' for s in result['timing']['streams'])
                    assert any('真实友方获取时钟未核验' in note for note in result['estimate']['notes'])
                    rec['scope']='Current catalog kaltsit alias and existing finite friendly medical fallback, not classic token mechanism or verified game acquisition.'
                raws[current]=native(raw);results[current]=native(result)
                components[current]=native(result.get('components',[]))
                if row.get('screenshot'):
                    window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
                    fragment='伤害观察窗口' if row.get('zero_damage') else '治疗观察窗口'
                    assert window.damage_text.find(fragment);window.damage_text.ensureCursorVisible();application.processEvents()
                    path=OUT/row['screenshot'];assert window.grab().save(str(path));rec['actual_screenshot']=path.name
            rec['actual_entries']=delta(before,counts);rec['passed']=True
            checks.append({'id':current,'passed':True,'outcome':'existing_error' if row.get('error') else 'numerical_result'})
            checkpoint()
        assert len(checks)==len(states)==19 and explicit_buttons==2 and explicit_texts==45
        assert all(a['caller_native_unchanged'] for a in API)
        assert not pending_api and not pending_main
        assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process and not isolated.joinpath('chat').exists()
        receipt['focused_actual_entries']=delta(phase_before,counts)
        receipt['focused_API_success_entries']=sum(a['step']!='startup' and a['outcome']=='returned_dict' for a in API)
        receipt['all_API_outcomes']={key:sum(a['outcome']==key for a in API) for key in ('returned_dict','raised_exception','returned_non_dict_or_unobserved_unwind')}
        receipt['numeric_state_success_count']=15;receipt['expected_error_state_count']=4
        receipt['explicit_button_requests']=explicit_buttons
        receipt['focused_automatic_numeric_entries']=receipt['focused_actual_entries']['calculate_damage']-explicit_buttons
        window.close();application.processEvents();window=None
        sys.setprofile(previous_profile);sys.settrace(previous_trace)
    receipt['passed']=True;receipt['focused_window_complete']=True
except BaseException as error:
    receipt['failure']={'type':type(error).__name__,'message':str(error),'step':current,'traceback':traceback.format_exc()}
    if window is not None:
        receipt['failure_current_window']={'owner':window.operator.currentData(),'skill':window.skill.currentData(),
            'limit_native':native(window.limit_window.isChecked()),'seconds_native':native(window.window_seconds.value()),
            'timing_text':window.timing_scenario.toPlainText(),'visible_text':window.damage_text.toPlainText(),
            'damage_result':copy.deepcopy(window.damage_result),'damage_result_native':native(window.damage_result)}
        try:
            path=OUT/'wine-focused-window-failure-092.png'
            if window.grab().save(str(path)):receipt['failure_screenshot']=path.name
        except Exception as screenshot_error:receipt['failure_screenshot_error']=str(screenshot_error)
finally:
    sys.setprofile(None);sys.settrace(None)
    if window is not None:
        window.close()
        if application is not None:application.processEvents()
    after={rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in SOURCE_HASHES}
    receipt['source_sha256_after']=after;receipt['source_drift']=[rel for rel in SOURCE_HASHES if after[rel]!=SOURCE_HASHES[rel]]
    if receipt['source_drift']:receipt['passed']=False;receipt['focused_window_complete']=False
    receipt['actual_main_thread_function_entries']=counts;receipt['all_rouge_main_thread_entries']=library_counts
    receipt['explicit_button_requests']=explicit_buttons;receipt['explicit_three_text_requests']=explicit_texts
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    checkpoint();RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'passed':receipt['passed'],'checks':len(checks),'actual_entries':counts,'records':receipt['lossless_records'],'failure':receipt.get('failure')}))
    sys.exit(0 if receipt['passed'] else 1)
