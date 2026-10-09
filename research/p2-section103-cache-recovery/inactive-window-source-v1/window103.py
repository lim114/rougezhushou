"""Source-only isolated real103 MainWindow Gold/candidate workflow for Root.

The author does not execute this file. Raw original743 observations are bound
as prior defect evidence; actual Gold must use completed102 and candidate103.
Public JSON and explicit API observations do not claim natural OCR production.
"""
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

HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
ORIGIN_SHA='9100d4cf424e46951faa8b6312964a3409b25d65486d2344350ed37b95c876cd'
SQUAD_SHA='9eaada838fa8d2d98f8314965cea865395f0978d27bd0fef18ba23b79a5c9472'
PROOF_SHA='c24b86863aa73ae0c47a85b38312ac848a6c9969138413804fdbd28f24b925be'
OWNER='mechanist'
BUFF='rogue_6_from_relic_13'
SQUAD='rogue_6_band_6'
SQUAD_NAME='矛头分队'
MARKER={'kind':'non_emergency','version':2,'score':0,
        'source':'等级左侧区域未显示应急人形/时钟标识'}
MISSING=object()
HEALTHY_COUNT=9
CASE_COUNT=19


def sha(raw):return hashlib.sha256(raw).hexdigest()


def account():
    return {'id':OWNER,'scope':'operator_profile','fields':{'elite':2,'level':80,
            'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':3},
            'skill_ranks':{'1':7,'3':10},'captured_at':1000.0,
            'sources':{},'field_times':{},'skill_times':{}}


def fixture():
    member={**account(),'scope':'run','present':True,'char_buff_ids':[BUFF],
            'char_buffs_complete':False,'char_buff_absent_ids':[],
            'char_buff_pending_ids':[],'invalid_fields':[],'invalid_skill_ranks':[],
            'missing_fields':[],'sources':{'public_opaque':[None,{'nullable':None}]}}
    return {'id':'public-cache-window103','started_at':0.0,'last_read':1000.0,
            'operators':{OWNER:member},'crew_count':1,'selected_operator':OWNER,
            'relics':{},'tactical_tools':{},'relic_count':0,'inventory_verified':True,
            'inventory_confirmed_at':1000.0,'bar_signature':[],
            'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
            'last_node_content':None,'node_contents':[],
            'public_opaque':{'signed_zero':-0.0,'nullable':None}}


def origin_case(identity,source=MISSING,*,old=MISSING,action='discovery',healthy=False):
    saved=fixture();member=saved['operators'][OWNER]
    if source is not MISSING:member['sources']['recruitment_kind']=deepcopy(source)
    if old is not MISSING:member['recruitment_kind']=old
    observed={'operators':[{'id':OWNER,'scope':'run','fields':{},'skill_ranks':{}}]}
    current=observed['operators'][0]
    if action=='unused':current['recruitment_kind']=None
    else:
        current.update(recruitment_kind='non_emergency',sources={'recruitment_kind':deepcopy(MARKER)})
        if action=='change':current.update(fields={'level':79},skill_ranks={'3':7})
    return {'id':identity,'healthy':healthy,'kind':'origin','saved':saved,
            'observed':observed,'at':999.0 if action=='stale' else 1001.0,
            'action':action,'apply_expected':action!='stale','initial_math':True,
            'after_math':True,'reuse_initial':False,'reuse_after':False}


def squad_record(identity=SQUAD,*,name=SQUAD_NAME,verified=False,level=None,captured=MISSING):
    value={'id':deepcopy(identity),'name':name,'level':level,'effect_verified':verified,
           'source':('本局分队提示的完整名称及效果' if verified else
                     '探索界面分队图标；基础与强化共用图案，效果未确认')}
    if captured is not MISSING:value['captured_at']=captured
    return value


def squad_case(identity,old_id,*,old_verified=True,old_level=0,old_name=SQUAD_NAME,
               old_time=1000.0,fresh_id=SQUAD,fresh_name=SQUAD_NAME,fresh_verified=False,
               fresh_level=None,protected=False,healthy=False):
    saved=fixture();saved['operators'][OWNER]['recruitment_kind']='non_emergency'
    saved['config']['squad']=squad_record(old_id,name=old_name,verified=old_verified,
                                         level=old_level,captured=old_time)
    observed={'operators':[],'config':{'squad':squad_record(fresh_id,name=fresh_name,
                                   verified=fresh_verified,level=fresh_level)}}
    known=isinstance(old_id,str) and old_id in (SQUAD,'rogue_6_band_20')
    return {'id':identity,'healthy':healthy,'kind':'squad','saved':saved,
            'observed':observed,'at':1001.0,'action':'protected' if protected else 'repair',
            'apply_expected':True,'initial_math':known,'after_math':True,
            'reuse_initial':known and old_time is not None,'reuse_after':True}


