"""Hash-check, copy and seal existing evidence only: zero API execution."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
CHILD = Path('/workspace/.continuation/p2-boolean-consumer-083-independent-static')
BASE = 'ea7866be6f2a8e89d382ec2982a45f1cb9231141'
def sha(data): return hashlib.sha256(data).hexdigest()
def save(name, value):
    with (OUT/name).open('x', encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False); f.write('\n')
freeze = json.loads((OUT/'freeze083.json').read_bytes())
assert freeze['fixed_commit'] == BASE
for rel, record in freeze['public_package'].items():
    data = (OUT/'fixed-public-package'/rel).read_bytes()
    assert len(data) == record['bytes'] and sha(data) == record['sha256']
    assert subprocess.check_output(['git','show',f'{BASE}:{rel}'],cwd=REPO) == data
for record in freeze['selected_static_consumers']:
    data = (OUT/record['archive_path']).read_bytes()
    assert len(data) == record['bytes'] and sha(data) == record['sha256']
    assert subprocess.check_output(['git','show',f'{BASE}:{record["path"]}'],cwd=REPO) == data
review = json.loads((OUT/'public-observation-review083.json').read_bytes())
assert review['actual_public_calls'] == 8 and review['successful_results'] == 7 and review['exact_errors'] == 1
rows = json.loads((OUT/'public-counterexamples083.json').read_bytes())['rows']
assert len(rows) == 8
for row in rows:
    assert json.loads((OUT/f'public-{row["case"]}.json').read_bytes()) == row
old = json.loads((OUT/'reused062-observations083.json').read_bytes())
assert len(old['rows']) == 28
for record in old['prior_bindings']:
    data = Path(record['path']).read_bytes()
    assert len(data) == record['bytes'] and sha(data) == record['sha256']
child_manifest = CHILD/'public-artifacts-manifest.json'
assert sha(child_manifest.read_bytes()) == 'ca5509e3d6d5b2d57fbedd33c84c1258c044c9d8917942160a089dae4b7e3f92'
child_rows = json.loads(child_manifest.read_bytes())['files']
assert len(child_rows) == 12
copied = []
for record in child_rows:
    data = Path(record['source_path']).read_bytes()
    assert len(data) == record['bytes'] and sha(data) == record['sha256']
    target = OUT/'independent-static'/record['archive_path']
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    assert target.read_bytes() == data
    copied.append(str(target.relative_to(OUT)))
target = OUT/'independent-static/public-artifacts-manifest.json'
with target.open('xb') as f:f.write(child_manifest.read_bytes())
copied.append(str(target.relative_to(OUT)))
save('seal-validation083.json', {'status':'passed','fixed_commit':BASE,'production_package_blobs_checked':len(freeze['public_package']),
    'selected_consumer_blobs_checked':len(freeze['selected_static_consumers']),
    'all_8_per_case_rows_match_aggregate':True,'reused_prior_rows':28,'prior_bound_files_rechecked':4,
    'child_manifest_rows_verified_and_copied':12,'child_manifest_also_copied':True,
    'new_API_calls':0,'tracked_mutations':False,'tests':0,'Qt':False,'Wine':False})
names = ['NOTE.md','source-scope083.json','audit_boolean083.py','audit-boolean083.log',
         'initial-prep1-audit_boolean083.py','initial-prep1-audit-boolean083.log',
         'initial-name-preparation-NOTE.md','preparation-diagnostics083.json','original-objects083.json',
         'reused062-observations083.json','freeze083.json','qt-option-rows083.json',
         'public-counterexamples083.json','public-observation-review083.json','seal_source083.py','seal-validation083.json']
names += [f'public-{row["case"]}.json' for row in rows]
names += [record['archive_path'] for record in freeze['selected_static_consumers']]
names += copied
assert len(names) == len(set(names))
save('handoff.json', {'status':'final_sealed_source_and_baseline_counterexamples', 'fixed_commit':BASE,
    'candidate_review_sha256':sha((OUT/'public-observation-review083.json').read_bytes()),
    'source_scope_sha256':sha((OUT/'source-scope083.json').read_bytes()),
    'fresh_public_calls':8,'successful_results':7,'exact_old_errors':1,
    'child_static_fresh_calls':0,'all_Qt_evidence_is_static_production_binding':True,
    'author_design_approved_scope':'two actual neural owners, all available skills, prepared scenario post-report str guards',
    'formal83_draft_numeric_validation':'pending separate fixed-author-package review; no claim of implementation verification',
    'Orchid_candidate':'retained for later section; original 2 near counterexamples may be reused with source binding',
    'not_additional_mechanism_or_global_input_domain_authorization':True,
    'preserved_preparation_evidence':True,'tracked_mutations':False,'tests_executed':0,'Qt_executed':False,'Wine_executed':False,
    'public_artifacts_excluding_this_handoff_and_manifest':len(names)})
names.append('handoff.json')
manifest = []
for name in sorted(names):
    path = OUT/name; data = path.read_bytes()
    manifest.append({'source_path':str(path),'archive_path':name,'bytes':len(data),'sha256':sha(data)})
save('public-artifacts-manifest.json',{'format_version':1,'status':'final_sealed_readonly',
    'files':manifest,'actual_public_calls':8,'fresh_calls_in_this_seal':0,
    'excluded_execution_copy':'fixed-public-package/, bound by freeze083.json and 125 exact git blobs',
    'bytes':sum(x['bytes'] for x in manifest)})
assert all(len(Path(row['source_path']).read_bytes())==row['bytes'] and sha(Path(row['source_path']).read_bytes())==row['sha256'] for row in manifest)
print(json.dumps({'status':'passed','public_files':len(manifest),'bytes':sum(x['bytes'] for x in manifest),
    'fresh_public_calls':8,'handoff_sha256':sha((OUT/'handoff.json').read_bytes()),
    'manifest_sha256':sha((OUT/'public-artifacts-manifest.json').read_bytes())},ensure_ascii=False))
