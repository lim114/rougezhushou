"""Read-only source/receipt audit plus strict full public comparisons."""
import ast
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-token-count-report-audit-063')
ROOT=Path('/workspace/rougezhushou')
BASE=AUTHOR/'baseline61';DRAFT=AUTHOR/'draft63'
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',', ':'),allow_nan=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def metrics(out,section):
    block=next(b for b in out['result']['report']['sections'] if b['id']==section)
    return {m['key']:m['value'] for m in block['metrics']}
def diff(a,b,path=''):
    if type(a) is not type(b):return [{'path':path,'before':a,'after':b}]
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        return [d for k in a for d in diff(a[k],b[k],path+'/'+str(k))]
    if isinstance(a,list):
        assert len(a)==len(b),path
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in diff(x,y,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'before':a,'after':b}]

patch=AUTHOR/'section63.patch';sourcepatch=AUTHOR/'source-count63.patch'
assert sha(patch)=='84277737d996fedd9c91307421a2ac2a1d3f3de64d3f49f4ecefab860c75aa12'
assert sha(sourcepatch)=='14f39e9c916fb9a9dc1e82c1fa2151a48483ecc815f379e82c7831e7828b85ee'
assert sha(DRAFT/'rouge/reporting.py')=='059697171e16a3959241a06e01290117155530d5a4e50bbb4339ce1e2b4ac79b'
insert="    if op=='char_110_deepcl' and type(scenario.get('summon_count')) is str:\n        # Combat.plan already validated this finite, nonnegative integer string.\n        scenario={**scenario,'summon_count':int(float(scenario['summon_count']))}\n"
b=(BASE/'rouge/reporting.py').read_text();d=(DRAFT/'rouge/reporting.py').read_text()
assert d.count(insert)==1 and d.replace(insert,'')==b
manifest={}
for package in (BASE,DRAFT):
    manifest[package.name]={p.relative_to(package).as_posix():sha(p) for p in sorted((package/'rouge').rglob('*'))
                           if p.is_file() and p.suffix in ('.py','.json')}
