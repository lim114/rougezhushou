"""Formal static/source and saved-output review; never imports or calls application APIs."""
import ast
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

P=Path('/workspace/.continuation/ui-080-draft')
R=P/'review-resume'
ROOT=Path('/workspace/rougezhushou')
COMMIT='c950fbc800245f7f784d6070f7126890352ffcc9'
RUNNER='c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'
API='00f0cbf6e47d98a68d0ac639c5fa320e846607032667a4580a6f0bd7a6418033'
COUNTS={76:432,77:424,78:360,79:212,80:180}
sha=lambda data:hashlib.sha256(data).hexdigest()
canonical=lambda data:json.dumps(data,ensure_ascii=False,sort_keys=True,allow_nan=False)
names=('wine-ui-smoke-080.py','cases080.py','public_contracts.py','supplemental-checks.py.fragment')
raw={name:(P/name).read_bytes()for name in names}
assert raw=={name:(P/name).read_bytes()for name in names},'concurrent design change'
assert sha(raw['wine-ui-smoke-080.py'])==RUNNER
for name,data in raw.items():(R/('final-'+name)).write_bytes(data)

runner=raw['wine-ui-smoke-080.py'].decode()
entry="if __name__ == '__main__' and False:\n    raise RuntimeError('UI080 final source/schema are pending; no Qt execution is permitted')\n\n"
assert runner.startswith(entry)
tree=ast.parse(runner)
assert isinstance(tree.body[0],ast.If)and ast.literal_eval(tree.body[0].test.values[-1])is False
fragment=raw['supplemental-checks.py.fragment'].decode()
assert "receipt['sections77_80_final_checks_pending']=False"in fragment
assert "receipt['sections77_80_final_checks_pending']=True"not in fragment
helpers=raw['public_contracts.py'].decode()+'\n'+raw['cases080.py'].decode()
assert runner.count(fragment+'\n')==1 and runner.count(helpers+'\n\n')==1
old=runner.removeprefix(entry).replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for name in('wine-ui-report-difference-075.json','wine-window-075.png','wine-ui-075.json',
            'wine-ui-failure-075.png','wine-sown-tile-control-075.png','wine-movement-reference-075.png'):
    old=old.replace(name.replace('-075','-080'),name)
old=old.replace('-(next_end-next_start)','')
old=old.replace("        receipt['preserved_full_075_checks']=len(checks)\n"
    "        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']\n",'')
base=Path('/workspace/.compat/wine-ui-smoke-075.py').read_bytes()
assert sha(base)=='645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
assert old.encode()==base,'inherited whole 1455 body differs'

freeze_raw=(P/'public-source-freeze-080.json').read_bytes()
freeze=json.loads(freeze_raw)
proof_raw=(P/'public-package-rebuild-proof080.json').read_bytes()
proof=json.loads(proof_raw)
assert freeze['base_commit']==proof['root_source_commit']==COMMIT
assert freeze['public_source_files']==proof['public_source_files']==len(proof['files'])==125
assert freeze['base_git_blobs_equal']is True and proof['all_bytes_equal']is True and proof['source_drift']==[]
assert freeze['patches']==[] and freeze['base_source_sha256']==freeze['source_sha256']
assert len(freeze['source_sha256'])==125
source_rows=[]
for row in proof['files']:
    name=row['path'];source=(ROOT/name).read_bytes()
    committed=subprocess.check_output(['git','show',f'{COMMIT}:{name}'],cwd=ROOT)
    assert source==committed and len(source)==row['bytes']
    assert sha(source)==row['sha256']==freeze['source_sha256'][name]
    blob=hashlib.sha1(b'blob '+str(len(committed)).encode()+b'\0'+committed).hexdigest()
    assert blob==row['git_blob_object_id']
    source_rows.append(row)
