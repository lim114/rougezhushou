"""Root-only isolated real MainWindow weight-consumer workflow.

Source prepared only. Gold749 and candidate750 are separate real executions;
changed talent branches are tested against healthy real manual Gold, not the
old defective fixed-identity result. No gameplay displacement/floor is inferred.
"""
import argparse
import ast
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
ORIGINAL_SHA='0a38276dda0ee3e6640f203cc61397686b6e83c365656578b6896dc461563d00'
TRANSPORT_SHA='6066dce8003d68a58ad71fc4210a9beb9495225b05b392f2d9ae57eeb9624522'
TEST_SHA='62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
FACT_SHA='c65213bc16625fed8f404e8cd1024d09c0b3e89d3c16443579a0b0f529f2090b'
BATTLE_PREVIEW_SHA='f0155647af8766eb2f01e84295f85b7300264fc49b40ffc82e89800837d274f3'
OP='char_1015_aglna2'
GRAVITY='rogue_6_relic_legacy_56'
TALENT='飘浮大地之上'
SELECTOR='tests.test_aglna_gravity_weight_107'
COUNT=13
DEADLINE=450


def sha(raw):return hashlib.sha256(raw).hexdigest()


def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}


def profile(owner,elite,potential,skill):
    return {'id':owner,'scope':'operator_profile','fields':{'elite':elite,
            'level':(50,80,90)[elite],'trust':100,'potential':potential,
            'module_id':None,'module_level':0,'selected_skill':skill},
            'skill_ranks':{str(i):(1,7,10)[elite] for i in range(1,elite+2)},
            'captured_at':1000.0,'sources':{},'field_times':{},'skill_times':{}}


def fixture(item):
    owner=item['owner'];member=profile(owner,item['elite'],item['potential'],item['skill'])
    member.update(scope='run',present=True,recruitment_kind='non_emergency',
                  char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],
                  char_buff_pending_ids=[],invalid_fields=[],invalid_skill_ranks=[],
                  missing_fields=[],sources={'public_opaque':[None,{'nullable':None}]})
    return {'id':'public-weight-window107','started_at':0.0,'last_read':1000.0,
            'operators':{owner:member},'crew_count':1,'selected_operator':owner,
            'relics':{},'tactical_tools':{},'relic_count':0,'inventory_verified':True,
            'inventory_confirmed_at':1000.0,'bar_signature':[],
            'relic_icon_memory':None,'history':[],'resources':{},
            'config':{'difficulty':{'value':4,'modeDifficulty':'NORMAL','mode':'NORMAL',
                                  'captured_at':1000.0,'source':'public107-fixed-normal-control'},
                      'zone':{'id':'zone_1','captured_at':1000.0,
                              'source':'public107-main-region-control'}},
            'maps':{},'last_node_content':None,'node_contents':[],
            'public_opaque':{'signed_zero':-0.0,'nullable':None}}


def cases(facts):
    fixed=facts['healthy_unique_fixed_weight0_to5']
    def one(identity,weight,skill=1,elite=2,potential=1,owner=OP):
        record=fixed[str(weight)] if weight is not None else None
        return {'id':identity,'owner':owner,'elite':elite,'potential':potential,
                'skill':skill,'target':None if record is None else {
                    'stage_id':record['stage_id'],'enemy_id':record['enemy_id'],'level':record['level']},
                'reference':None if record is None else deepcopy(record['reference_stats']),
                'weight':weight,'crossing':owner==OP and elite>0 and weight in (4,5),
                'window':30.0 if owner=='mechanist' else 10.0}
    rows=[one('fixed'+str(weight)+'-S'+str(skill),weight,skill)
          for weight in (4,5) for skill in (1,2,3)]
    rows += [one('fixed0-signed-boundary',0),one('fixed1-signed-boundary',1),
             one('fixed4-E0-talent-locked',4,elite=0),
             one('fixed4-E1-talent-selected',4,elite=1),
             one('fixed4-E2-potential3',4,potential=3),
             one('fixed4-mechanist-nonzero',4,owner='mechanist'),
             one('manual-no-target',None)]
    assert len(rows)==COUNT and sum(item['crossing'] for item in rows)==8
    return rows


def talent(result):
    return next(value for value in result['components'] if value['name']==TALENT)