assert manifest['baseline61'].keys()==manifest['draft63'].keys()
changed=[p for p in manifest['baseline61'] if manifest['baseline61'][p]!=manifest['draft63'][p]]
assert changed==['rouge/reporting.py']
engine=(DRAFT/'rouge/operator_engine.py').read_text()
engine_ast=ast.parse(engine)
combat=next(x for x in engine_ast.body if isinstance(x,ast.ClassDef) and x.name=='Combat')
option=next(x for x in combat.body if isinstance(x,ast.FunctionDef) and x.name=='option')
author61_ast=ast.parse(Path('/workspace/.continuation/p2-integer-option-audit-061/draft/rouge/operator_engine.py').read_text())
author61_combat=next(x for x in author61_ast.body if isinstance(x,ast.ClassDef) and x.name=='Combat')
author61_option=next(x for x in author61_combat.body if isinstance(x,ast.FunctionDef) and x.name=='option')
assert ast.dump(option,include_attributes=False)==ast.dump(author61_option,include_attributes=False)
assert "'first_tick_seconds':None,'actual_tick_times_seconds':None" in engine
assert "'native_attachment_verified':False,'clock_verified':False" in engine
source=load(AUTHOR/'source-closure.json');raw={};fresh=[]
for name,receipt in source['fresh_pinned_raw_tables'].items():
    p=ROOT/receipt['path'];assert p.stat().st_size==receipt['bytes'] and sha(p)==receipt['sha256']
    raw[name]=load(p);fresh.append({'table':name,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
def select(selector):
    names=re.findall(r'([^\.\[\]]+)|\[(\d+)\]',selector)
    first=names[0][0];value=raw[first]
    for key,index in names[1:]:value=value[int(index)] if index else value[key]
    return value
skillchecks=[]
for row in source['raw_skill_records']:
    original=select(row['selector']);binding=select(row['binding_selector'])
    assert canon({b['key']:b['value'] for b in original['blackboard']})==canon(row['blackboard'])
    assert original['duration']==row['duration_parameter_seconds']
    assert original['name']==row['name'] and original['description']==row['description']
    assert canon(original['spData'])==canon(row['sp_data'])
    assert binding['unlockCond']==row['unlock_condition']
    skillchecks.append({'selector':row['selector'],'binding_selector':row['binding_selector'],'match':True})
tokenchecks=[]
for row in source['raw_token_cultivation_records']:
    original=select(row['selector'])
    assert canon({key:original[key] for key in row['values']})==canon(row['values'])
    tokenchecks.append({'selector':row['selector'],'matched_fields':list(row['values']),
                        'projection_match':True,'raw_other_fields_not_in_receipt':sorted(set(original)-set(row['values']))})
historical=[]
for item in source['archived_evidence_fresh_file_hashes'].values():
    p=ROOT/item['path'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
    historical.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'meaning':'Archived receipt, not a fresh raw/native proof'})

base=load(HERE/'public-baseline063.json');draft=load(HERE/'public-draft063.json')
assert base['source_drift']==draft['source_drift']==[]
assert base['source_before']==manifest['baseline61'] and draft['source_before']==manifest['draft63']
left={r['id']:r for r in base['records']};right={r['id']:r for r in draft['records']};assert left.keys()==right.keys()
counts=Counter();changes=[];textpairs=[];hp=[]
for label,old in left.items():
    new=right[label]
    assert canon(old['input'])==canon(new['input'])
    a=old['outcome'];z=new['outcome']
    if old['group']=='legal_text':
        ref=right[old['equivalent']]['outcome']
        assert z['status']=='returned' and canon(z)==canon(ref),label
        textpairs.append({'id':label,'integer_control':old['equivalent'],'strict_full_json_equal':True})
        if a['status']=='raised':
            assert a['exception']['type']=='TypeError' and old['input']['skill']==1,label
            counts['S1_original_report_TypeError_repaired']+=1
        else:
            assert old['input']['skill']==2,label
            aq=deepcopy(a['result']);zq=deepcopy(z['result']);aq.pop('report');zq.pop('report')
            assert canon(aq)==canon(zq),label
            differences=diff(a,z)
            for entry in differences:
                assert entry['path'].startswith('/result/report/sections/') and entry['path'].endswith('/value')
                assert type(entry['before']) is str and type(entry['after']) is int
                assert int(float(entry['before']))==entry['after']
            changes.append({'id':label,'differences':differences})
            counts['S2_only_report_string_to_int']+=1
    else:
        assert canon(a)==canon(z),label
        counts['entire_outcome_strictly_unchanged']+=1
        if z['status']=='raised':counts['old_errors_preserved']+=1
        else:counts['old_returns_preserved']+=1
    if new['group']=='inactive':
        assert canon(z)==canon(right[new['equivalent']]['outcome']),label
        assert canon(a)==canon(left[new['equivalent']]['outcome']),label
        counts['inactive_strict_absent_equivalent']+=1
    if label.startswith('invalid-bool'):
        assert z['exception']=={'type':'ValueError','message':'summon_count需要范围内的有限非负整数。'},label
        counts['section61_bool_rejections_preserved']+=1
    if label.startswith(('float','int0','int1','int2')) and z['status']=='returned':
        incoming=old['input']['summon_count'];sm=metrics(z,'summons');tm=metrics(z,'relic_token_token_10001_deepcl_tentac')
        assert type(sm['summon_count']) is type(incoming) and type(tm['model_count']) is type(incoming),label
        counts['raw_int_float_metric_dtypes_preserved']+=1
    if label.startswith('obs-text'):
        assert metrics(z,'regeneration')['per_token_rate']==70 and metrics(z,'regeneration')['all_tokens_rate']==140
    if new['synthetic'] and z['status']=='returned':
        token=next(x for x in z['result']['relic_token_stats'] if x['id']=='token_10001_deepcl_tentac')
        stage=old['input']['module_level']
        if stage>1:
            assert token['hp'] is None and token['regeneration_rate'] is None
            assert token['module_reference']['hp_composition_pending'] is True and z['result']['complete'] is False
        else:
            assert token['hp'] is not None and token['regeneration_rate'] is not None
            assert token['module_reference']['hp_composition_pending'] is False
        if old['input']['skill']==1:assert metrics(z,'regeneration')['all_tokens_rate']==140
        hp.append({'id':label,'stage':stage,'hp_pending':token['module_reference']['hp_composition_pending'],
                   'synthetic_guard_only':True,'public_output_integer_text_equal':True})

# Independently recompare completed author JSON without repeating its expensive public matrix.
ab=load(AUTHOR/'validation-after61/baseline61.json');ad=load(AUTHOR/'validation-after61/draft63.json')
author_counts=Counter()
assert ab['source_drift']==ad['source_drift']==[]
assert ab['source_sha256']==manifest['baseline61'] and ad['source_sha256']==manifest['draft63']
for old,new in zip(ab['records'],ad['records'],strict=True):
    assert old['id']==new['id'] and canon(old['input'])==canon(new['input'])
    if old['status']=='raised':
        if new['status']=='raised':
            assert canon(old['exception'])==canon(new['exception']);author_counts['old_errors_unchanged']+=1
        else:
            assert old['exception']['type']=='TypeError' and type(old['input'].get('summon_count')) is str
            assert old['input']['operator']=='char_110_deepcl' and old['input']['skill']==1
            author_counts['S1_report_TypeError_repaired']+=1
    else:
        assert new['status']=='returned'
        if canon(old['result'])==canon(new['result']):author_counts['whole_output_unchanged']+=1
        else:
            assert type(old['input'].get('summon_count')) is str and old['input']['skill']==2
            ao=deepcopy(old['result']);az=deepcopy(new['result']);ao.pop('report');az.pop('report')
            assert canon(ao)==canon(az)
            for entry in diff(old['result'],new['result']):
                assert entry['path'].startswith('/report/sections/') and entry['path'].endswith('/value')
                assert type(entry['before']) is str and type(entry['after']) is int
                assert int(float(entry['before']))==entry['after']
            author_counts['S2_report_string_to_int_only']+=1
        if type(old['input'].get('summon_count')) in (int,float):
            assert canon(old['result'])==canon(new['result'])
            author_counts['numeric_output_strictly_unchanged']+=1
tests=load(HERE/'tests-draft063.json');assert tests['passed'] and tests['methods_run']==31 and not tests['skips']
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),
    'conclusion':'PASS: narrow built-in string report copy; no unresolved independent blocker',
    'source_scope':'baseline61 is fixed c3ccf25 plus exact accepted section61 option method; preserves Shu60; root current integration is separate',
    'patch_sha256':sha(patch),'source_patch_sha256':sha(sourcepatch),
    'source_files_each':len(manifest['baseline61']),'source_change_paths':changed,
    'source_manifest':manifest,'exact_section61_option_AST_match':True,
    'Shu60_unknown_clock_fields_retained':True,
    'fresh_local_raw_rehash':fresh,'skill_selector_checks':skillchecks,'token_selector_checks':tokenchecks,
    'archived_receipts_rehashed':historical,'raw_module_tables_not_fresh_revalidated':True,
    'independent_pairs':len(left),'independent_public_calls':len(left)*2,'strict_dtype_sensitive_JSON':True,
    'independent_counts':dict(counts),'S2_report_only_changes':changes,'legal_text_int_pairs':textpairs,
    'synthetic_HP_guard_observations':hp,
    'author_completed_pairs_independently_recompared':len(ab['records']),'author_recomparison_counts':dict(author_counts),
    'author_recalculation_performed':False,'test_receipt':tests,
    'preparation_failures_retained':[
        {'path':'tests063-preparation.log','cause':'Script requested absent Shu60 test before executing any methods; corrected to real 068/069 neighbors'},
        {'path':'review063-preparation.log','cause':'Review script asserted a clock field name absent from actual source; corrected using displayed actual dictionary'},
        {'path':'review063-preparation2.log','cause':'Review script still requested absent native clock name; actual source clock_verified/native_attachment_verified pair now checked'},
        {'path':'review063-preparation3.log','cause':'Source receipt stores selected token parameters, not all raw attribute flags; corrected to strict projection, all omitted raw keys listed'}],
    'root_tracked_edits':0,'author_draft_edits':0,'Wine_executed':False,'actual_GUI_executed':False,
    'scope_limits':'Static original skill values and current public model only; archived native layering proof reused, no new game timing/stock/deployment/native proof'}
(HERE/'receipt063.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'independent_pairs':len(left),'counts':dict(counts),'author_pairs':len(ab['records']),
                  'author_counts':dict(author_counts),'source_change_paths':changed,'tests':31},ensure_ascii=False))
