"""Source preparation only; Root runs one real already-ready next-attack resource window."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, write_record, source_map

OPERATORS = (('char_4204_mantra',1,2,7),)
INITIAL_SP_IDS = ('rogue_6_relic_legacy_98','rogue_6_relic_legacy_99')
DAMAGE_TYPES = ('physical','magic','true','elemental','weakness','damage_reference')
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 900
def sha(raw):return hashlib.sha256(raw).hexdigest()

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
    return {'id':'public121-window','started_at':0.0,'last_read':1000.0,'operators':members,
        'crew_count':1,'selected_operator':OPERATORS[0][0],
        'relics':{rid:{'held':True,'first_seen':1000.0,'last_seen':1000.0,
            'source':'public_manual_fixture'} for rid in INITIAL_SP_IDS},
        'tactical_tools':{},'relic_count':2,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

CASES = [{'id': 'mantra-frames-none', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'frames', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': [], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}, {'id': 'mantra-frames-98', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'frames', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': ['rogue_6_relic_legacy_98'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': True, 'technical_png': False}, {'id': 'mantra-frames-99', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'frames', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': ['rogue_6_relic_legacy_99'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}, {'id': 'mantra-frames-98-short', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'frames', 'shape': 'short_control', 'seconds': 1, 'relic_ids': ['rogue_6_relic_legacy_98'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}, {'id': 'mantra-continuous-none', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'continuous', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': [], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}, {'id': 'mantra-continuous-98', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'continuous', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': ['rogue_6_relic_legacy_98'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': True, 'technical_png': True}, {'id': 'mantra-continuous-99', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'continuous', 'shape': 'complete_control', 'seconds': 3, 'relic_ids': ['rogue_6_relic_legacy_99'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}, {'id': 'mantra-continuous-98-short', 'operator': 'char_4204_mantra', 'skill': 1, 'mode': 'continuous', 'shape': 'short_control', 'seconds': 1, 'relic_ids': ['rogue_6_relic_legacy_98'], 'timing': {'windup_frames': 0, 'recovery_frames': 0}, 'png': False, 'technical_png': False}]

# These fixed public profile parameters are pinned in the Source manifest. They
# describe the offline manual-zero-windup reference, not game-clock Gold.
BASE_ATTACK = {'char_4204_mantra':583}
LIFECYCLE_FIELDS = ('duration_seconds','total_damage','total_healing','phase_damage',
    'phase_healing','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing',
    'cycle_dps','cycle_hps')

def close_number(actual,expected,label):
    assert type(actual) in (int,float) and abs(actual-expected)<=max(1e-8,abs(expected)*1e-12),(label,actual,expected)

def hand_oracle(case):
    # Current catalog E2L1/trust0/P1 with no module:583 attack; S1R7:2.75x,
    # cost3/initial0, neural ratio.2. No triggered burst under320.65<1000.
    # This is offline manual zero-windup math, not client-clock Gold.
    initial=0.0 if case['relic_ids'] else 144/30 if case['mode']=='frames' else 3*1.6
    hits=0 if case['shape']=='short_control' and case['mode']=='continuous' else 1
    per=BASE_ATTACK[case['operator']]*2.75
    return {'initial_seconds':initial,'window_damage':per*hits,
        'full_damage':per,'window_buildup':per*.2*hits,'base_attack':583,
        'known_single_hit_magic_damage':per,'buildup_ratio':.2,'hits':hits}

def check_completion(case,caller,result):
    want=hand_oracle(case);skill=result['estimate']['skill']
    assert skill['mode']=='next_attack'
    close_number(result['estimate']['base_stats']['attack'],want['base_attack'],'actual catalog/profile baseattack')
    close_number(skill['initial_seconds'],want['initial_seconds'],'actual legal ready/charge stage')
    if case['relic_ids']:assert type(skill['initial_seconds']) in (int,float) and skill['initial_seconds']==0
    close_number(result['total_damage'],want['window_damage'],'actual GUI skill window damage')
    close_number(skill.get('window_damage',result['total_damage']),want['window_damage'],'actual GUI stored window damage')
    close_number(skill['total_damage'],want['full_damage'],'actual GUI full single-release damage')
    assert_native_equal(skill['window_seconds'],caller['window_seconds'],'actual observation denominator')
    damage=[c for c in result['components'] if c['name']=='共鸣溃缩']
    assert len(damage)==want['hits'] and all(c['damage_type']=='magic' for c in damage)
    for component in damage:
        assert component['hits']==1
        close_number(component['per_hit'],want['known_single_hit_magic_damage'],'actual release magic amount')
        close_number(component['total'],want['known_single_hit_magic_damage'],'actual release total')
    buildup=sum(c['total'] for c in result['components'] if c['damage_type']=='buildup')
    close_number(buildup,want['window_buildup'],'potential buildup is separate from life damage')
    assert not any(c['name']=='神经损伤爆发' and c['hits'] for c in result['components'])
    assert not any(c['damage_type']=='elemental' and c['hits'] for c in result['components'])
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
    assert type(guard['section']) is int and guard['section']==121
    assert type(args.source_count) is int and args.source_count>0
    assert type(expected) is dict and len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];active={'case':'bootstrap','phase':'constructor'}
    started=time.perf_counter();done=threading.Event();window=None;module=None;backend=None;calculator=None
    receipt={'kind':'ROOT_ACTUAL_121_REAL_MAINWINDOW','phase':'candidate','passed':False,
        'workflow_complete':False,'runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'rows':rows,'pairs':pairs,'records':records,'pngs':pngs,'Qt_errors':errors,
        'deadline_seconds':DEADLINE,'private_state_access':False,'native_windows_verified':False,
        'game_chat_sampling_executed':False,
        'comparison_scope':'One current real MainWindow, eight actual Mantra S1R7 cases: frames/continuous no birthSP, legacy98/99 readySP, and ready98 short-observation controls. Actual E2L1 trust0 P1 catalog base583; no GUI base_attack1000 claim.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads; no second MainWindow or live JSON alias claim.',
        'formatter_scope':'Three complete formatter joint purity; no per-formatter isolated-purity claim.',
        'timing_scope':'Manual zero windup/recovery reference through actual advanced JSON; does not prove actual game animation.',
        'PNG_scope':'Two ready98 actual frame/continuous views, complete skill-timing and damage blocks inside actual viewport; continuous view uses real technical checkbox. Full technical text and exact timing/report excerpts retained separately; hidden tail technical fields are not claimed visible. Root separately views both actual PNGs.'}
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
        from PySide6.QtCore import Qt,qVersion
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
        with tempfile.TemporaryDirectory(prefix='public121-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({values[0]:profile(*values) for values in OPERATORS},ensure_ascii=False,indent=2)+'\n').encode()
            run_path.write_bytes(run_raw);account_path.write_bytes(account_raw)
            module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
            window=module.MainWindow();window.resize(1400,1250);window.show();window.centralWidget().setCurrentIndex(1)
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
            def screenshot(identity,result,technical_view):
                assert window.damage_technical.isChecked() is technical_view
                blocks={block['id']:block for block in result['report']['sections']}
                assert 'timing' in blocks and 'damage' in blocks
                first=window.damage_text.document().find('【'+blocks['timing']['title']+'】')
                damage=window.damage_text.document().find('【'+blocks['damage']['title']+'】')
                assert not first.isNull() and not damage.isNull() and first.blockNumber()<damage.blockNumber()
                # Use actual document block boundaries, not unrendered DPS labels.
                last=QTextCursor(damage);last.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                assert last.movePosition(QTextCursor.MoveOperation.NextBlock)
                damage_rows=[]
                while True:
                    text=last.block().text()
                    if text.startswith('【') and text.endswith('】'):break
                    if text:damage_rows.append(text)
                    candidate=QTextCursor(last)
                    if not candidate.movePosition(QTextCursor.MoveOperation.NextBlock):break
                    if candidate.block().text().startswith('【') and candidate.block().text().endswith('】'):break
                    last=candidate
                    assert len(damage_rows)<30
                assert len(damage_rows)==len(blocks['damage']['metrics'])
                midpoint=(first.blockNumber()+last.blockNumber())//2
                middle=QTextCursor(window.damage_text.document().findBlockByNumber(midpoint))
                pure('center complete timing and damage blocks',lambda:(window.damage_text.setTextCursor(middle),window.damage_text.centerCursor()))
                head=QTextCursor(first);head.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                visible=[];rectangles=[]
                while head.blockNumber()<=last.blockNumber():
                    assert len(visible)<80
                    end=QTextCursor(head);end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    visible.append(head.block().text())
                    rectangles.extend((window.damage_text.cursorRect(head),window.damage_text.cursorRect(end)))
                    if head.blockNumber()==last.blockNumber():break
                    assert head.movePosition(QTextCursor.MoveOperation.NextBlock)
                viewport=window.damage_text.viewport().rect()
                assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                assert any(line.startswith('预计初动：') and '0' in line for line in visible)
                visual=save('actual_PNG_complete_timing_damage',technical_view=technical_view,
                    section_ids=('timing','damage'),displayed_text=window.damage_text.toPlainText(),
                    visible_blocks=visible,cursor_rects=[(r.x(),r.y(),r.width(),r.height()) for r in rectangles],
                    viewport_rect=(viewport.x(),viewport.y(),viewport.width(),viewport.height()),
                    full_timing_block=blocks['timing'],full_damage_block=blocks['damage'])
                path=out/(identity+'.png');assert window.grab().save(str(path),'PNG')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':visual})
            idle();assert not window.run.preserve_unreadable and window.run.save_issue is None
            initial=freeze(joint());assert run_path.read_bytes()==run_raw and account_path.read_bytes()==account_raw
            receipt['initial']=save('actual_public_fixture_loaded',run_bytes=run_raw,account_bytes=account_raw,value=initial)
            assert set(window.run.held_relic_ids())==set(INITIAL_SP_IDS)
            pure('manual per-case relic preview over unchanged actual held fixture',lambda:window.auto_relics.setChecked(False))
            pure('give actual report viewport enough height',lambda:window.damage_text.setMinimumHeight(760))
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
            baseline={};complete_ready={}
            def select_relics(ids):
                requested=set(ids);seen=set()
                for i in range(window.relic_list.count()):
                    item=window.relic_list.item(i);rid=item.data(Qt.ItemDataRole.UserRole)
                    if rid in requested:seen.add(rid)
                    item.setCheckState(Qt.CheckState.Checked if rid in requested else Qt.CheckState.Unchecked)
                assert seen==requested
            for case in CASES:
                op=case['operator'];skill=case['skill'];identity=case['id']
                active.update(case=identity,phase='actual_operator_configuration')
                pure('actual public recruited operator',lambda:window.operator_choices.select_value(op))
                index=window.skill.findData(skill);assert index>=0
                pure('actual selected skill',lambda:window.skill.setCurrentIndex(index))
                pure('actual frame/continuous widget',lambda:window.frame_timing.setChecked(case['mode']=='frames'))
                pure('actual manual None/initialSP relic selection',lambda:select_relics(case['relic_ids']))
                pure('zero declared healing targets',lambda:window.healing_targets.setValue(0))
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
                assert caller['continuous_attacks'] is True and caller['relic_ids']==case['relic_ids']
                assert caller['inventory_status']=={'source':'manual_test','complete':True,'recognized':len(case['relic_ids']),'expected_count':None}
                assert 'relic_history_context' not in caller
                assert caller['healing_targets']==0
                assert caller['initial_neural_buildup']==0 and caller['enemy_in_neural_break'] is False
                assert caller['enemy_is_boss'] is False and caller['palsy_triggers']==0
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
                if case['relic_ids']:
                    assert '预计初动：0.00 秒' in texts['default'] and '预计初动：0.00 秒' in texts['technical']
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                pure('actual technical checkbox',lambda:window.damage_technical.setChecked(True))
                assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                pure('restore actual ordinary report checkbox',lambda:window.damage_technical.setChecked(False))
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                assert_native_equal(freeze({'damage_result':window.damage_result,'joint':joint()}),before,'both report views preserve full result and state')
                snapshot=freeze({'caller':window.damage_result['scenario'],'damage_result':window.damage_result,'texts':texts,
                    'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':joint()})
                ref=save('actual_window_snapshot',value=snapshot,manual_oracle=want,case_definition=case,
                    technical_timing_excerpt={'initial_seconds':result['estimate']['skill']['initial_seconds'],
                        'timing':result['timing'],'report_blocks':[block for block in result['report']['sections'] if block['id'] in ('timing','damage')]})
                mode=case['mode']
                if not case['relic_ids']:
                    baseline[mode]=(snapshot,ref)
                elif case['shape']=='complete_control':
                    prior,prior_ref=baseline[mode]
                    normalized=freeze(caller);normalized['relic_ids']=prior['caller']['relic_ids']
                    normalized['inventory_status']=prior['caller']['inventory_status']
                    assert_native_equal(normalized,prior['caller'],'complete caller except declared relic ids/inventory recognition')
                    assert_native_equal(snapshot['state_and_disks'],prior['state_and_disks'],'birthSP preview preserves state/account/disks')
                    assert_native_equal(result['components'],prior['damage_result']['result']['components'],'birthSP changes no current output component graph')
                    assert_native_equal({key:result['estimate']['skill'][key] for key in LIFECYCLE_FIELDS},
                        {key:prior['damage_result']['result']['estimate']['skill'][key] for key in LIFECYCLE_FIELDS},'birthSP changes no cast/recharge/cycle lifecycle')
                    pairs.append({'mode':mode,'type':'noSP_vs_ready','without_SP_snapshot':prior_ref,'ready_snapshot':ref,
                        'complete_current_caller_only_relic_selection_changes':True,'full_component_graph_equal':True,
                        'all_noninitial_lifecycle_fields_equal':True,'state_account_disks_preserved':True})
                    if case['relic_ids']==['rogue_6_relic_legacy_98']:complete_ready[mode]=(snapshot,ref)
                else:
                    prior,prior_ref=complete_ready[mode]
                    normalized=freeze(caller);normalized['window_seconds']=prior['caller']['window_seconds']
                    assert_native_equal(normalized,prior['caller'],'ready complete/short caller differs only by actual observation interval')
                    assert_native_equal(snapshot['state_and_disks'],prior['state_and_disks'],'ready short control state/account/disks')
                    for key in (*LIFECYCLE_FIELDS,'initial_seconds'):
                        assert_native_equal(result['estimate']['skill'][key],prior['damage_result']['result']['estimate']['skill'][key],'ready complete/short unchanged lifecycle '+key)
                    pairs.append({'mode':mode,'type':'ready_complete_vs_short','complete_snapshot':prior_ref,'short_snapshot':ref,
                        'all_lifecycle_fields_equal':True,'state_account_disks_preserved':True})
                rows.append({'id':identity,'operator':op,'mode':case['mode'],'shape':case['shape'],
                    'window_seconds':case['seconds'],'snapshot':ref,'numeric':call['native'],'manual_oracle':want})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],'next_case_index':len(rows),
                        'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                if case['png']:
                    if case['technical_png']:pure('real technical view for ready zero screenshot',lambda:window.damage_technical.setChecked(True))
                    screenshot(identity,result,case['technical_png'])
                    if case['technical_png']:pure('restore ordinary view after ready zero screenshot',lambda:window.damage_technical.setChecked(False))
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
        assert len(rows)==8 and len(pairs)==6 and len(pngs)==2 and not errors
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
