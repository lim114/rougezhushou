"""Source preparation only; Root runs one real permanent-attack MainWindow."""
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

OP = 'char_4182_oblvns'
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 450
CLOCK_KEYS = ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds',
              'sp_recovery_per_second','mode')

def sha(raw):return hashlib.sha256(raw).hexdigest()

def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def profile():
    return {'id':OP,'scope':'operator_profile','fields':{'elite':2,'level':90,
        'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':1},
        'skill_ranks':{'1':10,'2':10,'3':10},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def fixture():
    member=profile();member.update(scope='run',present=True,recruitment_kind='non_emergency',
        char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
        invalid_fields=[],invalid_skill_ranks=[],missing_fields=[])
    return {'id':'public110-window','started_at':0.0,'last_read':1000.0,'operators':{OP:member},
        'crew_count':1,'selected_operator':OP,'relics':{},'tactical_tools':{},'relic_count':0,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

def sp_fields(result):
    skill=result['estimate']['skill']
    return {'skill':{key:skill[key] for key in CLOCK_KEYS},
        'estimate_fields':{key:value for key,value in result['estimate'].items() if key=='sp_events'},
        'timing_report':next(section for section in result['report']['sections'] if section['id']=='timing')}

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
    assert guard['section']==110 and len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];active={'case':'bootstrap','phase':'constructor'}
    started=time.perf_counter();done=threading.Event();window=None;module=None;backend=None;calculator=None
    receipt={'kind':'ROOT_ACTUAL_110_REAL_MAINWINDOW','phase':'candidate','passed':False,
        'workflow_complete':False,'runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'rows':rows,'pairs':pairs,'records':records,'pngs':pngs,'Qt_errors':errors,
        'deadline_seconds':DEADLINE,'private_state_access':False,'native_windows_verified':False,
        'game_chat_sampling_executed':False,
        'comparison_scope':'Within the current real window: six default/empty pairs. Prior original public API evidence is separate; this is not an original-window Gold comparison.',
        'restart_scope':'One real close then direct RunState reload; no second MainWindow or live JSON alias claim.',
        'formatter_scope':'Three complete formatter joint purity; no per-formatter isolated-purity claim.',
        'callback_scope':'No callback relic or synthetic callback events; independent unknown note collisions remain unknown.'}
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
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                details=error_record(error);after=freeze({'args':positional,'kwargs':keywords})
                ref=save('actual_calculate_exception',before=before,after=after,error=details)
                calls.append({'caller':before,'error':details,'native':ref})
                assert_native_equal(after,before,'exception caller purity');raise
            after=freeze({'args':positional,'kwargs':keywords})
            ref=save('actual_calculate_result',before=before,after={'args':positional,'kwargs':keywords},result=value)
            calls.append({'caller':before,'error':None,'native':ref})
            assert_native_equal(after,before,'numeric caller purity');return value
        module.calculate_damage=observed
        with tempfile.TemporaryDirectory(prefix='public110-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({OP:profile()},ensure_ascii=False,indent=2)+'\n').encode()
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
                before=freeze(joint());value=callback();idle();after=freeze(joint())
                save('actual_UI_step',label=label,before=before,after=after)
                assert_native_equal(after,before,label+' state/disk purity');return value
            def screenshot(identity):
                anchor='【伤害输出】';head=window.damage_text.document().find(anchor);assert not head.isNull()
                pure('center actual damage header',lambda:(window.damage_text.setTextCursor(head),window.damage_text.centerCursor()))
                cursors=[QTextCursor(head)]
                for _ in range(3):
                    tail=QTextCursor(cursors[-1]);assert tail.movePosition(QTextCursor.MoveOperation.NextBlock)
                    cursors.append(tail)
                viewport=window.damage_text.viewport().rect()
                rectangles=[window.damage_text.cursorRect(cursor) for cursor in cursors]
                assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                assert window.damage_text.textCursor().selectedText()==anchor
                visual=save('actual_PNG_visible_damage_rows',anchor=anchor,
                    displayed_text=window.damage_text.toPlainText(),visible_blocks=[cursor.block().text() for cursor in cursors],
                    cursor_rects=[(r.x(),r.y(),r.width(),r.height()) for r in rectangles],
                    viewport_rect=(viewport.x(),viewport.y(),viewport.width(),viewport.height()))
                path=out/(identity+'.png');assert window.grab().save(str(path),'PNG')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':visual})
            idle();assert not window.run.preserve_unreadable and window.run.save_issue is None
            initial=freeze(joint());assert run_path.read_bytes()==run_raw and account_path.read_bytes()==account_raw
            pure('manual no-relic inventory',lambda:window.auto_relics.setChecked(False))
            pure('permanent operator',lambda:window.operator_choices.select_value(OP))
            pure('ten-second observation value',lambda:window.window_seconds.setValue(10))
            pure('explicit observation enabled',lambda:window.limit_window.setChecked(True))
            pure('declared continuous attacks',lambda:window.continuous_attacks.setChecked(True))
            for owner,key,skills,widget in window.model_option_widgets:
                if owner==OP:
                    if key=='note_count':pure('zero existing notes',lambda widget=widget:widget.setValue(0))
                    elif key in ('organ_mode','fever'):pure('default piano/no Fever '+key,lambda widget=widget:widget.setChecked(False))
                    elif key=='ranged_attack':pure('default ranged condition',lambda widget=widget:widget.setChecked(True))
            for skill in (1,2,3):
                index=window.skill.findData(skill);assert index>=0
                pure('skill selection',lambda:window.skill.setCurrentIndex(index))
                pure('unbound normal animation',lambda:window.normal_animation_reference.setCurrentIndex(0))
                pure('unbound skill animation',lambda:window.skill_animation_reference.setCurrentIndex(0))
                for mode in ('frames','continuous'):
                    pure('timing mode',lambda:window.frame_timing.setChecked(mode=='frames'))
                    baseline=None
                    for empty in (False,True):
                        identity=f's{skill}-{mode}-'+('empty' if empty else 'baseline')
                        active.update(case=identity,phase='configure_actual_timing')
                        timing={'target_windows':[]} if empty else None
                        pure('public timing JSON',lambda:window.timing_scenario.setPlainText(json.dumps(timing) if empty else ''))
                        active['phase']='explicit_snapshot';start=len(calls);pure('MainWindow.calculate',window.calculate)
                        assert len(calls)==start+1 and calls[-1]['error'] is None and window.damage_result is not None
                        call=calls[-1];caller=call['caller']['args'][0];result=window.damage_result['result']
                        assert caller['operator']==OP and caller['skill']==skill and caller['timing_mode']==mode
                        assert caller['elite']==2 and caller['level']==90 and caller['skill_rank']==10
                        assert caller['module_id'] is None and caller['module_level']==0
                        assert caller['window_seconds']==10 and caller['continuous_attacks'] is True and caller['relic_ids']==[]
                        assert ('timing' in caller)==empty
                        if empty:assert_native_equal(caller['timing'],timing,'exact public empty declaration')
                        if skill==2:assert caller['organ_mode'] is False and caller['fever'] is False
                        assert_native_equal(window.damage_result['scenario'],caller,'actual UI/native caller match')
                        before=freeze({'result':result,'joint':joint()})
                        texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                               'technical':reporting.format_report(result,technical=True)}
                        after=freeze({'result':result,'joint':joint()})
                        save('actual_three_formatter_group',before=before,after=after,texts=texts)
                        assert_native_equal(after,before,'three formatter joint purity')
                        assert texts['estimate']==texts['default'] and window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                        snapshot=freeze({'caller':caller,'damage_result':window.damage_result,'texts':texts,
                            'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':joint()})
                        ref=save('actual_window_snapshot',value=snapshot,sp=sp_fields(result))
                        if skill==1:
                            assert result['total_damage'] is None and result['complete'] is False
                            assert result['unbound_cast_reference']['actual_hit_times_seconds'] is None
                            assert result['unbound_cast_reference']['actual_end_seconds'] is None
                        if not empty:
                            if skill!=1:assert result['total_damage']>0 and any(c['hits']>0 for c in result['components'])
                            baseline=snapshot;baseline_ref=ref
                        else:
                            old=baseline['damage_result']['result']
                            assert_native_equal(sp_fields(result),sp_fields(old),'complete preserved public SP fields/report')
                            current_caller=freeze(caller);current_caller.pop('timing')
                            assert_native_equal(current_caller,baseline['caller'],'same UI caller except explicit timing')
                            assert_native_equal(snapshot['state_and_disks'],baseline['state_and_disks'],'paired state/account/disk')
                            if skill==1:
                                assert_native_equal({'components':result['components'],'reference':result['unbound_cast_reference']},
                                    {'components':old['components'],'reference':old['unbound_cast_reference']},'S1 independent conditional notes unchanged')
                            else:
                                assert result['total_damage']==0
                                assert all(c['hits']==0 and c['total']==0 and c['times_seconds']==[] for c in result['components'])
                                for old_component,new_component in zip(old['components'],result['components'],strict=True):
                                    assert_native_equal(new_component['per_hit'],old_component['per_hit'],'same cultivated per-hit reference')
                                if skill==3:
                                    for key in ('total_damage','phase_damage','cycle_damage'):assert result['estimate']['skill'][key]==0
                            pairs.append({'skill':skill,'mode':mode,'baseline_snapshot':baseline_ref,'empty_snapshot':ref,
                                          'native_SP_fields_preserved':True,'independent_S1_unknown_preserved':skill==1})
                        rows.append({'id':identity,'skill':skill,'mode':mode,'empty':empty,'snapshot':ref,'numeric':call['native']})
                        with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                            stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],'next_case_index':len(rows),
                                'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                        if skill==3 and mode=='frames':screenshot(identity)
            active.update(case='window',phase='close_direct_RunState_reload');before=freeze(joint())
            window.close();application.processEvents();assert_native_equal(joint(),before,'real close purity')
            restarted=RunState(run_path);assert not restarted.preserve_unreadable and restarted.save_issue is None
            assert_native_equal(restarted.state,initial['run'],'direct reload original accepted loaded graph')
            assert_native_equal(joint(),before,'direct reload disk purity')
            receipt['close_reload']=save('actual_close_RunState_reload',live_before=before,
                persisted_json=json.loads(run_path.read_bytes()),restart_state=restarted.state,disks_after=joint()['disks'])
            window.deleteLater();application.processEvents();window=None
        assert len(rows)==12 and len(pairs)==6 and len(pngs)==2 and not errors
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
