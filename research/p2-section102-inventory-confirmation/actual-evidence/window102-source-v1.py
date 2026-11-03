"""Root-authored isolated real102 Qt Gold/candidate evidence; not yet run."""
import argparse
from copy import deepcopy
import datetime
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

RELICS=('rogue_6_relic_cargo_1','rogue_6_relic_fight_26')
TOOL='rogue_6_active_tool_5'
SNACK='rogue_6_from_relic_13'
HISTORY_BASE='rogue_6_relic_legacy_24'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def account():
    return {'id':'mechanist','scope':'operator_profile','fields':{'elite':2,'level':80,
            'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':3},
            'skill_ranks':{'1':7,'3':10},'captured_at':1000.0,'sources':{},'field_times':{},'skill_times':{}}


def fixture(flag,count=0,held=False):
    member={**account(),'scope':'run','present':True,'recruitment_kind':'non_emergency',
            'char_buff_ids':[SNACK],'char_buffs_complete':False,'char_buff_absent_ids':[],
            'char_buff_pending_ids':[],'invalid_fields':[],'invalid_skill_ranks':[],'missing_fields':[]}
    return {'id':'public-inventory-window102','started_at':0.0,'last_read':1000.0,
            'operators':{'mechanist':member},'crew_count':1,'selected_operator':'mechanist',
            'relics':{rid:{'held':True,'source':'held_bar','captured_at':1000.0} for rid in RELICS} if held else {},
            'tactical_tools':{TOOL:{'held':True,'source':'held_bar','captured_at':1000.0}} if held else {},
            'relic_count':count,'inventory_verified':deepcopy(flag),'inventory_confirmed_at':None,
            'bar_signature':[],'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
            'last_node_content':None,'node_contents':[],'public_opaque':{'signed_zero':-0.0,'nullable':None}}