def registry_change(before_raw,after_raw,name,prepend):
    before=ast.parse(before_raw.decode('utf-8'));after=ast.parse(after_raw.decode('utf-8'))
    def assignment(tree):
        rows=[node for node in tree.body if isinstance(node,ast.Assign)
              and any(isinstance(target,ast.Name) and target.id==name for target in node.targets)]
        assert len(rows)==1;return rows[0]
    old=assignment(before);new=assignment(after)
    old_value=ast.literal_eval(old.value);new_value=ast.literal_eval(new.value)
    assert type(old_value) is type(new_value) and type(old_value) in (list,tuple)
    added=type(old_value)([SELECTOR])
    assert new_value==(added+old_value if prepend else old_value+added)
    new.value=deepcopy(old.value)
    assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)


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
    assert original['planned_calculation_cases']==14 and original['actual_explicit_consumer_calls']==74
    assert original['actual_explicit_public_loader_calls']==1 and original['actual_native_records']==89
    assert original['source_before']==original['source_after'] and len(original['source_before'])==748
    assert original['consumer_error_count']==original['blocked_phase_count']==0
    facts_raw=(artifact/'fixture-facts.json').read_bytes();assert sha(facts_raw)==FACT_SHA
    facts=json.loads(facts_raw)
    transport_raw=(artifact/'exact-local-transports.json').read_bytes();assert sha(transport_raw)==TRANSPORT_SHA
    transport=json.loads(transport_raw);assert len(transport['changes'])==1
    change=transport['changes'][0];assert change['path']=='rouge/operator_engine.py'
    guard_path=Path(args.guard);guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert len(expected)==(749 if args.phase=='gold' else 750) and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    assert extra['CORE_0.70_VERIFICATION.json']==original['CORE_before']==original['CORE_after']
    assert expected[change['path']]==change['sha256_before' if args.phase=='gold' else 'sha256_after_source_composition']
    assert expected['rouge/data/previews.json']==facts['preview_source']['sha256']
    assert expected['rouge/data/battle-previews.json']==BATTLE_PREVIEW_SHA
    assert expected['rouge/data/catalog.json']==next(row['sha256'] for row in facts['source_refs']
                                                  if row['path'].endswith('/rouge/data/catalog.json'))
    gold=None;gold_dir=None
    if args.phase=='candidate':
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_text().strip()=='0'
        gold_dir=Path(args.gold);gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['phase']=='gold'
        assert gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA
        assert len(gold['rows'])==COUNT and len(gold['source_before'])==749
        assert gold['source_before']==gold['source_after'] and not gold['source_drift']
        assert gold['source_additional_before']==gold['source_additional_after']==extra
        assert gold['Qt_errors']==[] and gold['native_windows_verified'] is False
        assert set(expected)-set(gold['source_before'])=={'tests/test_aglna_gravity_weight_107.py'}
        assert not set(gold['source_before'])-set(expected)
        changed={name for name in gold['source_before'] if expected[name]!=gold['source_before'][name]}
        assert changed=={'rouge/operator_engine.py','scripts/verify_cloud.py'}
        assert expected['tests/test_aglna_gravity_weight_107.py']==TEST_SHA
        for path,name,prepend in (('scripts/verify_cloud.py','MODULES',True),):
            registry_change((gold_dir/'public-Source'/Path(path).name).read_bytes(),(root/path).read_bytes(),name,prepend)
        assert (gold_dir/'public-Source'/'verify_full_available.py').read_bytes()==(root/'scripts/verify_full_available.py').read_bytes()
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir();(out/'public-Source').mkdir()
    for path in ('scripts/verify_cloud.py','scripts/verify_full_available.py'):
        (out/'public-Source'/Path(path).name).write_bytes((root/path).read_bytes())
    rows=[];records=[];pngs=[];errors=[];calls=[];plan_calls=[]
    active={'case':'bootstrap','phase':'bootstrap','capture_plan':False};done=threading.Event();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_107_REAL_MAINWINDOW','phase':args.phase,'passed':False,
             'workflow_complete':False,'source_before':expected,'source_guard_sha256':sha(guard_raw),
             'source_additional_before':extra,'runner_sha256':sha(Path(__file__).read_bytes()),
             'original_receipt_sha256':ORIGINAL_SHA,
             'original_raw_exit_sha256':sha(Path(args.original_exit).read_bytes()),
             'fixture_facts_sha256':FACT_SHA,'transport_sha256':TRANSPORT_SHA,
             'rows':rows,'records':records,'pngs':pngs,'Qt_errors':errors,
             'deadline_seconds':DEADLINE,'native_windows_verified':False,'private_state_access':False,
             'game_chat_sampling_executed':False,'natural_OCR_producer_verified':False,
             'changed_branch_oracle':'Original real manual-light UI Gold components/estimate skill; old defective fixed Gold is not an equality oracle',
             'normal_scope':'Actual Combat.plan(normal=True) invocation within real MainWindow calculate, not skill0 or separately synthesized phase',
             'restart_scope':'Actual observation save/close/direct RunState JSON reload; no second MainWindow',
             'disk_scope':'Actual run/account JSON and their .tmp; isolated UI settings saves permitted',
             'negative_scope':'Existing signed report metadata and already-light damage only; no gameplay floor/clamp/displacement inference'}
    def save(kind,value):
        row=write_record(out/'records',len(records)+1,{'kind':kind,'case':active['case'],
                                                    'phase':active['phase'],**value})
        row.update(kind=kind,case=active['case'],phase=active['phase']);records.append(row);return row
    def deadline():
        if not done.wait(DEADLINE):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline':DEADLINE}))
            os._exit(124)
    threading.Thread(target=deadline,daemon=True).start()
    old_hook=sys.excepthook;window=None;module=None;backend=None;calculator=None;Combat=None;real_plan=None
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'phase':active['phase'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.path.insert(0,str(root))
        from PySide6 import __version__
        from PySide6.QtCore import qVersion,Qt
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.catalog import stage_previews
        from rouge.operator_engine import Combat
        from rouge.run_state import RunState
        assert __version__==qVersion()=='6.9.3'
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage;real_plan=Combat.plan
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                after=freeze({'args':positional,'kwargs':keywords});details=error_record(error)
                reference=save('actual_calculate_exception',{'before':before,'after':after,'error':details})
                calls.append({'case':active['case'],'phase':active['phase'],'caller':before,'error':details,'native':reference})
                assert_native_equal(after,before,'Actual error numeric caller unchanged');raise
            after=freeze({'args':positional,'kwargs':keywords})
            reference=save('actual_calculate_result',{'before':before,'after':after,'result':value})
            assert_native_equal(after,before,'Actual numeric caller unchanged')
            calls.append({'case':active['case'],'phase':active['phase'],'caller':before,'error':None,'native':reference})
            return value
        def observed_plan(self,*positional,**keywords):
            capture=active['capture_plan'];normal=keywords.get('normal',positional[0] if positional else False)
            before=freeze({'scenario':self.s,'attributes':self.a,'args':positional,'kwargs':keywords}) if capture and normal else None
            try:value=real_plan(self,*positional,**keywords)
            except Exception as error:
                if before is not None:
                    reference=save('actual_normal_plan_exception',{'before':before,
                        'after':freeze({'scenario':self.s,'attributes':self.a,'args':positional,'kwargs':keywords}),
                        'error':error_record(error)})
                    plan_calls.append({'case':active['case'],'phase':active['phase'],'native':reference,'error':True})
                raise
            if before is not None:
                frozen=freeze(value)
                reference=save('actual_normal_plan_result',{'before':before,
                    'after':freeze({'scenario':self.s,'attributes':self.a,'args':positional,'kwargs':keywords}),
                    'result':value})
                plan_calls.append({'case':active['case'],'phase':active['phase'],'native':reference,
                                   'error':False,'result':frozen})
            return value
        module.calculate_damage=observed;Combat.plan=observed_plan
        for item in cases(facts):
            active.update(case=item['id'],phase='constructor',capture_plan=False)
            if item['target']:
                target=item['target'];entries=[entry for entry in stage_previews()[target['stage_id']]['possible_enemies']
                                               if entry['id']==target['enemy_id'] and entry['level']==target['level']]
                assert len(entries)==1 and entries[0]['level_type'] in ('NORMAL','ELITE')
                actual_reference=entries[0]['reference_stats']
                assert set(actual_reference)==set(item['reference'])
                for key,wanted in item['reference'].items():
                    assert_native_equal(actual_reference[key],wanted,'Real public target reference scalar/type '+key)
                save('actual_public_fixed_fixture_qualification',{'target':target,'actual_entry':entries[0],
                     'declared_reference':item['reference'],'consumer_source':'rouge/data/previews.json'})
            with tempfile.TemporaryDirectory(prefix='public107-',dir=out/'public-state') as directory:
                folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
                saved=fixture(item);owner=item['owner']
                raw=(json.dumps(saved,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_raw=(json.dumps({owner:profile(owner,item['elite'],item['potential'],item['skill'])},
                                       ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                run_path.write_bytes(raw);account_path.write_bytes(account_raw)
                sentinel=b'public107-original-temporary-must-not-be-rewritten\n';run_path.with_suffix('.tmp').write_bytes(sentinel)
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
                    before=freeze({'durable':durable(),'disks':disks()});callback();idle()
                    after=freeze({'durable':durable(),'disks':disks()})
                    record=save('pure_actual_UI_step',{'label':label,'before':before,'after':after})
                    assert_native_equal(after,before,label+' joint raw state/original disk phase')
                    return record
                def gravity(checked):
                    wanted=Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
                    relic.setCheckState(wanted)
                    assert relic.checkState()==wanted
                def select_target(target):
                    if target is None:window.target_enemy.setCurrentIndex(0)
                    else:
                        window.target_stage_choices.select_value(target['stage_id'])
                        window.target_enemy_choices.select_value(target)
                        selected=window.target_enemy.currentData()
                        assert type(selected) is dict and set(selected)==set(target)
                        assert all(type(selected[key]) is type(value) and selected[key]==value for key,value in target.items())
                def snapshot(name):
                    active.update(phase=name,capture_plan=True);normal_start=len(plan_calls)
                    try:unchanged('Actual MainWindow.calculate '+name,window.calculate)
                    finally:active['capture_plan']=False
                    before=freeze({'durable':durable(),'disks':disks()});value=window.damage_result
                    assert value is not None
                    last=calls[-1]
                    assert last['case']==item['id'] and last['phase']==name and last['error'] is None
                    assert last['caller']['args'][0]['operator']==owner and last['caller']['args'][0]['skill']==item['skill']
                    assert_native_equal(last['caller']['args'][0],value['scenario'],'Actual UI scenario equals real numeric caller')
                    actual_caller=last['caller']['args'][0]
                    assert actual_caller['elite']==item['elite'] and actual_caller['potential']==item['potential']
                    assert actual_caller['level']==(50,80,90)[item['elite']]
                    assert actual_caller['skill_rank']==(1,7,10)[item['elite']]
                    if owner==OP:assert actual_caller['enemy_weight']==weight_widget.value()
                    if window.target_enemy.currentData():
                        selected=window.target_enemy.currentData()
                        assert all(type(actual_caller['target_enemy'][key]) is type(selected[key])
                                   and actual_caller['target_enemy'][key]==selected[key] for key in selected)
                    else:assert 'target_enemy' not in actual_caller
                    result=value['result'];native=freeze(result)
                    formatter_before=freeze({'result':result,'durable':durable(),'disks':disks()})
                    texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                           'technical':reporting.format_report(result,technical=True)}
                    formatter_after=freeze({'result':result,'durable':durable(),'disks':disks()})
                    save('pure_actual_three_formatter_group',{'before':formatter_before,'after':formatter_after,
                         'texts':texts,'scope':'Joint result/state/disks around all three formatters; no individual-formatter claim'})
                    assert_native_equal(formatter_after,formatter_before,'All three formatters joint actual graph unchanged')
                    assert texts['estimate']==texts['default']
                    assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                    assert_native_equal(result,native,'Common three-formatter graph remains unchanged')
                    normal=plan_calls[normal_start:]
                    assert all(row['case']==item['id'] and row['phase']==name and not row['error'] for row in normal)
                    if owner==OP and item['skill']==3:
                        assert result['estimate']['skill']['cycle_seconds'] is not None
                        assert len(normal)==1 and normal[0]['result']['components']
                        assert normal[0]['result']['damage']>0
                        assert_native_equal(result['timing']['recharge_streams'],normal[0]['result']['timing']['streams'],
                                            'Actual public recharge streams came from captured real normal plan')
                    else:
                        assert normal==[]
                        if owner==OP and item['skill']==2:
                            assert result['estimate']['skill']['duration_seconds'] is None
                            assert result['estimate']['skill']['recharge_seconds'] is None
                            assert result['estimate']['skill']['cycle_seconds'] is None
                    complete={'view':{'damage_result':value,'three_texts':texts,
                                      'normal_plans':[row['result'] for row in normal],
                                      'normal_refs':[row['native'] for row in normal],
                                      'summary':window.run.summary(),'inventory':window.run.inventory_status(),
                                      'displayed_damage':window.damage_text.toPlainText()},
                              'durable':freeze(durable()),'disks':freeze(disks())}
                    # Native filenames differ across executions; refs are evidence,
                    # not a value within the cross-execution Gold equality domain.
                    comparable=deepcopy(complete);comparable['view'].pop('normal_refs')
                    after=freeze({'durable':durable(),'disks':disks()})
                    assert_native_equal(after,before,'Actual math/format/view joint state and disks unchanged')
                    reference=save('actual_window_snapshot',complete)
                    return comparable,reference
                def match_gold(value,phase,gold_row):
                    record=read_record(gold_dir/'records',gold_row['snapshots'][phase])
                    assert record['kind']=='actual_window_snapshot' and record['case']==item['id'] and record['phase']==phase
                    expected_value={key:record[key] for key in ('view','durable','disks')}
                    expected_value['view']=dict(expected_value['view']);expected_value['view'].pop('normal_refs')
                    assert_native_equal(value,expected_value,'Complete healthy '+phase+' same-input Gold graph and three texts')
                    return expected_value
                def picture(name,technical=False):
                    unchanged('Actual technical report toggle for PNG',lambda:window.damage_technical.setChecked(technical))
                    unchanged('Actual damage tab for PNG',lambda:window.centralWidget().setCurrentIndex(1))
                    path=out/(name+'.png');assert window.grab().save(str(path),'PNG')
                    pngs.append({'case':item['id'],'phase':active['phase'],'tab_index':1,
                                 'technical':technical,'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
                    unchanged('Restore actual default text after PNG',lambda:window.damage_technical.setChecked(False))
                idle();assert window.run.preserve_unreadable is False and window.run.save_issue is None
                assert disks()=={'run':{'exists':True,'bytes':raw},'account':{'exists':True,'bytes':account_raw},
                                 'run_tmp':{'exists':True,'bytes':sentinel},'account_tmp':{'exists':False,'bytes':None}}
                unchanged('Select actual owner',lambda:window.operator_choices.select_value(owner))
                index=window.skill.findData(item['skill']);assert index>=0
                unchanged('Select actual unlocked skill',lambda:window.skill.setCurrentIndex(index))
                unchanged('Use explicit original window',lambda:window.window_seconds.setValue(item['window']))
                unchanged('Enable actual observation window',lambda:window.limit_window.setChecked(True))
                unchanged('Manual relic selection',lambda:window.auto_relics.setChecked(False))
                relic=next(window.relic_list.item(i) for i in range(window.relic_list.count())
                           if window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)==GRAVITY)
                weight_widget=None
                if owner==OP:
                    weight_widget=next(widget for option_owner,key,skills,widget in window.model_option_widgets
                                       if option_owner==OP and key=='enemy_weight' and item['skill'] in skills)
                    assert weight_widget.minimum()==0 and weight_widget.maximum()==100
                    unchanged('Set legal base manual weight',lambda:weight_widget.setValue(0 if item['target'] else 4))
                if item['target'] is None:
                    unchanged('Initial manual reference defense',lambda:window.defense.setValue(200))
                    unchanged('Initial manual reference resistance',lambda:window.resistance.setValue(50.0))
                unchanged('Select actual qualified fixed identity',lambda:select_target(item['target']))
                plain,plain_ref=snapshot('plain')
                if owner=='mechanist':assert plain['view']['damage_result']['result']['total_damage']>0
                if args.phase=='candidate' and item['id']=='fixed4-S1':picture('01-healthy-fixed4-plain')
                unchanged('Select actual held gravity test',lambda:gravity(True))
                affected,affected_ref=snapshot('gravity-base')
                if item['target']:
                    result=affected['view']['damage_result']['result']
                    assert result['run_resolution']['enemy']['reference_stats']['massLevel']==item['weight']
                    assert result['run_resolution']['enemy']['stats']['massLevel']==item['weight']-2
                    assert result['relic_resolution']['enemy_effects']['weight_delta']==-2.0
                    assert result['relic_resolution']['records'][0]['applied']
                else:
                    result=affected['view']['damage_result']['result']
                    assert result['relic_resolution']['enemy_effects']['weight_delta']==0
                    assert not result['relic_resolution']['records'][0]['applied']
                    assert 'target_enemy' in result['relic_resolution']['records'][0]['missing_conditions']
                if args.phase=='candidate' and item['id']=='fixed4-S1':picture('02-fixed4-gravity-light')
                if args.phase=='candidate' and item['id']=='fixed0-signed-boundary':picture('03-signed-negative-reference',True)
                if weight_widget is not None:unchanged('Selected identity versus stale legal manual100',lambda:weight_widget.setValue(100))
                precedence,precedence_ref=snapshot('gravity-manual100')
                assert_native_equal(precedence['view']['damage_result']['result'],affected['view']['damage_result']['result'],
                                    'Fixed identity wins or no-target remains heavy between manual4 and100')
                unchanged('Remove actual target for independent manual oracle',lambda:select_target(None))
                unchanged('Remove actual relic for independent manual oracle',lambda:gravity(False))
                stats=item['reference'] or {'def':200,'magicResistance':50.0}
                unchanged('Same manual reference defense',lambda:window.defense.setValue(stats['def']))
                unchanged('Same manual reference resistance',lambda:window.resistance.setValue(stats['magicResistance']))
                if weight_widget is not None:unchanged('Healthy original manual light3',lambda:weight_widget.setValue(3))
                manual,manual_ref=snapshot('manual-light-original-oracle')
                if args.phase=='candidate' and item['id']=='manual-no-target':picture('04-legal-manual-light-control')
                unchanged('Restore actual fixed identity',lambda:select_target(item['target']))
                if weight_widget is not None:unchanged('Restore legal base manual reference',lambda:weight_widget.setValue(0 if item['target'] else 4))
                restored,restored_ref=snapshot('restored-plain')
                # Manual controls can change raw declared DEF/MR but identity
                # still supplies the same original resolved full numeric graph.
                assert_native_equal(restored['view']['damage_result']['result'],plain['view']['damage_result']['result'],
                                    'Actual legal UI recovery restores complete original numeric result')
                values={'plain':plain,'gravity-base':affected,'gravity-manual100':precedence,
                        'manual-light-original-oracle':manual,'restored-plain':restored}
                refs={'plain':plain_ref,'gravity-base':affected_ref,'gravity-manual100':precedence_ref,
                      'manual-light-original-oracle':manual_ref,'restored-plain':restored_ref}
                old_row=next((row for row in gold['rows'] if row['id']==item['id']),None) if gold else None
                if old_row:
                    for phase in ('plain','manual-light-original-oracle','restored-plain'):
                        match_gold(values[phase],phase,old_row)
                    if not item['crossing']:
                        for phase in ('gravity-base','gravity-manual100'):match_gold(values[phase],phase,old_row)
                if item['crossing']:
                    old_manual=(match_gold(manual,'manual-light-original-oracle',old_row)
                                if old_row else manual)
                    oracle=old_manual['view']['damage_result']['result']
                    actual=affected['view']['damage_result']['result']
                    if args.phase=='candidate':
                        assert_native_equal(actual['components'],oracle['components'],'Full intended components equal actual original manual-light Gold')
                        assert_native_equal(actual['estimate']['skill'],oracle['estimate']['skill'],'Full intended estimate skill and normal-cycle values equal manual Gold')
                        assert_native_equal(affected['view']['normal_plans'],old_manual['view']['normal_plans'],
                                            'Full actual normal outputs equal original same DEF/MR/cultivation light Gold')
                        old_affected=read_record(gold_dir/'records',old_row['snapshots']['gravity-base'])['view']['damage_result']['result']
                        for key in ('run_resolution','relic_resolution','applied_effects','inapplicable_relics','complete','scope'):
                            assert_native_equal(actual[key],old_affected[key],'Existing '+key+' entire metadata retained')
                        assert_native_equal([component for component in actual['components'] if component['name']!=TALENT],
                                            [component for component in old_affected['components'] if component['name']!=TALENT],
                                            'All non-talent damage streams unchanged')
                        assert talent(actual)['per_hit']>talent(old_affected)['per_hit']
                    else:
                        assert talent(oracle)['per_hit']>talent(actual)['per_hit']
                elif owner==OP and item['elite']==0:
                    assert talent(affected['view']['damage_result']['result'])['hits']==0
                    assert talent(affected['view']['damage_result']['result'])['total']==0
                elif owner=='mechanist':
                    assert_native_equal(affected['view']['damage_result']['result']['components'],
                                        plain['view']['damage_result']['result']['components'],'Weight-independent nonzero mechanical components unchanged')
                active['phase']='actual-fresh-training-observation-save'
                observation={'operators':[{'id':owner,'fields':{'selected_skill':item['skill']}}],
                             'selected_operator':owner}
                caller=freeze((observation,1001.0));account_before=freeze(window.account_cache.records)
                assert window.apply_run_observation(observation,1001.0) is True;idle()
                assert_native_equal((observation,1001.0),caller,'Actual fresh observation caller unchanged')
                assert_native_equal(window.account_cache.records,account_before,'Run observation keeps account reference raw records')
                fresh,fresh_ref=snapshot('actual-fresh-save-view');refs['actual-fresh-save-view']=fresh_ref
                if old_row:match_gold(fresh,'actual-fresh-save-view',old_row)
                active['phase']='actual-close-RunState-reload'
                before=freeze({'durable':durable(),'disks':disks()});window.close();application.processEvents()
                assert_native_equal({'durable':durable(),'disks':disks()},before,'Actual close joint state/current disks preserved')
                persisted=json.loads(run_path.read_text(encoding='utf-8'));restarted=RunState(run_path)
                assert restarted.preserve_unreadable is False and restarted.save_issue is None
                assert_native_equal(restarted.state,persisted,'Direct real reload restores actual persisted JSON graph, not live aliases')
                assert_native_equal(disks(),before['disks'],'Accepted direct reload never rewrites current original disk phase')
                restart=save('actual_close_RunState_reload',{'live_before':before,'persisted_json':persisted,
                    'restart_state':restarted.state,'disks_after':disks(),'observation_before':caller,
                    'observation_after':(observation,1001.0),'oracle':'Actual saved JSON; no JSON live-alias guarantee'})
                rows.append({'id':item['id'],'crossing':item['crossing'],'qualification':{
                    'owner':owner,'skill':item['skill'],'elite':item['elite'],'potential':item['potential']},
                    'target':item['target'],'snapshots':refs,'restart':restart,
                    'healthy_snapshot_phases_complete_Gold_same':bool(old_row),
                    'all_gravity_snapshot_phases_complete_Gold_same':bool(old_row and not item['crossing']),
                    'intended_changed_branch_manual_Gold_equal':bool(old_row and item['crossing'])})
                window.deleteLater();application.processEvents();window=None
                print(json.dumps({'completed':len(rows),'case':item['id']}),flush=True)
        assert len(rows)==COUNT and not errors and len(pngs)==(0 if args.phase=='gold' else 4)
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
        if Combat is not None and real_plan is not None:Combat.plan=real_plan
        sys.excepthook=old_hook;done.set();receipt['elapsed_seconds']=time.perf_counter()-started
        receipt['source_after']=source_map(root)
        receipt['source_drift']=[name for name in set(expected)|set(receipt['source_after'])
                                 if expected.get(name)!=receipt['source_after'].get(name)]
        receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        if receipt['source_drift'] or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw:
            receipt.update(passed=False,workflow_complete=False)
        if args.phase=='candidate':receipt['actual_gold_receipt_sha256']=sha(gold_raw)
        receipt['actual_numeric_calls']=len(calls);receipt['actual_captured_normal_plans']=len(plan_calls)
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'windows':len(rows),'native_records':len(records),
                      'elapsed_seconds':receipt['elapsed_seconds']}))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
