"""Source-only public plan writer; never import or execute project code."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
V1=Path('/workspace/.continuation/p2-account-cache-candidate093-v1/candidate')
V2=Path('/workspace/.continuation/p2-account-cache-candidate093-v2/candidate')
CONTRACT=Path('/workspace/.continuation/p2-account-cache-design093-independent-v1/execution-contract.json')
def descriptor(p):
    data=p.read_bytes()
    return {'source_path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def save(name,obj):
    p=HERE/name
    assert not p.exists(),('new source preparation only',str(p))
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2 if name!='account-window-plan093.json' else None,allow_nan=False)+'\n',encoding='utf-8')
    return descriptor(p)

profiles=json.loads((ROOT/'rouge/data/operator-profiles.json').read_text())['operators']
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_text())
for key,value in catalog['operators'].items():profiles[key]={**profiles[key],**value}
assert len(profiles)==431 and len(catalog['operators'])==32
assert all(p['skills'] and any(s.get('unlock_elite',i)<=0 for i,s in enumerate(p['skills'])) for p in (profiles[k] for k in catalog['operators']))
assert not profiles['char_285_medic2']['skills'] and 'char_285_medic2' not in catalog['operators']
assert 'char_123_fang' not in catalog['operators']
assert (V1/'rouge/app.py').read_bytes()==(V2/'rouge/app.py').read_bytes()
assert hashlib.sha256((V2/'rouge/app.py').read_bytes()).hexdigest()=='3dd6810e3398471ddb6dbe9545824c7b92ba4d141fc23f889287a8044670a48f'
assert hashlib.sha256((V2/'rouge/account_cache.py').read_bytes()).hexdigest()=='17250d93fa3932fc6233bc5b8dd8d1a17d76a283feee5fe694ffebe530ecb5d5'
app_source=(V2/'rouge/app.py').read_text()
app_tree=ast.parse(app_source)
methods={n.name:n for n in ast.walk(app_tree) if isinstance(n,ast.FunctionDef)}
assert 'sample_received' in methods and 'sample_received_account_summary' not in methods
assert all(name in methods for name in ('apply_operator_observation','apply_run_observation','select_operator','current_operator_state','account_training_status'))
contract=json.loads(CONTRACT.read_text())
assert len(contract['minimal_execution_constraints'])==12

def record(owner,*,captured=100,fields=None,ranks=None,scope='operator_profile',**extra):
    if fields is None:
        fields=({'elite':1,'level':40,'trust':70,'potential':2,'module_id':None,'module_level':0,'selected_skill':2}
                if owner=='kaltsit' else {'elite':2,'level':60,'trust':35,'potential':1,'module_id':None,'module_level':0,'selected_skill':3})
    if ranks is None:ranks={'1':7,'2':7} if owner=='kaltsit' else {'1':7,'3':9}
    return {'id':owner,'name':profiles[owner]['name'],'scope':scope,'fields':fields,'skill_ranks':ranks,
            'sources':{'level':'public-synthetic-old-093'},'field_times':{'level':100,'elite':90},
            'skill_times':{str(k):100 for k in ranks},'captured_at':captured,**extra}
def step(id,action,**kw):return {'id':id,'action':action,**kw}
cases=[]
def corrupt_case(id,raw=None,decoded=None,issue=None,load_issue=None):
    rows=[step('startup','startup',preserve=True,issue_owner='kaltsit' if issue else None,issue=issue,load_issue=load_issue),
          step('browse-good','select',owner='silverash',preserve=True),
          step('recover-valid-id','observe',operator=record('kaltsit'),captured_at=200,preserve=True,
               expected_fields=record('kaltsit')['fields'],cleared_issue='kaltsit')]
    if id=='malformed-json':rows[0]['screenshot']='wine-account-isolation-093.png'
    cases.append({'id':id,'disk_raw':raw,'disk_decoded':decoded,'protect_original_all_steps':True,'steps':rows})

corrupt_case('malformed-json',raw='{',load_issue='账号档案未能读取')
for name,value in [('null',None),('false',False),('zero',0),('string','public'),('list',[])]:
    corrupt_case('root-'+name,raw=json.dumps(value),load_issue='账号档案结构不可用')
bad=[]
for key,value,label in [('fields',None,'培养字段'),('skill_ranks',None,'技能等级'),('sources',[],'读取来源'),
                        ('field_times',False,'字段读取时间'),('skill_times',0,'技能读取时间'),
                        ('captured_at',None,'读取时间'),('captured_at',True,'读取时间'),('captured_at',1e300,'读取时间'),
                        ('invalid_fields',[{'unhashable':'public'}],'培养字段读取状态'),
                        ('invalid_skill_ranks',None,'技能读取状态'),('missing_fields',[123],'未读取字段状态')]:
    current=record('kaltsit');current[key]=value
    suffix={'NoneType':'null','bool':'bool','float':'conversion-failing','list':'list','int':'number'}[type(value).__name__]
    bad.append((key+'-'+suffix,current,label))
none_level=record('kaltsit');none_level['fields']['level']=None
bad += [('known-level-none',none_level,'等级'),
        ('record-none',None,'记录结构'),
        ('identity-missing',{'fields':{}},'干员身份'),
        ('identity-mismatch',{'id':'silverash','fields':{}},'干员身份')]
bad_rank=record('kaltsit');bad_rank['skill_ranks']['2']='bad'
bad += [('active-bad-rank',bad_rank,'第2技能等级'),('foreign-run-scope',record('kaltsit',scope='run',advanced=True,recruitment_kind='emergency_hire'),'本局来源')]
for id,value,issue in bad:corrupt_case(id,decoded={'kaltsit':value,'silverash':record('silverash')},issue=issue)
cases.append({'id':'unbrowsed-bad-sibling','disk_decoded':{'kaltsit':record('kaltsit'),'silverash':none_level | {'id':'silverash'}},
    'protect_original_all_steps':True,'steps':[
        step('startup-good-with-unbrowsed-bad','startup',preserve=True,issue_owner='silverash',issue='等级'),
        step('good-observation-before-bad-browse','observe',operator={'id':'kaltsit','scope':'operator_profile','fields':{'level':45}},captured_at=120,preserve=True),
        step('browse-isolated-sibling','select',owner='silverash',preserve=True,expected_fields={}),
        step('recover-sibling-in-memory','observe',operator=record('silverash'),captured_at=200,preserve=True,cleared_issue='silverash',expected_fields=record('silverash')['fields'])]})

future_id='char_public_future_093'
future={'opaque':[None,False,0,{'public':'unknown-not-consumed'}]}
clean=record('silverash',old_extra='original producer drops this extra')
cases.append({'id':'clean-producer-and-browse','disk_decoded':{'silverash':clean,future_id:future},'unknown_id':future_id,'steps':[
    step('startup','startup',preserve=False),step('confirmed-silver','select',owner='silverash',expected_fields=clean['fields']),
    step('manual-numerical','button',numeric=True),
    step('valid-union','observe',operator={'id':'silverash','scope':'account','fields':{'level':65,'trust':55},'skill_ranks':{3:10},'sources':{'trust':'public-new-093'}},captured_at=120,merge='clean-first',expect_account_changed=True),
    step('older-time-rejected','observe',operator={'id':'silverash','scope':'account','fields':{'level':20}},captured_at=119,unchanged_account=True),
    step('equal-time-accepted','observe',operator={'id':'silverash','scope':'account','fields':{'level':66}},captured_at=120,expect_account_changed=True),
    step('source-only-no-save','observe',operator={'id':'silverash','scope':'account','fields':{},'sources':{'opaque-new':{'public':'uninterpreted'}}},captured_at=130,unchanged_account_file=True),
    step('local-level-override','level',value=20,expected_level=20,expected_override=True),
    step('same-id-observe-preserves-local-level','observe',operator={'id':'silverash','scope':'account','fields':{'level':70}},captured_at=140,expected_level=20,expected_override=True),
    step('restore-read-level','restore_level',expected_level=70,expected_override=False),
    step('manual-browse-other','select',owner='kaltsit'),
    step('repeat-observed-id-does-not-steal-browse','observe',operator={'id':'silverash','scope':'account','fields':{}},captured_at=150,expected_owner='kaltsit'),
    step('new-observed-identity-followed','observe',operator=record('char_123_fang',fields={'elite':1,'level':25,'trust':55,'potential':1,'module_id':None,'module_level':0},ranks={'1':7}),captured_at=160,expected_owner='char_123_fang',shape='unimplemented'),
    step('return-good-recovers','select',owner='silverash',expected_level=70,expected_override=False),
    step('timing-whitespace','timing',text='   ',numeric=True),step('timing-empty-object','timing',text='{}',numeric=True),
    step('timing-invalid-syntax','timing',text='{',error='战斗时序情景需要合法JSON对象。',numeric_error=False),
    *[step('timing-top-'+n,'timing',text=json.dumps(v),error='战斗时序情景需要JSON对象。',numeric_error=False) for n,v in [('null',None),('false',False),('zero',0),('list',[])]],
    step('timing-valid-target','timing',text='{"target_windows":[[0,5],[8,20]]}',numeric=True),
    step('timing-empty-target','timing',text='{"target_windows":[]}',numeric=True),
    step('timing-restore-valid','timing',text='{}',numeric=True),
    step('inactive-relic-stale-syntax','relic_context',text='{',numeric=True,expected_relic_context={}),
    step('manual-relic-select-needed','relic',rid='rogue_6_relic_cargo_2',checked=True,error='藏品测试条件需要合法JSON对象。',numeric_error=False),
    step('active-relic-empty-object','relic_context',text='{}',numeric=True),
    step('active-relic-valid-needed','relic_context',text='{"parts_count":3,"unrelated":false}',numeric=True,expected_relic_context={'parts_count':3}),
    step('active-relic-non-object','relic_context',text='null',error='藏品测试条件需要JSON对象。',numeric_error=False),
    step('active-relic-return-valid','relic_context',text='{"parts_count":3}',numeric=True),
    step('inactive-again','relic',rid='rogue_6_relic_cargo_2',checked=False,numeric=True,expected_relic_context={})]})
cases.append({'id':'genuinely-missing-normal-save','disk_missing':True,'steps':[
    step('startup','startup',preserve=False),step('new-valid-normal-save','observe',operator=record('silverash'),captured_at=200,expect_account_created=True),
    step('older-new-record-rejected','observe',operator={'id':'silverash','fields':{'level':20}},captured_at=199,unchanged_account=True)]})
cases.append({'id':'historical-partial-and-ignored-aliases','disk_decoded':{'kaltsit':{'id':'kaltsit','scope':'account','fields':{'trust':True,'module_id':None,'module_level':['ignored-public']}}},'steps':[
    step('startup-partial','startup',preserve=False,expected_fields={'trust':True,'module_id':None,'module_level':['ignored-public']}),
    step('natural-overview','overview',shape='overview'),
    step('natural-no-skill-profile','select',owner='char_285_medic2',shape='unimplemented-no-skill'),
    step('natural-unimplemented-with-skill','select',owner='char_123_fang',shape='unimplemented'),
    step('partial-preview-return','select',owner='kaltsit',numeric=True)]})
run_only={'recruitment_kind':'emergency_hire','advanced':True,'run_confirmed_fields':['elite'],
          'char_buff_ids':['public-run-only-unconsumed'],'char_buffs_complete':True,'char_buff_absent_ids':[],'char_buff_pending_ids':[]}
cases.append({'id':'account-run-only-extra-suppression','disk_decoded':{'kaltsit':record('kaltsit',**run_only)},'steps':[
    step('startup-sanitized','startup',preserve=False,sanitized=True),
    step('sample-summary-sanitized','sample',operator=record('kaltsit',**run_only),sanitized=True),
    step('manual-after-summary','button',numeric=True,sanitized=True)]})

def chain(label):
    value={'sentinel':'public-093-'+label,'values':[None,False,0,'原值']}
    for _ in range(500):value={'next':value}
    return value
deep_old=record('kaltsit',extra_metadata=chain('old'),old_extra='drop-under-original-producer-merge')
deep_old['sources']['opaque']=chain('source-old')
cases.append({'id':'B1-deep-ignored-opaque','disk_decoded':{'kaltsit':deep_old},'steps':[
    step('startup-500-layer-extra','startup',preserve=False,chain_label='old'),
    step('shallow-view-top-level-only','view_top',chain_label='old'),
    step('ordinary-producer-deep-save','observe',operator={'id':'kaltsit','scope':'operator_profile','fields':{'level':45},'sources':{'new':'public'},'extra_metadata':chain('new')},captured_at=200,chain_label='new',deep_merge=True,expect_account_changed=True),
    step('deep-safe-summary','sample',operator={'id':'kaltsit','scope':'operator_profile','fields':{'level':46},'extra_metadata':chain('new')},chain_label='new')]})
masked=record('silverash',fields={'elite':0,'level':40,'trust':55,'potential':2},ranks={'1':7,'3':'bad'},invalid_skill_ranks=['3'],old_extra='old masked public')
masked['sources']={'old-only':'public'}
cases.append({'id':'B2-masked-old-rank-incoming-only-recovery','disk_decoded':{'silverash':masked},'steps':[
    step('startup-masked-locked-old','startup',preserve=False),step('browse-lawful-masked-old','select',owner='silverash',preserve=False),
    step('new-elite-unlocks-unsafe-old-union','observe',operator={'id':'silverash','scope':'operator_profile','fields':{'elite':2},'sources':{'elite':'new-public'}},captured_at=200,preserve=True,incoming_only=True,cleared_issue='silverash',screenshot='wine-account-recovery-093.png'),
    step('older-time-after-recovery-rejected','observe',operator={'id':'silverash','scope':'operator_profile','fields':{'elite':1}},captured_at=199,preserve=True,unchanged_account=True)]})
run_member=record('silverash',fields={'elite':1,'level':25,'trust':60,'potential':2,'module_id':None,'module_level':0,'selected_skill':1},ranks={'1':7,'2':7},scope='run',advanced=False,recruitment_kind='non_emergency',public_metadata={'source':'real-RunState.apply-public-fixture'})
run_member.pop('captured_at');run_member.pop('field_times');run_member.pop('skill_times')
cases.append({'id':'real-run-precedence-and-stable-account-reference','disk_decoded':{'silverash':{'id':'silverash','fields':{'level':None}},'kaltsit':record('kaltsit')},'protect_original_all_steps':True,'steps':[
    step('startup-preserves-bad-reference','startup',preserve=True),
    step('real-run-apply-member','run',observed={'operators':[run_member],'selected_operator':'silverash','crew_count':None},run_update=True,preserve=True,expected_fields=run_member['fields'],screenshot='wine-account-run-priority-093.png'),
    step('recover-account-without-mutating-run','observe',operator=record('silverash',fields={'elite':2,'level':60,'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':3},ranks={'3':10}),captured_at=200,preserve=True,cleared_issue='silverash',expected_fields=run_member['fields'],run_precedence=True),
    step('account-only-toggle','run_training',value=False,preserve=True,expected_level=60),
    step('run-priority-toggle-back','run_training',value=True,preserve=True,expected_level=25,run_precedence=True),
    step('run-local-level-override','level',value=20,preserve=True,expected_level=20,expected_override=True,run_precedence=True),
    step('restore-real-run-level','restore_level',preserve=True,expected_level=25,expected_override=False,run_precedence=True),
    step('browse-good-keeps-real-run','select',owner='kaltsit',preserve=True),
    step('browse-run-back','select',owner='silverash',preserve=True,expected_level=25,run_precedence=True)]})

plan={'format_version':1,'status':'PENDING_SOURCE_ONLY_PUBLIC_WINDOW_WORKFLOW_ACTUAL_ROOT_GUARD_REQUIRED',
      'base_commit':'f509d186e501bfcfd042e45b46e398ec756840ec',
      'candidate_v2_app':descriptor(V2/'rouge/app.py'),'candidate_v2_helper':descriptor(V2/'rouge/account_cache.py'),
      'contract':descriptor(CONTRACT),'cases':cases,'profiles_count':len(profiles),'implemented_count':len(catalog['operators']),
      'fixture_scope':'Only constructed public account bytes and incoming observations in independent fresh MainWindows; real RunState class/apply; no private state, OCR/game capture or chat.',
      'codec':'flat-typed-graph-v1 with iterative encode/decode/JSON clone; lossless inverse validation during actual root run, never recursive deepcopy of 500-layer opaque extras.',
      'coverage_limits':['No legal current implemented profile naturally reaches implemented+skillNone branch. Lancet-2 naturally covers skillNone/rank no-skill and earlier unimplemented branch. No cleared skill widget or negative elite fixture.',
                         'Target-platform localtime rejection of finite1e300 is an actual runtime check, not a claimed preparation execution.',
                         'B1/B2 assertions express root-approved v2 contract; v1 is not executable approval and final must source-check actual v2 before binding.'],
      'expected_PNGs':['wine-account-isolation-093.png','wine-account-run-priority-093.png','wine-account-recovery-093.png'],
      'constraints':[row['id'] for row in contract['minimal_execution_constraints']],
      'prep_calls':{'project_imports':0,'API':0,'helpers':0,'formatter':0,'tests':0,'Qt':0,'Wine':0,'private_reads':0,'tracked_writes':0}}
plan['counts']={'fresh_MainWindows':len(cases),'planned_states':sum(len(c['steps']) for c in cases),
                'manual_button_requests':sum(s['action']=='button' for c in cases for s in c['steps']),
                'different_declared_JSON_error_states':sum('error' in s for c in cases for s in c['steps']),
                'success_PNGs':3,'explicit_three_text_requests':'3 per actual selected numerical state, measured rather than guessed'}
inputs=[CONTRACT,V1/'rouge/app.py',V1/'rouge/account_cache.py',V2/'rouge/app.py',V2/'rouge/account_cache.py',ROOT/'rouge/catalog.py',ROOT/'rouge/run_state.py',ROOT/'rouge/branch_choice.py',
        ROOT/'rouge/operator_summary.py',ROOT/'rouge/offline_scope.py',ROOT/'rouge/relics.py',ROOT/'rouge/data/operator-profiles.json',ROOT/'rouge/data/catalog.json',ROOT/'rouge/data/relic-mechanics.json']
qualification={'format_version':1,'status':'SOURCE_ONLY_PLAN_QUALIFIED_V2_BYTES_EXACT_RUNTIME_UNRUN_ACTUAL_ROOT_BIND_PENDING','sources':[descriptor(p) for p in inputs],
               'app_method_lines':{name:[methods[name].lineno,methods[name].end_lineno] for name in ('sample_received','apply_operator_observation','apply_run_observation','select_operator','current_operator_state','account_training_status','update_operator','calculate')},
               'actual_sample_interface':'events.sample.emit((np.zeros((8,8,3),dtype=np.uint8), public observation)); no invented sample_received_account_summary method',
               'validity_checks':'Profiles/catalog raw JSON top-level merge only; no catalog/profiles/function execution. Real RunState incoming id/fields/scope and runtime timestamp; no fixture replacement of RunState or preserve flag.',
               'source_reader_subagent':'window093_source_flow read-only qualification, not independent final approval',
               'pending_v2_issues':['B1 shallow opaque extra preservation, no recursive clone requirement','B2 unsafe old union protection with incoming-only memory recovery'],
               'counts':plan['counts'],'prep_calls':plan['prep_calls']}
print(json.dumps({'plan':save('account-window-plan093.json',plan),'source_qualification':save('source-qualification093.json',qualification),'counts':plan['counts'],'project_calls':0}))