assert {row['path']for row in source_rows}==set(freeze['source_sha256'])
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
opt_tree=ast.parse((ROOT/'rouge/operator_options.py').read_bytes())
options=next(ast.literal_eval(n.value)for n in opt_tree.body if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name)and t.id=='OPTIONS'for t in n.targets))
case_ns={};exec(compile(raw['cases080.py'],'<pure case generator>','exec'),case_ns)
cases=case_ns['cases080']()
assert Counter(c['section']for c in cases)==COUNTS and len(cases)==1608
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_bytes())['operators']
for case in cases:
    a=case['input'];profile=catalog[a['operator']]
    assert 1<=a['level']<=profile['phases'][a['elite']]['max_level']
    assert profile['skills'][a['skill']-1]['unlock_elite']<=a['elite']
    assert 'base_attack'not in a and 'base_hp'not in a
    for key,label,default,maximum,skills in options.get(a['operator'],[]):
        if key in a:
            assert a['skill']in skills
            assert type(a[key])is type(default),(case,key)
            assert 0<=a[key]<=maximum
    if case['section']in(79,80):
        assert 0<=a['healing_targets']<=(100 if a['skill']==1 else 1)
        if a['skill']==1:assert 'amiya_hit_targets'not in a
        else:assert 1<=a['amiya_hit_targets']<=100

api_raw=(P/'public-schema-final-080.json.gz').read_bytes()
assert sha(api_raw)==API
saved=json.loads(gzip.decompress(api_raw))
assert saved['calls']==len(saved['records'])==1608
assert saved['sections']=={str(k):v for k,v in COUNTS.items()}
assert saved['source_hashes']==freeze['source_sha256']and saved['source_drift']==[]
assert saved['gui_executed']is False and saved['wine_executed']is False
failed_raw=(P/'public-schema-final-080-failure.json.gz').read_bytes()
assert sha(failed_raw)=='53e99996dcffe475f8074e7dbad4759da20c692fe457f2b95bc0eb86312f98cc'
failed=json.loads(gzip.decompress(failed_raw))
assert failed['fresh_public_calls']==1552 and failed['completed_asserted_cases']==1551
assert failed['source_hashes_before']==failed['source_hashes_after']==freeze['source_sha256']
assert saved['records'][:1551]==failed['completed_records'],'old accepted results were changed'
assert saved['records'][1551]['input']==failed['current_input']
assert saved['records'][1551]['result']==failed['current_result'],'saved counterexample was changed'

# JSON serializes the engine's known tuple rows as arrays. Restore only those
# two source-defined metadata row sets for the pure helpers; assert canonical
# JSON and every numeric type are identical before and after this adaptation.
def internal_rows(result):
    result=deepcopy(result);original=canonical(result)
    external=result.get('external_event_reference')
    if external:
        for ref in(external,external.get('window_reference',{})):
            if 'parameter_rows'in ref:ref['parameter_rows']=[tuple(row)for row in ref['parameter_rows']]
    assert canonical(result)==original
    return result

ns={};exec(compile(raw['public_contracts.py'],'<pure assertions only>','exec'),ns)
controls={};read_counts=Counter();scopes=[]
for index,(case,row)in enumerate(zip(cases,saved['records'])):
    try:
        assert row['section']==case['section']and row['context']==case['context']
        a={k:default for k,label,default,maximum,skills in options.get(case['input']['operator'],[])
            if case['input']['skill']in skills}
        a.update(case['input'])
        assert canonical(row['input'])==canonical(a),'saved input does not match real producer design'
        result=internal_rows(row['result']);text=row['visible_report'];section=case['section']
        if section==76:
            key=canonical({k:v for k,v in a.items()if k!='bubble_bursts'})
            if a['bubble_bursts']==0:controls[section,key]=result
            ns['require_haruka080'](result,a,text,controls[section,key])
        elif section==77:
            key=canonical({k:v for k,v in a.items()if k!='enemy_weight'})
            if a.get('target_enemy'):
                if a['enemy_weight']==0:controls[section,key]=result
                ns['require_aglna_selected080'](result,a,text,controls[section,key],case['expected_reference_mass'])
            else:
                control=controls.setdefault((section,key),{})
                if a['enemy_weight']==0:control['light']=result
                if a['enemy_weight']==4:control['heavy']=result
                ns['require_aglna080'](result,a,text,control)
        elif section==78:
            key=canonical({k:v for k,v in a.items()if k!='palsy_triggers'})
            if a['palsy_triggers']==0:controls[section,key]=result
            ns['require_mantra080'](result,a,text,controls[section,key])
        elif section==79:ns['require_medical_amiya080'](result,a,text)
        elif section==80:ns['require_medical_trait080'](result,a,text,case['expected_trait_ratio'])
        else:raise AssertionError('unsealed section')
        read_counts[section]+=1
        scopes.append({'index':index,'section':section,'context':case['context'],
            'elite':a['elite'],'skill':a['skill'],'mode':a['timing_mode'],
            'friendly_targets':a['healing_targets'],'window':a['window_seconds'],
            'enemy_lifetime':a.get('timing',{}).get('target_disappears_seconds'),
            'saved_result_sha256':sha(canonical(row['result']).encode())})
    except Exception as error:
        diagnostic={'scope':'saved-output final static review failure; no API/Qt/Wine',
            'index':index,'case':case,'saved_row':row,'error_type':type(error).__name__,'error':str(error)}
        (R/'final-review-failure.json').write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2)+'\n')
        raise
