"""Additive manifest transport, reusing the immutable already-reviewed237 file list."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OLD=Path('/workspace/.continuation/ui-090-final')
def sha(b):return hashlib.sha256(b).hexdigest()
def f(p,a):return {'source_path':str(p),'archive_path':a,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def save(name,obj):
    p=HERE/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');return f(p,name)
original_mf=OLD/'public-artifacts-manifest-final-runner090.json'
assert sha(original_mf.read_bytes())=='7675565345cd55711cb975c83dc49c433d1be7cfe0054634bc68938576822e10'
packet=json.loads(original_mf.read_bytes());assert packet['file_count']==237
runner=HERE/'wine-ui-smoke-090-final-gate-revision.py'
assert sha(runner.read_bytes())=='9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
handoff=save('handoff-two-gate-revision090.json',{'format_version':1,'status':'FINAL_STABLE_TWO_GATE_ONLY_REVISION_PENDING_ROOT_DIFFERENCE_REVIEW_AND_SOLE_ACTUAL_QT','runner':f(runner,'wine-ui-smoke-090-final-gate-revision.py'),'original237_manifest':f(original_mf,'original237-manifest.json'),'original_frozen_runner_immutable':f(OLD/'wine-ui-smoke-090-final.py','original-frozen-runner.py'),'original_named_actual730_binding':f(OLD/'actual-root090-source-binding.json','original-source-binding.json'),'original_old4217_inverse':f(OLD/'old4217-byte-inverse-proof090.json','original-old4217-inverse.json'),'exact_two_gate_inverse_proof':f(HERE/'two-gate-diff-and-reachability-proof090.json','two-gate-diff-and-reachability-proof090.json'),'scope':f(HERE/'runner-scope-and-source-freeze090-revision.json','runner-scope-and-source-freeze090-revision.json'),'planned_total':4283,'planned_new_rows':66,'fresh_API_helper_formatter_tests_Qt_Wine':0,'all_passed_original237_source730_old4217_and_preflights_reused_not_reexecuted':True,'original_qualification_row_labels_preserved':True,'root_sole_execution':'After bounded difference static PASS, root copies only this revised runner to /workspace/.compat/wine-ui-smoke-090.py. The original final/pending runners remain immutable, unexecuted.','manifest_name':'public-artifacts-manifest-two-gate-revision090.json','original237_list_transport_without_duplicate_file_copy':True})
own=[f(p,'two-gate-revision090/'+p.relative_to(HERE).as_posix()) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='public-artifacts-manifest-two-gate-revision090.json' and '__pycache__' not in p.parts]
oldrows=[{**r,'archive_path':'original-final237/'+r['archive_path']} for r in packet['files']]
rows=own+oldrows+[f(original_mf,'original-final237/public-artifacts-manifest-final-runner090.json')]
assert len({r['source_path'] for r in rows})==len(rows)
assert len({r['archive_path'] for r in rows})==len(rows)
mf=save('public-artifacts-manifest-two-gate-revision090.json',{'format_version':1,'status':'FINAL_STABLE_MINIMAL_REVISION_TRANSPORT','files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'manifest_self_excluded':True,'original237_immutable_all_evidence_transported_from_its_existing_passed_manifest':True,'old_full_formal_and_preflight_calls_repeated':False,'fresh_API_helper_formatter_tests_Qt_Wine':0})
print(json.dumps({'manifest':mf,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'handoff':handoff,'runner':f(runner,runner.name)}))
