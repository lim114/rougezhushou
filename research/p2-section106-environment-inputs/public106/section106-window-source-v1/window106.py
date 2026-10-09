"""Source-only isolated real MainWindow environment/recovery workflow for Root.

Original105 public API observations are evidence, not candidate PASS. Gold must
finish on actual105 Source748; candidate106 must bind its exact real Source749.
No author execution, natural OCR producer claim, or native Windows claim.
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
ORIGINAL_SHA='c09e542f3d1cee720c31daa638663a133bd1894268eb7bb20abc062ccfb92b25'
ORIGINAL_MANIFEST_SHA='2e8f3e9b74a84cb9d4ef7cee49df8bc8510c6b2bc3e09afd74b94d6af32ce217'
TRANSPORT_SHA='028063cf676eee596c07046fd009b18cf48b2bc71ed2665ac12fc477988e9624'
TEST_SHA='6cd75f91e466daa6b231a6e318b44795f596a2b8d292c0fd6939329117521a8e'
OWNER='mechanist'
HEALTHY_COUNT=9
CASE_COUNT=23
MISSING=object()
ZERO={'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0}
ONE={'stage_id':'ro6_n_3_1','enemy_id':'enemy_2001_duckmi','level':1}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def account():
    return {'id':OWNER,'scope':'operator_profile','fields':{'elite':2,'level':90,
            'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':3},
            'skill_ranks':{'1':7,'3':10},'captured_at':1000.0,
            'sources':{},'field_times':{},'skill_times':{}}


def fixture(record):
    member={**account(),'scope':'run','present':True,'recruitment_kind':'non_emergency',
            'char_buff_ids':[],'char_buffs_complete':False,'char_buff_absent_ids':[],
            'char_buff_pending_ids':[],'invalid_fields':[],'invalid_skill_ranks':[],
            'missing_fields':[],'sources':{'public_opaque':[None,{'nullable':None}]}}
    return {'id':'public-environment-window106','started_at':0.0,'last_read':1000.0,
            'operators':{OWNER:member},'crew_count':1,'selected_operator':OWNER,
            'relics':{},'tactical_tools':{},'relic_count':0,'inventory_verified':True,
            'inventory_confirmed_at':1000.0,'bar_signature':[],
            'relic_icon_memory':None,'history':[],'resources':{},
            'config':{'difficulty':deepcopy(record)},'maps':{},
            'last_node_content':None,'node_contents':[],
            'public_opaque':{'signed_zero':-0.0,'nullable':None}}


def case(identity,*,value=2,source='public-normal-control',aliases=None,target=None,
         healthy=False,error=None,source_pending=False):
    record={'value':deepcopy(value),'captured_at':1000.0}
    if source is not MISSING:record['source']=deepcopy(source)
    record.update(deepcopy(aliases or {}))
    return {'id':identity,'healthy':healthy,'error':error,'source_pending':source_pending,
            'saved':fixture(record),'target':deepcopy(target),
            'observed':{'operators':[],'config':{'difficulty':{
                'value':2,'source':'public106-fresh-normal-label'}}},'at':1001.0}


def cases(phase):
    rows=[case('healthy-mode-missing-source-missing',source=MISSING,healthy=True),
          case('healthy-mode-normal',aliases={'mode':'NORMAL'},healthy=True),
          case('healthy-modeDifficulty-zero',value=0,aliases={'modeDifficulty':'NORMAL'},healthy=True),
          case('healthy-both-normal-fifteen',value=15,aliases={'mode':'NORMAL','modeDifficulty':'NORMAL'},healthy=True),
          case('healthy-source-empty',source='',healthy=True),
          case('healthy-source-whitespace',source='  public source  ',healthy=True),
          case('healthy-source-text',source='public-present-source',healthy=True),
          case('healthy-target-zero',target=ZERO,healthy=True),
          case('healthy-target-one',target=ONE,healthy=True)]
    if phase=='candidate':
        rows.extend(case(identity,aliases=aliases,error='mode') for identity,aliases in (
            ('bad-mode-month-team',{'mode':'MONTH_TEAM'}),
            ('bad-modeDifficulty-month-team',{'modeDifficulty':'MONTH_TEAM'}),
            ('bad-mode-conflicting',{'mode':'MONTH_TEAM','modeDifficulty':'NORMAL'}),
            ('bad-mode-null',{'mode':None}),('bad-mode-list',{'mode':['NORMAL']})))
        rows.extend(case(identity,value=value,error='grade') for identity,value in (
            ('bad-grade-bool',True),('bad-grade-float',2.0),
            ('bad-grade-text','2'),('bad-grade-list',[2])))
        rows.extend(case(identity,source=source,source_pending=True) for identity,source in (
            ('bad-source-null',None),('bad-source-list',[]),('bad-source-number',1),
            ('bad-source-map',{}),('bad-source-bool',False)))
    assert len(rows)==(HEALTHY_COUNT if phase=='gold' else CASE_COUNT)
    return rows


def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase','original','original-exit'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--gold');parser.add_argument('--gold-exit')
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;original_dir=Path(args.original).resolve()
    assert args.phase in ('gold','candidate') and not out.exists() and out!=root and root not in out.parents
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    assert Path(args.original_exit).read_text().strip()=='0'
    original_raw=(original_dir/'observations.json').read_bytes();assert sha(original_raw)==ORIGINAL_SHA
    original=json.loads(original_raw)
    assert original['observation_only'] is True and original['product_pass'] is False
    assert original['observation_complete'] is True and original['source_and_CORE_unchanged'] is True
    assert original['cached_cases']==22 and original['direct_cases']==11
    assert original['actual_public_consumer_calls']==284 and original['actual_native_records']==350
    assert len(original['source_before'])==748 and original['source_before']==original['source_after']
    manifest_raw=(artifact/'original-fixture-manifest.json').read_bytes()
    assert sha(manifest_raw)==ORIGINAL_MANIFEST_SHA
    original_manifest=json.loads(manifest_raw)
    transport_raw=(artifact/'exact-local-transports.json').read_bytes();assert sha(transport_raw)==TRANSPORT_SHA
    transport=json.loads(transport_raw);assert len(transport['changes'])==5
    guard_path=Path(args.guard);guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert len(expected)==(748 if args.phase=='gold' else 749) and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    assert extra['CORE_0.70_VERIFICATION.json']==original['CORE_before']==original['CORE_after']
    for change in transport['changes']:
        want=change['before_source_sha256'] if args.phase=='gold' else change['after_source_sha256']
        assert expected[change['path']]==want
    gold=None
    if args.phase=='gold':assert expected==original['source_before']
    else:
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_text().strip()=='0'
        gold_dir=Path(args.gold);gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['phase']=='gold'
        assert gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA
        assert len(gold['rows'])==HEALTHY_COUNT and gold['source_before']==gold['source_after'] and not gold['source_drift']
        original_sources=gold['source_before'];assert original_sources==original['source_before']
        assert set(expected)-set(original_sources)=={'tests/test_environment_input_106.py'}
        assert not set(original_sources)-set(expected)
        changed={name for name in original_sources if expected[name]!=original_sources[name]}
        assert changed=={change['path'] for change in transport['changes']}|{'scripts/verify_cloud.py'}
        assert expected['tests/test_environment_input_106.py']==TEST_SHA
        assert gold['source_additional_before']==gold['source_additional_after']==extra
        assert gold['Qt_errors']==[] and gold['native_windows_verified'] is False
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];errors=[];calls=[];direct=[];active={'case':'preimport','phase':'preimport'}
    done=threading.Event();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_106_REAL_MAINWINDOW','phase':args.phase,'passed':False,
             'workflow_complete':False,'source_before':expected,'source_guard_sha256':sha(guard_raw),
             'source_additional_before':extra,'runner_sha256':sha(Path(__file__).read_bytes()),
             'original_receipt_sha256':ORIGINAL_SHA,
             'original_raw_exit_sha256':sha(Path(args.original_exit).read_bytes()),
             'rows':rows,'records':records,'pngs':pngs,
             'Qt_errors':errors,'direct_API':direct,'deadline_seconds':450,
             'native_windows_verified':False,'private_state_access':False,
             'game_chat_sampling_executed':False,'natural_OCR_producer_verified':False,
             'restart_scope':'Direct RunState reload after actual observation/close; no second MainWindow',
             'disk_scope':'Actual run/account JSON and their .tmp; isolated settings are allowed UI saves'}
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
        from rouge.battle_preview import enemy_preview
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
                assert_native_equal({'args':positional,'kwargs':keywords},before,'Actual numeric error caller unchanged')
                details=error_record(error)
                calls.append({'case':active['case'],'error':details,'caller':before})
                save('actual_calculate_exception',{'before':before,
                     'after':freeze({'args':positional,'kwargs':keywords}),'error':details})
                raise
            assert_native_equal({'args':positional,'kwargs':keywords},before,'Actual numeric caller unchanged')
            calls.append({'case':active['case'],'error':None,'caller':before})
            save('actual_calculate_result',{'before':before,
                 'after':freeze({'args':positional,'kwargs':keywords}),'result':value})
            return value
        module.calculate_damage=observed
        # Public direct APIs cover bool identities that real Qt selectors never emit.
        # Historical floats are compared against their own complete original record.
        for item in original_manifest['direct_cases']:
            identity=item['id'];active.update(case=identity,phase='direct-actual-public-API')
            caller={**original_manifest['base_calculation'],'target_enemy':deepcopy(item['target']),
                    'run_config':{'difficulty':{'value':2,'source':'public-normal-control'}}}
            old_call=next(row for row in original['calls'] if row['case']==identity and row['phase']=='direct_calculate_damage')
            old_value=read_record(original_dir/'native',old_call['native'])
            assert_native_equal(((caller,),None,None),old_value['before'],'Direct original full caller identity')
            result=None;problem=None
            try:result=observed(caller)
            except Exception as error:problem=error_record(error)
            expected_boolean=identity in ('enemy-level-zero-bool','enemy-level-one-bool') and args.phase=='candidate'
            if expected_boolean:
                assert problem and problem['type']=='ValueError' and problem['message']=='目标敌人身份/等级必须与关卡引用唯一匹配。'
                assert old_call['returned'] is True and old_value['error'] is None
            elif old_call['returned']:
                assert problem is None
                assert_native_equal(result,old_value['result'],'Complete direct same-input original result, including old float types')
            else:
                assert problem and problem['type']==old_call['error']['type'] and problem['message']==old_call['error']['message']
            target=item['target'];preview=None;preview_error=None
            if type(target) is dict and target:
                args_preview=(target['stage_id'],target['enemy_id'],target['level'],caller['run_config'])
                preview_before=freeze(args_preview)
                try:preview=enemy_preview(*args_preview)
                except Exception as error:preview_error=error_record(error)
                assert_native_equal(args_preview,preview_before,'Original preview caller unchanged')
                old_preview=next(row for row in original['calls'] if row['case']==identity and row['phase']=='direct_enemy_preview')
                old_preview_value=read_record(original_dir/'native',old_preview['native'])
                assert_native_equal((args_preview,None,None),old_preview_value['before'],'Actual preview full original caller')
                if old_preview['returned']:
                    assert preview_error is None
                    assert_native_equal(preview,old_preview_value['result'],'Complete original normal integer preview')
                else:
                    assert preview_error and preview_error['type']==old_preview['error']['type'] and preview_error['message']==old_preview['error']['message']
            direct.append({'id':identity,'numeric_returned':problem is None,'numeric_error':problem,
                           'record':save('actual_direct_API_contract',{'caller':caller,'result':result,'error':problem,
                                        'preview':preview,'preview_error':preview_error}),
                           'old_complete_result_equal':not expected_boolean and old_call['returned']})
        for case_value in cases(args.phase):
            active.update(case=case_value['id'],phase='constructor')
            with tempfile.TemporaryDirectory(prefix='public106-',dir=out/'public-state') as directory:
                folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
                saved=deepcopy(case_value['saved'])
                raw=(json.dumps(saved,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_raw=(json.dumps({OWNER:account()},ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                run_path.write_bytes(raw);account_path.write_bytes(account_raw)
                sentinel=b'public106-unmodified-original-temporary\n';run_path.with_suffix('.tmp').write_bytes(sentinel)
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
                    assert_native_equal(disks(),disk,label+' current original disk phase')
                def reuse(run):
                    before=freeze(run.state);disk=freeze(disks())
                    context=run.recognition_context();caller=freeze(context);result=confirmed_config(context)
                    assert_native_equal(context,caller,'Actual confirmed_config caller unchanged')
                    assert_native_equal(run.state,before,'Actual recognition/reuse keeps raw state')
                    assert_native_equal(disks(),disk,'Actual recognition/reuse keeps disks')
                    return {'context':context,'confirmed':result}
                def snapshot(math_expected,error_kind=None):
                    before=freeze(durable());disk=freeze(disks());result=window.damage_result
                    last=next(value for value in reversed(calls) if value['case']==case_value['id'])
                    assert last['caller']['args'][0]['operator']==OWNER and last['caller']['args'][0]['skill']==3
                    assert_native_equal(last['caller']['args'][0]['run_config'],window.run.state['config'],
                                        'Original raw environment still reaches actual numeric API')
                    if math_expected:
                        assert result is not None and last['error'] is None
                        assert result['scenario']['operator']==OWNER and result['scenario']['skill']==3
                        native=freeze(result)
                        texts={'estimate':estimate.format_estimate(result['result']),
                               'default':reporting.format_report(result['result']),
                               'technical':reporting.format_report(result['result'],technical=True)}
                        assert texts['estimate']==texts['default']
                        assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                        assert_native_equal(result,native,'All three original formatter callers unchanged')
                    else:
                        assert result is None and last['error']['type']=='ValueError'
                        expected_error=('当前保密等级数值计算仅支持NORMAL模式，其他模式不能套用常规难度修正。'
                                        if error_kind=='mode' else '本局保密等级需要0–15的整数。')
                        assert last['error']['message']==expected_error and window.damage_text.toPlainText()==expected_error
                        texts={'pending':window.damage_text.toPlainText()}
                    value={'view':{'damage_result':result,'three_texts':texts,'summary':window.run.summary(),
                                   'inventory':window.run.inventory_status(),'reuse':reuse(window.run),
                                   'displayed_damage':window.damage_text.toPlainText(),
                                   'difficulty_UI':{'enabled':window.difficulty.isEnabled(),
                                                    'tooltip':window.difficulty.toolTip(),
                                                    'preset':window.difficulty.currentData()}},
                           'durable':freeze(durable()),'disks':freeze(disks())}
                    assert_native_equal(durable(),before,'Actual math/format/view keeps raw state')
                    assert_native_equal(disks(),disk,'Actual math/format/view keeps disks')
                    return value
                def picture(name,tab):
                    unchanged('show actual screenshot tab',lambda:window.centralWidget().setCurrentIndex(tab))
                    path=out/(name+'.png');assert window.grab().save(str(path),'PNG')
                    pngs.append({'case':case_value['id'],'phase':active['phase'],'tab_index':tab,
                                 'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
                def match_gold(value,label,gold_row,key):
                    original_record=read_record(gold_dir/'records',gold_row[key])
                    assert original_record['case']==case_value['id']
                    assert original_record['kind']==('actual_initial_window_snapshot' if key=='before' else 'actual_observation_window_snapshot')
                    assert original_record['phase']==('initial-actual-view' if key=='before' else 'actual-fresh-observation-save')
                    original_view={name:original_record[name] for name in ('view','durable','disks')}
                    assert_native_equal(value,original_view,label)
                idle()
                assert disks()=={'run':{'exists':True,'bytes':raw},'account':{'exists':True,'bytes':account_raw},
                                 'run_tmp':{'exists':True,'bytes':sentinel},'account_tmp':{'exists':False,'bytes':None}}
                assert window.run.preserve_unreadable is False and window.run.save_issue is None
                assert window.run.state['id']==saved['id']
                assert_native_equal(window.run.state['config'],saved['config'],'Accepted raw environment metadata retained')
                active['phase']='initial-actual-view'
                unchanged('select actual mechanist',lambda:window.operator_choices.select_value(OWNER))
                index=window.skill.findData(3);assert index>=0
                unchanged('select actual S3',lambda:window.skill.setCurrentIndex(index))
                if case_value['target']:
                    target=case_value['target']
                    unchanged('select actual known stage',lambda:window.target_stage_choices.select_value(target['stage_id']))
                    unchanged('select actual known integer enemy',lambda:window.target_enemy_choices.select_value(target))
                    selected=window.target_enemy.currentData()
                    assert type(selected) is dict and set(selected)==set(target)
                    assert all(type(selected[key]) is type(value) and selected[key]==value for key,value in target.items())
                    # Qt may choose its own mapping order. The actual emitted
                    # caller/native graph is saved and matched against real Gold.
                unchanged('actual calculate method',window.calculate)
                initial_ok=case_value['error'] is None
                before=snapshot(initial_ok,case_value['error'])
                ui=before['view']['difficulty_UI'];confirmed=before['view']['reuse']['confirmed']
                if initial_ok:
                    assert ui['enabled'] is False and ui['preset']==saved['config']['difficulty']['value']
                    assert ui['tooltip']=='自动读取本局保密等级；切换页面后保留最近确认值。'
                    assert 'difficulty' in confirmed
                    if case_value['source_pending']:
                        raw_result=before['view']['damage_result']['result']
                        assert_native_equal(raw_result['run_resolution']['difficulty']['source'],saved['config']['difficulty']['source'],
                                            'Unknown source is retained in original numeric provenance')
                        note=next(section for section in raw_result['report']['sections'] if section['id']=='run_environment')['notes'][0]
                        assert note=='本局保密等级：2；来源：未确认（来源字段不是文本）'
                else:
                    assert ui['enabled'] is True and '尚未满足当前常规模式资格' in ui['tooltip']
                    assert '保密等级未确认' in before['view']['summary'] and 'difficulty' not in confirmed
                    # A real enabled preset change is only analysis UI; it cannot
                    # replace unknown raw current-run input or suppress its error.
                    preset=window.difficulty.findData(15);assert preset>=0
                    unchanged('choose analysis preset without writing run',lambda:window.difficulty.setCurrentIndex(preset))
                    unchanged('actual calculate retains raw config after preset change',window.calculate)
                    manual=snapshot(False,case_value['error'])
                    assert manual['view']['difficulty_UI']['preset']==15
                    save('actual_unconfirmed_manual_preset_snapshot',manual)
                row={'id':case_value['id'],'constructor_returned':True,'initial_math_succeeded':initial_ok,
                     'before':save('actual_initial_window_snapshot',before)}
                gold_row=None
                if case_value['healthy'] and args.phase=='candidate':
                    gold_row=next(value for value in gold['rows'] if value['id']==case_value['id'])
                    match_gold(before,'Complete healthy initial native math, three texts, UI and raw disks equal Gold',gold_row,'before')
                if args.phase=='candidate':
                    if case_value['id']=='healthy-mode-normal':picture('healthy-normal-environment',0)
                    elif case_value['id']=='bad-mode-month-team':picture('mode-unconfirmed-original-retained',0)
                    elif case_value['id']=='bad-source-null':picture('source-unconfirmed-calculate-retained',1)
                active['phase']='actual-fresh-observation-save'
                observed_value=deepcopy(case_value['observed']);caller=freeze((observed_value,case_value['at']))
                assert window.apply_run_observation(observed_value,case_value['at']) is True;idle()
                assert_native_equal((observed_value,case_value['at']),caller,'Real fresh observation caller unchanged')
                assert window.run.preserve_unreadable is False and window.run.save_issue is None
                assert window.run.state['config']['difficulty']=={'value':2,'source':'public106-fresh-normal-label','captured_at':case_value['at']}
                assert_native_equal(window.run.state['operators'],saved['operators'],'Legal environment recovery retains public operator records')
                assert window.run.state['public_opaque']==saved['public_opaque']
                index=window.skill.findData(3);assert index>=0
                unchanged('select actual S3 after observation',lambda:window.skill.setCurrentIndex(index))
                unchanged('actual calculate after legal recovery',window.calculate)
                after=snapshot(True)
                assert 'difficulty' in after['view']['reuse']['confirmed']
                assert after['view']['difficulty_UI']=={'enabled':False,
                       'tooltip':'自动读取本局保密等级；切换页面后保留最近确认值。','preset':2}
                row['apply_result']=True;row['after']=save('actual_observation_window_snapshot',after)
                if gold_row is not None:
                    match_gold(after,'Complete healthy post-observation native math, three texts, UI and raw disks equal Gold',gold_row,'after')
                    row['complete_healthy_initial_and_after_native_and_three_texts_equal']=True
                if args.phase=='candidate' and case_value['id']=='bad-mode-month-team':picture('legal-new-normal-observation-recovered',1)
                active['phase']='actual-close-and-RunState-reload'
                state=freeze(durable());disk=freeze(disks());window.close();application.processEvents()
                assert_native_equal(durable(),state,'Actual close keeps current raw state')
                assert_native_equal(disks(),disk,'Actual close keeps current disk phase')
                persisted_json=json.loads(run_path.read_text(encoding='utf-8'))
                restarted=RunState(run_path)
                assert restarted.preserve_unreadable is False and restarted.save_issue is None
                assert_native_equal(restarted.state,persisted_json,'Actual reload restores entire actual persisted JSON native graph')
                restarted_reuse=reuse(restarted)
                assert_native_equal(restarted_reuse,after['view']['reuse'],'Actual reload retains complete confirmed environment view')
                assert_native_equal(disks(),disk,'Actual reload does not rewrite accepted saved disk phase')
                row['restart']=save('actual_close_RunState_reload',{'state':restarted.state,
                                   'live_state_before_close':state['run'],'persisted_json':persisted_json,
                                   'restart_oracle':'Actual saved JSON graph; no live-alias preservation claim',
                                   'reuse':restarted_reuse,'disks':disks(),'observation_caller_before':caller,
                                   'observation_caller_after':(observed_value,case_value['at'])})
                window.deleteLater();application.processEvents();window=None;rows.append(row)
                print(json.dumps({'completed':len(rows),'case':case_value['id']}),flush=True)
        assert len(rows)==(HEALTHY_COUNT if args.phase=='gold' else CASE_COUNT) and not errors
        assert len(direct)==11 and len(pngs)==(0 if args.phase=='gold' else 4)
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