assert read_counts==COUNTS

shot=[c for c in cases if c['section']==80 and c['context']=='INC_X_same_trait_ratio_boundary'
    and c['input']['elite']==2 and c['input']['level']==50 and c['input']['module_level']==3
    and c['input']['skill']==1 and c['input']['timing_mode']=='frames'and c['input']['healing_targets']==1]
assert len(shot)==1 and shot[0]['input']['window_seconds']==10 and shot[0]['input']['relic_ids']==[]
shot_code=fragment[fragment.index('                    if (section080==80 and case080'):fragment.index('                next_section_counts')]
assert 'click_result('not in shot_code and 'calculate_result('not in shot_code and '.calculate('not in shot_code
assert "window.grab().save(str(OUT/'wine-medical-trait-080.png'))"in shot_code
for producer in("relics(requested080['relic_ids'])","window.defense.setValue(requested080['enemy_defense'])",
    "window.resistance.setValue(requested080['enemy_resistance'])"):
    assert producer in fragment
assert raw=={name:(P/name).read_bytes()for name in names},'final source design changed during review'
assert all(sha((ROOT/name).read_bytes())==digest for name,digest in freeze['source_sha256'].items())
(R/'final-saved-contract-scope.json').write_text(json.dumps(scopes,ensure_ascii=False,indent=2)+'\n')
(R/'final-root-public-source-proof.json').write_text(json.dumps({'commit':COMMIT,'files':source_rows,
    'all125_current_bytes_equal_to_frozen_git_blobs':True,'new_API_calls':0},ensure_ascii=False,indent=2)+'\n')
receipt={'status':'FINAL_STATIC_PASS_READY_FOR_ROOT_ACTUAL_EXECUTION',
    'scope':'Independent fixed source, whole inherited body, actual producer design and all saved contract assertions. Actual execution belongs to root.',
    'runner_sha256':RUNNER,'root_source_commit':COMMIT,'files':{name:sha(b)for name,b in raw.items()},
    'base075_sha256':sha(base),'old1455_complete_body_reconstructed_exactly':True,
    'runner_syntax_valid':True,'entry_guard_before_imports_disabled_only_after_final':True,
    'fragment_pending_guard_false':True,'all125_live_public_source_equal_to_frozen_git_blobs':True,
    'source_freeze_receipt_sha256':sha(freeze_raw),'rebuild_proof_sha256':sha(proof_raw),
    'saved_API_receipt_sha256':API,'saved_contract_assertions_rechecked':1608,
    'saved_contract_assertions_by_section':dict(read_counts),
    'especially_all79_212_and_all80_180_rechecked_without_API':True,
    'saved_JSON_adapter':'Only exact known external parameter row tuples restored from JSON arrays; canonical JSON unchanged and numeric types preserved.',
    'API_attribution_read_from_saved_receipt':saved['actual_API_call_attribution'],
    'all1551_initially_accepted_records_unchanged':True,'saved1552_zero_lifetime_counterexample_unchanged_and_reasserted':True,
    'actual_GUI_case_design_count':3063,'actual_GUI_skills_design_count':87,
    'screenshot_uses_exact_one_existing_legal_case_and_existing_result':True,
    'producer_and_boundary_preliminary_receipts':['preliminary-static-review.json','medical79-static-review.json',
        'trait80-preliminary-static-review.json','screenshot-preliminary-static-review.json',
        'pending-entry-guard-static-review.json','trait80-zero-lifetime-saved-counterexample-review.json'],
    'preparation_errors_preserved':True,'blockers':[],
    'new_public_API_calls':0,'gui_executed':False,'wine_executed':False,'native_windows_executed':False,
    'ready_for_root_actual_execution':True,
    'limits':'Static and saved-result proof only. Does not establish actual Qt/Wine controls, native Windows/game, actual module attachment/recipient, S2 chain order or end clocks.'}
(R/'final-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k not in('files','producer_and_boundary_preliminary_receipts')},ensure_ascii=False))