def cases(phase):
    rows=[origin_case('healthy-origin-missing',healthy=True),
          origin_case('healthy-origin-empty',{},healthy=True),
          origin_case('healthy-origin-valid',MARKER,healthy=True),
          origin_case('healthy-origin-real-change',{'source':'等级左侧人形与时钟应急标识'},
                      old='emergency_hire',action='change',healthy=True),
          origin_case('healthy-legacy-gold',{'source':'金色应急雇佣标记'},
                      old='emergency_hire',action='legacy',healthy=True),
          squad_case('healthy-known-true-protected',SQUAD,protected=True,healthy=True),
          squad_case('healthy-trade20-protected','rogue_6_band_20',old_name='多边贸易分队',
                     old_level=1,fresh_id='rogue_6_band_19',fresh_name='多边贸易分队',
                     protected=True,healthy=True),
          origin_case('healthy-unused-null',None,action='unused',healthy=True),
          origin_case('healthy-stale-null',None,action='stale',healthy=True)]
    if phase=='candidate':
        rows.extend(origin_case(identity,source) for identity,source in (
            ('bad-origin-null',None),('bad-origin-list',[]),
            ('bad-origin-text','public-opaque'),('bad-origin-number',1)))
        rows.extend([
            origin_case('bad-origin-real-change',None,old='emergency_hire',action='change'),
            squad_case('bad-squad-list-true-false',[]),
            squad_case('bad-squad-dict-false-false',{},old_verified=False,old_level=None),
            squad_case('bad-squad-dict-true-false',{}),
            squad_case('bad-squad-list-true-true',[],fresh_verified=True,fresh_level=0),
            squad_case('unused-squad-null-time',[],old_verified=False,old_level=None,old_time=None)])
    assert len(rows)==(HEALTHY_COUNT if phase=='gold' else CASE_COUNT)
    return rows


