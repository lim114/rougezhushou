"""Source preparation only; Root executes six real producer/report window states."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, write_record, source_map

DEEP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
SHU = 'char_2025_shu'
OPERATORS = ((DEEP,1,2,10),(SHU,3,2,7),('mechanist',3,2,7))
DEEP_TIMING = {'windup_frames':1,'recovery_frames':0,
    'initial_target_windows':[[0,3]],'movement_windows':[[2,3]],'interrupt_windows':[],
    'units':{TOKEN:{'windup_frames':1,'recovery_frames':0,
        'projectile_travel_seconds':10,'target_windows':[[0,30]]}}}
CASES = (
    {'id':'deep-s1-tail-one','operator':DEEP,'skill':1,'mode':'frames','window':30,'summon_count':1,'timing':DEEP_TIMING},
    {'id':'deep-s1-tail-zero','operator':DEEP,'skill':1,'mode':'frames','window':30,'summon_count':0,'timing':DEEP_TIMING},
    {'id':'shu-s1-known-and-unknown','operator':SHU,'skill':1,'mode':'frames','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'shu-s3-enemy-friendly','operator':SHU,'skill':3,'mode':'frames','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'shu-s3-continuous-reference','operator':SHU,'skill':3,'mode':'continuous','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'mechanist-s3-release-no-impact','operator':'mechanist','skill':3,'mode':'frames','window':2,
        'timing':{'windup_frames':6,'recovery_frames':9,'target_disappears_seconds':.3}},
)
DAMAGE_TYPES = ('physical','magic','true','elemental','weakness','damage_reference')
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 600
def sha(raw):return hashlib.sha256(raw).hexdigest()

def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def profile(op,skill,elite,rank):
    return {'id':op,'scope':'operator_profile','fields':{'elite':elite,'level':70 if op==DEEP else 1,
        'trust':100 if op==DEEP else 0,'potential':1,'module_id':None,'module_level':0,'selected_skill':skill},
        'skill_ranks':{str(n):rank for n in ((1,3) if op==SHU else (skill,))},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def fixture():
    members={}
    for values in OPERATORS:
        member=profile(*values);member.update(scope='run',present=True,recruitment_kind='non_emergency',
            char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
            invalid_fields=[],invalid_skill_ranks=[],missing_fields=[])
        members[values[0]]=member
    return {'id':'public117-window','started_at':0.0,'last_read':1000.0,'operators':members,
        'crew_count':len(OPERATORS),'selected_operator':OPERATORS[0][0],'relics':{},'tactical_tools':{},'relic_count':0,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

def report_fields(caller,result):
    """Read only returned graph and declared UI inputs; call no production helper."""
    sections=result['report']['sections']
    blocks={b['id']:b for b in sections if b['id']=='calculation_context'
        or b['id'].startswith(('event_clock_','output_domain_'))}
    assert len(blocks)==sum(b['id']=='calculation_context' or b['id'].startswith(
        ('event_clock_','output_domain_')) for b in sections)
    wanted_ids={'calculation_context'}
    skill=result['estimate']['skill'];context=blocks['calculation_context']
    context_wanted={'timing_mode':'30帧/秒事件参考' if result['timing']['mode']=='frames' else '连续供靶参数参考',
        'window':skill['window_seconds'],'declared_window':str(caller['window_seconds'])+' 秒',
        'target_source':'手动情景输入参考','enemy_defense':caller['enemy_defense'],
        'enemy_resistance':caller['enemy_resistance']}
    actual={m['key']:m['value'] for m in context['metrics']}
    assert len(actual)==len(context['metrics'])
    assert_native_equal(actual,context_wanted,'actual context scalars to caller/returned observation')
    notes='\n'.join(context['notes']);timing=caller['timing']
    for field,label in (('windup_frames','前摇预览'),('recovery_frames','后摇预览')):
        assert '本体声明 · '+label+'：'+str(timing[field])+' 帧。' in notes
    if caller['operator']==DEEP:
        for text in ('本体声明 · 初动敌方可获取区间：[0, 3) 秒。',
                     '本体声明 · 移动区间：[2, 3) 秒。',
                     '本体声明 · 打断区间：明确为空。',
                     '触手声明 · 手动弹道延迟：10 秒。',
                     '触手声明 · 敌方可获取区间：[0, 30) 秒。'):
            assert text in notes
    if caller['timing_mode']=='continuous':assert '连续模式保持既有参数参考' in notes
    if 'target_disappears_seconds' in timing:
        assert '本体声明 · 当前目标生命周期终点：'+str(timing['target_disappears_seconds'])+' 秒。' in notes
    assert '敌方供靶不等于友方受疗资格' in notes
    if result['timing']['mode']=='frames':
        for source_key in ('streams','recharge_streams'):
            for index,stream in enumerate(result['timing'].get(source_key,[])):
                identity='event_clock_'+source_key+'_'+str(index);wanted_ids.add(identity)
                block=blocks[identity]
                wanted={'target_scope':{'enemy':'敌方获取参考','friendly':'友方获取参考'}.get(
                    stream.get('target_scope'),'获取来源未确认')}
                for field in ('start_frames','release_frames','impact_frames','times_seconds',
                              'emitted_impact_frames','emitted_times_seconds'):
                    values=stream.get(field)
                    assert values is None or type(values) is list and all(type(v) in (int,float)
                        and math.isfinite(v) for v in values)
                    wanted.update({field+'_count':len(values) if values is not None else None,
                        field+'_first':values[0] if values else None,field+'_last':values[-1] if values else None})
                actual={m['key']:m['value'] for m in block['metrics']}
                assert len(actual)==len(block['metrics'])
                assert_native_equal(actual,wanted,'actual separate phase/index raw stream '+identity)
                if stream['unit']==TOKEN:assert '触手' in block['title']
                assert '各自阶段的相对参考' in '\n'.join(block['notes'])
                assert '多只或零只' in '\n'.join(block['notes'])
    kinds=('healing',) if caller['operator']==SHU and caller['skill']==1 else (
        ('damage','healing') if caller['operator']==SHU else ('damage',))
    for kind in kinds:
        identity='output_domain_'+kind;wanted_ids.add(identity);block=blocks[identity]
        total='total_'+kind;phase='phase_'+kind;window='window_'+kind;cycle='cycle_'+kind
        average='cycle_dps' if kind=='damage' else 'cycle_hps'
        wanted={'window_seconds':skill['window_seconds'],'window_total':skill.get(window,
            result.get('total_damage') if kind=='damage' else None),'cast_total':skill.get(total),
            'duration_seconds':skill.get('duration_seconds'),'phase_total':skill.get(phase),
            'recharge_seconds':skill.get('recharge_seconds'),'cycle_seconds':skill.get('cycle_seconds'),
            'cycle_total':skill.get(cycle),'cycle_average':skill.get(average)}
        subtotal=result.get('known_'+kind+'_subtotals')
        if type(subtotal) is dict:
            for field in (window,total,phase,cycle):
                if field in subtotal:wanted['known_'+field]=subtotal[field]
        actual={m['key']:m['value'] for m in block['metrics']}
        assert len(actual)==len(block['metrics'])
        assert_native_equal(actual,wanted,'actual output domain to existing masked/raw scalars '+kind)
        assert '不重新结算' in '\n'.join(block['notes'])
    assert set(blocks)==wanted_ids
    return blocks


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--source-count',type=int,required=True)
    parser.add_argument('--section',type=int,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;guard_path=Path(args.guard).resolve()
    assert not out.exists() and root not in out.parents and out!=root
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==args.section and args.section==117
    assert len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];active={'case':'bootstrap','phase':'constructor'}
    started=time.perf_counter();done=threading.Event();window=None;module=None;backend=None;calculator=None;old_paths=None
    receipt={'kind':'ROOT_ACTUAL_117_REAL_MAINWINDOW','phase':'candidate','section':args.section,'passed':False,
        'workflow_complete':False,'runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'rows':rows,'pairs':pairs,'records':records,'pngs':pngs,'Qt_errors':errors,
        'deadline_seconds':DEADLINE,'private_state_access':False,'native_windows_verified':False,
        'game_chat_sampling_executed':False,
        'comparison_scope':'Six actual public producer states. Every new context/domain/clock scalar is checked against the exact UI caller and returned complete raw graph; no original GUI Gold or independent formula/native gameplay proof.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads; no second MainWindow.',
        'formatter_scope':'Three complete formatter group purity plus actual technical checkbox on/off; all complete texts are saved native.',
        'timing_scope':'Explicit manual owner/unit timing through actual advanced JSON; declarations are retained separately and do not establish client animation.',
        'PNG_scope':'Exactly two bounded visible excerpts: Deepcolor token window/potential-tail records, and Shu S1 window/full/phase rows with unknowns. Entire long tables are saved text/native; no whole-table PNG visibility claim.'}

    def save(kind,**value):
        ref=write_record(out/'records',len(records)+1,{'kind':kind,**active,**value})
        ref.update(kind=kind,**active);records.append(ref);return ref
    def watchdog():
        if not done.wait(DEADLINE):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline_seconds':DEADLINE}))
            os._exit(124)
    threading.Thread(target=watchdog,daemon=True).start();old_hook=sys.excepthook
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'phase':active['phase'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.dont_write_bytecode=True;sys.path.insert(0,str(root))
        from PySide6.QtCore import qVersion
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from rouge import app as module,estimate,reporting
        from rouge.run_state import RunState
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage
        old_paths=(module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS)
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                details=error_record(error);after=freeze({'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})})
                ref=save('actual_calculate_exception',before=before,after=after,error=details)
                calls.append({'caller':before,'error':details,'native':ref})
                assert_native_equal(after,before,'exception caller purity');raise
            after_context={'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})}
            after=freeze(after_context)
            ref=save('actual_calculate_result',before=before,after=after_context,result=value)
            calls.append({'caller':before,'error':None,'native':ref,'return_value':value})
            assert_native_equal(after,before,'numeric caller purity');return value
        module.calculate_damage=observed
        with tempfile.TemporaryDirectory(prefix='public117-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({values[0]:profile(*values) for values in OPERATORS},ensure_ascii=False,indent=2)+'\n').encode()
            run_path.write_bytes(run_raw);account_path.write_bytes(account_raw)
            module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
            window=module.MainWindow();window.resize(1400,1100);window.show();window.centralWidget().setCurrentIndex(1)
            def idle():
                application.processEvents()
                assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                assert window.desktop.process is None and not window.desktop.pending and not errors
            def joint():
                return {'run':window.run.state,'account':window.account_cache.records,'disks':{
                    p.relative_to(folder).as_posix():p.read_bytes() for p in sorted(folder.rglob('*')) if p.is_file()}}
            def pure(label,callback):
                before=freeze({'joint':joint(),'damage_result':window.damage_result})
                value=callback();idle();after=freeze({'joint':joint(),'damage_result':window.damage_result})
                save('actual_UI_step',label=label,before=before,after=after)
                assert_native_equal(after['joint'],before['joint'],label+' state/account/disk purity');return value
            def screenshot(identity,block,first_key,last_key,include_title=False):
                title='【'+block['title']+'】';document=window.damage_text.document()
                title_cursor=document.find(title);assert not title_cursor.isNull()
                first=title_cursor if include_title else document.find(
                    next(m['label'] for m in block['metrics'] if m['key']==first_key)+'：',title_cursor)
                last=document.find(next(m['label'] for m in block['metrics'] if m['key']==last_key)+'：',first)
                assert not first.isNull() and not last.isNull() and first.blockNumber()<=last.blockNumber()
                middle=QTextCursor(first)
                for _ in range((last.blockNumber()-first.blockNumber())//2):
                    assert middle.movePosition(QTextCursor.MoveOperation.NextBlock)
                pure('center actual bounded report excerpt',lambda:(window.damage_text.setTextCursor(middle),window.damage_text.centerCursor()))
                head=QTextCursor(first);head.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                visible=[];rectangles=[]
                while head.blockNumber()<=last.blockNumber():
                    assert len(visible)<12
                    end=QTextCursor(head);end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    visible.append(head.block().text());rectangles.extend((window.damage_text.cursorRect(head),window.damage_text.cursorRect(end)))
                    if head.blockNumber()==last.blockNumber():break
                    assert head.movePosition(QTextCursor.MoveOperation.NextBlock)
                viewport=window.damage_text.viewport().rect()
                assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                visual=save('actual_PNG_bounded_report_excerpt',section=block['id'],title=title,
                    first_key=first_key,last_key=last_key,title_visible=include_title,
                    entire_long_section_visible=False,displayed_text=window.damage_text.toPlainText(),visible_blocks=visible,
                    cursor_rects=[(r.x(),r.y(),r.width(),r.height()) for r in rectangles],
                    viewport_rect=(viewport.x(),viewport.y(),viewport.width(),viewport.height()))
                path=out/(identity+'.png');assert window.grab().save(str(path),'PNG')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':visual})
            idle();assert not window.run.preserve_unreadable and window.run.save_issue is None
            initial=freeze(joint());assert run_path.read_bytes()==run_raw and account_path.read_bytes()==account_raw
            receipt['initial']=save('actual_public_fixture_loaded',run_bytes=run_raw,account_bytes=account_raw,value=initial)
            pure('manual no-relic inventory',lambda:window.auto_relics.setChecked(False))
            pure('read actual run training',lambda:window.use_run_training.setChecked(True))
            pure('use requested observation interval',lambda:window.limit_window.setChecked(True))
            pure('framed timing',lambda:window.frame_timing.setChecked(True))
            pure('zero manual enemy defense',lambda:window.defense.setValue(0))
            pure('zero manual enemy resistance',lambda:window.resistance.setValue(0))
            pure('declared continuous attacks',lambda:window.continuous_attacks.setChecked(True))
            pure('unbound normal animation',lambda:window.normal_animation_reference.setCurrentIndex(0))
            pure('unbound skill animation',lambda:window.skill_animation_reference.setCurrentIndex(0))
            pure('default report presentation',lambda:window.raw_damage.setChecked(False))
            pure('default report without technical expansion',lambda:window.damage_technical.setChecked(False))
            assert window.target_enemy.currentData() is None and not window.target_buff_test.isChecked()
            deep_snapshots=[]
            for case in CASES:
                identity=case['id'];op=case['operator'];skill=case['skill'];mode=case['mode']
                active.update(case=identity,phase='actual_operator_configuration')
                pure('actual public recruited operator',lambda:window.operator_choices.select_value(op))
                index=window.skill.findData(skill);assert index>=0
                pure('actual selected skill',lambda:window.skill.setCurrentIndex(index))
                pure('actual frame/continuous checkbox',lambda:window.frame_timing.setChecked(mode=='frames'))
                pure('explicit observation window',lambda:window.window_seconds.setValue(case['window']))
                pure('explicit manual owner/unit timing JSON',lambda:window.timing_scenario.setPlainText(json.dumps(case['timing'])))
                if op==DEEP:
                    controls=[w for owner,key,skills,w in window.model_option_widgets
                        if owner==DEEP and key=='summon_count' and skill in skills]
                    assert len(controls)==1 and window.damage_form.isRowVisible(controls[0])
                    pure('actual deployed count assumption',lambda:controls[0].setValue(case['summon_count']))
                assert window.healing_targets.value()==1
                active['phase']='explicit_actual_snapshot';start=len(calls);pure('actual MainWindow.calculate',window.calculate)
                assert len(calls)==start+1 and calls[-1]['error'] is None and window.damage_result is not None
                call=calls[-1];caller=call['caller']['args'][0];result=window.damage_result['result']
                assert result is call['return_value']
                assert caller['operator']==op and caller['skill']==skill and caller['timing_mode']==mode
                assert caller['elite']==2 and caller['level']==(70 if op==DEEP else 1)
                assert caller['skill_rank']==(10 if op==DEEP else 7) and caller['trust']==(100 if op==DEEP else 0)
                assert caller['potential']==1 and caller['module_id'] is None and caller['module_level']==0
                assert caller['relic_ids']==[] and caller['continuous_attacks'] is True and caller['healing_targets']==1
                assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
                assert 'base_attack' not in caller and 'target_enemy' not in caller
                assert window.normal_animation_reference.currentData() is None and window.skill_animation_reference.currentData() is None
                assert_native_equal(caller['window_seconds'],window.window_seconds.value(),'real widget/native caller observation')
                assert caller['window_seconds']==case['window']
                assert_native_equal(caller['timing'],case['timing'],'actual complete owner/unit timing caller')
                assert_native_equal(window.damage_result['scenario'],caller,'actual complete UI/native caller')
                blocks=report_fields(caller,result)
                if op==DEEP:
                    token_index=next(i for i,s in enumerate(result['timing']['streams']) if s['unit']==TOKEN)
                    token_stream=result['timing']['streams'][token_index]
                    component=next(c for c in result['components'] if c['name']=='触手')
                    assert len(token_stream['emitted_impact_frames'])>len(token_stream['impact_frames'])
                    assert token_stream['emitted_times_seconds'][-1]>result['estimate']['skill']['duration_seconds']
                    assert len(result['timing']['recharge_streams'])>=2
                    if case['summon_count']==0:
                        assert component['hits']==0 and component['total']==0 and len(token_stream['release_frames'])>0
                    else:assert component['hits']>0
                elif op==SHU and skill==1:
                    assert result['total_healing'] is None and result['estimate']['skill']['total_healing'] is None
                    assert result['next_attack_healing_reference']['actual_acquisition_times_seconds'] is None
                    assert 'known_window_healing' in {m['key'] for m in blocks['output_domain_healing']['metrics']}
                elif op==SHU and mode=='frames':
                    current=result['timing']['streams'];assert len(current)>=2
                    assert {s['target_scope'] for s in current}>={'enemy','friendly'}
                    assert {s['unit'] for s in current}=={SHU}
                elif mode=='continuous':assert not any(b.startswith('event_clock_') for b in blocks)
                else:
                    stream=result['timing']['streams'][0]
                    assert stream['release_frames'] and stream['impact_frames']==[] and stream['emitted_impact_frames']==[]
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                       'technical':reporting.format_report(result,technical=True)}
                after=freeze({'damage_result':window.damage_result,'joint':joint()})
                save('actual_three_formatter_group',before=before,after=after,texts=texts)
                assert_native_equal(after,before,'three formatter joint purity')
                assert texts['estimate']==texts['default'] and window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                for block in blocks.values():
                    for text in texts.values():assert '【'+block['title']+'】' in text
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                pure('actual technical checkbox on',lambda:window.damage_technical.setChecked(True))
                assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                pure('actual ordinary checkbox restored',lambda:window.damage_technical.setChecked(False))
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                assert_native_equal(freeze({'damage_result':window.damage_result,'joint':joint()}),before,
                    'both actual report views preserve complete result/run/account/disks')
                snapshot=freeze({'caller':caller,'damage_result':window.damage_result,'texts':texts,
                    'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':joint()})
                ref=save('actual_window_snapshot',value=snapshot,report_blocks=blocks)
                rows.append({'id':identity,'operator':op,'skill':skill,'mode':mode,'window_seconds':case['window'],
                    'snapshot':ref,'numeric':call['native'],'new_report_ids':list(blocks)})
                if op==DEEP:
                    deep_snapshots.append((snapshot,ref))
                    if len(deep_snapshots)==2:
                        old,old_ref=deep_snapshots[0];new_caller=freeze(caller);new_caller['summon_count']=1
                        assert_native_equal(new_caller,old['caller'],'same exact UI caller except count0/1')
                        assert_native_equal(snapshot['state_and_disks'],old['state_and_disks'],'count preview state/account/all disk purity')
                        pairs.append({'kind':'count0_vs_count1','one':old_ref,'zero':ref,
                            'same_caller_except_count':True,'state_account_all_disks_preserved':True})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],'next_case_index':len(rows),
                        'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                if identity=='deep-s1-tail-one':
                    screenshot('deep-token-window-and-tail',blocks['event_clock_streams_'+str(token_index)],
                        'impact_frames_count','emitted_impact_frames_last')
                if identity=='shu-s1-known-and-unknown':
                    screenshot('shu-next-attack-window-cast-unknown',blocks['output_domain_healing'],
                        'window_seconds','phase_total',True)
            active.update(case='window',phase='close_direct_RunState_reload');before=freeze(joint())
            window.close();application.processEvents();assert_native_equal(joint(),before,'real close purity')
            restarted=RunState(run_path);assert not restarted.preserve_unreadable and restarted.save_issue is None
            assert_native_equal(restarted.state,initial['run'],'direct reload original accepted loaded graph')
            assert_native_equal(joint(),before,'direct reload disk purity')
            from rouge.account_cache import AccountCache
            from rouge.catalog import catalog,operator_profiles
            account_restarted=AccountCache(account_path,profiles=operator_profiles(),implemented_ids=catalog()['operators'])
            assert not account_restarted.issues and account_restarted.load_issue is None and not account_restarted.preserve_original
            assert_native_equal(account_restarted.records,initial['account'],'direct account reload original graph')
            assert_native_equal(joint(),before,'direct account reload disk purity')
            receipt['close_reload']=save('actual_close_RunState_reload',live_before=before,
                persisted_json=json.loads(run_path.read_bytes()),restart_state=restarted.state,
                account_restart_records=account_restarted.records,disks_after=joint()['disks'])
            window.deleteLater();application.processEvents();window=None
        assert len(rows)==len(CASES)==6 and len(pairs)==1 and len(pngs)==2 and not errors
        assert all(call['error'] is None for call in calls)
        receipt.update(passed=True,workflow_complete=True,actual_windows=1)
    except BaseException as error:receipt['failure']=error_record(error)
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
            if old_paths is not None:module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS=old_paths
        sys.excepthook=old_hook;receipt['actual_numeric_calls']=len(calls)
        receipt['source_after']=source_map(root)
        receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        receipt['source_drift']=[p for p in set(expected)|set(receipt['source_after']) if expected.get(p)!=receipt['source_after'].get(p)]
        if receipt['source_drift'] or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw or errors:
            receipt.update(passed=False,workflow_complete=False)
        receipt['elapsed_seconds']=time.perf_counter()-started
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed':receipt['passed'],'rows':len(rows),'pairs':len(pairs),'pngs':len(pngs)}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
