"""Source preparation only; Root runs one real legacy ammo completion window."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, write_record, source_map

OPERATORS = (('mechanist',1,2,7),('kaltsit',2,2,7))
DAMAGE_TYPES = ('physical','magic','true','elemental','weakness','damage_reference')
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 900
def sha(raw):return hashlib.sha256(raw).hexdigest()

def visible_metric_label(label):
    """Verified ordinary-report label wording, not an output-mechanism change."""
    assert type(label) is str
    for raw,shown in (('DPS/HPS','每秒伤害 / 每秒治疗'),('DPS','每秒伤害'),('HPS','每秒治疗')):
        label=label.replace(raw,shown)
    return re.sub(r' (?=每秒伤害|每秒治疗)','',label).strip()

def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def profile(op,skill,elite,rank):
    return {'id':op,'scope':'operator_profile','fields':{'elite':elite,'level':1,
        'trust':0,'potential':1,'module_id':None,'module_level':0,'selected_skill':skill},
        'skill_ranks':{str(skill):rank},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def fixture():
    members={}
    for values in OPERATORS:
        member=profile(*values);member.update(scope='run',present=True,recruitment_kind='non_emergency',
            char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
            invalid_fields=[],invalid_skill_ranks=[],missing_fields=[])
        members[values[0]]=member
    return {'id':'public119-window','started_at':0.0,'last_read':1000.0,'operators':members,
        'crew_count':2,'selected_operator':OPERATORS[0][0],'relics':{},'tactical_tools':{},'relic_count':0,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

CASES = [{'id': 'mechanist-frames-limited_windows', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'limited_windows', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': [[0, 3]]}, 'png': True}, {'id': 'mechanist-frames-positive_lifetime', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'positive_lifetime', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_disappears_seconds': 3}, 'png': False}, {'id': 'mechanist-frames-interrupted_tail', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'interrupted_tail', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'interrupt_windows': [[3, 3600]]}, 'png': False}, {'id': 'mechanist-frames-complete_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'complete_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'mechanist-frames-short_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'short_control', 'seconds': 2, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'mechanist-frames-empty_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'empty_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}, {'id': 'mechanist-frames-late_complete_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'frames', 'shape': 'late_complete_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'projectile_travel_seconds': 100}, 'png': False}, {'id': 'mechanist-continuous-complete_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'continuous', 'shape': 'complete_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'mechanist-continuous-short_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'continuous', 'shape': 'short_control', 'seconds': 2, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'mechanist-continuous-empty_control', 'operator': 'mechanist', 'skill': 1, 'mode': 'continuous', 'shape': 'empty_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}, {'id': 'kaltsit-frames-limited_windows', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'limited_windows', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': [[0, 3]]}, 'png': True}, {'id': 'kaltsit-frames-positive_lifetime', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'positive_lifetime', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_disappears_seconds': 3}, 'png': False}, {'id': 'kaltsit-frames-interrupted_tail', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'interrupted_tail', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'interrupt_windows': [[3, 3600]]}, 'png': False}, {'id': 'kaltsit-frames-complete_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'complete_control', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'kaltsit-frames-short_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'short_control', 'seconds': 2, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'kaltsit-frames-empty_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'empty_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}, {'id': 'kaltsit-frames-late_complete_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'late_complete_control', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'projectile_travel_seconds': 100}, 'png': False}, {'id': 'kaltsit-continuous-complete_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'continuous', 'shape': 'complete_control', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'kaltsit-continuous-short_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'continuous', 'shape': 'short_control', 'seconds': 2, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False}, {'id': 'kaltsit-continuous-empty_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'continuous', 'shape': 'empty_control', 'seconds': 10, 'healing_targets': 0, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}, {'id': 'kaltsit-frames-friendly_complete_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'frames', 'shape': 'friendly_complete_control', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}, {'id': 'kaltsit-continuous-friendly_complete_control', 'operator': 'kaltsit', 'skill': 2, 'mode': 'continuous', 'shape': 'friendly_complete_control', 'seconds': 10, 'healing_targets': 2, 'timing': {'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}, 'png': False}]

# These fixed public profile parameters are pinned in the Source manifest. They
# describe the offline manual-zero-windup reference, not game-clock Gold.
BASE_ATTACK = {'mechanist':425,'kaltsit':408}

def close_number(actual,expected,label):
    assert type(actual) in (int,float) and abs(actual-expected)<=max(1e-8,abs(expected)*1e-12),(label,actual,expected)

def hand_oracle(case):
    op=case['operator'];shape=case['shape'];framed=case['mode']=='frames'
    incomplete=shape in ('limited_windows','positive_lifetime','interrupted_tail','empty_control')
    if not framed:incomplete=shape=='empty_control'
    if op=='mechanist':
        per=BASE_ATTACK[op]*1.1
        count=10 if shape in ('limited_windows','interrupted_tail') else 5 if shape=='positive_lifetime' else 4 if shape=='short_control' and framed else 0 if shape in ('short_control','empty_control','late_complete_control') else 15
        damage=per*count;healing=0;full_damage=per*15
        duration=175/30 if framed else 7.5
    else:
        attack=BASE_ATTACK[op]*2.25;per=attack*3.5;heal_per=attack*1.7*case['healing_targets']
        count=2 if shape in ('limited_windows','positive_lifetime','interrupted_tail') else 1 if shape=='short_control' and framed else 0 if shape in ('short_control','empty_control','late_complete_control') else 4 if framed else 3
        damage=0 if shape=='friendly_complete_control' else per*count
        healing=heal_per*count
        full_damage=0 if shape=='friendly_complete_control' else per*10
        full_healing=heal_per*10
        duration=775/30 if framed else 28.5
    return {'window_damage':damage,'window_healing':healing,'duration':None if incomplete else duration,
        'full_damage':0 if shape=='empty_control' else None if incomplete else full_damage,
        'full_healing':0 if op=='mechanist' or shape=='empty_control' else None if incomplete else full_healing,
        'incomplete':incomplete,'literal_base_attack':BASE_ATTACK[op]}

def check_completion(case,caller,result):
    want=hand_oracle(case);skill=result['estimate']['skill']
    close_number(result['total_damage'],want['window_damage'],'actual GUI currentdamage')
    close_number(skill['window_damage'],want['window_damage'],'actual GUI windowdamage')
    close_number(skill['window_healing'],want['window_healing'],'actual GUI potential windowhealing')
    assert skill['window_seconds']==case['seconds']
    close_number(result['estimate']['base_stats']['attack'],BASE_ATTACK[case['operator']],'actual public profile baseattack')
    for key,oracle in [('duration_seconds','duration'),('total_damage','full_damage'),('total_healing','full_healing')]:
        value=want[oracle]
        if value is None:assert skill[key] is None,(case['id'],key,skill[key])
        else:close_number(skill[key],value,case['id']+' '+key)
    if want['incomplete']:
        for key in ('cycle_seconds','cycle_damage','cycle_dps','cycle_healing','cycle_hps'):assert skill[key] is None
        if want['full_damage'] is None:assert skill['phase_damage'] is None
        if want['full_healing'] is None:assert skill['phase_healing'] is None
    return want

def component_fields(result):
    blocks={s['id']:s for s in result['report']['sections'] if s['id'].startswith('output_breakdown_')}
    assert len(blocks)==len([s for s in result['report']['sections'] if s['id'].startswith('output_breakdown_')])
    rows={m['key']:(key,m) for key,block in blocks.items() for m in block['metrics']}
    assert len(rows)==sum(len(block['metrics']) for block in blocks.values())
    expected_groups=set()
    for index,component in enumerate(result['components']):
        dtype=component['damage_type']
        group=dtype if dtype in ('healing','regeneration','buildup') else 'damage' if dtype in DAMAGE_TYPES else 'other'
        identifier='output_breakdown_'+group;expected_groups.add(identifier);prefix='component_'+str(index)+'_'
        for shown,original in (('count','hits'),('per_hit','per_hit'),('total','total')):
            key=prefix+shown;assert rows[key][0]==identifier
            assert_native_equal(rows[key][1]['value'],component[original],'actual component scalar '+key)
        if 'actual_total' in component:
            key=prefix+'actual_total';assert rows[key][0]==identifier
            assert_native_equal(rows[key][1]['value'],component['actual_total'],'actual total scalar '+key)
        else:assert prefix+'actual_total' not in rows
    assert set(blocks)==expected_groups
    return blocks

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--source-count',type=int,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;guard_path=Path(args.guard).resolve()
    assert not out.exists() and root not in out.parents and out!=root
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==119 and len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];active={'case':'bootstrap','phase':'constructor'}
    started=time.perf_counter();done=threading.Event();window=None;module=None;backend=None;calculator=None
    receipt={'kind':'ROOT_ACTUAL_119_REAL_MAINWINDOW','phase':'candidate','passed':False,
        'workflow_complete':False,'runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'rows':rows,'pairs':pairs,'records':records,'pngs':pngs,'Qt_errors':errors,
        'deadline_seconds':DEADLINE,'private_state_access':False,'native_windows_verified':False,
        'game_chat_sampling_executed':False,
        'comparison_scope':'One current real legacy ammo window: 22 actual states covering mechanist S1 and Kaltsit S2; finite target supply, disappearance, interruption, complete/short/delayed/empty/friendly controls. Literal Source manual-profile math uses actual caller E2L1R7 trust0 P1 without base_attack1000 GUI claim.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads; no second MainWindow or live JSON alias claim.',
        'formatter_scope':'Three complete formatter joint purity; no per-formatter isolated-purity claim.',
        'timing_scope':'Manual zero windup/recovery reference through actual advanced JSON; does not prove actual game animation.',
        'PNG_scope':'Mechanist partial damage report and Kaltsit partial potential healing report, each full metrics block visible. Full window and resource/other fields remain saved numeric/text proof. Root separately views two actual PNGs.'}
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
        with tempfile.TemporaryDirectory(prefix='public119-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({values[0]:profile(*values) for values in OPERATORS},ensure_ascii=False,indent=2)+'\n').encode()
            run_path.write_bytes(run_raw);account_path.write_bytes(account_raw)
            module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
            window=module.MainWindow();window.resize(1400,1050);window.show();window.centralWidget().setCurrentIndex(1)
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
            def screenshot(identity,block):
                title='【'+block['title']+'】'
                document=window.damage_text.document();first=document.find(title)
                assert not first.isNull() and block['metrics']
                search=QTextCursor(first);search.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                metric_cursors=[]
                # Source format_report emits each metric in the next document block.
                # Start after the title and reject any forward match outside that bounded block.
                for index,metric in enumerate(block['metrics']):
                    prefix=visible_metric_label(metric['label'])+'：'
                    found=document.find(prefix,search)
                    assert not found.isNull()
                    assert found.blockNumber()==first.blockNumber()+index+1
                    assert found.block().text().startswith(prefix)
                    metric_cursors.append(found)
                    search=QTextCursor(found);search.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                last=metric_cursors[-1];middle=metric_cursors[len(metric_cursors)//2]
                assert first.blockNumber()<middle.blockNumber()<=last.blockNumber()
                pure('center complete current breakdown metrics',lambda:(
                    window.damage_text.setTextCursor(middle),window.damage_text.centerCursor()))
                head=QTextCursor(first);head.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                visible=[];rectangles=[]
                while head.blockNumber()<=last.blockNumber():
                    assert len(visible)<20
                    end=QTextCursor(head);end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    visible.append(head.block().text())
                    rectangles.extend((window.damage_text.cursorRect(head),window.damage_text.cursorRect(end)))
                    if head.blockNumber()==last.blockNumber():break
                    assert head.movePosition(QTextCursor.MoveOperation.NextBlock)
                viewport=window.damage_text.viewport().rect()
                assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                visual=save('actual_PNG_complete_current_breakdown',section=block['id'],title=title,
                    displayed_text=window.damage_text.toPlainText(),visible_blocks=visible,
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
            baseline={}
            for case in CASES:
                op=case['operator'];skill=case['skill'];identity=case['id']
                active.update(case=identity,phase='actual_operator_configuration')
                pure('actual public recruited operator',lambda:window.operator_choices.select_value(op))
                index=window.skill.findData(skill);assert index>=0
                pure('actual selected skill',lambda:window.skill.setCurrentIndex(index))
                pure('actual frame/continuous widget',lambda:window.frame_timing.setChecked(case['mode']=='frames'))
                pure('actual declared healing targets',lambda:window.healing_targets.setValue(case['healing_targets']))
                pure('actual declared finite/complete timing',lambda:window.timing_scenario.setPlainText(json.dumps(case['timing'])))
                pure('actual observation window',lambda:window.window_seconds.setValue(case['seconds']))
                active['phase']='explicit_snapshot';start=len(calls);pure('MainWindow.calculate',window.calculate)
                assert len(calls)==start+1 and calls[-1]['error'] is None and window.damage_result is not None
                call=calls[-1];caller=call['caller']['args'][0];result=window.damage_result['result']
                assert result is call['return_value']
                assert caller['operator']==op and caller['skill']==skill and caller['timing_mode']==case['mode']
                assert caller['elite']==2 and caller['level']==1 and caller['skill_rank']==7
                assert caller['trust']==0 and caller['potential']==1
                assert caller['module_id'] is None and caller['module_level']==0
                assert caller['continuous_attacks'] is True and caller['relic_ids']==[]
                assert caller['healing_targets']==case['healing_targets']
                assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
                assert 'base_attack' not in caller and 'target_enemy' not in caller
                assert_native_equal(caller['window_seconds'],window.window_seconds.value(),'actual window widget to numeric caller')
                assert caller['window_seconds']==case['seconds']
                assert_native_equal(caller['timing'],case['timing'],'complete actual finite supply input')
                assert_native_equal(window.damage_result['scenario'],caller,'actual UI/native caller match')
                want=check_completion(case,caller,result)
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                       'technical':reporting.format_report(result,technical=True)}
                after=freeze({'damage_result':window.damage_result,'joint':joint()})
                save('actual_three_formatter_group',before=before,after=after,texts=texts)
                assert_native_equal(after,before,'three formatter joint purity')
                assert texts['estimate']==texts['default'] and window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                if want['full_damage'] is None:assert '单次技能总伤：未知' in texts['default']
                if want['full_healing'] is None:assert '单次技能总治疗：未知' in texts['default']
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                pure('actual technical checkbox',lambda:window.damage_technical.setChecked(True))
                assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                pure('restore actual ordinary report checkbox',lambda:window.damage_technical.setChecked(False))
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                assert_native_equal(freeze({'damage_result':window.damage_result,'joint':joint()}),before,'both report views preserve full result and state')
                snapshot=freeze({'caller':window.damage_result['scenario'],'damage_result':window.damage_result,'texts':texts,
                    'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':joint()})
                ref=save('actual_window_snapshot',value=snapshot,manual_oracle=want,case_definition=case)
                pair_key=(op,case['mode'])
                if case['shape']=='complete_control':baseline[pair_key]=(snapshot,ref)
                elif case['shape']=='short_control':
                    prior,prior_ref=baseline[pair_key]
                    normalized=freeze(caller);normalized['window_seconds']=prior['caller']['window_seconds']
                    assert_native_equal(normalized,prior['caller'],'same complete caller except actual observation window')
                    assert_native_equal(snapshot['state_and_disks'],prior['state_and_disks'],'paired complete/short state/account/disks')
                    lifecycle=('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','total_damage','total_healing','phase_damage','phase_healing','cycle_damage','cycle_healing','cycle_dps','cycle_hps')
                    assert_native_equal({k:result['estimate']['skill'][k] for k in lifecycle},
                        {k:prior['damage_result']['result']['estimate']['skill'][k] for k in lifecycle},'complete versus short unchanged lifecycle')
                    pairs.append({'operator':op,'mode':case['mode'],'complete_snapshot':prior_ref,'short_snapshot':ref,
                        'all_lifecycle_fields_equal':True,'state_account_disks_preserved':True})
                rows.append({'id':identity,'operator':op,'mode':case['mode'],'shape':case['shape'],
                    'window_seconds':case['seconds'],'snapshot':ref,'numeric':call['native'],'manual_oracle':want})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],'next_case_index':len(rows),
                        'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                if case['png']:
                    block=next(b for b in result['report']['sections'] if b['id']==('damage' if op=='mechanist' else 'healing'))
                    screenshot(identity,block)
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
        assert len(rows)==22 and len(pairs)==4 and len(pngs)==2 and not errors
        receipt.update(passed=True,workflow_complete=True,actual_windows=1)
    except BaseException as error:receipt['failure']=error_record(error)
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
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
