"""Source-only preparation: Root runs the real 109 MainWindow workflow."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, read_record, write_record, source_map

HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
TOKEN = 'token_10001_deepcl_tentac'
DEADLINE = 450
LEVELS = {'char_002_amiya':80, 'mechanist':90, 'kaltsit':90,
          'char_110_deepcl':70, 'char_4182_oblvns':90, 'char_1037_amiya3':80,
          'char_1046_sbell2':90, 'char_206_gnosis':90}
CHANGED_PATHS = {'rouge/timing.py','rouge/damage.py','rouge/estimate.py',
                 'rouge/operator_engine.py','rouge/app.py','scripts/verify_cloud.py',
                 'tests/test_aglna_gravity_weight_107.py'}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def profile(op):
    return {'id':op,'scope':'operator_profile','fields':{'elite':2,'level':LEVELS[op],
        'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':1},
        'skill_ranks':{str(n):10 for n in range(1,3 if op in ('char_110_deepcl','char_1037_amiya3') else 4)},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def fixture():
    operators={}
    for op in LEVELS:
        member=profile(op);member.update(scope='run',present=True,recruitment_kind='non_emergency',
            char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
            invalid_fields=[],invalid_skill_ranks=[],missing_fields=[])
        operators[op]=member
    return {'id':'public109-window','started_at':0.0,'last_read':1000.0,'operators':operators,
        'crew_count':len(operators),'selected_operator':'char_002_amiya','relics':{},
        'tactical_tools':{},'relic_count':0,'inventory_verified':True,
        'inventory_confirmed_at':1000.0,'bar_signature':[],'relic_icon_memory':None,
        'history':[],'resources':{},'config':{},'maps':{},'last_node_content':None,
        'node_contents':[],'public_opaque':{'signed_zero':-0.0,'nullable':None}}

def cases():
    rows=[]
    def add(identity,op,skill=1,mode='continuous',kind='healthy',timing=None,window=10,recipients=1,manual=None):
        rows.append({'id':identity,'op':op,'skill':skill,'mode':mode,'kind':kind,
            'timing':timing,'window':window,'recipients':recipients,'manual':manual})
    add('healthy-ordinary-frames','char_002_amiya',mode='frames')
    add('healthy-ordinary-continuous','char_002_amiya')
    add('healthy-legacy-ammo','mechanist')
    add('healthy-independent-token','char_110_deepcl',mode='frames',timing={'target_windows':[]})
    add('healthy-permanent-reference','char_4182_oblvns',2)
    add('empty-ordinary-continuous','char_002_amiya',kind='zero',timing={'target_windows':[]})
    for mode in ('frames','continuous'):
        add('empty-legacy-ammo-'+mode,'mechanist',mode=mode,kind='ammo',window=None,timing={'target_windows':[]})
        for recipients in (1,0):
            add('empty-medical-'+mode+'-'+str(recipients),'kaltsit',2,mode,
                'medical',{'target_windows':[]},None,recipients)
        add('empty-manual-duration-'+mode,'mechanist',2,mode,'manual',{'target_windows':[]},10,1,20)
    add('empty-generic-medical','char_1037_amiya3',2,kind='opening-medical',timing={'target_windows':[]})
    add('empty-generic-snow','char_1046_sbell2',1,kind='opening-snow',timing={'target_windows':[]})
    add('empty-gnosis','char_206_gnosis',2,kind='zero',timing={'target_windows':[]})
    add('empty-token-own-scope','char_110_deepcl',mode='continuous',kind='token',
        timing={'units':{TOKEN:{'target_windows':[]}}})
    assert len(rows)==18 and len({r['id'] for r in rows})==18
    return rows

def candidate_contract(item,result):
    kind=item['kind'];skill=result['estimate']['skill']
    if kind=='healthy':return
    if kind=='token':
        components={c['name']:c for c in result['components']}
        assert components['触手']['total']==0 and components['触手']['hits']==0
        assert components['本体普攻']['total']>0 and result['total_damage']>0
        return
    if kind in ('zero','ammo','medical','manual'):
        assert result['total_damage']==0 and skill['total_damage']==0
    if kind=='ammo':
        assert result['hits']==0 and result['execution_seconds'] is None
        assert skill['recharge_seconds'] is None
    if kind=='medical':
        if item['recipients']:
            assert skill['total_healing']>0 and skill['duration_seconds'] is not None
        else:
            assert result['hits']==0 and result['execution_seconds'] is None
            assert skill['total_healing']==0 and skill['duration_seconds'] is None
    if kind=='manual':
        assert skill['duration_seconds']==20 and result['shield_break_reference']['actual_end_seconds'] is None
        for key in ('phase_damage','cycle_damage','window_damage'):assert skill[key]==0
    if kind in ('opening-medical','opening-snow'):
        name='慈悲愿景开启伤害' if kind=='opening-medical' else '施放伤害'
        component=next(c for c in result['components'] if c['name']==name)
        assert component['total']==0 and component['hits']==0
        assert result['total_damage'] is None  # Later independent clocks remain unbound.

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--source-count',type=int,required=True)
    parser.add_argument('--gold');parser.add_argument('--gold-exit')
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;guard_path=Path(args.guard).resolve()
    assert args.phase in ('gold','candidate') and not out.exists() and root not in out.parents and out!=root
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    gold=None;gold_dir=None;gold_raw=None
    if args.phase=='gold':assert args.source_count==751
    else:
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_bytes()==b'0\n'
        gold_dir=Path(args.gold).resolve();gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)
        assert gold['kind']=='ROOT_ACTUAL_109_REAL_MAINWINDOW' and gold['phase']=='gold'
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['Qt_errors']==[]
        assert gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['native_helper_sha256']==HELPER_SHA
        assert gold['source_before']==gold['source_after'] and len(gold['source_before'])==751
        assert gold['source_additional_before']==gold['source_additional_after']==extra
        assert not gold['source_drift'] and len(gold['rows'])==18 and len(gold['windows'])==1
        assert set(expected)-set(gold['source_before'])=={'tests/test_empty_owner_acquisition_109.py'}
        assert not set(gold['source_before'])-set(expected)
        assert {p for p in gold['source_before'] if expected[p]!=gold['source_before'][p]}==CHANGED_PATHS
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];windows=[];records=[];pngs=[];errors=[];calls=[];active={'case':'bootstrap','phase':'constructor'}
    done=threading.Event();started=time.perf_counter();window=None;module=None;backend=None;calculator=None
    receipt={'kind':'ROOT_ACTUAL_109_REAL_MAINWINDOW','phase':args.phase,'passed':False,'workflow_complete':False,
        'runner_sha256':sha(Path(__file__).read_bytes()),'native_helper_sha256':HELPER_SHA,
        'source_guard_sha256':sha(guard_raw),'source_before':expected,'source_additional_before':extra,
        'rows':rows,'windows':windows,'records':records,'pngs':pngs,'Qt_errors':errors,'deadline_seconds':DEADLINE,
        'native_windows_verified':False,'private_state_access':False,'game_chat_sampling_executed':False,
        'scope':'18 actual UI states; healthy whole Gold; changed explicit source contracts; unknown clocks remain unknown.',
        'restart_scope':'One real close then direct RunState reload; no second MainWindow or live JSON alias claim.',
        'formatter_scope':'Three complete formatter joint purity, not independent per-formatter purity.'}
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
        from PySide6.QtWidgets import QApplication
        from rouge import app as module,estimate,reporting
        from rouge.run_state import RunState
        application=QApplication.instance() or QApplication([]);backend=module.DesktopBackend;calculator=module.calculate_damage
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                details=error_record(error);after=freeze({'args':positional,'kwargs':keywords})
                ref=save('actual_calculate_exception',before=before,after=after,error=details)
                calls.append({'caller':before,'error':details,'native':ref})
                assert_native_equal(after,before,'exception caller purity');raise
            after=freeze({'args':positional,'kwargs':keywords});ref=save('actual_calculate_result',before=before,
                after={'args':positional,'kwargs':keywords},result=value)
            calls.append({'caller':before,'error':None,'native':ref});assert_native_equal(after,before,'numeric caller purity');return value
        module.calculate_damage=observed
        with tempfile.TemporaryDirectory(prefix='public109-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({op:profile(op) for op in LEVELS},ensure_ascii=False,indent=2)+'\n').encode()
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
            idle();assert not window.run.preserve_unreadable and window.run.save_issue is None
            baseline=freeze(joint());assert run_path.read_bytes()==run_raw and account_path.read_bytes()==account_raw
            pure('manual relic selection',lambda:window.auto_relics.setChecked(False))
            for item in cases():
                active.update(case=item['id'],phase='configure_actual_controls')
                pure('operator',lambda:window.operator_choices.select_value(item['op']))
                index=window.skill.findData(item['skill']);assert index>=0
                pure('skill',lambda:window.skill.setCurrentIndex(index))
                pure('timing mode',lambda:window.frame_timing.setChecked(item['mode']=='frames'))
                pure('window value',lambda:window.window_seconds.setValue(item['window'] if item['window'] is not None else 10))
                pure('window enabled',lambda:window.limit_window.setChecked(item['window'] is not None))
                pure('healing recipients',lambda:window.healing_targets.setValue(item['recipients']))
                pure('break count zero',lambda:window.shield_breaks.setValue(0))
                pure('manual duration',lambda:window.shield_duration.setValue(item['manual'] or 20))
                pure('manual duration enabled',lambda:window.shield_duration_known.setChecked(item['manual'] is not None))
                pure('public timing JSON',lambda:window.timing_scenario.setPlainText('' if item['timing'] is None else json.dumps(item['timing'])))
                active['phase']='explicit_snapshot';start=len(calls);pure('MainWindow.calculate',window.calculate)
                assert len(calls)==start+1;call=calls[-1];assert call['error'] is None and window.damage_result is not None
                caller=call['caller']['args'][0];result=window.damage_result['result']
                assert caller['operator']==item['op'] and caller['skill']==item['skill'] and caller['timing_mode']==item['mode']
                assert caller['elite']==2 and caller['level']==LEVELS[item['op']] and caller['skill_rank']==10
                assert_native_equal(caller.get('timing'),item['timing'],'actual timing control input')
                assert ('window_seconds' in caller)==(item['window'] is not None)
                assert_native_equal(window.damage_result['scenario'],caller,'actual UI caller match')
                before=freeze({'result':result,'joint':joint()})
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                       'technical':reporting.format_report(result,technical=True)}
                after=freeze({'result':result,'joint':joint()});save('actual_three_formatter_group',before=before,after=after,texts=texts)
                assert_native_equal(after,before,'three formatter joint purity');assert texts['estimate']==texts['default']
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                if args.phase=='candidate':candidate_contract(item,result)
                value={'caller':caller,'damage_result':window.damage_result,'texts':texts,
                       'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':freeze(joint())}
                ref=save('actual_window_snapshot',value=value)
                if gold:
                    old_row=next(r for r in gold['rows'] if r['id']==item['id']);old=read_record(gold_dir/'records',old_row['snapshot'])['value']
                    if item['kind']=='healthy':assert_native_equal(value,old,'whole healthy Gold result/caller/text/state/disk')
                    else:
                        assert_native_equal(value['caller'],old['caller'],'changed same raw Gold caller')
                        assert_native_equal(value['state_and_disks'],old['state_and_disks'],'changed same Gold state/disk')
                rows.append({'id':item['id'],'kind':item['kind'],'snapshot':ref,'numeric':call['native'],
                             'healthy_complete_Gold_same':bool(gold and item['kind']=='healthy')})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],
                        'next_case_index':len(rows),'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                if args.phase=='candidate' and item['id'] in ('empty-ordinary-continuous','empty-medical-continuous-1','empty-manual-duration-continuous','empty-token-own-scope'):
                    anchor='技能情况：';cursor=window.damage_text.document().find(anchor);assert not cursor.isNull()
                    pure('visible report anchor',lambda:(window.damage_text.setTextCursor(cursor),window.damage_text.ensureCursorVisible()))
                    rectangle=window.damage_text.cursorRect();viewport=window.damage_text.viewport().rect()
                    assert window.damage_text.isVisible() and viewport.contains(rectangle.center()) and window.damage_text.textCursor().selectedText()==anchor
                    visual=save('actual_PNG_anchor',text=window.damage_text.toPlainText(),anchor=anchor,
                        cursor_rect=(rectangle.x(),rectangle.y(),rectangle.width(),rectangle.height()),
                        viewport_rect=(viewport.x(),viewport.y(),viewport.width(),viewport.height()))
                    path=out/(item['id']+'.png');assert window.grab().save(str(path),'PNG')
                    pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':visual})
            active.update(case='window',phase='close_direct_RunState_reload');before=freeze(joint())
            window.close();application.processEvents();assert_native_equal(joint(),before,'real close purity')
            persisted=json.loads(run_path.read_bytes());restarted=RunState(run_path)
            assert not restarted.preserve_unreadable and restarted.save_issue is None
            assert_native_equal(restarted.state,baseline['run'],'direct reload original accepted loaded graph')
            assert_native_equal(joint(),before,'direct reload disk purity')
            ref=save('actual_close_RunState_reload',live_before=before,persisted_json=persisted,
                restart_state=restarted.state,disks_after=joint()['disks'])
            windows.append({'id':'public109-window','restart':ref,'input_disk_sha256':sha(run_raw)})
            window.deleteLater();application.processEvents();window=None
        assert len(rows)==18 and len(windows)==1 and len(pngs)==(4 if args.phase=='candidate' else 0) and not errors
        receipt.update(passed=True,workflow_complete=True)
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
        if gold_raw is not None:receipt['actual_gold_receipt_sha256']=sha(gold_raw)
        receipt['elapsed_seconds']=time.perf_counter()-started
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed':receipt['passed'],'rows':len(rows),'windows':len(windows),'pngs':len(pngs)}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