def cases(phase):
    rows=[('healthy-true',True,0,False),('healthy-false',False,0,False),
          ('healthy-count-float-zero',True,0.0,False),('healthy-count-float-negative-zero',True,-0.0,False),
          ('healthy-count-float-tools',True,3.0,True),('healthy-null-flag',None,0,False)]
    result=[{'id':key,'fixture':fixture(flag,count,held),'healthy':True} for key,flag,count,held in rows]
    if phase=='candidate':
        result.extend({'id':key,'fixture':fixture(flag,count,held),'healthy':False,'action':action}
                      for key,flag,count,held,action in (
                          ('bad-text', 'false',0,False,None),('bad-list',[1],3,True,None),
                          ('bad-dict',{'confirmed':True},0,False,None),
                          ('partial-no-history','false',3,True,'partial'),
                          ('current-full','false',0,False,'full'),('current-zero',[1],3,True,'zero'),
                          ('valid-history-replay','false',1,False,'history'),
                          ('history-invalidated-count',[1],1,False,'invalidated')))
    return result


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--gold')
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    assert args.phase in ('gold','candidate') and not out.exists() and root not in out.parents
    helper=Path(__file__).with_name('native_evidence.py')
    assert sha(helper.read_bytes())=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
    guard_raw=Path(args.guard).read_bytes();guard=json.loads(guard_raw);expected=guard['source_sha256']
    assert len(expected)==(745 if args.phase=='gold' else 746) and source_map(root)==expected
    extra=guard['source_additional_sha256']
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    gold=None
    if args.phase=='candidate':
        assert args.gold
        gold_dir=Path(args.gold);gold=json.loads((gold_dir/'receipt.json').read_bytes())
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['phase']=='gold'
        assert len(gold['rows'])==6
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];errors=[];active={'case':'preimport'};done=threading.Event();start=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_102_REAL_MAINWINDOW','phase':args.phase,'passed':False,
             'workflow_complete':False,'source_before':expected,'source_guard_sha256':sha(guard_raw),
             'runner_sha256':sha(Path(__file__).read_bytes()),'rows':rows,'records':records,'pngs':pngs,
             'Qt_errors':errors,'deadline_seconds':450,'native_windows_verified':False,
             'private_state_access':False,'game_chat_sampling_executed':False}
    def save(kind,value):
        row=write_record(out/'records',len(records)+1,{'kind':kind,'case':active['case'],**value})
        row.update(kind=kind,case=active['case']);records.append(row);return row
    def deadline():
        if not done.wait(450):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline':450}))
            os._exit(124)
    threading.Thread(target=deadline,daemon=True).start()
    old_hook=sys.excepthook;window=None;application=None;module=None;backend=None;calculator=None
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.path.insert(0,str(root))
        from PySide6 import __version__
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.run_state import RunState
        assert __version__==qVersion()=='6.9.3'
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            value=calculator(*positional,**keywords)
            assert_native_equal({'args':positional,'kwargs':keywords},before,'Original API caller unchanged')
            save('actual_calculate_result',{'before':before,'after':freeze({'args':positional,'kwargs':keywords}),'result':value})
            return value
        module.calculate_damage=observed
        for case in cases(args.phase):
            active['case']=case['id']
            with tempfile.TemporaryDirectory(prefix='public102-',dir=out/'public-state') as directory:
                folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
                saved=deepcopy(case['fixture']);action=case.get('action')
                if action in ('history','invalidated'):
                    run_path.write_text(json.dumps(saved,ensure_ascii=False))
                    seed=RunState(run_path)
                    icon={'id':HISTORY_BASE,'candidates':[HISTORY_BASE,HISTORY_BASE+'_a',HISTORY_BASE+'_b',HISTORY_BASE+'_c'],
                          'confirmed':False,'score':.97,'center':[.2,.9]}
                    assert seed.apply({'relics':{'icons':[icon],'ids':[],'count':1,'source':'held_bar'}},1001.0) is True
                    if action=='invalidated':
                        assert seed.apply({'relics':{'icons':[],'ids':[],'count':2,'source':'held_bar'}},1002.0) is True
                    saved=deepcopy(seed.state);saved['inventory_verified']=deepcopy(case['fixture']['inventory_verified'])
                raw=(json.dumps(saved,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_raw=(json.dumps({'mechanist':account()},ensure_ascii=False,indent=2)+'\n').encode()
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
                def disks():return {'run':run_path.read_bytes(),'account':account_path.read_bytes(),
                                    'run_tmp':run_path.with_suffix('.tmp').exists(),'account_tmp':account_path.with_suffix('.tmp').exists()}
                def unchanged(label,callback):
                    before=freeze(durable());disk=freeze(disks());callback();idle()
                    assert_native_equal(durable(),before,label+' state');assert_native_equal(disks(),disk,label+' disks')
                def snapshot():
                    before=freeze(durable());disk=freeze(disks());result=window.damage_result
                    assert result is not None
                    native=freeze(result)
                    texts={'estimate':estimate.format_estimate(result['result']),
                           'default':reporting.format_report(result['result']),
                           'technical':reporting.format_report(result['result'],technical=True)}
                    assert texts['estimate']==texts['default']
                    assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                    assert_native_equal(result,native,'All three original formatter callers unchanged')
                    view={'damage_result':result,'three_texts':texts,'summary':window.run.summary(),
                          'inventory':window.run.inventory_status(),'held':window.run.held_relic_ids(),
                          'tools':window.run.held_tool_ids()}
                    assert_native_equal(durable(),before,'Views keep raw state');assert_native_equal(disks(),disk,'Views keep disks')
                    return {'view':view,'durable':freeze(durable()),'disks':freeze(disks())}
                idle()
                assert disks()=={'run':raw,'account':account_raw,'run_tmp':False,'account_tmp':False}
                unchanged('select actual mechanist',lambda:window.operator_choices.select_value('mechanist'))
                index=window.skill.findData(3);assert index>=0
                unchanged('select actual S3',lambda:window.skill.setCurrentIndex(index))
                unchanged('actual calculate button method',window.calculate)
                value=snapshot();row={'id':case['id'],'constructor_returned':True,'snapshot':save('actual_window_snapshot',value)}
                if case['healthy'] and args.phase=='candidate':
                    gold_row=next(v for v in gold['rows'] if v['id']==case['id'])
                    original=read_record(gold_dir/'records',gold_row['snapshot'])
                    assert_native_equal(value,original,'Complete healthy native value, three texts, caller/raw disks equal Gold')
                    row['complete_healthy_Gold_native_and_three_texts_equal']=True
                if not case['healthy']:
                    assert value['view']['inventory']['complete'] is False
                    assert '持有清单已核对（本局记录）' not in value['view']['summary']
                    assert_native_equal(window.run.state['inventory_verified'],saved['inventory_verified'],'Malformed raw flag is not washed')
                if action:
                    if action=='partial':observed_value={'operators':[]}
                    elif action=='zero':observed_value={'relics':{'ids':[],'icons':[],'count':0,'source':'held_bar'}}
                    elif action=='full':observed_value={'relics':{'ids':list(RELICS),'icons':[{'id':rid,'candidates':[rid],'confirmed':True} for rid in (*RELICS,TOOL)],'count':3,'source':'held_bar'},'tactical_tools':{'ids':[TOOL],'source':'held_bar'}}
                    else:observed_value={'config':{'difficulty':{'value':10,'source':'本局等级标签'}}}
                    caller=freeze(observed_value);at=window.run.state['last_read']+1
                    assert window.apply_run_observation(observed_value,at) is True;idle()
                    assert_native_equal(observed_value,caller,'Real fresh observation caller unchanged')
                    if action in ('full','zero','history'):
                        assert window.run.state['inventory_verified'] is True and window.run.inventory_status()['complete'] is True
                    else:assert window.run.inventory_status()['complete'] is False
                    if action=='partial':assert_native_equal(window.run.state['inventory_verified'],saved['inventory_verified'],'No historical proof does not upgrade')
                    if action=='history':assert window.run.held_relic_ids()==[HISTORY_BASE+'_c']
                    if action=='full':assert window.run.held_tool_ids()==[TOOL] and window.run.inventory_status()['expected_count']==2
                    if action=='zero':assert not window.run.held_relic_ids() and not window.run.held_tool_ids()
                    phase=freeze(disks());restarted=RunState(run_path)
                    assert_native_equal(restarted.state['inventory_verified'],window.run.state['inventory_verified'],'Actual restart flag exact')
                    assert_native_equal(restarted.inventory_status(),window.run.inventory_status(),'Actual restart status exact')
                    assert_native_equal(disks(),phase,'Restart does not rewrite accepted phase')
                    row['after_observation']=save('actual_authorized_observation_save_restart',snapshot())
                if args.phase=='candidate' and case['id'] in ('bad-text','bad-list','current-full','valid-history-replay'):
                    unchanged('show actual summary',lambda:window.centralWidget().setCurrentIndex(0))
                    image_path=out/(case['id']+'.png');assert window.grab().save(str(image_path),'PNG')
                    pngs.append({'file':image_path.name,'bytes':image_path.stat().st_size,'sha256':sha(image_path.read_bytes())})
                state=freeze(durable());disk=freeze(disks());window.close();application.processEvents()
                assert_native_equal(durable(),state,'Actual close state');assert_native_equal(disks(),disk,'Actual close disk phase')
                window.deleteLater();application.processEvents();window=None;rows.append(row)
                print(json.dumps({'completed':len(rows),'case':case['id']}),flush=True)
        assert len(rows)==(6 if args.phase=='gold' else 14) and not errors
        assert len(pngs)==(0 if args.phase=='gold' else 4)
        assert source_map(root)==expected
        for name,want in extra.items():assert sha((root/name).read_bytes())==want
        receipt.update(passed=True,workflow_complete=True)
    except BaseException as error:
        receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
        sys.excepthook=old_hook;done.set();receipt['elapsed_seconds']=time.perf_counter()-start
        receipt['source_after']=source_map(root);receipt['source_drift']=[k for k in set(expected)|set(receipt['source_after']) if expected.get(k)!=receipt['source_after'].get(k)]
        if receipt['source_drift']:receipt.update(passed=False,workflow_complete=False)
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'windows':len(rows),'native_records':len(records),'elapsed_seconds':receipt['elapsed_seconds']}))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':sys.exit(main())
