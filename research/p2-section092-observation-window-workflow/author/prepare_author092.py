"""Actual91 Git source transport and static92 preparation; zero project execution."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
ACTUAL='59961ec3d633ac91b01014fb06b357d45e5979f7'
OLD=Path('/workspace/.continuation/p2-window-target-timing-flow-candidate')
BOUNDARY=Path('/workspace/.continuation/root-future092-preparation-attempt-boundary091.json')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def put(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def git(*args):return subprocess.run(['git',*args],cwd=REPO,check=True,stdout=subprocess.PIPE).stdout


assert git('rev-parse','HEAD').decode().strip()==ACTUAL
assert git('rev-parse','p2-section-091').decode().strip()==ACTUAL
assert not git('status','--short')
old_mf=(OLD/'public-candidate-manifest.json').read_bytes()
assert sha(old_mf)=='285a6ae53be573b6323f3144fd2a9ed26237162abe211faff7b0a5a1b772fece'
old=json.loads(old_mf);assert old['format_version']==1 and old['file_count']==49
assert old['total_bytes']==1048120 and isinstance(old['files'],list)
for item in old['files']:
    raw=(OLD/item['archive_path']).read_bytes()
    assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
(HERE/'old49-manifest-immutable.json').write_bytes(old_mf)
boundary=BOUNDARY.read_bytes();(HERE/'root-attempt-boundary091-immutable.json').write_bytes(boundary)

names=[]
for raw in git('ls-tree','-r','-z',ACTUAL).split(b'\0'):
    if not raw:continue
    meta,path=raw.split(b'\t',1);mode,kind,oid=meta.decode().split();rel=path.decode()
    if kind=='blob' and rel.startswith(('rouge/','tests/','scripts/')) and rel.endswith(('.py','.json')):
        names.append((rel,oid))
assert len(names)==730,len(names)
batch=subprocess.run(['git','cat-file','--batch'],cwd=REPO,input=('\n'.join(oid for _,oid in names)+'\n').encode(),
                     check=True,stdout=subprocess.PIPE).stdout
offset=0;inventory=[];blobs={}
for rel,oid in names:
    end=batch.index(b'\n',offset);header=batch[offset:end].decode().split();assert header[:2]==[oid,'blob']
    size=int(header[2]);raw=batch[end+1:end+1+size];assert batch[end+1+size:end+2+size]==b'\n'
    offset=end+2+size;assert (REPO/rel).read_bytes()==raw,rel
    inventory.append({'source_path':str(REPO/rel),'git_ref':ACTUAL,'git_blob':oid,'bytes':size,'sha256':sha(raw)})
    blobs[rel]=raw
assert offset==len(batch)
put('maintained730-git-and-current-hashes092.json',{'format_version':1,'actual_root_commit':ACTUAL,
     'scope':'Only maintained tracked rouge/tests/scripts .py/.json; research archived Python excluded',
     'files':inventory,'file_count':730,'total_bytes':sum(r['bytes'] for r in inventory),'all_current_bytes_equal_git':True,
     'whole_source_trees_copied':False,'project_calls':0})

leafs=('rouge/app.py','rouge/reporting.py','rouge/operator_engine.py','rouge/estimate.py','rouge/timing.py',
       'rouge/damage.py','rouge/catalog.py','rouge/condition_inputs.py','rouge/animation_reference.py',
       'rouge/data/timing-profiles.json','rouge/data/skill-impact-delays.json')
for rel in leafs:
    p=HERE/'actual91-leaves'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blobs[rel])
base_expected={'rouge/app.py':'fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143',
               'rouge/reporting.py':'b71dec77a7cb7ba88da7324982be6f4fd59c02ae8cd91bce44fe92f3546f5d01'}
products=[]
for rel,expected in base_expected.items():
    before=blobs[rel];prospective=(OLD/'prospective91-base'/rel).read_bytes();assert before==prospective and sha(before)==expected
    after=(OLD/'candidate'/rel).read_bytes();dest=HERE/'candidate'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(after)
    ast.parse(before.decode());ast.parse(after.decode())
    products.append({'path':rel,'baseline_path':str(HERE/'actual91-leaves'/rel),'candidate_path':str(dest),
                     'old_sha256':sha(before),'old_bytes':len(before),'new_sha256':sha(after),'new_bytes':len(after),
                     'actual91_equals_prospective_exact':True})
(HERE/'candidate-flow092.patch').write_bytes((OLD/'candidate-flow.patch').read_bytes())
(HERE/'old49-candidate-static-proof-immutable.json').write_bytes((OLD/'candidate-static-proof.json').read_bytes())
oldproof=json.loads((OLD/'candidate-static-proof.json').read_text())
assert sha((HERE/'candidate-flow092.patch').read_bytes())==oldproof['patch_sha256']
for product in products:
    match=next(p for p in oldproof['products'] if p['candidate_path'].endswith('/'+product['path']))
    assert match['old_sha256']==product['old_sha256'] and match['new_sha256']==product['new_sha256']
    assert match['exact_byte_inverse'] and match['whole_AST_inverse']
put('actual91-transport-proof092.json',{
    'format_version':1,'status':'ACTUAL91_TRANSPORT_AND_STATIC_SCOPE_PASS_ZERO_PROJECT_CALLS',
    'actual_root_commit':ACTUAL,'actual_root_tag':'p2-section-091','root_clean':True,
    'products':products,'only_changed_files':['rouge/app.py','rouge/reporting.py'],
    'app_only_function':'MainWindow.make_damage_tab','report_only_function':'build_report',
    'baseline730_hashes':'maintained730-git-and-current-hashes092.json',
    'unchanged':'Engine/estimate/timing/damage/prepare/conditionguards/calculate/update_operator/91 all other code and native semantics',
    'new_tests_or_registry':None,'original49_final_unchanged':True,
    'old_failure_boundary':{'source_path':str(BOUNDARY),'archive_path':'root-attempt-boundary091-immutable.json','bytes':len(boundary),'sha256':sha(boundary),
       'meaning':'Previous metadata objective third discovery step was partial; later leaf binding crossed stop boundary. Old4errors and all original packets remain historical immutable. New restart is explicitly authorized from actual91 commit/tag, not reset by exception labels.'},
    'new_API_helper_formatter_tests_Qt_Wine':0})

catalog=json.loads(blobs['rouge/data/catalog.json'])
projections=[]
for owner,skill in [('silverash',3),('char_196_sunbr',2),('kaltsit',3)]:
    p=catalog['operators'][owner];s=p['skills'][skill-1];assert s['unlock_elite']<=2 and p['phases'][2]['max_level']>=60
    rawlevel=s['levels'][9]
    projections.append({'owner':owner,'skill':skill,'E2_max_level':p['phases'][2]['max_level'],'unlock_elite':s['unlock_elite'],
                        'actual_rank10_level':rawlevel,'actual_E2_frame_interval':p['phases'][2]['frames'][-1]['interval'],
                        'source_catalog_sha256':sha(blobs['rouge/data/catalog.json'])})
assert next(p for p in projections if p['owner']=='char_196_sunbr')['actual_rank10_level']['duration']==30
cases=[]
for caseid,owner,skill,window,timing in [
    ('damage-zero','silverash',3,0.0,{}),
    ('finite-healing-zero','char_196_sunbr',2,0.0,{}),
    ('friendly-healing-enemy-zero','kaltsit',3,6.0,{'target_disappears_seconds':0}),
    ('finite-healing-long','char_196_sunbr',2,60.0,{})]:
    cases.append({'id':caseid,'input':{'operator':owner,'skill':skill,'skill_rank':10,'elite':2,'level':60,
                   'trust':100,'potential':1,'module_id':None,'module_level':0,'relic_ids':[],
                   'enemy_defense':0,'enemy_resistance':0,'healing_targets':1,'continuous_attacks':True,
                   'timing_mode':'frames','window_seconds':window,'timing':timing}})
put('public-inputs092.json',{'format_version':1,'status':'EXACT_FOUR_RISKS_FROZEN_BEFORE_API','cases':cases,
    'max_public_API_entries':8,'external_formatter_requests_per_successful_result':3,
    'max_external_formatter_requests':24,'internal_entries':'Measured by actual profiler, not derived from requests',
    'GUI_API_error_cases_added':False,'source_qualification':projections,
    'friendly_case_owner_change':'GummyS2 disarm10 makes window6 unsuitable positive consumption evidence; source-confirmed KaltsitS3 friendly path chosen, no fifth case/no native clock assertion',
    'public_case_scope':'Existing current models and qualified report.window_seconds projection only; no raw aliases/old error mirror tests'})
print(json.dumps({'status':'ACTUAL91_SOURCE_PREPARATION_PASS','maintained_files':730,'actual_leaves':len(leafs),
                  'cases':len(cases),'max_public_entries':8,'max_external_formatter_requests':24,'project_calls':0}))
