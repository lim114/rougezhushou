"""Root-only bounded real MainWindow active-zone consumer workflow.

Source prepared only. Bad shapes are explicitly public in-memory consumer
inputs after healthy startup, never malformed saved-cache/OCR admission.
Healthy results use complete real same-runner Gold; handled errors/pending
remain unknown and are not complete game-mechanism claims.
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
FACT_SHA='af66d1b06a98b46660a501c67144a074c330213d05c11c0241d28be63dda42d9'
TRANSPORT_SHA='7df1d49d0927c33b59a67dc005cad7ef0fb300d92f7c75327f2839c4b2cfbb2c'
TEST_SHA='da7a739664f19e55186a8e12581bbb72c85a08a4d1640c9299bcd51943ba8b59'
TEST107_SHA='2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
ORIGINAL_SHA='caadc9ecfd748e1172820abe460735b0563210e1c25312482e0d2a541ac5a790'
ORIGINAL_GUARD_SHA='409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
ORIGINAL_RUNNER_SHA='16396e96ad48b151932977eaa5fe95d3414c058aa1b0cde3a90648ecb9611ad2'
SELECTOR='tests.test_zone_environment_input_108'
OP='mechanist'
TARGET={'enemy_id':'enemy_1093_ccsbr','level':0,'stage_id':'ro6_n_1_2'}
DEADLINE=450


def sha(raw):return hashlib.sha256(raw).hexdigest()


def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}


def brief_error(error):
    return None if error is None else {key:error[key] for key in ('type','message')}


def profile():
    return {'id':OP,'scope':'operator_profile','fields':{'elite':2,'level':90,
        'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':1},
        'skill_ranks':{'1':10,'2':10,'3':10},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}


def difficulty(grade=10):
    return {'value':grade,'modeDifficulty':'NORMAL','mode':'NORMAL',
            'captured_at':1000.0,'source':'public108-normal-consumer-control'}


def zone(facts,identity,**extra):
    return {'id':identity,'name':facts['zones'][identity]['name'],
            'captured_at':1000.0,'source':'public108-fixed-zone-control',**extra}


def fixture(facts,recovery=False):
    member=profile();member.update(scope='run',present=True,recruitment_kind='non_emergency',
        char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
        invalid_fields=[],invalid_skill_ranks=[],missing_fields=[],sources={'public_opaque':[None,{'nullable':None}]})
    return {'id':'public108-zone-window','started_at':0.0,'last_read':1000.0,
        'operators':{OP:member},'crew_count':1,'selected_operator':OP,'relics':{},
        'tactical_tools':{},'relic_count':0,'inventory_verified':True,
        'inventory_confirmed_at':1000.0,'bar_signature':[],'relic_icon_memory':None,
        'history':[],'resources':{},'config':{'difficulty':difficulty(),
            'zone':{} if recovery else zone(facts,'zone_4_1',main_zone_index=[6])},
        'maps':{},'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}


def cases(facts):
    rows=[]
    def add(identity,value=None,*,absent=False,grade=10,target=True,active=True,changed=False,kind=None):
        config={'difficulty':difficulty(grade)} if active else {}
        if not absent:config['zone']=deepcopy(value)
        rows.append({'id':identity,'config':config,'target':target,'changed':changed,
                     'error_kind':kind,'admission':'public_in_memory_consumer_after_healthy_constructor'})
    for identity in ('zone_1','zone_2','zone_3','zone_4','zone_4_1','zone_5','zone_6'):
        add('known-'+identity,zone(facts,identity))
    for label,value in (('bool',True),('text','2'),('list',[6]),('float',2.0)):
        add('known-4_1-stale-'+label,zone(facts,'zone_4_1',main_zone_index=value))
    portal={'id':None,'name':facts['zones']['zone_portal_normal_1_1']['name'],
            'hidden':True,'candidates':['zone_portal_normal_1_1','zone_portal_normal_1_2'],
            'captured_at':1000.0,'source':'public108-ambiguous-portal-control'}
    add('known-portal-no-derived-main',zone(facts,'zone_portal_normal_1_1'))
    add('ambiguous-portal-no-main',portal)
    add('ambiguous-portal-inherited2',{**portal,'main_zone_index':2})
    add('unknown-id-explicit2',{'id':'public108-unknown-zone','main_zone_index':2})
    add('unknown-id-float-depth',{'id':'public108-unknown-zone','main_zone_index':2.0})
    add('absent-zone',absent=True)
    for label,value in (('none',None),('dict',{}),('false',False),('zero',0),('text',''),('list',[])):
        add('safe-falsey-'+label,value)
    for label,value in (('true',True),('int',1),('float',1.5)):
        add('safe-hashable-id-'+label,{'id':value,'main_zone_index':2})
    add('unused-bad-zone-no-target','zone_2',target=False)
    add('unused-bad-id-no-difficulty',{'id':[]},active=False)
    for grade in (0,4):add('healthy-zero-rate-grade'+str(grade),zone(facts,'zone_2'),grade=grade)
    for label,value in (('text','zone_2'),('true',True),('one',1),('float',1.5),('list',['zone_2'])):
        add('truthy-zone-'+label,value,changed=True,kind='container')
    for label,value in (('empty-list',[]),('dict',{}),('list',['zone_2'])):
        add('unhashable-id-'+label,{'id':value},changed=True,kind='id')
    add('active-zero-rate-text','zone_2',grade=0,changed=True,kind='container')
    add('active-zero-rate-list-id',{'id':[]},grade=0,changed=True,kind='id')
    assert len(rows)==40 and len({row['id'] for row in rows})==40
    assert sum(row['changed'] for row in rows)==10
    return rows


def registry_change(before_raw,after_raw):
    before=ast.parse(before_raw.decode('utf-8'));after=ast.parse(after_raw.decode('utf-8'))
    def assignment(tree):
        found=[node for node in tree.body if isinstance(node,ast.Assign)
               and any(isinstance(target,ast.Name) and target.id=='MODULES' for target in node.targets)]
        assert len(found)==1;return found[0]
    old=assignment(before);new=assignment(after)
    values=ast.literal_eval(old.value);updated=ast.literal_eval(new.value)
    assert type(updated) is type(values) and type(values) in (list,tuple)
    assert updated==type(values)([SELECTOR])+values
    new.value=deepcopy(old.value)
    assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase','original','original-exit','original-sha256','original-guard'):
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--gold');parser.add_argument('--gold-exit')
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;guard_path=Path(args.guard).resolve()
    assert args.phase in ('gold','candidate') and not out.exists() and out!=root and root not in out.parents
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    facts_raw=(artifact/'fixture-facts.json').read_bytes();assert sha(facts_raw)==FACT_SHA
    facts=json.loads(facts_raw)
    transport_raw=(artifact/'exact-local-transports.json').read_bytes();assert sha(transport_raw)==TRANSPORT_SHA
    transport=json.loads(transport_raw);assert len(transport['replacements'])==2
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert len(expected)==(750 if args.phase=='gold' else 751) and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    for change in transport['replacements']:
        assert expected[change['path']]==change['before_sha256' if args.phase=='gold' else 'after_sha256']
    assert expected['tests/test_aglna_gravity_weight_107.py']==TEST107_SHA
    for name,want in facts['public_source_sha256'].items():assert expected[name]==want
    original_dir=Path(args.original).resolve();original_raw=(original_dir/'observations.json').read_bytes()
    assert args.original_sha256==ORIGINAL_SHA and len(original_raw)==640662 and sha(original_raw)==ORIGINAL_SHA
    assert Path(args.original_exit).read_bytes()==b'0\n'
    original=json.loads(original_raw);original_guard_raw=Path(args.original_guard).read_bytes()
    original_guard=json.loads(original_guard_raw)
    assert sha(original_guard_raw)==ORIGINAL_GUARD_SHA
    assert original['runner_sha256']==ORIGINAL_RUNNER_SHA and original['native_helper_sha256']==HELPER_SHA
    assert original['kind']=='ROOT_ACTUAL_ORIGINAL108_ZONE_CONSUMERS'
    assert original['observation_complete'] is True and original['product_pass'] is False and original['observation_only'] is True
    assert original['source_and_CORE_unchanged'] is True
    assert original['source_before']==original['source_after']==original_guard['source_sha256']
    assert len(original['source_before'])==750 and original['source_before']['tests/test_aglna_gravity_weight_107.py']==TEST107_SHA
    assert original['source_guard_sha256']==sha(original_guard_raw)
    assert original_guard['source_additional_sha256']==extra
    assert original['CORE_before']==original['CORE_after']==extra['CORE_0.70_VERIFICATION.json']
    assert original['planned_calculation_cases']==47 and original['planned_previews']==8
    assert original['actual_explicit_consumer_calls']==178 and original['actual_native_records']==225
    assert original['consumer_error_count']==22 and original['blocked_phase_count']==10
    gold=None;gold_dir=None
    if args.phase=='gold':assert expected==original['source_before']
    else:
        assert args.gold and args.gold_exit and Path(args.gold_exit).read_bytes()==b'0\n'
        gold_dir=Path(args.gold).resolve();gold_raw=(gold_dir/'receipt.json').read_bytes();gold=json.loads(gold_raw)
        assert gold['kind']=='ROOT_ACTUAL_108_REAL_MAINWINDOW' and gold['phase']=='gold'
        assert gold['passed'] is True and gold['workflow_complete'] is True and gold['Qt_errors']==[]
        assert gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['fixture_facts_sha256']==FACT_SHA
        assert gold['original_receipt_sha256']==args.original_sha256 and gold['original_guard_sha256']==sha(original_guard_raw)
        assert gold['source_before']==gold['source_after']==original['source_before'] and not gold['source_drift']
        assert gold['source_additional_before']==gold['source_additional_after']==extra
        assert len(gold['rows'])==43 and len(gold['windows'])==2 and len(gold['pngs'])==0
        assert set(expected)-set(gold['source_before'])=={'tests/test_zone_environment_input_108.py'}
        assert not set(gold['source_before'])-set(expected)
        assert {name for name in gold['source_before'] if gold['source_before'][name]!=expected[name]}=={
            'rouge/enemy_environment.py','scripts/verify_cloud.py'}
        assert expected['tests/test_zone_environment_input_108.py']==TEST_SHA
        registry_change((gold_dir/'public-Source/verify_cloud.py').read_bytes(),(root/'scripts/verify_cloud.py').read_bytes())
        assert (gold_dir/'public-Source/verify_full_available.py').read_bytes()==(root/'scripts/verify_full_available.py').read_bytes()
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir();(out/'public-Source').mkdir()
    for name in ('scripts/verify_cloud.py','scripts/verify_full_available.py'):
        (out/'public-Source'/Path(name).name).write_bytes((root/name).read_bytes())
    rows=[];windows=[];records=[];pngs=[];errors=[];calls=[]
    active={'case':'bootstrap','phase':'bootstrap'};done=threading.Event();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_108_REAL_MAINWINDOW','phase':args.phase,'passed':False,'workflow_complete':False,
        'runner_sha256':sha(Path(__file__).read_bytes()),'fixture_facts_sha256':FACT_SHA,
        'transport_sha256':TRANSPORT_SHA,'source_guard_sha256':sha(guard_raw),
        'original_receipt_sha256':args.original_sha256,'original_guard_sha256':sha(original_guard_raw),
        'original_raw_exit_sha256':sha(Path(args.original_exit).read_bytes()),
        'source_before':expected,'source_additional_before':extra,'rows':rows,'windows':windows,
        'records':records,'pngs':pngs,'Qt_errors':errors,'deadline_seconds':DEADLINE,
        'native_windows_verified':False,'private_state_access':False,'game_chat_sampling_executed':False,
        'natural_OCR_producer_verified':False,'malformed_saved_cache_admission_claimed':False,
        'matrix_scope':'40 independent public in-memory config inputs after one healthy constructor; raw matrix inputs never saved.',
        'cached_scope':'One accepted real saved zone4_1 with list-valued legacy main; known ID resolves without washing raw record.',
        'restart_scope':'Two direct RunState reloads after real close; read-only loaded graph or actual persisted JSON graph; no second MainWindow/live JSON alias claim.',
        'formatter_scope':'Joint result/state/disks around all three complete formatters; no individual-formatter claim.',
        'preview_scope':'Real independent battle_preview API per targeted matrix case; candidate-only actual panel rendering of malformed pending; no original panel success claim.',
        'pending_scope':'ValueError/preview unknown remains pending; successful workflow verification is not complete gameplay mechanics.'}
    def save(kind,value):
        reference=write_record(out/'records',len(records)+1,{'kind':kind,'case':active['case'],
            'phase':active['phase'],**value})
        reference.update(kind=kind,case=active['case'],phase=active['phase']);records.append(reference);return reference
    def deadline():
        if not done.wait(DEADLINE):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline':DEADLINE}))
            os._exit(124)
    threading.Thread(target=deadline,daemon=True).start()
    old_hook=sys.excepthook;window=None;module=None;backend=None;calculator=None
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'phase':active['phase'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.dont_write_bytecode=True;sys.path.insert(0,str(root))
        from PySide6 import __version__
        from PySide6.QtCore import qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module,estimate,reporting
        from rouge.catalog import stage_previews
        from rouge.battle_preview import battle_data,enemy_preview,enemy_text
        from rouge.run_config import config_data
        from rouge.run_state import RunState
        assert __version__==qVersion()=='6.9.3'
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage
        receipt.update(python=sys.version,qt=qVersion())
        actual_config=config_data()
        assert_native_equal({key:actual_config['zones'][key]['name'] for key in facts['zones']},
                            {key:value['name'] for key,value in facts['zones'].items()},'Actual public zone names')
        for grade,value in facts['bossValue'].items():
            assert_native_equal(actual_config['difficulties'][grade]['bossValue'],value,'Existing public coefficient source')
        entries=[entry for entry in stage_previews()[TARGET['stage_id']]['possible_enemies']
                 if entry['id']==TARGET['enemy_id'] and entry['level']==TARGET['level']]
        preview_entries=[entry for entry in battle_data()['stages'][TARGET['stage_id']]['enemies']
                         if entry['id']==TARGET['enemy_id'] and entry['level']==TARGET['level']]
        assert len(entries)==len(preview_entries)==1 and entries[0]['level_type']=='NORMAL'
        for entry in (entries[0],preview_entries[0]):
            for key,value in facts['target_reference'].items():
                assert_native_equal(entry['reference_stats'][key],value,'Real public fixed reference scalar '+key)
        save('actual_public_fixture_qualification',{'numeric_entry':entries[0],'preview_entry':preview_entries[0],
            'zone_names':facts['zones'],'bossValue':facts['bossValue'],
            'numeric_getter_source':'rouge/data/previews.json','independent_preview_getter_source':'rouge/data/battle-previews.json'})
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                after=freeze({'args':positional,'kwargs':keywords});details=error_record(error)
                reference=save('actual_calculate_exception',{'before':before,'after':after,'error':details})
                calls.append({'case':active['case'],'phase':active['phase'],'caller':before,
                              'error':details,'native':reference})
                assert_native_equal(after,before,'Actual numeric exception caller unchanged');raise
            after=freeze({'args':positional,'kwargs':keywords})
            reference=save('actual_calculate_result',{'before':before,'after':after,'result':value})
            calls.append({'case':active['case'],'phase':active['phase'],'caller':before,'error':None,'native':reference})
            assert_native_equal(after,before,'Actual numeric caller unchanged');return value
        module.calculate_damage=observed
        for recovery in (False,True):
            window_id='legal-observation-recovery' if recovery else 'accepted-cache-and-memory-matrix'
            active.update(case=window_id,phase='constructor')
            with tempfile.TemporaryDirectory(prefix='public108-',dir=out/'public-state') as directory:
                folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
                raw=(json.dumps(fixture(facts,recovery),ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                account_raw=(json.dumps({OP:profile()},ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
                run_path.write_bytes(raw);account_path.write_bytes(account_raw)
                sentinel=b'public108-original-temporary-must-not-be-rewritten\n';run_path.with_suffix('.tmp').write_bytes(sentinel)
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
                            ('run_tmp',run_path.with_suffix('.tmp')),('account_tmp',account_path.with_suffix('.tmp')))}
                def unchanged(label,callback):
                    before=freeze({'durable':durable(),'disks':disks()});returned=callback();idle()
                    after=freeze({'durable':durable(),'disks':disks()})
                    reference=save('pure_actual_UI_step',{'label':label,'before':before,'after':after})
                    assert_native_equal(after,before,label+' joint state/current disk phase');return returned,reference
                def select_target(enabled):
                    if not enabled:window.target_enemy.setCurrentIndex(0)
                    else:
                        window.target_stage_choices.select_value(TARGET['stage_id'])
                        window.target_enemy_choices.select_value(TARGET)
                        assert_native_equal(window.target_enemy.currentData(),TARGET,'Actual selected target identity')
                def picture(name,tab,anchor):
                    unchanged('Actual tab for PNG '+name,lambda:window.centralWidget().setCurrentIndex(tab))
                    widget=window.damage_text if tab==1 else window.battle_preview.enemy_detail if tab==4 else window.run_summary
                    if tab in (1,4):
                        def scroll_to_real_anchor():
                            cursor=widget.document().find(anchor)
                            assert not cursor.isNull()
                            widget.setTextCursor(cursor);widget.ensureCursorVisible()
                        unchanged('Scroll real report to visible PNG anchor '+anchor,scroll_to_real_anchor)
                        rectangle=widget.cursorRect();viewport=widget.viewport().rect()
                        assert widget.isVisible() and viewport.contains(rectangle.center())
                        visual={'actual_text':widget.toPlainText(),'anchor':anchor,
                            'selection':widget.textCursor().selectedText(),'cursor_position':widget.textCursor().position(),
                            'scroll_value':widget.verticalScrollBar().value(),
                            'cursor_rect':(rectangle.x(),rectangle.y(),rectangle.width(),rectangle.height()),
                            'viewport_rect':(viewport.x(),viewport.y(),viewport.width(),viewport.height())}
                        assert visual['selection']==anchor
                    else:
                        assert widget.isVisible() and anchor in widget.text()
                        rectangle=widget.geometry()
                        visual={'actual_text':widget.text(),'anchor':anchor,
                            'widget_rect':(rectangle.x(),rectangle.y(),rectangle.width(),rectangle.height()),
                            'scope':'Actual visible QLabel summary; no report-scroll or text-cursor claim'}
                    visual_ref=save('actual_PNG_visible_report_anchor',visual)
                    path=out/(name+'.png');assert window.grab().save(str(path),'PNG')
                    pngs.append({'case':active['case'],'phase':active['phase'],'tab_index':tab,
                        'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),
                        'visible_anchor':anchor,'anchor_native':visual_ref,'Root_visual_verified':False})
                    unchanged('Restore damage tab after PNG',lambda:window.centralWidget().setCurrentIndex(1))
                def snapshot(identity,changed=False,error_kind=None):
                    active.update(case=identity,phase='explicit-consumer-snapshot')
                    start=len(calls);unchanged('Actual MainWindow.calculate',window.calculate)
                    assert len(calls)==start+1
                    last=calls[-1];assert last['case']==identity and last['phase']==active['phase']
                    before=freeze({'durable':durable(),'disks':disks()})
                    caller=last['caller']['args'][0]
                    assert caller['operator']==OP and caller['skill']==1 and caller['elite']==2
                    assert caller['level']==90 and caller['skill_rank']==10
                    assert_native_equal(caller['run_config'],window.run.state['config'],'Actual raw config used by numerical caller')
                    texts=None
                    if changed:
                        expected_type='ValueError' if args.phase=='candidate' else ('AttributeError' if error_kind=='container' else 'TypeError')
                        assert last['error'] is not None and last['error']['type']==expected_type
                        assert window.damage_result is None and window.damage_text.toPlainText()==last['error']['message'].replace(chr(160),' ')
                        if args.phase=='candidate':
                            assert last['error']['message']==('本局区域配置需要对象。' if error_kind=='container' else '本局区域ID不能用于固定区域查询。')
                    else:
                        assert last['error'] is None and window.damage_result is not None
                        assert_native_equal(window.damage_result['scenario'],caller,'Actual UI scenario equals native original caller')
                        result=window.damage_result['result']
                        formatter_before=freeze({'result':result,'durable':durable(),'disks':disks()})
                        texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                               'technical':reporting.format_report(result,technical=True)}
                        formatter_after=freeze({'result':result,'durable':durable(),'disks':disks()})
                        save('pure_actual_three_formatter_group',{'before':formatter_before,'after':formatter_after,'texts':texts})
                        assert_native_equal(formatter_after,formatter_before,'Complete three formatter joint graph unchanged')
                        assert texts['estimate']==texts['default']
                        assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                    preview=None;preview_error=None;preview_text=None;preview_args=None;preview_ref=None
                    if window.target_enemy.currentData():
                        preview_args=(TARGET['stage_id'],TARGET['enemy_id'],TARGET['level'],deepcopy(window.run.state['config']))
                        preview_before=freeze(preview_args)
                        try:preview=enemy_preview(*preview_args)
                        except Exception as error:preview_error=error_record(error)
                        preview_ref=save('actual_independent_enemy_preview',{'before':preview_before,'after':preview_args,
                            'result':preview,'error':preview_error})
                        assert_native_equal(preview_args,preview_before,'Actual preview raw caller unchanged')
                        if changed and args.phase=='gold':
                            assert preview_error is not None and preview_error['type']==last['error']['type'] and preview is None
                        else:
                            assert preview_error is None and preview is not None
                            text_before=freeze(preview);preview_text=enemy_text(preview)
                            save('pure_actual_preview_formatter',{'before':text_before,'after':preview,'text':preview_text})
                            assert_native_equal(preview,text_before,'Actual complete preview formatter input unchanged')
                            if changed:
                                assert preview['environment'] is None
                                assert preview['context_pending']==['本局环境无法确认：'+last['error']['message']]
                                assert '【面板待确认】' in preview_text and '预计生命值：未知' in preview_text
                            elif window.damage_result:
                                numeric_environment=window.damage_result['result']['run_resolution']['enemy']
                                preview_environment=preview['environment']
                                boundary_before=freeze({'numeric_environment':numeric_environment,
                                    'preview_environment':preview_environment,'damage_result':window.damage_result,
                                    'durable':durable(),'disks':disks()})
                                assert type(numeric_environment) is type(preview_environment) is dict
                                numeric_keys=list(numeric_environment);preview_keys=list(preview_environment)
                                assert numeric_keys[:3]==['enemy_id','level','stage_id']
                                assert preview_keys[:3]==['stage_id','enemy_id','level']
                                assert numeric_keys[3:]==preview_keys[3:]
                                # The two public APIs declare different identity insertion
                                # order. Compare separate shallow copies in the actual
                                # numerical key order; retain every original value/alias.
                                numeric_comparison={key:numeric_environment[key] for key in numeric_keys}
                                preview_comparison={key:preview_environment[key] for key in numeric_keys}
                                assert_native_equal(preview_comparison,numeric_comparison,
                                                    'Independent API explicit identity-prefix projection; complete remainder native unchanged')
                                boundary_after=freeze({'numeric_environment':numeric_environment,
                                    'preview_environment':preview_environment,'damage_result':window.damage_result,
                                    'durable':durable(),'disks':disks()})
                                save('actual_cross_API_identity_order_boundary',{'before':boundary_before,
                                    'after':boundary_after,'numeric_keys':numeric_keys,'preview_keys':preview_keys,
                                    'numeric_comparison':numeric_comparison,'preview_comparison':preview_comparison,
                                    'scope':'Only declared three scalar identity keys reordered in separate comparison copies; original results/callers/text/raw cache never normalized'})
                                assert_native_equal(boundary_after,boundary_before,
                                                    'Explicit independent API comparison preserves original complete joint graphs')
                    after=freeze({'durable':durable(),'disks':disks()})
                    assert_native_equal(after,before,'Actual snapshot math/preview/format group state and disks unchanged')
                    value={'view':{'damage_result':window.damage_result,'numeric_error':brief_error(last['error']),
                        'displayed_damage':window.damage_text.toPlainText(),'three_texts':texts,
                        'preview':preview,'preview_error':brief_error(preview_error),'preview_text':preview_text,
                        'numeric_caller':caller,'preview_caller':preview_args,
                        'run_summary_widget':window.run_summary.text()},
                        'durable':freeze(durable()),'disks':freeze(disks())}
                    reference=save('actual_window_snapshot',value)
                    old_row=next((row for row in gold['rows'] if row['id']==identity),None) if gold else None
                    if old_row:
                        old=read_record(gold_dir/'records',old_row['snapshot'])
                        assert old['kind']=='actual_window_snapshot' and old['case']==identity
                        old_value={key:old[key] for key in ('view','durable','disks')}
                        if not changed:assert_native_equal(value,old_value,'Complete same-input healthy Gold native/math/three texts/view/state/disks')
                        else:
                            assert_native_equal(value['durable'],old_value['durable'],'Intended error change retains full raw durable Gold')
                            assert_native_equal(value['disks'],old_value['disks'],'Intended error change retains all original Gold disk bytes')
                            for key in ('numeric_caller','preview_caller','run_summary_widget'):
                                assert_native_equal(value['view'][key],old_value['view'][key],'Intended error same raw '+key)
                            assert old_value['view']['damage_result'] is None and old_value['view']['preview'] is None
                    rows.append({'id':identity,'window':window_id,'changed':changed,'error_kind':error_kind,
                        'snapshot':reference,'actual_numeric_ref':last['native'],'actual_preview_ref':preview_ref,
                        'healthy_complete_Gold_same':bool(old_row and not changed),
                        'changed_preserved_raw_Gold_same':bool(old_row and changed)})
                    return value
                idle();assert window.run.preserve_unreadable is False and window.run.save_issue is None
                assert disks()=={'run':{'exists':True,'bytes':raw},'account':{'exists':True,'bytes':account_raw},
                                 'run_tmp':{'exists':True,'bytes':sentinel},'account_tmp':{'exists':False,'bytes':None}}
                unchanged('Select actual qualified owner',lambda:window.operator_choices.select_value(OP))
                index=window.skill.findData(1);assert index>=0
                unchanged('Select actual unlocked skill1',lambda:window.skill.setCurrentIndex(index))
                unchanged('Use real ten-second window',lambda:window.window_seconds.setValue(10.0))
                unchanged('Enable actual observation window',lambda:window.limit_window.setChecked(True))
                unchanged('Original frame timing',lambda:window.frame_timing.setChecked(True))
                unchanged('Manual empty relic selection',lambda:window.auto_relics.setChecked(False))
                unchanged('Select actual qualified fixed target',lambda:select_target(True))
                baseline=freeze(durable());baseline_disks=freeze(disks())
                if not recovery:
                    initial=snapshot('accepted-cached-known4_1-legacy-list-main')
                    assert_native_equal(window.run.state['config']['zone']['main_zone_index'],[6],'Accepted legacy raw list depth stays untouched')
                    if args.phase=='candidate':picture('01-healthy-known-main-cache',1,'预计生命值')
                    for item in cases(facts):
                        active.update(case=item['id'],phase='restore-before-public-memory-fixture')
                        window.run.state=deepcopy(baseline['run'])
                        assert_native_equal(window.account_cache.records,baseline['account'],'Matrix account unchanged')
                        unchanged('Actual healthy target choice before raw memory install',lambda enabled=item['target']:select_target(enabled))
                        previous=freeze(durable());before_disks=freeze(disks())
                        window.run.state['config']=deepcopy(item['config'])
                        installed=freeze(durable())
                        assert_native_equal(disks(),before_disks,'Explicit raw consumer install never writes any cache')
                        assert_native_equal(installed['account'],previous['account'],'Explicit memory install keeps account raw')
                        expected_run=deepcopy(previous['run']);expected_run['config']=deepcopy(item['config'])
                        assert_native_equal(installed['run'],expected_run,'Only explicit public raw config changed in memory')
                        save('public_memory_consumer_admission',{'before':previous,'after':installed,
                            'disks_before':before_disks,'disks_after':disks(),'fixture':item,
                            'saved_schema_admission':False,'natural_OCR_producer':False,'save_permitted':False})
                        value=snapshot(item['id'],item['changed'],item['error_kind'])
                        if args.phase=='candidate' and item['id']=='truthy-zone-text':
                            picture('02-clear-active-zone-error',1,'本局区域配置需要对象。')
                            panel=window.battle_preview
                            def render_actual_pending():
                                panel.set_stage(TARGET['stage_id'])
                                panel.set_context(deepcopy(item['config']))
                                panel._render_enemy(TARGET['enemy_id'],TARGET['level'])
                                assert panel._shown_enemy==(TARGET['stage_id'],TARGET['enemy_id'],TARGET['level'])
                                assert panel.enemy_detail.toPlainText()==value['view']['preview_text'].replace(chr(160),' ')
                            unchanged('Actual candidate BattlePreviewPanel pending rendering',render_actual_pending)
                            assert window.centralWidget().indexOf(panel)==4
                            save('actual_candidate_pending_panel',{'context':panel.context,'shown_enemy':panel._shown_enemy,
                                'displayed_preview':panel.enemy_detail.toPlainText(),'expected_preview':value['view']['preview_text'],
                                'original_panel_success_claimed':False})
                            picture('03-real-preview-pending',4,'本局环境无法确认：本局区域配置需要对象。')
                            unchanged('Restore actual panel to healthy context',lambda:panel.set_context(deepcopy(baseline['run']['config'])))
                        print(json.dumps({'matrix_completed':len(rows)-1,'case':item['id']}),flush=True)
                    active.update(case=window_id,phase='restore-valid-loaded-state-before-close')
                    window.run.state=deepcopy(baseline['run'])
                    assert_native_equal(durable(),baseline,'Complete valid loaded graph restored before close; raw matrix is never saved')
                    assert_native_equal(disks(),baseline_disks,'Read-only matrix never overwrites original cache or tmp')
                    restart_oracle='original-loaded-state'
                else:
                    account_before=freeze(window.account_cache.records);observation_refs=[]
                    for identity,record,at in (
                        ('actual-fresh-main4_1-save',zone(facts,'zone_4_1'),1001.0),
                        ('actual-fresh-portal-inherits4-save',{'id':None,
                            'name':facts['zones']['zone_portal_normal_1_1']['name'],'hidden':True,
                            'candidates':['zone_portal_normal_1_1','zone_portal_normal_1_2'],
                            'main_zone_index':6,'source':'public108-fresh-hidden-zone-observation'},1002.0)):
                        active.update(case=identity,phase='actual-legal-observation-save')
                        observation={'config':{'zone':deepcopy(record)}}
                        caller=freeze((observation,at));before=freeze({'durable':durable(),'disks':disks()})
                        assert window.apply_run_observation(observation,at) is True;idle()
                        assert_native_equal((observation,at),caller,'Actual legal fresh observation caller unchanged')
                        assert_native_equal(window.account_cache.records,account_before,'Legal run observation keeps account raw')
                        assert_native_equal(window.run.state['config']['zone']['main_zone_index'],4,'Known main establishes4 and portal inherits previous4, not incoming6 or portal digits')
                        assert disks()['account']==before['disks']['account'] and disks()['account_tmp']==before['disks']['account_tmp']
                        observation_refs.append(save('actual_legal_observation_save',{'before':before,
                            'after':{'durable':durable(),'disks':disks()},'caller_before':caller,'caller_after':(observation,at)}))
                        value=snapshot(identity)
                        if args.phase=='candidate' and identity=='actual-fresh-portal-inherits4-save':
                            assert '未萌生的摇篮' in window.run_summary.text()
                            picture('04-legal-portal-recovery-summary',0,'未萌生的摇篮')
                    restart_oracle='actual-persisted-JSON'
                active.update(case=window_id,phase='actual-close-direct-RunState-reload')
                before=freeze({'durable':durable(),'disks':disks()});window.close();application.processEvents()
                assert_native_equal({'durable':durable(),'disks':disks()},before,'Real close preserves current graph and disk phase')
                persisted=json.loads(run_path.read_text(encoding='utf-8'));restarted=RunState(run_path)
                assert restarted.preserve_unreadable is False and restarted.save_issue is None
                assert_native_equal(restarted.state,persisted if recovery else baseline['run'],
                                    'Direct reload follows actual persisted JSON or already-loaded read-only contract')
                assert_native_equal(disks(),before['disks'],'Direct reload never rewrites accepted original disk phase')
                reference=save('actual_close_RunState_reload',{'live_before':before,'persisted_json':persisted,
                    'restart_state':restarted.state,'disks_after':disks(),'oracle':restart_oracle})
                windows.append({'id':window_id,'restart':reference,'oracle':restart_oracle,
                    'legal_observation_refs':observation_refs if recovery else [],'original_disk_sha256':sha(raw),
                    'constructor_saved_schema_accepted':True,'matrix_invalid_inputs_saved':False})
                window.deleteLater();application.processEvents();window=None
        assert len(rows)==43 and len(windows)==2 and not errors and len(pngs)==(0 if args.phase=='gold' else 4)
        assert source_map(root)==expected and guard_path.read_bytes()==guard_raw
        for name,want in extra.items():assert sha((root/name).read_bytes())==want
        receipt.update(passed=True,workflow_complete=True)
    except BaseException as error:receipt['failure']=error_record(error)
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
        receipt['actual_numeric_calls']=len(calls)
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'windows':len(windows),'snapshots':len(rows),
                      'native_records':len(records),'elapsed_seconds':receipt['elapsed_seconds']}))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