def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--gold');parser.add_argument('--gold-exit')
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent
    assert args.phase in ('gold','candidate') and not out.exists() and out!=root and root not in out.parents
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    previous={}
    for name,want,count in (('actual-original-origin-observations.json',ORIGIN_SHA,14),
                            ('actual-original-squad-observations.json',SQUAD_SHA,17)):
        raw=(artifact/'evidence'/name).read_bytes();assert sha(raw)==want
        value=json.loads(raw);assert value['observation_complete'] is True
        assert value['product_pass'] is False and value['observation_only'] is True
        assert len(value['rows'])==count
        previous[name]={'sha256':want,'rows':count,'source_sha256':value['source_before']}
    proof_raw=(artifact/'evidence'/'original100-public-source743-proof.json').read_bytes()
    assert sha(proof_raw)==PROOF_SHA
    proof=json.loads(proof_raw);assert proof['git_blobs_all_verified'] is True
    assert proof['source_commit']=='e839c3489fe3f0bff445db2ab5771ed1388c51b4'
    assert len(proof['source_sha256'])==743
    assert all(value['source_sha256']==proof['source_sha256'] for value in previous.values())
    guard_path=Path(args.guard);guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert len(expected)==(746 if args.phase=='gold' else 747) and source_map(root)==expected
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    gold=None
    if args.phase=='candidate':
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_text().strip()=='0'
        gold_dir=Path(args.gold);gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['phase']=='gold'
        assert gold['runner_sha256']==sha(Path(__file__).read_bytes())
        assert len(gold['rows'])==HEALTHY_COUNT and gold['source_before']==gold['source_after'] and not gold['source_drift']
        original_sources=gold['source_before']
        assert len(original_sources)==746 and set(expected)-set(original_sources)=={'tests/test_cache_recovery_103.py'}
        assert not set(original_sources)-set(expected)
        assert {name for name in original_sources if expected[name]!=original_sources[name]}=={
            'rouge/run_state.py','rouge/run_config.py','scripts/verify_cloud.py'}
        assert gold['source_additional_before']==gold['source_additional_after']==extra
        assert gold['Qt_errors']==[] and gold['native_windows_verified'] is False
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];errors=[];calls=[];active={'case':'preimport','phase':'preimport'}
    done=threading.Event();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_103_REAL_MAINWINDOW','phase':args.phase,'passed':False,
             'workflow_complete':False,'source_before':expected,'source_guard_sha256':sha(guard_raw),
             'source_additional_before':extra,'runner_sha256':sha(Path(__file__).read_bytes()),
             'original743_actual_evidence':previous,'original743_gitblob_proof_sha256':PROOF_SHA,
             'rows':rows,'records':records,'pngs':pngs,'Qt_errors':errors,'deadline_seconds':450,
             'native_windows_verified':False,'private_state_access':False,
             'game_chat_sampling_executed':False,'natural_OCR_producer_verified':False,
             'restart_scope':'Direct RunState reload after actual observation/close; no second MainWindow'}
    def save(kind,value):
        row=write_record(out/'records',len(records)+1,{'kind':kind,'case':active['case'],
                                                   'phase':active['phase'],**value})
        row.update(kind=kind,case=active['case'],phase=active['phase']);records.append(row);return row
    def deadline():
        if not done.wait(450):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline':450}))
            os._exit(124)
    threading.Thread(target=deadline,daemon=True).start()
    old_hook=sys.excepthook;window=None;application=None;module=None;backend=None;calculator=None
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'phase':active['phase'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.path.insert(0,str(root))
        from PySide6 import __version__
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.run_config import confirmed_config
        from rouge.run_state import RunState
        assert __version__==qVersion()=='6.9.3'
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                assert_native_equal({'args':positional,'kwargs':keywords},before,'Original numeric error caller unchanged')
                details=error_record(error)
                calls.append({'case':active['case'],'error':details,'caller':before})
                save('actual_calculate_exception',{'before':before,
                     'after':freeze({'args':positional,'kwargs':keywords}),'error':details})
                raise
            assert_native_equal({'args':positional,'kwargs':keywords},before,'Original numeric caller unchanged')
            calls.append({'case':active['case'],'error':None,'caller':before})
            save('actual_calculate_result',{'before':before,
                 'after':freeze({'args':positional,'kwargs':keywords}),'result':value})
            return value
        module.calculate_damage=observed
        for case in cases(args.phase):
            active.update(case=case['id'],phase='constructor')
            with tempfile.TemporaryDirectory(prefix='public103-',dir=out/'public-state') as directory:
                folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
                saved=deepcopy(case['saved'])
                raw=(json.dumps(saved,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_raw=(json.dumps({OWNER:account()},ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                run_path.write_bytes(raw);account_path.write_bytes(account_raw)
                module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
                module.DesktopBackend=lambda _path,callback,public=folder:backend(public/'chat',callback)
                window=module.MainWindow();window.resize(1400,1050);window.show();window.centralWidget().setCurrentIndex(1)
                def idle():
                    application.processEvents()
                    assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending and not errors
                def durable():return {'run':window.run.state,'account':window.account_cache.records}
                def disks():
                    return {name:{'exists':path.exists(),'bytes':path.read_bytes() if path.exists() else None}
                            for name,path in (('run',run_path),('account',account_path),
                                              ('run_tmp',run_path.with_suffix('.tmp')),
                                              ('account_tmp',account_path.with_suffix('.tmp')))}
                def unchanged(label,callback):
                    before=freeze(durable());disk=freeze(disks());callback();idle()
                    assert_native_equal(durable(),before,label+' raw state')
                    assert_native_equal(disks(),disk,label+' original disk phase')
                def reuse(run):
                    before=freeze(run.state);disk=freeze(disks())
                    context=run.recognition_context();caller=freeze(context);result=confirmed_config(context)
                    assert_native_equal(context,caller,'Actual confirmed_config caller unchanged')
                    assert_native_equal(run.state,before,'Actual recognition/reuse view keeps raw state')
                    assert_native_equal(disks(),disk,'Actual recognition/reuse view keeps disks')
                    return {'context':context,'confirmed':result}
                def snapshot(math_expected):
                    before=freeze(durable());disk=freeze(disks());result=window.damage_result
                    last=next(value for value in reversed(calls) if value['case']==case['id'])
                    if math_expected:
                        assert result is not None and last['error'] is None
                        native=freeze(result)
                        texts={'estimate':estimate.format_estimate(result['result']),
                               'default':reporting.format_report(result['result']),
                               'technical':reporting.format_report(result['result'],technical=True)}
                        assert texts['estimate']==texts['default']
                        assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                        assert_native_equal(result,native,'All original formatter callers unchanged')
                    else:
                        assert result is None and last['error']['type']=='ValueError'
                        assert last['error']['message']=='本局分队身份与固定档案不符。'
                        assert window.damage_text.toPlainText()==last['error']['message']
                        original_config=last['caller']['args'][0]['run_config']
                        assert_native_equal(original_config,window.run.state['config'],'Bad raw config reaches unchanged original numeric API')
                        texts={'pending':window.damage_text.toPlainText()}
                    config=reuse(window.run)
                    value={'view':{'damage_result':result,'three_texts':texts,'summary':window.run.summary(),
                                   'inventory':window.run.inventory_status(),'reuse':config,
                                   'displayed_damage':window.damage_text.toPlainText()},
                           'durable':freeze(durable()),'disks':freeze(disks())}
                    assert_native_equal(durable(),before,'Actual math/format/view keeps raw state')
                    assert_native_equal(disks(),disk,'Actual math/format/view keeps disks')
                    return value
                def picture(name,tab):
                    unchanged('show actual screenshot tab',lambda:window.centralWidget().setCurrentIndex(tab))
                    path=out/(name+'.png');assert window.grab().save(str(path),'PNG')
                    pngs.append({'case':case['id'],'phase':active['phase'],'tab_index':tab,
                                 'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
                def match_gold(value,label,gold_row,key):
                    original_record=read_record(gold_dir/'records',gold_row[key])
                    assert original_record['case']==case['id']
                    original={name:original_record[name] for name in ('view','durable','disks')}
                    assert_native_equal(value,original,label)
                idle()
                assert disks()=={'run':{'exists':True,'bytes':raw},'account':{'exists':True,'bytes':account_raw},
                                 'run_tmp':{'exists':False,'bytes':None},'account_tmp':{'exists':False,'bytes':None}}
                assert window.run.preserve_unreadable is False and window.run.save_issue is None
                active['phase']='initial-actual-view'
                unchanged('select actual mechanist',lambda:window.operator_choices.select_value(OWNER))
                index=window.skill.findData(3);assert index>=0
                unchanged('select actual S3',lambda:window.skill.setCurrentIndex(index))
                unchanged('actual calculate method',window.calculate)
                before=snapshot(case['initial_math'])
                initial_reuse=before['view']['reuse']['confirmed']
                assert ('squad' in initial_reuse) is case['reuse_initial']
                row={'id':case['id'],'constructor_returned':True,'initial_math_succeeded':case['initial_math'],
                     'before':save('actual_initial_window_snapshot',before)}
                gold_row=None
                if case['healthy'] and args.phase=='candidate':
                    gold_row=next(value for value in gold['rows'] if value['id']==case['id'])
                    match_gold(before,'Complete healthy initial native math, three texts and raw disks equal Gold',gold_row,'before')
                if args.phase=='candidate' and case['id']=='bad-squad-list-true-false':
                    picture('bad-squad-list-before',1)
                active['phase']='actual-fresh-observation-save'
                observed_value=deepcopy(case['observed']);caller=freeze((observed_value,case['at']))
                prior=freeze(durable());prior_disks=freeze(disks())
                result=window.apply_run_observation(observed_value,case['at']);idle()
                assert result is case['apply_expected']
                assert_native_equal((observed_value,case['at']),caller,'Real fresh observation caller unchanged')
                assert window.run.preserve_unreadable is False and window.run.save_issue is None
                if not result:
                    assert_native_equal(durable(),prior,'Stale observation keeps original raw state')
                    assert_native_equal(disks(),prior_disks,'Stale observation keeps original disk phase')
                member=window.run.state['operators'][OWNER]
                history=window.run.state['history']
                changed=[item for item in history if item.get('kind')=='recruitment_changed']
                corrected=[item for item in history if item.get('kind')=='classification_corrected']
                if case['kind']=='origin':
                    assert member['sources']['public_opaque']==[None,{'nullable':None}]
                    if case['action']=='stale':
                        assert member['sources']['recruitment_kind'] is None and not changed and not corrected
                    elif case['action']=='unused':
                        assert member['sources']['recruitment_kind'] is None and member['recruitment_kind'] is None
                        assert member['char_buff_ids']==[BUFF] and not changed and not corrected
                    else:
                        assert member['recruitment_kind']=='non_emergency' and member['sources']['recruitment_kind']==MARKER
                        if case['action']=='change':
                            assert member['char_buff_ids']==[] and len(changed)==1 and not corrected
                            assert (changed[0]['previous_kind'],changed[0]['kind_now'])==('emergency_hire','non_emergency')
                            assert member['invalid_fields']==sorted(set(account()['fields'])-{'level'})
                            assert member['invalid_skill_ranks']==['1']
                        else:
                            assert member['char_buff_ids']==[BUFF] and not changed
                            assert member['invalid_fields']==[] and member['invalid_skill_ranks']==[]
                            assert len(corrected)==(1 if case['action']=='legacy' else 0)
                            if corrected:assert (corrected[0]['previous_kind'],corrected[0]['kind_now'])==('emergency_hire','non_emergency')
                else:
                    current=window.run.state['config']['squad']
                    if case['action']=='protected':
                        assert_native_equal(current,saved['config']['squad'],'Healthy stronger known squad fact is retained')
                    else:
                        incoming=case['observed']['config']['squad']
                        assert current['id']==incoming['id'] and current['name']==incoming['name']
                        assert current['effect_verified'] is incoming['effect_verified']
                        assert current['captured_at']==case['at']
                unchanged('select actual S3 after observation',lambda:window.skill.setCurrentIndex(window.skill.findData(3)))
                unchanged('recalculate actual saved observation',window.calculate)
                after=snapshot(case['after_math'])
                assert ('squad' in after['view']['reuse']['confirmed']) is case['reuse_after']
                row['apply_result']=result;row['after']=save('actual_observation_window_snapshot',after)
                if gold_row is not None:
                    match_gold(after,'Complete healthy post-observation native math, three texts and raw disks equal Gold',gold_row,'after')
                    row['complete_healthy_initial_and_after_native_and_three_texts_equal']=True
                if args.phase=='candidate':
                    if case['id']=='bad-origin-null':picture('bad-origin-null-after',0)
                    elif case['id']=='bad-squad-list-true-false':picture('bad-squad-list-after',0)
                    elif case['id']=='healthy-trade20-protected':picture('healthy-trade20-after',0)
                active['phase']='actual-close-and-RunState-reload'
                state=freeze(durable());disk=freeze(disks());window.close();application.processEvents()
                assert_native_equal(durable(),state,'Actual close keeps current raw state')
                assert_native_equal(disks(),disk,'Actual close keeps current disk phase')
                restarted=RunState(run_path)
                assert restarted.preserve_unreadable is False and restarted.save_issue is None
                assert_native_equal(restarted.state,window.run.state,'Actual disk reload restores entire current native RunState')
                restarted_reuse=reuse(restarted)
                assert_native_equal(restarted_reuse,after['view']['reuse'],'Actual reload retains confirmed-config eligibility')
                assert_native_equal(disks(),disk,'Actual direct reload does not rewrite accepted disk phase')
                row['restart']=save('actual_close_RunState_reload',{'state':restarted.state,
                                  'reuse':restarted_reuse,'disks':disks(),'observation_caller_before':caller,
                                  'observation_caller_after':(observed_value,case['at'])})
                window.deleteLater();application.processEvents();window=None;rows.append(row)
                print(json.dumps({'completed':len(rows),'case':case['id']}),flush=True)
        assert len(rows)==(HEALTHY_COUNT if args.phase=='gold' else CASE_COUNT) and not errors
        assert len(pngs)==(0 if args.phase=='gold' else 4)
        assert source_map(root)==expected and guard_path.read_bytes()==guard_raw
        for name,want in extra.items():assert sha((root/name).read_bytes())==want
        receipt.update(passed=True,workflow_complete=True)
    except BaseException as error:
        receipt['failure']=error_record(error)
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
        sys.excepthook=old_hook;done.set();receipt['elapsed_seconds']=time.perf_counter()-started
        receipt['source_after']=source_map(root)
        receipt['source_drift']=[name for name in set(expected)|set(receipt['source_after'])
                                 if expected.get(name)!=receipt['source_after'].get(name)]
        receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        if receipt['source_drift'] or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw:
            receipt.update(passed=False,workflow_complete=False)
        if args.phase=='candidate':receipt['actual_gold_receipt_sha256']=sha(gold_raw)
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'windows':len(rows),'native_records':len(records),
                      'elapsed_seconds':receipt['elapsed_seconds']}))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':sys.exit(main())
